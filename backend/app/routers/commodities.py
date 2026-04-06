"""
Commodities API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.services.technical_analysis import TechnicalAnalysisService
from app.routers.predictions import DEFAULT_COMMODITIES, get_asset_type

router = APIRouter()

# Commodity name mapping
COMMODITY_NAMES = {
    # Precious Metals
    'GC=F': 'Gold',
    'SI=F': 'Silver',
    'PL=F': 'Platinum',
    'PA=F': 'Palladium',
    # Energy
    'CL=F': 'Crude Oil (WTI)',
    'BZ=F': 'Brent Crude Oil',
    'NG=F': 'Natural Gas',
    'RB=F': 'RBOB Gasoline',
    'HO=F': 'Heating Oil',
    # Industrial Metals
    'HG=F': 'Copper',
    'ALI=F': 'Aluminum',
    'ZN=F': 'Zinc',
    'NI=F': 'Nickel',
    'PB=F': 'Lead',
    # Agriculture
    'ZC=F': 'Corn',
    'ZW=F': 'Wheat',
    'ZS=F': 'Soybeans',
    'KC=F': 'Coffee',
    'CT=F': 'Cotton',
    'CC=F': 'Cocoa',
    'SB=F': 'Sugar',
    'LC=F': 'Live Cattle',
    'LH=F': 'Lean Hogs',
    # Softs
    'OJ=F': 'Orange Juice',
    'DX=F': 'US Dollar Index',
}

# Commodity category mapping
COMMODITY_CATEGORIES = {
    'GC=F': 'precious_metals', 'SI=F': 'precious_metals', 'PL=F': 'precious_metals', 'PA=F': 'precious_metals',
    'CL=F': 'energy', 'BZ=F': 'energy', 'NG=F': 'energy', 'RB=F': 'energy', 'HO=F': 'energy',
    'HG=F': 'industrial_metals', 'ALI=F': 'industrial_metals', 'ZN=F': 'industrial_metals', 
    'NI=F': 'industrial_metals', 'PB=F': 'industrial_metals',
    'ZC=F': 'agriculture', 'ZW=F': 'agriculture', 'ZS=F': 'agriculture',
    'KC=F': 'softs', 'CT=F': 'softs', 'CC=F': 'softs', 'SB=F': 'softs',
    'LC=F': 'livestock', 'LH=F': 'livestock',
    'OJ=F': 'softs', 'DX=F': 'currency',
}

class CommodityResponse(BaseModel):
    symbol: str
    name: str
    category: str
    price: float
    change_24h: float
    change_24h_percent: float
    volume: float

class CommodityPredictionResponse(BaseModel):
    symbol: str
    name: str
    bullish_score: float
    confidence: float
    recommendation: str
    signals: dict

@router.get("/", response_model=List[CommodityResponse])
async def get_commodities(db: Session = Depends(get_db)):
    """Get list of tracked commodities"""
    results = []
    for symbol in DEFAULT_COMMODITIES:
        try:
            data = TechnicalAnalysisService.get_data(symbol, days=2)
            if data and len(data) >= 2:
                current = data[-1]['close']
                previous = data[-2]['close']
                change = current - previous
                change_pct = (change / previous) * 100
                volume = data[-1]['volume']
                
                results.append(CommodityResponse(
                    symbol=symbol,
                    name=COMMODITY_NAMES.get(symbol, symbol),
                    category=COMMODITY_CATEGORIES.get(symbol, 'other'),
                    price=round(current, 2),
                    change_24h=round(change, 2),
                    change_24h_percent=round(change_pct, 2),
                    volume=volume
                ))
        except:
            continue
    
    return results

@router.get("/{symbol}/prediction", response_model=CommodityPredictionResponse)
async def get_commodity_prediction(symbol: str, db: Session = Depends(get_db)):
    """Get AI prediction for a commodity"""
    symbol = symbol.upper()
    
    # Validate symbol
    if symbol not in DEFAULT_COMMODITIES:
        raise HTTPException(status_code=400, detail="Invalid commodity symbol")
    
    prediction = TechnicalAnalysisService.analyze(symbol)
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Could not analyze commodity")
    
    return CommodityPredictionResponse(
        symbol=prediction.symbol,
        name=COMMODITY_NAMES.get(symbol, symbol),
        bullish_score=prediction.bullish_score,
        confidence=prediction.confidence,
        recommendation=prediction.recommendation,
        signals=prediction.signals
    )

@router.get("/categories/{category}")
async def get_commodities_by_category(category: str, db: Session = Depends(get_db)):
    """Get commodities filtered by category"""
    valid_categories = ['precious_metals', 'energy', 'industrial_metals', 'agriculture', 'softs', 'livestock', 'currency']
    
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Valid: {', '.join(valid_categories)}")
    
    # Get symbols in category
    category_symbols = [s for s, cat in COMMODITY_CATEGORIES.items() if cat == category]
    
    results = []
    for symbol in category_symbols:
        try:
            data = TechnicalAnalysisService.get_data(symbol, days=2)
            if data and len(data) >= 2:
                current = data[-1]['close']
                previous = data[-2]['close']
                change = current - previous
                change_pct = (change / previous) * 100
                volume = data[-1]['volume']
                
                results.append({
                    'symbol': symbol,
                    'name': COMMODITY_NAMES.get(symbol, symbol),
                    'category': category,
                    'price': round(current, 2),
                    'change_24h': round(change, 2),
                    'change_24h_percent': round(change_pct, 2),
                    'volume': volume
                })
        except:
            continue
    
    return results
