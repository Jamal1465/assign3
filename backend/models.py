from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    # Hashed password for security
    hashed_password = Column(String)
    # Start every user with dummy money (e.g., $10,000)
    wallet_balance = Column(Float, default=10000.0)

    # Relationship to transactions
    transactions = relationship("Transaction", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker = Column(String)  # The Stock Symbol (e.g., AAPL)
    quantity = Column(Integer) # How many shares
    price_per_share = Column(Float) # Price at purchase/sale
    type = Column(String) # "BUY" or "SELL"
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Link back to User
    owner = relationship("User", back_populates="transactions")