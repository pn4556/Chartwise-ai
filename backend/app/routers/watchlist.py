"""
Watchlist API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import WatchlistItem, User
from app.services.technical_analysis import TechnicalAnalysisService
from app.routers.auth import get_current_user

router = APIRouter()

class WatchlistItemCreate(BaseModel):
    symbol: str
    asset_type: str  # 'stock' or 'crypto'
    alert_threshold: float = None

class WatchlistItemResponse(BaseModel):
    id: int
    symbol: str
    asset_type: str
    current_price: float
    bullish_score: float
    recommendation: str
    added_date: datetime
    alert_threshold: float = None

@router.get("/", response_model=List[WatchlistItemResponse])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's watchlist with current predictions"""
    user_id = str(current_user.id)
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()
    
    response = []
    for item in items:
        # Get current prediction
        prediction = TechnicalAnalysisService.analyze(item.symbol)
        
        if prediction:
            data = TechnicalAnalysisService.get_data(item.symbol, days=1)
            current_price = data[-1]['close'] if data else 0
            
            response.append(WatchlistItemResponse(
                id=item.id,
                symbol=item.symbol,
                asset_type=item.asset_type,
                current_price=current_price,
                bullish_score=prediction.bullish_score,
                recommendation=prediction.recommendation,
                added_date=item.added_date,
                alert_threshold=item.alert_threshold
            ))
    
    return response

@router.post("/", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    item: WatchlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to watchlist"""
    user_id = str(current_user.id)
    # Check if already exists
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.symbol == item.symbol.upper()
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Symbol already in watchlist")
    
    # Create new item
    db_item = WatchlistItem(
        user_id=user_id,
        symbol=item.symbol.upper(),
        asset_type=item.asset_type,
        alert_threshold=item.alert_threshold
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Get prediction for response
    prediction = TechnicalAnalysisService.analyze(item.symbol.upper())
    data = TechnicalAnalysisService.get_data(item.symbol.upper(), days=1)
    current_price = data[-1]['close'] if data else 0
    
    return WatchlistItemResponse(
        id=db_item.id,
        symbol=db_item.symbol,
        asset_type=db_item.asset_type,
        current_price=current_price,
        bullish_score=prediction.bullish_score if prediction else 50,
        recommendation=prediction.recommendation if prediction else "Hold",
        added_date=db_item.added_date,
        alert_threshold=db_item.alert_threshold
    )

@router.delete("/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from watchlist"""
    user_id = str(current_user.id)
    item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.symbol == symbol.upper()
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    
    return {"message": f"Removed {symbol} from watchlist"}
