from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str  # Can be either username or email
    password: str

class UserResponse(UserBase):
    id: int
    wallet_balance: float
    # We don't return the password for security
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user_id: int
    username: str
    message: str = "Login successful"

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    ticker: str
    quantity: int

class TransactionCreate(TransactionBase):
    user_id: int
    # Logic: If quantity > 0 it's a BUY, if < 0 it's a SELL

class TransactionResponse(TransactionBase):
    id: int
    price_per_share: float
    type: str
    timestamp: datetime
    class Config:
        from_attributes = True

# --- Portfolio Schema (For the Dashboard) ---
class PortfolioItem(BaseModel):
    ticker: str
    company_name: str
    quantity: int
    current_price: float
    total_value: float
    day_change: float      # Dollar change for the day
    day_change_percent: float  # Percentage change for the day
    total_return: float    # Total return in dollars
    total_return_percent: float  # Total return percentage
    average_cost: float    # Average purchase price

class PortfolioSummary(BaseModel):
    total_value: float
    day_gain_loss: float
    day_gain_loss_percent: float
    total_positions: int
    cash_available: float
    total_profit_loss: float
    total_profit_loss_percent: float

# --- Risk Metrics Schema ---
class RiskMetrics(BaseModel):
    sharpe_ratio: float
    sharpe_status: str
    beta: float
    beta_status: str
    volatility: float
    volatility_status: str
    max_drawdown: float
    max_drawdown_status: str

# --- Trade History Schema ---
class TradeHistoryItem(BaseModel):
    id: int
    ticker: str
    company_name: str
    type: str  # "BUY" or "SELL"
    quantity: int
    price_per_share: float
    total_amount: float
    timestamp: datetime

# --- Market Price Schema ---
class MarketPrice(BaseModel):
    ticker: str
    company_name: str
    current_price: float
    day_change: float
    day_change_percent: float

# --- Portfolio Allocation Item ---
class PortfolioAllocationItem(BaseModel):
    ticker: str
    percentage: float
    value: float

# --- Sector Breakdown Item ---
class SectorBreakdownItem(BaseModel):
    sector: str
    holdings: int
    percentage: float
    total_value: float

# --- Performance Data Point ---
class PerformanceDataPoint(BaseModel):
    day: int
    value: float