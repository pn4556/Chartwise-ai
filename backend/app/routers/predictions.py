"""
Predictions API Routes
Top 10 and prediction-related endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import time

from app.database import get_db
from app.services.technical_analysis import TechnicalAnalysisService, SignalScore

router = APIRouter()

# Simple in-memory cache for top picks
_cache: Dict[str, Any] = {}
_cache_ttl = 300  # 5 minutes cache

def get_cached_top_picks(key: str) -> Optional[List[SignalScore]]:
    """Get cached results if not expired"""
    if key in _cache:
        cached_data, timestamp = _cache[key]
        if time.time() - timestamp < _cache_ttl:
            return cached_data
    return None

def set_cached_top_picks(key: str, data: List[SignalScore]):
    """Cache results with timestamp"""
    _cache[key] = (data, time.time())

# Default stock universe for scanning
DEFAULT_STOCKS = [
    # Tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
    'AMD', 'INTC', 'CRM', 'ADBE', 'PYPL', 'UBER', 'COIN', 'ROKU',
    'AXON', 'SHOP', 'ZM', 'DOCU', 'PLTR', 'SNOW', 'CRWD', 'NET',
    'DDOG', 'OKTA', 'TWLO', 'FSLY', 'PINS', 'LYFT', 'ABNB', 'DASH',
    'CSCO', 'ORCL', 'IBM', 'QCOM', 'TXN', 'MU', 'PANW', 'FTNT',
    # Finance
    'JPM', 'BAC', 'GS', 'MS', 'WFC', 'C', 'BLK', 'AXP', 'V', 'MA',
    'SCHW', 'PNC', 'TFC', 'USB', 'COF', 'PYPL', 'COIN', 'SQ',
    # Healthcare
    'JNJ', 'PFE', 'MRK', 'ABBV', 'LLY', 'TMO', 'ABT', 'DHR', 'BMY', 'UNH',
    'GILD', 'AMGN', 'VRTX', 'REGN', 'BIIB', 'ZTS', 'MRNA', 'BNTX',
    # Energy
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY', 'MPC', 'VLO', 'PSX', 'WMB',
    # Consumer
    'AMZN', 'TSLA', 'NFLX', 'UBER', 'LYFT', 'ABNB', 'DASH', 'MAR', 'HLT',
    'MCD', 'SBUX', 'NKE', 'LULU', 'TGT', 'WMT', 'COST', 'HD', 'LOW',
    # Industrial
    'AXON', 'CAT', 'BA', 'GE', 'RTX', 'LMT', 'NOC', 'HON', 'UPS', 'FDX',
    # Communication Services
    'GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'ATVI', 'EA',
    # Real Estate (REITs)
    'AMT', 'PLD', 'CCI', 'PSA', 'O', 'SPG', 'WELL', 'AVB', 'EQR', 'DLR',
    # Materials
    'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'DOW', 'DD', 'ECL', 'NUE', 'VMC',
    # Utilities
    'NEE', 'DUK', 'SO', 'AEP', 'EXC', 'SRE', 'XEL', 'ED', 'D', 'NGG',
    # AI/Machine Learning
    'PLTR', 'AI', 'BBAI', 'SOUN', 'AMST', 'VRNS', 'PATH', 'U', 'CFLT', 'GTLB',
    'MDB', 'ESTC', 'AYX', 'DSGX', 'TDC', 'SMAR', 'MOND', 'INFA', 'ASAN', 'BOX',
    # Photonics/Optics
    'COHR', 'LITE', 'IIVI', 'NPTN', 'LASR', 'AVNW', 'KOPN', 'EMKR', 'POET', 'LPTH',
    'AOSL', 'PLAB', 'CAMT', 'MRAM', 'PXLW', 'SIGA', 'OLED', 'UEIC'
]

DEFAULT_CRYPTOS = [
    # Layer 1s
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'DOT-USD', 'AVAX-USD', 'ATOM-USD',
    'NEAR-USD', 'ALGO-USD', 'FTM-USD', 'VET-USD', 'TRX-USD', 'EOS-USD', 'XTZ-USD',
    'EGLD-USD', 'HBAR-USD', 'ICP-USD', 'FIL-USD', 'APT-USD', 'SUI-USD', 'SEI-USD',
    'INJ-USD', 'TIA-USD', 'MANTA-USD', 'STRK-USD', 'OP-USD', 'ARB-USD', 'METIS-USD',
    # DeFi Blue Chips
    'UNI-USD', 'AAVE-USD', 'MKR-USD', 'SNX-USD', 'COMP-USD', 'CRV-USD', 'LDO-USD',
    'CVX-USD', 'YFI-USD', 'SUSHI-USD', '1INCH-USD', 'BAL-USD', 'LRC-USD', 'ZRX-USD',
    'KNC-USD', 'DYDX-USD', 'GMX-USD', 'GNS-USD', 'PERP-USD', 'APEX-USD', 'MUX-USD',
    # Layer 2 / Scaling
    'MATIC-USD', 'IMX-USD', 'SKL-USD', 'OMG-USD', 'BOBA-USD', 'ZKS-USD', 'LOOP-USD',
    # Infrastructure / Oracle
    'LINK-USD', 'GRT-USD', 'BAND-USD', 'API3-USD', 'UMB-USD', 'DIA-USD', 'TRB-USD',
    'LPT-USD', 'RNDR-USD', 'AKT-USD', 'STORJ-USD', 'AR-USD', 'SC-USD', 'HOT-USD',
    # Gaming / Metaverse
    'SAND-USD', 'MANA-USD', 'AXS-USD', 'GALA-USD', 'ENJ-USD', 'CHZ-USD', 'FLOW-USD',
    'IMX-USD', 'MAGIC-USD', 'ILV-USD', 'YGG-USD', 'MC-USD', 'ALICE-USD', 'TLM-USD',
    'WEMIX-USD', 'GMT-USD', 'STEPN-USD', 'VOXEL-USD', 'BIGTIME-USD', 'PYR-USD',
    # Meme Coins
    'DOGE-USD', 'SHIB-USD', 'PEPE-USD', 'FLOKI-USD', 'BONK-USD', 'WIF-USD', 'BOME-USD',
    'DOBO-USD', 'ELON-USD', 'AKITA-USD', 'KISHU-USD', 'SAITAMA-USD', 'SAMO-USD',
    # DePIN
    'HNT-USD', 'DIMO-USD', 'WIFI-USD', 'HONEY-USD', 'PAAL-USD', 'IO-USD', 'AIOZ-USD',
    # AI / Big Data
    'FET-USD', 'AGIX-USD', 'OCEAN-USD', 'RLC-USD', 'NMR-USD', 'PHA-USD', 'GLM-USD',
    'AKASH-USD', 'RNDR-USD', 'LAT-USD', 'CTXC-USD', 'DBC-USD', 'OCTA-USD',
    # Payments / Stablecoins (for volume analysis)
    'XRP-USD', 'XLM-USD', 'LTC-USD', 'BCH-USD', 'XMR-USD', 'ZEC-USD', 'DASH-USD',
    # Exchange Tokens
    'BNB-USD', 'CRO-USD', 'FTT-USD', 'KCS-USD', 'HT-USD', 'OKB-USD', 'GT-USD',
    'LEO-USD', 'MX-USD', 'BIT-USD', 'PLEX-USD', 'WOO-USD', 'JUP-USD', 'DRIFT-USD'
]

DEFAULT_COMMODITIES = [
    # Precious Metals
    'GC=F',     # Gold
    'SI=F',     # Silver
    'PL=F',     # Platinum
    'PA=F',     # Palladium
    # Energy
    'CL=F',     # Crude Oil (WTI)
    'BZ=F',     # Brent Crude Oil
    'NG=F',     # Natural Gas
    'RB=F',     # RBOB Gasoline
    'HO=F',     # Heating Oil
    # Industrial Metals
    'HG=F',     # Copper
    'ALI=F',    # Aluminum
    'ZN=F',     # Zinc
    'NI=F',     # Nickel
    'PB=F',     # Lead
    # Agriculture
    'ZC=F',     # Corn
    'ZW=F',     # Wheat
    'ZS=F',     # Soybeans
    'KC=F',     # Coffee
    'CT=F',     # Cotton
    'CC=F',     # Cocoa
    'SB=F',     # Sugar
    'LC=F',     # Live Cattle
    'LH=F',     # Lean Hogs
    # Softs
    'OJ=F',     # Orange Juice
    'DX=F',     # US Dollar Index
]

# Sector mapping for stocks
SECTOR_MAPPING = {
    # Technology
    'AAPL': 'Tech', 'MSFT': 'Tech', 'GOOGL': 'Tech', 'NVDA': 'Tech', 'META': 'Tech',
    'AMD': 'Tech', 'INTC': 'Tech', 'CRM': 'Tech', 'ADBE': 'Tech', 'SHOP': 'Tech',
    'ZM': 'Tech', 'DOCU': 'Tech', 'PLTR': 'Tech', 'SNOW': 'Tech', 'CRWD': 'Tech',
    'NET': 'Tech', 'DDOG': 'Tech', 'OKTA': 'Tech', 'TWLO': 'Tech', 'FSLY': 'Tech',
    'ROKU': 'Tech', 'PINS': 'Tech', 'CSCO': 'Tech', 'ORCL': 'Tech', 'IBM': 'Tech',
    'QCOM': 'Tech', 'TXN': 'Tech', 'MU': 'Tech', 'PANW': 'Tech', 'FTNT': 'Tech',
    # Finance
    'JPM': 'Finance', 'BAC': 'Finance', 'GS': 'Finance', 'MS': 'Finance', 'WFC': 'Finance',
    'C': 'Finance', 'BLK': 'Finance', 'AXP': 'Finance', 'V': 'Finance', 'MA': 'Finance',
    'SCHW': 'Finance', 'PNC': 'Finance', 'TFC': 'Finance', 'USB': 'Finance', 'COF': 'Finance',
    'PYPL': 'Finance', 'COIN': 'Finance', 'SQ': 'Finance',
    # Healthcare
    'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'MRK': 'Healthcare', 'ABBV': 'Healthcare',
    'LLY': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare', 'DHR': 'Healthcare',
    'BMY': 'Healthcare', 'UNH': 'Healthcare', 'GILD': 'Healthcare', 'AMGN': 'Healthcare',
    'VRTX': 'Healthcare', 'REGN': 'Healthcare', 'BIIB': 'Healthcare', 'ZTS': 'Healthcare',
    'MRNA': 'Healthcare', 'BNTX': 'Healthcare',
    # Energy
    'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy', 'SLB': 'Energy',
    'OXY': 'Energy', 'MPC': 'Energy', 'VLO': 'Energy', 'PSX': 'Energy', 'WMB': 'Energy',
    # Consumer
    'AMZN': 'Consumer', 'TSLA': 'Consumer', 'NFLX': 'Consumer', 'UBER': 'Consumer',
    'LYFT': 'Consumer', 'ABNB': 'Consumer', 'DASH': 'Consumer', 'MAR': 'Consumer',
    'HLT': 'Consumer', 'MCD': 'Consumer', 'SBUX': 'Consumer', 'NKE': 'Consumer',
    'LULU': 'Consumer', 'TGT': 'Consumer', 'WMT': 'Consumer', 'COST': 'Consumer',
    'HD': 'Consumer', 'LOW': 'Consumer',
    # Industrial
    'AXON': 'Industrial', 'CAT': 'Industrial', 'BA': 'Industrial', 'GE': 'Industrial',
    'RTX': 'Industrial', 'LMT': 'Industrial', 'NOC': 'Industrial', 'HON': 'Industrial',
    'UPS': 'Industrial', 'FDX': 'Industrial',
    # Communication Services
    'DIS': 'CommServices', 'CMCSA': 'CommServices', 'VZ': 'CommServices', 'T': 'CommServices',
    'TMUS': 'CommServices', 'ATVI': 'CommServices', 'EA': 'CommServices',
    # Real Estate
    'AMT': 'RealEstate', 'PLD': 'RealEstate', 'CCI': 'RealEstate', 'PSA': 'RealEstate',
    'O': 'RealEstate', 'SPG': 'RealEstate', 'WELL': 'RealEstate', 'AVB': 'RealEstate',
    'EQR': 'RealEstate', 'DLR': 'RealEstate',
    # Materials
    'LIN': 'Materials', 'APD': 'Materials', 'SHW': 'Materials', 'FCX': 'Materials',
    'NEM': 'Materials', 'DOW': 'Materials', 'DD': 'Materials', 'ECL': 'Materials',
    'NUE': 'Materials', 'VMC': 'Materials',
    # Utilities
    'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities', 'AEP': 'Utilities',
    'EXC': 'Utilities', 'SRE': 'Utilities', 'XEL': 'Utilities', 'ED': 'Utilities',
    'D': 'Utilities', 'NGG': 'Utilities',
    # AI/Machine Learning
    'PLTR': 'AI', 'AI': 'AI', 'BBAI': 'AI', 'SOUN': 'AI', 'AMST': 'AI',
    'VRNS': 'AI', 'PATH': 'AI', 'U': 'AI', 'CFLT': 'AI', 'GTLB': 'AI',
    'MDB': 'AI', 'ESTC': 'AI', 'AYX': 'AI', 'DSGX': 'AI', 'TDC': 'AI',
    'SMAR': 'AI', 'MOND': 'AI', 'INFA': 'AI', 'ASAN': 'AI', 'BOX': 'AI',
    # Photonics/Optics
    'COHR': 'Photonics', 'LITE': 'Photonics', 'IIVI': 'Photonics', 'NPTN': 'Photonics',
    'LASR': 'Photonics', 'AVNW': 'Photonics', 'KOPN': 'Photonics', 'EMKR': 'Photonics',
    'POET': 'Photonics', 'LPTH': 'Photonics', 'AOSL': 'Photonics', 'PLAB': 'Photonics',
    'CAMT': 'Photonics', 'MRAM': 'Photonics', 'PXLW': 'Photonics', 'SIGA': 'Photonics',
    'OLED': 'Photonics', 'UEIC': 'Photonics',
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
    """Determine if symbol is crypto, stock, or commodity"""
    if '-USD' in symbol:
        return 'crypto'
    elif symbol.endswith('=F') or symbol in DEFAULT_COMMODITIES:
        return 'commodity'
    else:
        return 'stock'

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
            # Handle 'stocks' plural form
            check_type = 'stock' if asset_type == 'stocks' else asset_type
            if symbol_type != check_type:
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
    asset_type: str = Query("all", regex="^(all|stocks|crypto|commodity)$"),
    min_score: float = Query(0, ge=0, le=100),
    max_score: float = Query(100, ge=0, le=100),
    min_confidence: float = Query(0, ge=0, le=100),
    recommendations: Optional[str] = Query(None, description="Comma-separated list: Strong Buy,Buy,Hold,Sell,Strong Sell"),
    sector: str = Query("all", regex="^(all|Tech|Finance|Healthcare|Energy|Consumer|Industrial|CommServices|RealEstate|Materials|Utilities|AI|Photonics)$"),
    db: Session = Depends(get_db)
):
    """
    Get top trading picks ranked by bullish score with advanced filtering
    
    Query Parameters:
    - limit: Number of results to return (1-50, default: 10)
    - asset_type: Filter by asset type (all, stocks, crypto, commodity)
    - min_score: Minimum bullish score (0-100)
    - max_score: Maximum bullish score (0-100)
    - min_confidence: Minimum confidence level (0-100)
    - recommendations: Comma-separated list of recommendations to include
    - sector: Filter stocks by sector (Tech, Finance, Healthcare, Energy, Consumer)
    """
    # Build cache key from query params
    cache_key = f"top_picks:{asset_type}:{sector}:{min_score}:{max_score}:{min_confidence}:{recommendations}"
    
    # Check cache first
    cached_results = get_cached_top_picks(cache_key)
    if cached_results is not None:
        # Apply limit to cached results
        filtered_cached = cached_results[:limit]
        return format_top_picks_response(filtered_cached, limit)
    
    symbols = []
    
    if asset_type in ['all', 'stocks']:
        # Apply sector pre-filter for stocks if specified
        if sector != 'all':
            sector_stocks = [s for s in DEFAULT_STOCKS if matches_sector_filter(s, sector)]
            symbols.extend(sector_stocks[:20])  # Limit to 20 for performance
        else:
            # Limit stocks for performance - scan top 20 most popular
            symbols.extend(DEFAULT_STOCKS[:20])
    
    if asset_type in ['all', 'crypto']:
        # Limit cryptos for performance - scan top 10
        symbols.extend(DEFAULT_CRYPTOS[:10])
    
    if asset_type in ['all', 'commodity']:
        # Limit commodities for performance - scan top 5
        symbols.extend(DEFAULT_COMMODITIES[:5])
    
    # Scan all symbols
    results = TechnicalAnalysisService.scan_multiple(symbols)
    
    # Cache the full results
    set_cached_top_picks(cache_key, results)
    
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
    
    return format_top_picks_response(top_results, limit)

def format_top_picks_response(top_results: List[SignalScore], limit: int) -> List[TopPickResponse]:
    """Format SignalScore objects into TopPickResponse"""
    response = []
    for i, score in enumerate(top_results[:limit], 1):
        # Get current price from cached data or fetch fresh
        data = TechnicalAnalysisService.get_data(score.symbol, days=5)
        current_price = data[-1]['close'] if data else 0
        
        # Extract key signals
        key_signals = []
        for signal_type, signal_value in score.signals.items():
            if 'bullish' in signal_value or 'bearish' in signal_value:
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
    all_symbols = DEFAULT_STOCKS + DEFAULT_CRYPTOS + DEFAULT_COMMODITIES
    
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

@router.get("/sectors/{sector}")
async def get_sector_details(sector: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific sector including all stocks and their scores
    """
    # Validate sector
    valid_sectors = ['Tech', 'Finance', 'Healthcare', 'Energy', 'Consumer', 
                     'Industrial', 'CommServices', 'RealEstate', 'Materials', 
                     'Utilities', 'AI', 'Photonics']
    
    if sector not in valid_sectors:
        raise HTTPException(status_code=400, detail=f"Invalid sector. Valid sectors: {', '.join(valid_sectors)}")
    
    # Get all stocks in this sector
    sector_stocks = [symbol for symbol, sec in SECTOR_MAPPING.items() if sec == sector]
    
    if not sector_stocks:
        raise HTTPException(status_code=404, detail=f"No stocks found for sector: {sector}")
    
    # Analyze all stocks in sector
    results = TechnicalAnalysisService.scan_multiple(sector_stocks)
    
    # Sort by bullish score
    results.sort(key=lambda x: x.bullish_score, reverse=True)
    
    # Calculate sector statistics
    avg_score = sum(r.bullish_score for r in results) / len(results) if results else 0
    avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0
    bullish_count = sum(1 for r in results if r.bullish_score >= 60)
    bearish_count = sum(1 for r in results if r.bullish_score <= 40)
    neutral_count = len(results) - bullish_count - bearish_count
    
    # Get current prices for top stocks
    stocks_with_details = []
    for score in results:
        data = TechnicalAnalysisService.get_data(score.symbol, days=2)
        current_price = data[-1]['close'] if data else 0
        change_pct = 0
        if data and len(data) >= 2:
            change_pct = ((data[-1]['close'] - data[-2]['close']) / data[-2]['close']) * 100
        
        stocks_with_details.append({
            "symbol": score.symbol,
            "bullish_score": score.bullish_score,
            "confidence": score.confidence,
            "recommendation": score.recommendation,
            "current_price": round(current_price, 2),
            "change_percent": round(change_pct, 2),
            "signals": score.signals
        })
    
    return {
        "sector": sector,
        "total_stocks": len(sector_stocks),
        "analyzed": len(results),
        "statistics": {
            "average_score": round(avg_score, 1),
            "average_confidence": round(avg_confidence, 1),
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count
        },
        "top_performer": stocks_with_details[0] if stocks_with_details else None,
        "stocks": stocks_with_details
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
            {"value": "Industrial", "label": "Industrial"},
            {"value": "CommServices", "label": "Communication Services"},
            {"value": "RealEstate", "label": "Real Estate"},
            {"value": "Materials", "label": "Materials"},
            {"value": "Utilities", "label": "Utilities"},
            {"value": "AI", "label": "AI / Machine Learning"},
            {"value": "Photonics", "label": "Photonics / Optics"},
        ],
        "crypto_categories": [
            {"value": "all", "label": "All Cryptos"},
            {"value": "layer1", "label": "Layer 1 Blockchains"},
            {"value": "defi", "label": "DeFi"},
            {"value": "gaming", "label": "Gaming / Metaverse"},
            {"value": "meme", "label": "Meme Coins"},
            {"value": "ai", "label": "AI / Big Data"},
            {"value": "depin", "label": "DePIN"},
            {"value": "infra", "label": "Infrastructure / Oracles"},
            {"value": "l2", "label": "Layer 2 / Scaling"},
            {"value": "payments", "label": "Payments"},
            {"value": "exchange", "label": "Exchange Tokens"},
        ],
        "commodity_categories": [
            {"value": "all", "label": "All Commodities"},
            {"value": "precious_metals", "label": "Precious Metals (Gold, Silver, Platinum)"},
            {"value": "energy", "label": "Energy (Oil, Gas)"},
            {"value": "industrial_metals", "label": "Industrial Metals (Copper, Aluminum)"},
            {"value": "agriculture", "label": "Agriculture (Corn, Wheat, Soybeans)"},
            {"value": "softs", "label": "Softs (Coffee, Cotton, Sugar)"},
            {"value": "livestock", "label": "Livestock (Cattle, Hogs)"},
        ]
    }
