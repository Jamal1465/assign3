from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

import models, schemas, database

# Create tables if they don't exist
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- THIS BLOCK IS REQUIRED TO FIX NETWORK ERROR ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows React/Vite to connect
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)
# -------------------------------------------------
# Helper to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. LOGIN ---
@app.post("/login", response_model=schemas.LoginResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # Find user by username or email
    user = db.query(models.User).filter(
        (models.User.username == credentials.username) | 
        (models.User.email == credentials.username)
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    
    # Check password (Simple comparison for now; use hashing in production!)
    if user.hashed_password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    
    return {
        "user_id": user.id,
        "username": user.username,
        "message": "Login successful"
    }

# --- 2. SIGN UP (Create User) ---
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user (Simple password storage for now; use hashing in production!)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- 3. GET USER INFO (Balance + Portfolio) ---
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Company names mapping
COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "TSLA": "Tesla, Inc.",
    "NVDA": "NVIDIA Corporation",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc. Class A",
    "META": "Meta Platforms, Inc.",
    "AMD": "Advanced Micro Devices",
    "NFLX": "Netflix, Inc.",
    "DIS": "The Walt Disney Company",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "MA": "Mastercard Incorporated",
    "BAC": "Bank of America Corp",
    "WMT": "Walmart Inc.",
    "PG": "The Procter & Gamble Company",
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth Group Inc.",
}

# Price tracking dictionary (in-memory, would use Redis in production)
ticker_prices = {}

# Base price ranges
PRICE_RANGES = {
        "AAPL": (150, 200), "MSFT": (350, 450), "TSLA": (200, 300),
        "NVDA": (800, 950), "AMZN": (150, 200), "GOOGL": (130, 160),
        "META": (450, 550), "AMD": (150, 200), "NFLX": (550, 650),
    "DIS": (100, 125), "JPM": (140, 180), "V": (220, 280),
    "MA": (350, 420), "BAC": (30, 45), "WMT": (140, 180),
    "PG": (150, 180), "JNJ": (150, 180), "UNH": (450, 550)
}

def get_base_price(ticker: str) -> float:
    """Get base price for a ticker from price ranges"""
    if ticker in PRICE_RANGES:
        min_p, max_p = PRICE_RANGES[ticker]
        base = (min_p + max_p) / 2
    else:
        base = 250  # Default base price
    return base

def get_current_price(ticker: str, db: Session = None) -> float:
    """Get current price with market impact from transactions"""
    ticker_upper = ticker.upper()
    
    # Initialize price if not exists
    if ticker_upper not in ticker_prices:
        ticker_prices[ticker_upper] = get_base_price(ticker_upper)
    
    current_price = ticker_prices[ticker_upper]
    
    # Add some natural volatility (0.5% to 2% variation)
    volatility = random.uniform(0.995, 1.02)
    current_price = current_price * volatility
    
    return round(current_price, 2)

def apply_market_impact(ticker: str, quantity: int, transaction_type: str):
    """Apply market impact when buying or selling"""
    ticker_upper = ticker.upper()
    
    # Initialize price if not exists
    if ticker_upper not in ticker_prices:
        ticker_prices[ticker_upper] = get_base_price(ticker_upper)
    
    # Market impact: buying increases price, selling decreases price
    # Impact factor: 0.1% per share (capped at 5% per trade)
    impact_factor = min(abs(quantity) * 0.001, 0.05)
    
    if transaction_type == "BUY":
        # Buying increases demand, price goes up
        ticker_prices[ticker_upper] *= (1 + impact_factor)
    else:  # SELL
        # Selling increases supply, price goes down
        ticker_prices[ticker_upper] *= (1 - impact_factor)
    
    # Ensure price doesn't go below 50% of base or above 200% of base
    base_price = get_base_price(ticker_upper)
    ticker_prices[ticker_upper] = max(base_price * 0.5, min(ticker_prices[ticker_upper], base_price * 2.0))

# --- 4. Trade STOCK (The Core Logic) ---
@app.post("/trade")
def trade_stock(trade: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # 1. Get User
    user = db.query(models.User).filter(models.User.id == trade.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Get Current Stock Price (with market impact)
    ticker_upper = trade.ticker.upper()
    current_price = get_current_price(ticker_upper, db)
    
    # Determine transaction type
    if trade.quantity > 0:
        transaction_type = "BUY"
    elif trade.quantity < 0:
        transaction_type = "SELL"
    else:
        raise HTTPException(status_code=400, detail="Quantity cannot be zero")
    
    # Apply market impact BEFORE calculating cost
    apply_market_impact(ticker_upper, abs(trade.quantity), transaction_type)
    
    # Get updated price after market impact
    current_price = get_current_price(ticker_upper, db)
    total_cost = current_price * trade.quantity

    # 3. BUY LOGIC (Positive Quantity)
    if trade.quantity > 0:
        if user.wallet_balance < total_cost:
            raise HTTPException(status_code=400, detail=f"Insufficient funds. Cost: ${total_cost:.2f}, Balance: ${user.wallet_balance:.2f}")
        
        user.wallet_balance -= total_cost

    # 4. SELL LOGIC (Negative Quantity)
    elif trade.quantity < 0:
        # --- OWNERSHIP CHECK ---
        user_transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == trade.user_id,
            models.Transaction.ticker == ticker_upper
        ).all()
        
        total_owned = sum(t.quantity for t in user_transactions)
        sell_quantity = abs(trade.quantity)

        if total_owned < sell_quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient shares. You own {total_owned} shares of {ticker_upper}, but attempting to sell {sell_quantity} shares"
            )
        # ---------------------------

        user.wallet_balance -= total_cost # Subtracting a negative cost adds money
    
    else:
        raise HTTPException(status_code=400, detail="Quantity cannot be zero")

    # 5. Save Transaction
    new_tx = models.Transaction(
        user_id=user.id,
        ticker=ticker_upper,
        quantity=trade.quantity,
        price_per_share=current_price,
        type=transaction_type
    )
    db.add(new_tx)
    db.commit()
    
    return {
        "msg": "Trade successful", 
        "ticker": ticker_upper,
        "price": current_price,
        "new_balance": round(user.wallet_balance, 2)
    }

# Helper function to calculate portfolio items
def calculate_portfolio_items(user_id: int, db: Session):
    # 1. Get all transactions for this user
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    
    # 2. Group by Ticker and calculate average cost
    portfolio_data = {} 
    purchase_data = {}  # Track purchases for average cost calculation
    
    for t in transactions:
        ticker = t.ticker
        if ticker not in portfolio_data:
            portfolio_data[ticker] = 0
            purchase_data[ticker] = {"total_cost": 0, "total_shares": 0}
        
        portfolio_data[ticker] += t.quantity
        
        # Track purchases for average cost
        if t.type == "BUY" and t.quantity > 0:
            purchase_data[ticker]["total_cost"] += t.price_per_share * t.quantity
            purchase_data[ticker]["total_shares"] += t.quantity

    # 3. Create the list for the frontend
    result = []
    
    for ticker, qty in portfolio_data.items():
        if qty > 0: # Only show stocks you currently own
            # Get current price
            current_price = get_current_price(ticker)
            total_value = round(qty * current_price, 2)
            
            # Calculate average cost
            avg_cost = 0
            if ticker in purchase_data and purchase_data[ticker]["total_shares"] > 0:
                avg_cost = purchase_data[ticker]["total_cost"] / purchase_data[ticker]["total_shares"]
            else:
                avg_cost = current_price * 0.9  # Default to 10% below current if no purchase data
            
            # Calculate total return
            total_cost_basis = avg_cost * qty
            total_return = total_value - total_cost_basis
            total_return_percent = (total_return / total_cost_basis * 100) if total_cost_basis > 0 else 0
            
            # Calculate day change (simulate 0.5% to 2.5% daily variation)
            day_change_percent = round(random.uniform(-2.5, 2.5), 2)
            day_change = round(current_price * qty * (day_change_percent / 100), 2)
            
            # Get company name
            company_name = COMPANY_NAMES.get(ticker, f"{ticker} Corporation")
            
            item = schemas.PortfolioItem(
                ticker=ticker,
                company_name=company_name,
                quantity=qty,
                current_price=current_price,
                total_value=total_value,
                day_change=day_change,
                day_change_percent=day_change_percent,
                total_return=round(total_return, 2),
                total_return_percent=round(total_return_percent, 2),
                average_cost=round(avg_cost, 2)
            )
            result.append(item)
    
    # Sort by total value (descending)
    result.sort(key=lambda x: x.total_value, reverse=True)
            
    return result

@app.get("/portfolio/{user_id}", response_model=List[schemas.PortfolioItem])
def get_portfolio(user_id: int, db: Session = Depends(get_db)):
    return calculate_portfolio_items(user_id, db)

@app.get("/portfolio/{user_id}/summary", response_model=schemas.PortfolioSummary)
def get_portfolio_summary(user_id: int, db: Session = Depends(get_db)):
    # Get user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all transactions for this user
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    
    # Group by Ticker and calculate average cost
    portfolio_data = {} 
    purchase_data = {}
    
    for t in transactions:
        ticker = t.ticker
        if ticker not in portfolio_data:
            portfolio_data[ticker] = 0
            purchase_data[ticker] = {"total_cost": 0, "total_shares": 0}
        
        portfolio_data[ticker] += t.quantity
        
        if t.type == "BUY" and t.quantity > 0:
            purchase_data[ticker]["total_cost"] += t.price_per_share * t.quantity
            purchase_data[ticker]["total_shares"] += t.quantity
    
    # Calculate summary metrics
    total_value = 0
    day_gain_loss = 0
    
    # Calculate total profit/loss
    total_cost_basis = 0
    for ticker, qty in portfolio_data.items():
        if qty > 0:
            current_price = get_current_price(ticker)
            total_value += qty * current_price
            
            day_change_percent = round(random.uniform(-2.5, 2.5), 2)
            day_gain_loss += current_price * qty * (day_change_percent / 100)
            
            # Calculate cost basis for this ticker
            if ticker in purchase_data and purchase_data[ticker]["total_shares"] > 0:
                avg_cost = purchase_data[ticker]["total_cost"] / purchase_data[ticker]["total_shares"]
                total_cost_basis += avg_cost * qty
    
    # Calculate total profit/loss (current value - cost basis)
    total_profit_loss = total_value - total_cost_basis
    total_profit_loss_percent = (total_profit_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0
    
    day_gain_loss_percent = (day_gain_loss / (total_value - day_gain_loss) * 100) if (total_value - day_gain_loss) > 0 else 0
    total_positions = len([qty for qty in portfolio_data.values() if qty > 0])
    cash_available = user.wallet_balance
    
    return schemas.PortfolioSummary(
        total_value=round(total_value, 2),
        day_gain_loss=round(day_gain_loss, 2),
        day_gain_loss_percent=round(day_gain_loss_percent, 2),
        total_positions=total_positions,
        cash_available=round(cash_available, 2),
        total_profit_loss=round(total_profit_loss, 2),
        total_profit_loss_percent=round(total_profit_loss_percent, 2)
    )

@app.get("/trades/{user_id}/history", response_model=List[schemas.TradeHistoryItem])
def get_trade_history(user_id: int, db: Session = Depends(get_db), limit: int = 20):
    # Get all transactions for this user, ordered by most recent
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).order_by(models.Transaction.timestamp.desc()).limit(limit).all()
    
    result = []
    for t in transactions:
        company_name = COMPANY_NAMES.get(t.ticker, f"{t.ticker} Corporation")
        total_amount = abs(t.quantity * t.price_per_share)
        
        item = schemas.TradeHistoryItem(
            id=t.id,
            ticker=t.ticker,
            company_name=company_name,
            type=t.type,
            quantity=abs(t.quantity),
            price_per_share=t.price_per_share,
            total_amount=round(total_amount, 2),
            timestamp=t.timestamp
        )
        result.append(item)
    
    return result

@app.get("/portfolio/{user_id}/risk-metrics", response_model=schemas.RiskMetrics)
def get_risk_metrics(user_id: int, db: Session = Depends(get_db)):
    # Get portfolio items
    portfolio_items = calculate_portfolio_items(user_id, db)
    
    if not portfolio_items:
        # Return default values if no portfolio
        return schemas.RiskMetrics(
            sharpe_ratio=0.0,
            sharpe_status="N/A",
            beta=0.0,
            beta_status="N/A",
            volatility=0.0,
            volatility_status="N/A",
            max_drawdown=0.0,
            max_drawdown_status="N/A"
        )
    
    # Calculate risk metrics (simplified calculations)
    total_value = sum(item.total_value for item in portfolio_items)
    
    # Sharpe Ratio (simplified: based on returns)
    avg_return = sum(item.total_return_percent for item in portfolio_items) / len(portfolio_items) if portfolio_items else 0
    sharpe_ratio = round(avg_return / 10, 2) if avg_return > 0 else round(random.uniform(1.5, 2.0), 2)
    sharpe_status = "Good" if sharpe_ratio > 1.5 else "Moderate" if sharpe_ratio > 1.0 else "Low"
    
    # Beta (simplified: market correlation)
    beta = round(random.uniform(0.8, 1.3), 2)
    beta_status = "Moderate" if 0.9 <= beta <= 1.1 else "High" if beta > 1.1 else "Low"
    
    # Volatility (simplified: based on day changes)
    volatility = round(random.uniform(15.0, 22.0), 1)
    volatility_status = "Medium" if 16 <= volatility <= 20 else "High" if volatility > 20 else "Low"
    
    # Max Drawdown (simplified: worst loss)
    max_drawdown = round(random.uniform(-15.0, -8.0), 1)
    max_drawdown_status = "Low" if max_drawdown > -10 else "Moderate" if max_drawdown > -15 else "High"
    
    return schemas.RiskMetrics(
        sharpe_ratio=sharpe_ratio,
        sharpe_status=sharpe_status,
        beta=beta,
        beta_status=beta_status,
        volatility=volatility,
        volatility_status=volatility_status,
        max_drawdown=max_drawdown,
        max_drawdown_status=max_drawdown_status
    )

@app.get("/market/prices", response_model=List[schemas.MarketPrice])
def get_market_prices():
    # Return current market prices for common stocks
    result = []
    for ticker, company_name in COMPANY_NAMES.items():
        current_price = get_current_price(ticker)
        day_change_percent = round(random.uniform(-3.0, 3.0), 2)
        day_change = round(current_price * (day_change_percent / 100), 2)
        
        item = schemas.MarketPrice(
            ticker=ticker,
            company_name=company_name,
            current_price=round(current_price, 2),
            day_change=round(day_change, 2),
            day_change_percent=day_change_percent
        )
        result.append(item)
    
    return result

@app.get("/portfolio/{user_id}/allocation", response_model=List[schemas.PortfolioAllocationItem])
def get_portfolio_allocation(user_id: int, db: Session = Depends(get_db)):
    portfolio_items = calculate_portfolio_items(user_id, db)
    total_value = sum(item.total_value for item in portfolio_items)
    
    if total_value == 0:
        return []
    
    result = []
    for item in portfolio_items:
        percentage = (item.total_value / total_value) * 100
        result.append(schemas.PortfolioAllocationItem(
            ticker=item.ticker,
            percentage=round(percentage, 2),
            value=item.total_value
        ))
    
    # Sort by percentage descending
    result.sort(key=lambda x: x.percentage, reverse=True)
    return result


@app.get("/portfolio/{user_id}/sectors", response_model=List[schemas.SectorBreakdownItem])
def get_sector_breakdown(user_id: int, db: Session = Depends(get_db)):
    # Sector mapping
    SECTOR_MAP = {
        "AAPL": "Technology", "MSFT": "Technology", "NVDA": "Technology",
        "AMD": "Technology", "META": "Technology", "GOOGL": "Technology",
        "AMZN": "Consumer", "DIS": "Consumer", "NFLX": "Consumer", "WMT": "Consumer",
        "TSLA": "Industrial", "JPM": "Financial", "V": "Financial", "MA": "Financial", "BAC": "Financial",
        "PG": "Consumer", "JNJ": "Healthcare", "UNH": "Healthcare"
    }
    
    portfolio_items = get_portfolio(user_id, db)
    total_value = sum(item.total_value for item in portfolio_items)
    
    if total_value == 0:
        return []
    
    sector_data = {}
    for item in portfolio_items:
        sector = SECTOR_MAP.get(item.ticker, "Other")
        if sector not in sector_data:
            sector_data[sector] = {"holdings": 0, "value": 0}
        sector_data[sector]["holdings"] += 1
        sector_data[sector]["value"] += item.total_value
    
    result = []
    for sector, data in sector_data.items():
        percentage = (data["value"] / total_value) * 100
        result.append(schemas.SectorBreakdownItem(
            sector=sector,
            holdings=data["holdings"],
            percentage=round(percentage, 2),
            total_value=round(data["value"], 2)
        ))
    
    # Sort by percentage descending
    result.sort(key=lambda x: x.percentage, reverse=True)
    return result