"""
Stock API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.data_service import DataService
import yfinance as yf

router = APIRouter()

class StockResponse(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    
    class Config:
        from_attributes = True

class StockDetailResponse(StockResponse):
    pe_ratio: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    avg_volume: Optional[int] = None

class PredictionResponse(BaseModel):
    symbol: str
    bullish_score: float
    confidence: float
    recommendation: str
    signals: dict
    technical_score: float
    trend_score: float
    volume_score: float
    rsi: Optional[float] = None
    calculated_at: datetime

@router.get("/", response_model=List[StockResponse])
async def get_stocks(db: Session = Depends(get_db)):
    """Get list of all tracked stocks"""
    stocks = DataService.get_popular_stocks()
    return stocks

@router.get("/search")
async def search_stocks(query: str, db: Session = Depends(get_db)):
    """Search for stocks by symbol or name"""
    results = DataService.search_stocks(query)
    return results

@router.get("/{symbol}", response_model=StockDetailResponse)
async def get_stock_detail(symbol: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific stock"""
    stock = DataService.get_stock_detail(symbol.upper())
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.get("/{symbol}/prediction", response_model=PredictionResponse)
async def get_stock_prediction(symbol: str, db: Session = Depends(get_db)):
    """Get AI prediction for a specific stock"""
    symbol = symbol.upper()
    
    # Calculate prediction using technical analysis
    prediction = TechnicalAnalysisService.analyze(symbol)
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Could not analyze stock")
    
    # Get current indicators for additional data
    data = TechnicalAnalysisService.get_data(symbol)
    if data:
        prices = [d['close'] for d in data]
        rsi = TechnicalAnalysisService.calculate_rsi(prices)
    else:
        rsi = None
    
    return PredictionResponse(
        symbol=prediction.symbol,
        bullish_score=prediction.bullish_score,
        confidence=prediction.confidence,
        recommendation=prediction.recommendation,
        signals=prediction.signals,
        technical_score=prediction.technical_score,
        trend_score=prediction.trend_score,
        volume_score=prediction.volume_score,
        rsi=rsi,
        calculated_at=datetime.now()
    )

@router.get("/{symbol}/history")
async def get_stock_history(
    symbol: str, 
    period: str = "1y",
    interval: str = "1d",
    db: Session = Depends(get_db)
):
    """Get historical price data for a stock"""
    symbol = symbol.upper()
    history = DataService.get_price_history(symbol, period, interval)
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    return history
