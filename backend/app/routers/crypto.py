"""
Crypto API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.data_service import DataService

router = APIRouter()

class CryptoResponse(BaseModel):
    symbol: str
    name: str
    price: float
    change_24h: float
    change_24h_percent: float
    volume_24h: float
    market_cap: float

class CryptoPredictionResponse(BaseModel):
    symbol: str
    bullish_score: float
    confidence: float
    recommendation: str
    signals: dict

@router.get("/", response_model=List[CryptoResponse])
async def get_cryptos(db: Session = Depends(get_db)):
    """Get list of tracked cryptocurrencies"""
    # Using yfinance for crypto as well (e.g., BTC-USD)
    cryptos = [
        {'symbol': 'BTC-USD', 'name': 'Bitcoin'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum'},
        {'symbol': 'SOL-USD', 'name': 'Solana'},
        {'symbol': 'ADA-USD', 'name': 'Cardano'},
        {'symbol': 'DOT-USD', 'name': 'Polkadot'},
    ]
    
    results = []
    for crypto in cryptos:
        try:
            data = TechnicalAnalysisService.get_data(crypto['symbol'], days=2)
            if data and len(data) >= 2:
                current = data[-1]['close']
                previous = data[-2]['close']
                change = current - previous
                change_pct = (change / previous) * 100
                volume = data[-1]['volume']
                
                results.append(CryptoResponse(
                    symbol=crypto['symbol'],
                    name=crypto['name'],
                    price=round(current, 2),
                    change_24h=round(change, 2),
                    change_24h_percent=round(change_pct, 2),
                    volume_24h=volume,
                    market_cap=0  # Would need CoinGecko for accurate market cap
                ))
        except:
            continue
    
    return results

@router.get("/{symbol}/prediction", response_model=CryptoPredictionResponse)
async def get_crypto_prediction(symbol: str, db: Session = Depends(get_db)):
    """Get AI prediction for a cryptocurrency"""
    symbol = symbol.upper()
    
    prediction = TechnicalAnalysisService.analyze(symbol)
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Could not analyze crypto")
    
    return CryptoPredictionResponse(
        symbol=prediction.symbol,
        bullish_score=prediction.bullish_score,
        confidence=prediction.confidence,
        recommendation=prediction.recommendation,
        signals=prediction.signals
    )
