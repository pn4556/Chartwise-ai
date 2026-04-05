"""
Alert/Ticket Service
Creates alerts when specific patterns, signals, or conditions are detected
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid


class AlertType(Enum):
    PATTERN = "pattern"
    PRICE = "price"
    INDICATOR = "indicator"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    VOLUME = "volume"
    COACH = "coach"


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Trading alert/ticket"""
    id: str
    symbol: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: str
    triggered_by: List[str]  # What signals triggered this
    pattern_name: Optional[str] = None
    price_at_trigger: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    timeframe: str = "1d"
    expiry: Optional[str] = None
    acknowledged: bool = False
    category: str = "trading"  # trading, pattern, coach, system


@dataclass
class PatternAlertConfig:
    """Configuration for pattern-based alerts"""
    patterns: List[str] = field(default_factory=lambda: [
        'hammer_bullish', 'engulfing_bullish', 'morning_star',
        'shooting_star_bearish', 'engulfing_bearish', 'doji'
    ])
    min_pattern_strength: float = 0.6
    enabled: bool = True


@dataclass
class IndicatorAlertConfig:
    """Configuration for indicator-based alerts"""
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    adx_strong_trend: float = 35
    volume_spike: float = 1.5  # 1.5x average
    enabled: bool = True


class AlertService:
    """
    Service for generating trading alerts and tickets
    """
    
    # In-memory store (would be database in production)
    _alerts: Dict[str, List[Alert]] = {}  # symbol -> alerts
    _global_alerts: List[Alert] = []
    _pattern_config = PatternAlertConfig()
    _indicator_config = IndicatorAlertConfig()
    
    @classmethod
    def create_alert(cls, symbol: str, alert_type: AlertType, severity: AlertSeverity,
                     title: str, message: str, triggered_by: List[str],
                     pattern_name: Optional[str] = None, price: Optional[float] = None,
                     target: Optional[float] = None, stop: Optional[float] = None,
                     timeframe: str = "1d", category: str = "trading") -> Alert:
        """Create a new alert"""
        
        alert = Alert(
            id=str(uuid.uuid4())[:8],
            symbol=symbol,
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now().isoformat(),
            triggered_by=triggered_by,
            pattern_name=pattern_name,
            price_at_trigger=price,
            target_price=target,
            stop_loss=stop,
            timeframe=timeframe,
            expiry=(datetime.now() + timedelta(days=5)).isoformat(),
            category=category
        )
        
        # Store by symbol
        if symbol not in cls._alerts:
            cls._alerts[symbol] = []
        cls._alerts[symbol].append(alert)
        cls._global_alerts.append(alert)
        
        return alert
    
    @classmethod
    def check_pattern_alerts(cls, symbol: str, indicators) -> Optional[Alert]:
        """Check if any pattern alerts should be triggered"""
        if not cls._pattern_config.enabled:
            return None
        
        if not indicators or indicators.candlestick_pattern == 'none':
            return None
        
        pattern = indicators.candlestick_pattern
        strength = indicators.pattern_strength
        
        if pattern not in cls._pattern_config.patterns:
            return None
        
        if strength < cls._pattern_config.min_pattern_strength:
            return None
        
        # Check for duplicates (same pattern in last 24h)
        recent_alerts = cls.get_symbol_alerts(symbol, hours=24)
        for alert in recent_alerts:
            if alert.pattern_name == pattern:
                return None
        
        # Create appropriate alert
        if 'bullish' in pattern:
            return cls.create_alert(
                symbol=symbol,
                alert_type=AlertType.PATTERN,
                severity=AlertSeverity.HIGH if strength > 0.8 else AlertSeverity.MEDIUM,
                title=f"🎯 {pattern.replace('_', ' ').title()} Detected",
                message=f"Bullish reversal pattern detected on {indicators.timeframe if hasattr(indicators, 'timeframe') else 'daily'} timeframe. "
                        f"Pattern strength: {strength:.0%}. Consider entry on confirmation.",
                triggered_by=['candlestick_pattern', 'price_action'],
                pattern_name=pattern,
                price=indicators.current_price if hasattr(indicators, 'current_price') else None,
                target=indicators.resistance_level if hasattr(indicators, 'resistance_level') else None,
                stop=indicators.support_level if hasattr(indicators, 'support_level') else None,
                category="pattern"
            )
        elif 'bearish' in pattern:
            return cls.create_alert(
                symbol=symbol,
                alert_type=AlertType.PATTERN,
                severity=AlertSeverity.HIGH if strength > 0.8 else AlertSeverity.MEDIUM,
                title=f"⚠️ {pattern.replace('_', ' ').title()} Detected",
                message=f"Bearish reversal pattern detected. "
                        f"Pattern strength: {strength:.0%}. Consider reducing exposure or hedging.",
                triggered_by=['candlestick_pattern', 'price_action'],
                pattern_name=pattern,
                price=indicators.current_price if hasattr(indicators, 'current_price') else None,
                category="pattern"
            )
        
        return None
    
    @classmethod
    def check_indicator_alerts(cls, symbol: str, indicators) -> List[Alert]:
        """Check for indicator-based alerts"""
        alerts = []
        
        if not cls._indicator_config.enabled:
            return alerts
        
        # RSI Oversold alert
        if hasattr(indicators, 'rsi') and indicators.rsi < cls._indicator_config.rsi_oversold:
            recent = cls.get_symbol_alerts(symbol, hours=24)
            if not any(a.title == "RSI Oversold" for a in recent):
                alerts.append(cls.create_alert(
                    symbol=symbol,
                    alert_type=AlertType.INDICATOR,
                    severity=AlertSeverity.MEDIUM,
                    title="📉 RSI Oversold",
                    message=f"RSI at {indicators.rsi:.1f} indicates oversold conditions. Potential bounce opportunity.",
                    triggered_by=['rsi'],
                    price=indicators.current_price if hasattr(indicators, 'current_price') else None,
                    category="indicator"
                ))
        
        # RSI Overbought alert
        if hasattr(indicators, 'rsi') and indicators.rsi > cls._indicator_config.rsi_overbought:
            recent = cls.get_symbol_alerts(symbol, hours=24)
            if not any(a.title == "RSI Overbought" for a in recent):
                alerts.append(cls.create_alert(
                    symbol=symbol,
                    alert_type=AlertType.INDICATOR,
                    severity=AlertSeverity.MEDIUM,
                    title="📈 RSI Overbought",
                    message=f"RSI at {indicators.rsi:.1f} indicates overbought conditions. Consider taking profits.",
                    triggered_by=['rsi'],
                    price=indicators.current_price if hasattr(indicators, 'current_price') else None,
                    category="indicator"
                ))
        
        # Strong trend alert (ADX)
        if hasattr(indicators, 'adx') and indicators.adx > cls._indicator_config.adx_strong_trend:
            recent = cls.get_symbol_alerts(symbol, hours=48)
            if not any(a.title == "Strong Trend Detected" for a in recent):
                direction = "bullish" if hasattr(indicators, 'plus_di') and indicators.plus_di > indicators.minus_di else "bearish"
                alerts.append(cls.create_alert(
                    symbol=symbol,
                    alert_type=AlertType.INDICATOR,
                    severity=AlertSeverity.HIGH,
                    title="💪 Strong Trend Detected",
                    message=f"ADX at {indicators.adx:.1f} shows strong {direction} trend. Trend-following strategies favored.",
                    triggered_by=['adx', 'di'],
                    price=indicators.current_price if hasattr(indicators, 'current_price') else None,
                    category="indicator"
                ))
        
        # Volume spike alert
        if hasattr(indicators, 'volume') and hasattr(indicators, 'avg_volume'):
            if indicators.volume > indicators.avg_volume * cls._indicator_config.volume_spike:
                recent = cls.get_symbol_alerts(symbol, hours=12)
                if not any(a.title == "Volume Spike" for a in recent):
                    ratio = indicators.volume / indicators.avg_volume
                    alerts.append(cls.create_alert(
                        symbol=symbol,
                        alert_type=AlertType.VOLUME,
                        severity=AlertSeverity.MEDIUM,
                        title="📊 Volume Spike",
                        message=f"Volume at {ratio:.1f}x average. Significant institutional activity detected.",
                        triggered_by=['volume'],
                        price=indicators.current_price,
                        category="indicator"
                    ))
        
        # Bollinger Band squeeze/breakout
        if hasattr(indicators, 'bb_width'):
            if indicators.bb_width < 0.05:
                recent = cls.get_symbol_alerts(symbol, hours=48)
                if not any(a.title == "Bollinger Squeeze" for a in recent):
                    alerts.append(cls.create_alert(
                        symbol=symbol,
                        alert_type=AlertType.BREAKOUT,
                        severity=AlertSeverity.HIGH,
                        title="🎯 Bollinger Squeeze",
                        message="Bollinger Bands squeezed - volatility expansion imminent. Watch for breakout.",
                        triggered_by=['bollinger_bands', 'volatility'],
                        price=indicators.current_price if hasattr(indicators, 'current_price') else None,
                        category="pattern"
                    ))
        
        # Support/Resistance bounce
        if hasattr(indicators, 'current_price') and hasattr(indicators, 'support_level'):
            price = indicators.current_price
            support = indicators.support_level
            resistance = getattr(indicators, 'resistance_level', None)
            
            # Near support
            if abs(price - support) / price < 0.015:
                recent = cls.get_symbol_alerts(symbol, hours=24)
                if not any(a.title == "Near Support" for a in recent):
                    alerts.append(cls.create_alert(
                        symbol=symbol,
                        alert_type=AlertType.PRICE,
                        severity=AlertSeverity.MEDIUM,
                        title="🛡️ Near Support",
                        message=f"Price within 1.5% of support level (${support:.2f}). Watch for bounce.",
                        triggered_by=['support_resistance'],
                        price=price,
                        category="price"
                    ))
            
            # Near resistance
            if resistance and abs(price - resistance) / price < 0.015:
                recent = cls.get_symbol_alerts(symbol, hours=24)
                if not any(a.title == "Near Resistance" for a in recent):
                    alerts.append(cls.create_alert(
                        symbol=symbol,
                        alert_type=AlertType.PRICE,
                        severity=AlertSeverity.MEDIUM,
                        title="🚧 Near Resistance",
                        message=f"Price within 1.5% of resistance level (${resistance:.2f}). Profit taking zone.",
                        triggered_by=['support_resistance'],
                        price=price,
                        category="price"
                    ))
        
        return alerts
    
    @classmethod
    def check_reversal_alerts(cls, symbol: str, indicators, prediction) -> Optional[Alert]:
        """Check for potential reversal alerts"""
        
        # Multiple confluence factors for reversal
        reversal_signals = []
        
        if hasattr(indicators, 'rsi'):
            if indicators.rsi < 25:
                reversal_signals.append("extreme_oversold")
            elif indicators.rsi > 75:
                reversal_signals.append("extreme_overbought")
        
        if hasattr(indicators, 'candlestick_pattern'):
            if indicators.candlestick_pattern in ['hammer_bullish', 'morning_star']:
                reversal_signals.append("bullish_pattern")
            elif indicators.candlestick_pattern in ['shooting_star_bearish', 'engulfing_bearish']:
                reversal_signals.append("bearish_pattern")
        
        if hasattr(indicators, 'williams_r'):
            if indicators.williams_r < -90:
                reversal_signals.append("williams_extreme")
        
        if hasattr(indicators, 'cci'):
            if indicators.cci < -200:
                reversal_signals.append("cci_extreme")
        
        # Need at least 2 confluence signals
        if len(reversal_signals) < 2:
            return None
        
        # Check for recent duplicate
        recent = cls.get_symbol_alerts(symbol, hours=48)
        if any(a.type == AlertType.REVERSAL for a in recent):
            return None
        
        direction = "bullish" if any(s in reversal_signals for s in ['extreme_oversold', 'bullish_pattern']) else "bearish"
        
        return cls.create_alert(
            symbol=symbol,
            alert_type=AlertType.REVERSAL,
            severity=AlertSeverity.CRITICAL,
            title=f"🔄 Potential {direction.title()} Reversal",
            message=f"Multiple reversal signals detected: {', '.join(reversal_signals)}. "
                    f"High probability {direction} reversal setting up.",
            triggered_by=reversal_signals,
            price=indicators.current_price if hasattr(indicators, 'current_price') else None,
            category="pattern"
        )
    
    @classmethod
    def analyze_and_alert(cls, symbol: str, indicators, prediction=None) -> List[Alert]:
        """Run full analysis and generate all applicable alerts"""
        alerts = []
        
        # Check pattern alerts
        pattern_alert = cls.check_pattern_alerts(symbol, indicators)
        if pattern_alert:
            alerts.append(pattern_alert)
        
        # Check indicator alerts
        indicator_alerts = cls.check_indicator_alerts(symbol, indicators)
        alerts.extend(indicator_alerts)
        
        # Check reversal alerts
        reversal_alert = cls.check_reversal_alerts(symbol, indicators, prediction)
        if reversal_alert:
            alerts.append(reversal_alert)
        
        # Check for breakout conditions
        if prediction and hasattr(indicators, 'current_price'):
            prob_up = prediction.get('probabilities', {}).get('up', 0)
            prob_down = prediction.get('probabilities', {}).get('down', 0)
            confidence = prediction.get('confidence', 0)
            
            if prob_up > 70 and confidence > 70:
                recent = cls.get_symbol_alerts(symbol, hours=48)
                if not any(a.title == "High Conviction Bullish Setup" for a in recent):
                    alerts.append(cls.create_alert(
                        symbol=symbol,
                        alert_type=AlertType.BREAKOUT,
                        severity=AlertSeverity.HIGH,
                        title="🚀 High Conviction Bullish Setup",
                        message=f"{prob_up:.0f}% probability up with {confidence:.0f}% confidence. "
                                "Multiple indicators aligned. Strong buy consideration.",
                        triggered_by=['probability_model', 'confidence_score'],
                        price=indicators.current_price,
                        category="trading"
                    ))
            elif prob_down > 70 and confidence > 70:
                recent = cls.get_symbol_alerts(symbol, hours=48)
                if not any(a.title == "High Conviction Bearish Setup" for a in recent):
                    alerts.append(cls.create_alert(
                        symbol=symbol,
                        alert_type=AlertType.BREAKOUT,
                        severity=AlertSeverity.HIGH,
                        title="🔻 High Conviction Bearish Setup",
                        message=f"{prob_down:.0f}% probability down with {confidence:.0f}% confidence. "
                                "Defensive positioning recommended.",
                        triggered_by=['probability_model', 'confidence_score'],
                        price=indicators.current_price,
                        category="trading"
                    ))
        
        return alerts
    
    @classmethod
    def get_symbol_alerts(cls, symbol: str, hours: Optional[int] = None) -> List[Alert]:
        """Get alerts for a symbol"""
        alerts = cls._alerts.get(symbol, [])
        
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            alerts = [a for a in alerts if datetime.fromisoformat(a.timestamp) > cutoff]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    @classmethod
    def get_all_alerts(cls, severity: Optional[AlertSeverity] = None, 
                       alert_type: Optional[AlertType] = None,
                       limit: int = 50) -> List[Alert]:
        """Get all alerts with optional filtering"""
        alerts = cls._global_alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if alert_type:
            alerts = [a for a in alerts if a.type == alert_type]
        
        # Remove expired alerts
        now = datetime.now()
        alerts = [a for a in alerts if datetime.fromisoformat(a.expiry) > now]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    @classmethod
    def get_unacknowledged_alerts(cls, limit: int = 20) -> List[Alert]:
        """Get unacknowledged alerts"""
        alerts = [a for a in cls._global_alerts if not a.acknowledged]
        now = datetime.now()
        alerts = [a for a in alerts if datetime.fromisoformat(a.expiry) > now]
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    @classmethod
    def acknowledge_alert(cls, alert_id: str) -> bool:
        """Mark alert as acknowledged"""
        for alert in cls._global_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                # Also update in symbol list
                symbol_alerts = cls._alerts.get(alert.symbol, [])
                for a in symbol_alerts:
                    if a.id == alert_id:
                        a.acknowledged = True
                return True
        return False
    
    @classmethod
    def clear_old_alerts(cls, days: int = 7):
        """Clear alerts older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        cls._global_alerts = [
            a for a in cls._global_alerts 
            if datetime.fromisoformat(a.timestamp) > cutoff
        ]
        
        for symbol in cls._alerts:
            cls._alerts[symbol] = [
                a for a in cls._alerts[symbol]
                if datetime.fromisoformat(a.timestamp) > cutoff
            ]
    
    @classmethod
    def get_alert_stats(cls) -> Dict:
        """Get alert statistics"""
        total = len(cls._global_alerts)
        unacknowledged = len([a for a in cls._global_alerts if not a.acknowledged])
        
        by_type = {}
        for alert_type in AlertType:
            count = len([a for a in cls._global_alerts if a.type == alert_type])
            if count > 0:
                by_type[alert_type.value] = count
        
        by_severity = {}
        for severity in AlertSeverity:
            count = len([a for a in cls._global_alerts if a.severity == severity])
            if count > 0:
                by_severity[severity.value] = count
        
        return {
            'total': total,
            'unacknowledged': unacknowledged,
            'by_type': by_type,
            'by_severity': by_severity,
            'symbols_with_alerts': len(cls._alerts)
        }


# Global alert service instance
alert_service = AlertService()
