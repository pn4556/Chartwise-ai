"""
Database models for Chartwise AI
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # User stats
    portfolio_value = Column(Float, default=10000.0)
    trades_count = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String)
    market_cap = Column(Float)
    last_price = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    predictions = relationship("Prediction", back_populates="stock")

class Crypto(Base):
    __tablename__ = "cryptos"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    last_price = Column(Float)
    market_cap = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    predictions = relationship("Prediction", back_populates="crypto")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    asset_type = Column(String)  # 'stock' or 'crypto'
    
    # Scores (0-100)
    bullish_score = Column(Float)
    confidence = Column(Float)
    
    # Technical indicators
    rsi = Column(Float)
    macd_signal = Column(String)
    ma_signal = Column(String)
    bb_signal = Column(String)
    
    # Individual component scores
    technical_score = Column(Float)
    trend_score = Column(Float)
    volume_score = Column(Float)
    
    # Prediction metadata
    timeframe = Column(String, default="1d")  # 1d, 1w, 1m
    prediction_date = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    
    # Relationships
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    crypto_id = Column(Integer, ForeignKey("cryptos.id"), nullable=True)
    
    stock = relationship("Stock", back_populates="predictions")
    crypto = relationship("Crypto", back_populates="predictions")

class WatchlistItem(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    symbol = Column(String)
    asset_type = Column(String)  # 'stock' or 'crypto'
    added_date = Column(DateTime, default=datetime.utcnow)
    alert_threshold = Column(Float, nullable=True)  # Price alert threshold

class PaperTrade(Base):
    __tablename__ = "paper_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    symbol = Column(String)
    asset_type = Column(String)
    direction = Column(String)  # 'long' or 'short'
    entry_price = Column(Float)
    entry_date = Column(DateTime, default=datetime.utcnow)
    exit_price = Column(Float, nullable=True)
    exit_date = Column(DateTime, nullable=True)
    quantity = Column(Float)
    
    # Trade metadata
    status = Column(String, default="open")  # open, closed
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    
    # Analysis
    thesis = Column(String, nullable=True)
    exit_reason = Column(String, nullable=True)
    lessons = Column(String, nullable=True)

class UserPortfolio(Base):
    __tablename__ = "user_portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    cash_balance = Column(Float, default=10000.0)  # Start with $10k
    total_value = Column(Float, default=10000.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
