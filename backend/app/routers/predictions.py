"""
Predictions API Routes
Top 10 and prediction-related endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.technical_analysis import TechnicalAnalysisService, SignalScore

router = APIRouter()

# Default stock universe for scanning
DEFAULT_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
    'AMD', 'INTC', 'CRM', 'ADBE', 'PYPL', 'UBER', 'COIN', 'ROKU',
    'AXON', 'SHOP', 'ZM', 'DOCU', 'PLTR', 'SNOW', 'CRWD', 'NET',
    'DDOG', 'OKTA', 'TWLO', 'FSLY', 'PINS', 'LYFT', 'ABNB', 'DASH'
]

DEFAULT_CRYPTOS = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'DOT-USD',
    'AVAX-USD', 'LINK-USD', 'LTC-USD', 'AAVE-USD', 'ATOM-USD'
]

# Sector mapping for stocks
SECTOR_MAPPING = {
    # Tech
    'AAPL': 'Tech', 'MSFT': 'Tech', 'GOOGL': 'Tech', 'NVDA': 'Tech', 'META': 'Tech',
    'AMD': 'Tech', 'INTC': 'Tech', 'CRM': 'Tech', 'ADBE': 'Tech', 'SHOP': 'Tech',
    'ZM': 'Tech', 'DOCU': 'Tech', 'PLTR': 'Tech', 'SNOW': 'Tech', 'CRWD': 'Tech',
    'NET': 'Tech', 'DDOG': 'Tech', 'OKTA': 'Tech', 'TWLO': 'Tech', 'FSLY': 'Tech',
    'ROKU': 'Tech', 'PINS': 'Tech',
    # Finance
    'PYPL': 'Finance', 'COIN': 'Finance',
    # Healthcare
    # (Add healthcare stocks here if available)
    # Energy
    # (Add energy stocks here if available)
    # Consumer
    'AMZN': 'Consumer', 'TSLA': 'Consumer', 'NFLX': 'Consumer', 'UBER': 'Consumer',
    'LYFT': 'Consumer', 'ABNB': 'Consumer', 'DASH': 'Consumer',
    # Industrial
    'AXON': 'Industrial',
}

class TopPickResponse(BaseModel):
    rank: int
    symbol: str
    asset_type: str
    bullish_score: float
    confidence: float
    recommendation: str
    current_price: float
    key_signals: List[str]
    sector: Optional[str] = None
    
class MarketOverviewResponse(BaseModel):
    bullish_count: int
    bearish_count: int
    neutral_count: int
    average_score: float
    top_performer: str
    most_bearish: str
    last_updated: datetime

def get_sector(symbol: str) -> Optional[str]:
    """Get sector for a stock symbol"""
    return SECTOR_MAPPING.get(symbol)

def get_asset_type(symbol: str) -> str:
    """Determine if symbol is crypto or stock"""
    return 'crypto' if '-USD' in symbol else 'stock'

def matches_recommendation_filter(recommendation: str, filter_recs: List[str]) -> bool:
    """Check if recommendation matches any of the filter recommendations"""
    if not filter_recs:
        return True
    return recommendation in filter_recs

def matches_sector_filter(symbol: str, sector_filter: str) -> bool:
    """Check if symbol matches sector filter"""
    if sector_filter == 'all':
        return True
    symbol_sector = get_sector(symbol)
    return symbol_sector == sector_filter

def apply_filters(
    results: List[SignalScore],
    min_score: float = 0,
    max_score: float = 100,
    min_confidence: float = 0,
    recommendations: Optional[List[str]] = None,
    sector: str = 'all',
    asset_type: str = 'all'
) -> List[SignalScore]:
    """Apply all filters to results"""
    filtered = []
    
    for score in results:
        # Asset type filter
        if asset_type != 'all':
            symbol_type = get_asset_type(score.symbol)
            if symbol_type != asset_type:
                continue
        
        # Bullish score range filter
        if score.bullish_score < min_score or score.bullish_score > max_score:
            continue
        
        # Confidence filter
        if score.confidence < min_confidence:
            continue
        
        # Recommendation filter
        if recommendations and not matches_recommendation_filter(score.recommendation, recommendations):
            continue
        
        # Sector filter (only applies to stocks)
        if sector != 'all' and get_asset_type(score.symbol) == 'stock':
            if not matches_sector_filter(score.symbol, sector):
                continue
        
        filtered.append(score)
    
    return filtered

@router.get("/top-picks", response_model=List[TopPickResponse])
async def get_top_picks(
    limit: int = Query(10, ge=1, le=50),
    asset_type: str = Query("all", regex="^(all|stocks|crypto)$"),
    min_score: float = Query(0, ge=0, le=100),
    max_score: float = Query(100, ge=0, le=100),
    min_confidence: float = Query(0, ge=0, le=100),
    recommendations: Optional[str] = Query(None, description="Comma-separated list: Strong Buy,Buy,Hold,Sell,Strong Sell"),
    sector: str = Query("all", regex="^(all|Tech|Finance|Healthcare|Energy|Consumer)$"),
    db: Session = Depends(get_db)
):
    """
    Get top trading picks ranked by bullish score with advanced filtering
    
    Query Parameters:
    - limit: Number of results to return (1-50, default: 10)
    - asset_type: Filter by asset type (all, stocks, crypto)
    - min_score: Minimum bullish score (0-100)
    - max_score: Maximum bullish score (0-100)
    - min_confidence: Minimum confidence level (0-100)
    - recommendations: Comma-separated list of recommendations to include
    - sector: Filter stocks by sector (Tech, Finance, Healthcare, Energy, Consumer)
    """
    symbols = []
    
    if asset_type in ['all', 'stocks']:
        # Apply sector pre-filter for stocks if specified
        if sector != 'all':
            sector_stocks = [s for s in DEFAULT_STOCKS if matches_sector_filter(s, sector)]
            symbols.extend(sector_stocks)
        else:
            symbols.extend(DEFAULT_STOCKS)
    
    if asset_type in ['all', 'crypto']:
        symbols.extend(DEFAULT_CRYPTOS)
    
    # Scan all symbols
    results = TechnicalAnalysisService.scan_multiple(symbols)
    
    # Parse recommendations filter
    rec_filter = None
    if recommendations:
        rec_filter = [r.strip() for r in recommendations.split(',') if r.strip()]
    
    # Apply all filters
    filtered_results = apply_filters(
        results,
        min_score=min_score,
        max_score=max_score,
        min_confidence=min_confidence,
        recommendations=rec_filter,
        sector=sector,
        asset_type=asset_type
    )
    
    # Take top N
    top_results = filtered_results[:limit]
    
    # Format response
    response = []
    for i, score in enumerate(top_results, 1):
        # Get current price
        data = TechnicalAnalysisService.get_data(score.symbol, days=5)
        current_price = data[-1]['close'] if data else 0
        
        # Extract key signals
        key_signals = []
        for signal_type, signal_value in score.signals.items():
            if 'bullish' in signal_value:
                key_signals.append(f"{signal_type}: {signal_value}")
        
        response.append(TopPickResponse(
            rank=i,
            symbol=score.symbol,
            asset_type=get_asset_type(score.symbol),
            bullish_score=score.bullish_score,
            confidence=score.confidence,
            recommendation=score.recommendation,
            current_price=current_price,
            key_signals=key_signals[:3],  # Top 3 signals
            sector=get_sector(score.symbol)
        ))
    
    return response

@router.get("/market-overview", response_model=MarketOverviewResponse)
async def get_market_overview(db: Session = Depends(get_db)):
    """Get overall market sentiment based on tracked assets"""
    all_symbols = DEFAULT_STOCKS + DEFAULT_CRYPTOS
    
    results = TechnicalAnalysisService.scan_multiple(all_symbols)
    
    if not results:
        raise HTTPException(status_code=500, detail="Could not analyze market")
    
    bullish_count = sum(1 for r in results if r.bullish_score >= 60)
    bearish_count = sum(1 for r in results if r.bullish_score <= 40)
    neutral_count = len(results) - bullish_count - bearish_count
    
    average_score = sum(r.bullish_score for r in results) / len(results)
    
    top_performer = results[0].symbol if results else "N/A"
    most_bearish = results[-1].symbol if results else "N/A"
    
    return MarketOverviewResponse(
        bullish_count=bullish_count,
        bearish_count=bearish_count,
        neutral_count=neutral_count,
        average_score=round(average_score, 1),
        top_performer=top_performer,
        most_bearish=most_bearish,
        last_updated=datetime.now()
    )

@router.get("/scan")
async def scan_custom_symbols(
    symbols: str,  # Comma-separated list
    min_score: float = Query(0, ge=0, le=100),
    max_score: float = Query(100, ge=0, le=100),
    min_confidence: float = Query(0, ge=0, le=100),
    recommendations: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Scan custom list of symbols with filtering"""
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
    if len(symbol_list) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 symbols allowed")
    
    results = TechnicalAnalysisService.scan_multiple(symbol_list)
    
    # Parse recommendations filter
    rec_filter = None
    if recommendations:
        rec_filter = [r.strip() for r in recommendations.split(',') if r.strip()]
    
    # Apply filters
    filtered_results = apply_filters(
        results,
        min_score=min_score,
        max_score=max_score,
        min_confidence=min_confidence,
        recommendations=rec_filter
    )
    
    return {
        "scanned": len(symbol_list),
        "results_found": len(filtered_results),
        "total_analyzed": len(results),
        "predictions": filtered_results
    }

@router.get("/sectors")
async def get_available_sectors():
    """Get list of available sectors for filtering"""
    return {
        "sectors": [
            {"value": "all", "label": "All Sectors"},
            {"value": "Tech", "label": "Technology"},
            {"value": "Finance", "label": "Finance"},
            {"value": "Healthcare", "label": "Healthcare"},
            {"value": "Energy", "label": "Energy"},
            {"value": "Consumer", "label": "Consumer"},
        ]
    }
