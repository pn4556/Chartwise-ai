"""
Alerts/Tickets Router
Endpoints for trading alerts and pattern signals
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.services.alert_service import AlertService, AlertType, AlertSeverity
from app.services.enhanced_analysis import EnhancedTechnicalAnalysis
from app.routers.predictions import DEFAULT_STOCKS, DEFAULT_CRYPTOS

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/")
async def get_alerts(
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    alert_type: Optional[str] = Query(None, regex="^(pattern|price|indicator|breakout|reversal|volume|coach)$"),
    acknowledged: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all alerts with optional filtering
    """
    severity_enum = AlertSeverity(severity) if severity else None
    type_enum = AlertType(alert_type) if alert_type else None
    
    alerts = AlertService.get_all_alerts(
        severity=severity_enum,
        alert_type=type_enum,
        limit=limit
    )
    
    if acknowledged is not None:
        alerts = [a for a in alerts if a.acknowledged == acknowledged]
    
    return {
        'alerts': [
            {
                'id': a.id,
                'symbol': a.symbol,
                'type': a.type.value,
                'severity': a.severity.value,
                'title': a.title,
                'message': a.message,
                'timestamp': a.timestamp,
                'pattern_name': a.pattern_name,
                'price_at_trigger': a.price_at_trigger,
                'target_price': a.target_price,
                'stop_loss': a.stop_loss,
                'timeframe': a.timeframe,
                'acknowledged': a.acknowledged,
                'category': a.category,
                'triggered_by': a.triggered_by
            }
            for a in alerts
        ],
        'count': len(alerts),
        'filters': {
            'severity': severity,
            'type': alert_type,
            'acknowledged': acknowledged
        }
    }


@router.get("/unacknowledged")
async def get_unacknowledged_alerts(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get unacknowledged (new) alerts
    """
    alerts = AlertService.get_unacknowledged_alerts(limit=limit)
    
    return {
        'alerts': [
            {
                'id': a.id,
                'symbol': a.symbol,
                'type': a.type.value,
                'severity': a.severity.value,
                'title': a.title,
                'message': a.message,
                'timestamp': a.timestamp,
                'pattern_name': a.pattern_name,
                'price_at_trigger': a.price_at_trigger,
                'target_price': a.target_price,
                'stop_loss': a.stop_loss,
                'category': a.category
            }
            for a in alerts
        ],
        'count': len(alerts)
    }


@router.get("/symbol/{symbol}")
async def get_symbol_alerts(
    symbol: str = Path(..., description="Stock or crypto symbol"),
    hours: Optional[int] = Query(None, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    Get alerts for a specific symbol
    """
    alerts = AlertService.get_symbol_alerts(symbol, hours=hours)
    
    return {
        'symbol': symbol,
        'alerts': [
            {
                'id': a.id,
                'type': a.type.value,
                'severity': a.severity.value,
                'title': a.title,
                'message': a.message,
                'timestamp': a.timestamp,
                'pattern_name': a.pattern_name,
                'price_at_trigger': a.price_at_trigger,
                'target_price': a.target_price,
                'stop_loss': a.stop_loss,
                'acknowledged': a.acknowledged,
                'triggered_by': a.triggered_by
            }
            for a in alerts
        ],
        'count': len(alerts)
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str = Path(..., description="Alert ID"),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert (mark as read)
    """
    success = AlertService.acknowledge_alert(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        'success': True,
        'message': 'Alert acknowledged',
        'alert_id': alert_id
    }


@router.post("/analyze/{symbol}")
async def analyze_symbol_for_alerts(
    symbol: str = Path(..., description="Stock or crypto symbol"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger analysis for a symbol and generate alerts
    """
    try:
        # Get analysis
        result = EnhancedTechnicalAnalysis.analyze(symbol)
        if not result:
            raise HTTPException(status_code=404, detail=f"Could not analyze {symbol}")
        
        # Get indicators from first timeframe
        indicators = result.timeframe_analyses[0] if result.timeframe_analyses else None
        
        if not indicators:
            raise HTTPException(status_code=500, detail="No indicator data available")
        
        # Run alert analysis
        prediction_data = {
            'probabilities': result.probabilities,
            'confidence': result.confidence
        }
        
        alerts = AlertService.analyze_and_alert(symbol, indicators, prediction_data)
        
        return {
            'symbol': symbol,
            'alerts_generated': len(alerts),
            'alerts': [
                {
                    'id': a.id,
                    'type': a.type.value,
                    'severity': a.severity.value,
                    'title': a.title,
                    'message': a.message
                }
                for a in alerts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/active")
async def get_active_pattern_alerts(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get active pattern-based alerts
    """
    alerts = AlertService.get_all_alerts(alert_type=AlertType.PATTERN, limit=limit)
    
    # Filter unacknowledged
    alerts = [a for a in alerts if not a.acknowledged]
    
    return {
        'patterns': [
            {
                'id': a.id,
                'symbol': a.symbol,
                'pattern': a.pattern_name,
                'title': a.title,
                'severity': a.severity.value,
                'timestamp': a.timestamp,
                'price': a.price_at_trigger,
                'target': a.target_price,
                'stop_loss': a.stop_loss
            }
            for a in alerts
        ],
        'count': len(alerts)
    }


@router.get("/scan")
async def scan_for_alerts(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols to scan"),
    db: Session = Depends(get_db)
):
    """
    Scan multiple symbols for alerts
    """
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
    else:
        symbol_list = DEFAULT_STOCKS[:15]  # Default to top 15
    
    all_alerts = []
    scanned = 0
    
    for symbol in symbol_list:
        try:
            result = EnhancedTechnicalAnalysis.analyze(symbol)
            if not result:
                continue
            
            indicators = result.timeframe_analyses[0] if result.timeframe_analyses else None
            if not indicators:
                continue
            
            prediction_data = {
                'probabilities': result.probabilities,
                'confidence': result.confidence
            }
            
            alerts = AlertService.analyze_and_alert(symbol, indicators, prediction_data)
            all_alerts.extend(alerts)
            scanned += 1
            
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
            continue
    
    return {
        'scanned': scanned,
        'alerts_found': len(all_alerts),
        'alerts': [
            {
                'id': a.id,
                'symbol': a.symbol,
                'type': a.type.value,
                'severity': a.severity.value,
                'title': a.title,
                'pattern': a.pattern_name
            }
            for a in sorted(all_alerts, key=lambda x: x.timestamp, reverse=True)
        ]
    }


@router.get("/stats")
async def get_alert_stats(
    db: Session = Depends(get_db)
):
    """
    Get alert statistics
    """
    stats = AlertService.get_alert_stats()
    
    return {
        'statistics': stats,
        'generated_at': datetime.now().isoformat()
    }


@router.delete("/clear-old")
async def clear_old_alerts(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Clear alerts older than specified days
    """
    AlertService.clear_old_alerts(days=days)
    
    return {
        'success': True,
        'message': f'Alerts older than {days} days cleared'
    }
