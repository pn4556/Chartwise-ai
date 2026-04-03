"""
Paper Trading API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import PaperTrade, UserPortfolio, User
from app.services.technical_analysis import TechnicalAnalysisService
from app.routers.auth import get_current_user

router = APIRouter()

class TradeCreate(BaseModel):
    symbol: str
    asset_type: str
    direction: str  # 'long' or 'short'
    quantity: float
    entry_price: float = None  # If None, use current market price
    thesis: str = None

class TradeResponse(BaseModel):
    id: int
    symbol: str
    asset_type: str
    direction: str
    entry_price: float
    entry_date: datetime
    quantity: float
    status: str
    current_pnl: float = None
    current_pnl_percent: float = None
    thesis: str = None

class PortfolioResponse(BaseModel):
    cash_balance: float
    total_value: float
    open_positions: int
    total_pnl: float
    win_rate: float

class TradeExitRequest(BaseModel):
    exit_price: float = None  # If None, use current market price
    exit_reason: str = None
    lessons: str = None

@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's paper trading portfolio"""
    user_id = str(current_user.id)
    # Get or create portfolio
    portfolio = db.query(UserPortfolio).filter(UserPortfolio.user_id == user_id).first()
    if not portfolio:
        portfolio = UserPortfolio(user_id=user_id)
        db.add(portfolio)
        db.commit()
    
    # Get all trades
    trades = db.query(PaperTrade).filter(PaperTrade.user_id == user_id).all()
    open_trades = [t for t in trades if t.status == 'open']
    closed_trades = [t for t in trades if t.status == 'closed']
    
    # Calculate open positions value
    open_positions_value = 0
    for trade in open_trades:
        data = TechnicalAnalysisService.get_data(trade.symbol, days=1)
        if data:
            current_price = data[-1]['close']
            position_value = trade.quantity * current_price
            open_positions_value += position_value
    
    # Calculate total P&L
    total_pnl = sum(t.pnl for t in closed_trades if t.pnl) + \
                sum(((data[-1]['close'] if (data := TechnicalAnalysisService.get_data(t.symbol, days=1)) else t.entry_price) - t.entry_price) * t.quantity 
                    for t in open_trades)
    
    # Calculate win rate
    winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
    win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
    
    # Update portfolio total value
    portfolio.total_value = portfolio.cash_balance + open_positions_value
    db.commit()
    
    return PortfolioResponse(
        cash_balance=portfolio.cash_balance,
        total_value=portfolio.total_value,
        open_positions=len(open_trades),
        total_pnl=round(total_pnl, 2),
        win_rate=round(win_rate, 1)
    )

@router.post("/trade", response_model=TradeResponse)
async def create_trade(
    trade: TradeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new paper trade"""
    user_id = str(current_user.id)
    # Get current price if not provided
    if trade.entry_price is None:
        data = TechnicalAnalysisService.get_data(trade.symbol.upper(), days=1)
        if not data:
            raise HTTPException(status_code=404, detail="Could not get price for symbol")
        entry_price = data[-1]['close']
    else:
        entry_price = trade.entry_price
    
    # Check if user has enough cash
    portfolio = db.query(UserPortfolio).filter(UserPortfolio.user_id == user_id).first()
    if not portfolio:
        portfolio = UserPortfolio(user_id=user_id)
        db.add(portfolio)
        db.commit()
    
    trade_value = entry_price * trade.quantity
    if trade_value > portfolio.cash_balance:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Create trade
    db_trade = PaperTrade(
        user_id=user_id,
        symbol=trade.symbol.upper(),
        asset_type=trade.asset_type,
        direction=trade.direction,
        entry_price=entry_price,
        quantity=trade.quantity,
        thesis=trade.thesis,
        status='open'
    )
    
    # Deduct from cash balance
    portfolio.cash_balance -= trade_value
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    return TradeResponse(
        id=db_trade.id,
        symbol=db_trade.symbol,
        asset_type=db_trade.asset_type,
        direction=db_trade.direction,
        entry_price=db_trade.entry_price,
        entry_date=db_trade.entry_date,
        quantity=db_trade.quantity,
        status=db_trade.status,
        thesis=db_trade.thesis
    )

@router.post("/trade/{trade_id}/exit")
async def exit_trade(
    trade_id: int,
    exit_request: TradeExitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close a paper trade"""
    user_id = str(current_user.id)
    trade = db.query(PaperTrade).filter(
        PaperTrade.id == trade_id,
        PaperTrade.user_id == user_id
    ).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade.status != 'open':
        raise HTTPException(status_code=400, detail="Trade is already closed")
    
    # Get exit price
    if exit_request.exit_price is None:
        data = TechnicalAnalysisService.get_data(trade.symbol, days=1)
        if not data:
            raise HTTPException(status_code=404, detail="Could not get current price")
        exit_price = data[-1]['close']
    else:
        exit_price = exit_request.exit_price
    
    # Calculate P&L
    if trade.direction == 'long':
        pnl = (exit_price - trade.entry_price) * trade.quantity
        pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
    else:  # short
        pnl = (trade.entry_price - exit_price) * trade.quantity
        pnl_percent = ((trade.entry_price - exit_price) / trade.entry_price) * 100
    
    # Update trade
    trade.exit_price = exit_price
    trade.exit_date = datetime.now()
    trade.pnl = pnl
    trade.pnl_percent = pnl_percent
    trade.exit_reason = exit_request.exit_reason
    trade.lessons = exit_request.lessons
    trade.status = 'closed'
    
    # Return cash to portfolio
    portfolio = db.query(UserPortfolio).filter(UserPortfolio.user_id == user_id).first()
    exit_value = exit_price * trade.quantity
    portfolio.cash_balance += exit_value
    
    db.commit()
    
    return {
        "message": "Trade closed successfully",
        "trade_id": trade_id,
        "exit_price": exit_price,
        "pnl": round(pnl, 2),
        "pnl_percent": round(pnl_percent, 2)
    }

@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    status: str = "all",  # all, open, closed
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's paper trades"""
    user_id = str(current_user.id)
    query = db.query(PaperTrade).filter(PaperTrade.user_id == user_id)
    
    if status != 'all':
        query = query.filter(PaperTrade.status == status)
    
    trades = query.order_by(PaperTrade.entry_date.desc()).all()
    
    response = []
    for trade in trades:
        current_pnl = None
        current_pnl_percent = None
        
        if trade.status == 'open':
            data = TechnicalAnalysisService.get_data(trade.symbol, days=1)
            if data:
                current_price = data[-1]['close']
                if trade.direction == 'long':
                    current_pnl = (current_price - trade.entry_price) * trade.quantity
                    current_pnl_percent = ((current_price - trade.entry_price) / trade.entry_price) * 100
                else:
                    current_pnl = (trade.entry_price - current_price) * trade.quantity
                    current_pnl_percent = ((trade.entry_price - current_price) / trade.entry_price) * 100
        
        response.append(TradeResponse(
            id=trade.id,
            symbol=trade.symbol,
            asset_type=trade.asset_type,
            direction=trade.direction,
            entry_price=trade.entry_price,
            entry_date=trade.entry_date,
            quantity=trade.quantity,
            status=trade.status,
            current_pnl=round(current_pnl, 2) if current_pnl else None,
            current_pnl_percent=round(current_pnl_percent, 2) if current_pnl_percent else None,
            thesis=trade.thesis
        ))
    
    return response
