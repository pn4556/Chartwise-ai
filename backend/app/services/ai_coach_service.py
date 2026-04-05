"""
AI Coach Service
Provides AI-powered insights, predictions, and coaching for trading decisions
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import random

from app.services.enhanced_analysis import EnhancedTechnicalAnalysis, TechnicalIndicators


@dataclass
class AIInsight:
    """Single AI insight/recommendation"""
    type: str  # 'prediction', 'warning', 'opportunity', 'coach_tip'
    asset: str
    message: str
    confidence: float
    action: str  # 'buy', 'sell', 'hold', 'watch'
    timeframe: str
    reasoning: List[str]
    risk_level: str  # 'low', 'medium', 'high'
    timestamp: str


@dataclass
class SectorAIAnalysis:
    """AI analysis for an entire sector"""
    sector: str
    outlook: str  # 'bullish', 'bearish', 'neutral', 'mixed'
    confidence: float
    top_picks: List[Dict]
    avoid: List[Dict]
    insight: str
    catalysts: List[str]
    risks: List[str]
    ai_score: float  # 0-100 composite score


@dataclass
class AICoachResponse:
    """Complete AI coach response"""
    summary: str
    insights: List[AIInsight]
    sector_analysis: List[SectorAIAnalysis]
    market_sentiment: str
    top_opportunities: List[Dict]
    warnings: List[str]
    generated_at: str


class AICoachService:
    """
    AI Coach that analyzes market data and provides actionable insights
    Simulates AI analysis with sophisticated rule-based logic
    """
    
    # Sector-specific context and keywords
    SECTOR_CONTEXT = {
        'Tech': {
            'catalysts': ['AI adoption', 'cloud growth', 'semiconductor demand', 'software expansion'],
            'risks': ['valuation concerns', 'interest rate sensitivity', 'regulatory scrutiny'],
            'momentum_factors': ['earnings beats', 'guidance raises', 'product launches']
        },
        'AI': {
            'catalysts': ['generative AI boom', 'enterprise adoption', 'infrastructure buildout', 'compute demand'],
            'risks': ['bubble concerns', 'profitability timeline', 'competition intensity'],
            'momentum_factors': ['contract wins', 'partnership announcements', 'revenue acceleration']
        },
        'Healthcare': {
            'catalysts': ['drug approvals', 'aging demographics', 'innovation pipeline', 'M&A activity'],
            'risks': ['regulatory delays', 'patent cliffs', 'pricing pressure'],
            'momentum_factors': ['trial results', 'FDA approvals', 'guidance raises']
        },
        'Finance': {
            'catalysts': ['rate environment', 'M&A activity', 'trading volumes', 'fintech disruption'],
            'risks': ['credit cycle', 'regulatory changes', 'economic slowdown'],
            'momentum_factors': ['NIM expansion', 'loan growth', 'fee income']
        },
        'Energy': {
            'catalysts': ['supply constraints', 'geopolitical tensions', 'transition investments', 'OPEC+ decisions'],
            'risks': ['demand destruction', 'renewable transition', 'price volatility'],
            'momentum_factors': ['production beats', 'cost reductions', 'dividend growth']
        },
        'Consumer': {
            'catalysts': ['consumer spending', 'brand strength', 'e-commerce growth', 'travel recovery'],
            'risks': ['inflation impact', 'discretionary cuts', 'competition'],
            'momentum_factors': ['same-store sales', 'guidance raises', 'market share gains']
        },
        'Photonics': {
            'catalysts': ['data center growth', 'lidar adoption', 'defense spending', 'quantum computing'],
            'risks': ['cyclical demand', 'customer concentration', 'tech transitions'],
            'momentum_factors': ['design wins', 'capacity expansion', 'new product ramps']
        }
    }
    
    COACH_PERSONALITIES = [
        "Based on my analysis of over 50 technical indicators",
        "Looking at the convergence of multiple signals",
        "After analyzing institutional flow patterns",
        "Based on multi-timeframe momentum analysis",
        "Considering both technical and market structure factors"
    ]
    
    @classmethod
    def generate_asset_insight(cls, symbol: str, indicators: TechnicalIndicators, 
                               prediction_data: Dict) -> AIInsight:
        """Generate AI insight for a specific asset"""
        
        # Determine primary signal
        prob_up = prediction_data.get('probabilities', {}).get('up', 33)
        prob_down = prediction_data.get('probabilities', {}).get('down', 33)
        confidence = prediction_data.get('confidence', 50)
        
        # Generate AI message based on signals
        if prob_up > 60 and confidence > 65:
            message_template = random.choice([
                "🚀 {symbol} showing strong bullish convergence. Multiple indicators aligned for upside.",
                "📈 {symbol} technical structure suggests imminent breakout. High conviction setup.",
                "✅ {symbol} momentum building across timeframes. Institutional accumulation detected."
            ])
            action = 'buy'
            insight_type = 'opportunity'
            
        elif prob_down > 60 and confidence > 65:
            message_template = random.choice([
                "⚠️ {symbol} flashing warning signs. Distribution patterns emerging.",
                "📉 {symbol} bearish divergence across multiple timeframes. Consider reducing exposure.",
                "🔴 {symbol} momentum decelerating. Support levels being tested."
            ])
            action = 'sell'
            insight_type = 'warning'
            
        elif confidence < 40:
            message_template = random.choice([
                "🤔 {symbol} in consolidation phase. Mixed signals - best to watch from sidelines.",
                "⏸️ {symbol} lacking clear direction. Range-bound conditions expected to continue.",
                "⚖️ {symbol} equilibrium between buyers and sellers. Awaiting catalyst."
            ])
            action = 'watch'
            insight_type = 'coach_tip'
            
        else:
            message_template = random.choice([
                "📊 {symbol} showing {direction} bias with moderate confidence. Manage position size.",
                "🎯 {symbol} technicals suggest {direction} momentum but expect volatility.",
                "💡 {symbol} trend intact but be mindful of overhead resistance/support levels."
            ])
            action = 'hold' if prob_up > 50 else 'watch'
            insight_type = 'coach_tip'
        
        direction = "bullish" if prob_up > prob_down else "bearish"
        message = message_template.format(symbol=symbol, direction=direction)
        
        # Generate reasoning
        reasoning = cls._generate_reasoning(indicators, prediction_data)
        
        # Determine risk level
        if indicators.atr > 5 or indicators.bb_width > 0.15:
            risk_level = 'high'
        elif indicators.atr > 2.5 or indicators.bb_width > 0.08:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Determine timeframe
        if indicators.adx > 35:
            timeframe = 'short-term (1-5 days)'
        elif indicators.current_price > indicators.ma50:
            timeframe = 'medium-term (1-4 weeks)'
        else:
            timeframe = 'swing trade (2-8 weeks)'
        
        return AIInsight(
            type=insight_type,
            asset=symbol,
            message=message,
            confidence=confidence,
            action=action,
            timeframe=timeframe,
            reasoning=reasoning,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat()
        )
    
    @classmethod
    def _generate_reasoning(cls, ind: TechnicalIndicators, prediction_data: Dict) -> List[str]:
        """Generate detailed reasoning for AI insight"""
        reasons = []
        
        # Momentum reasoning
        if ind.rsi < 30:
            reasons.append(f"RSI at {ind.rsi:.1f} indicates oversold conditions")
        elif ind.rsi > 70:
            reasons.append(f"RSI at {ind.rsi:.1f} shows overbought conditions")
        
        # Trend reasoning
        if ind.current_price > ind.ma20 > ind.ma50:
            reasons.append("Price above key MAs - bullish structure intact")
        elif ind.current_price < ind.ma20 < ind.ma50:
            reasons.append("Price below key MAs - bearish structure")
        
        # Volume reasoning
        if ind.volume > ind.avg_volume * 1.3:
            reasons.append(f"Volume {ind.volume/ind.avg_volume:.1f}x average confirms conviction")
        
        # Pattern reasoning
        if ind.candlestick_pattern != 'none':
            pattern_clean = ind.candlestick_pattern.replace('_', ' ').title()
            reasons.append(f"{pattern_clean} pattern detected")
        
        # VWAP reasoning
        if ind.price_vs_vwap == 'above':
            reasons.append("Trading above VWAP - bullish institutional flow")
        elif ind.price_vs_vwap == 'below':
            reasons.append("Trading below VWAP - bearish institutional flow")
        
        # Support/Resistance
        price = ind.current_price
        if abs(price - ind.support_level) / price < 0.02:
            reasons.append("Price near support - risk/reward favorable for longs")
        if abs(price - ind.resistance_level) / price < 0.02:
            reasons.append("Price approaching resistance - profit taking zone")
        
        # Bollinger Bands
        if ind.bb_width < 0.05:
            reasons.append("Bollinger squeeze - volatility expansion imminent")
        
        return reasons[:4]  # Top 4 reasons
    
    @classmethod
    def analyze_sector(cls, sector: str, stocks_data: List[Dict]) -> SectorAIAnalysis:
        """Generate AI analysis for an entire sector"""
        
        if not stocks_data:
            return SectorAIAnalysis(
                sector=sector,
                outlook='neutral',
                confidence=50,
                top_picks=[],
                avoid=[],
                insight="Insufficient data for analysis",
                catalysts=[],
                risks=[],
                ai_score=50
            )
        
        # Calculate sector metrics
        avg_score = sum(s.get('score', 50) for s in stocks_data) / len(stocks_data)
        avg_confidence = sum(s.get('confidence', 50) for s in stocks_data) / len(stocks_data)
        bullish_count = sum(1 for s in stocks_data if s.get('score', 50) > 60)
        bearish_count = sum(1 for s in stocks_data if s.get('score', 50) < 40)
        
        # Determine outlook
        if bullish_count > len(stocks_data) * 0.6 and avg_score > 60:
            outlook = 'bullish'
            confidence = min(95, avg_confidence * 1.1)
        elif bearish_count > len(stocks_data) * 0.6 and avg_score < 40:
            outlook = 'bearish'
            confidence = min(95, avg_confidence * 1.1)
        elif abs(avg_score - 50) < 10:
            outlook = 'neutral'
            confidence = avg_confidence * 0.9
        else:
            outlook = 'mixed'
            confidence = avg_confidence
        
        # Top picks and avoids
        sorted_stocks = sorted(stocks_data, key=lambda x: x.get('score', 50), reverse=True)
        top_picks = sorted_stocks[:3]
        avoid = sorted_stocks[-3:] if len(sorted_stocks) > 5 else []
        
        # Get sector context
        context = cls.SECTOR_CONTEXT.get(sector, {
            'catalysts': ['market conditions', 'sector rotation'],
            'risks': ['macro headwinds', 'volatility'],
            'momentum_factors': ['earnings', 'guidance']
        })
        
        # Select relevant catalysts and risks
        catalysts = random.sample(context['catalysts'], min(2, len(context['catalysts'])))
        risks = random.sample(context['risks'], min(2, len(context['risks'])))
        
        # Generate insight
        if outlook == 'bullish':
            insight = f"🟢 {sector} sector showing broad-based strength. {bullish_count}/{len(stocks_data)} stocks bullish. Key drivers: {', '.join(catalysts)}. Favor quality names with strong setups."
        elif outlook == 'bearish':
            insight = f"🔴 {sector} sector under pressure. {bearish_count}/{len(stocks_data)} stocks bearish. Headwinds include: {', '.join(risks)}. Defensive positioning warranted."
        elif outlook == 'neutral':
            insight = f"🟡 {sector} sector in consolidation. Mixed signals suggest range-bound conditions. Stock selection critical - focus on individual setups over sector beta."
        else:
            insight = f"🟠 {sector} sector showing dispersion. Leaders and laggards diverging. Best opportunities in select names with idiosyncratic catalysts."
        
        # AI score (composite)
        ai_score = (avg_score + avg_confidence) / 2
        
        return SectorAIAnalysis(
            sector=sector,
            outlook=outlook,
            confidence=round(confidence, 1),
            top_picks=[{'symbol': s['symbol'], 'score': s.get('score', 50)} for s in top_picks],
            avoid=[{'symbol': s['symbol'], 'score': s.get('score', 50)} for s in avoid],
            insight=insight,
            catalysts=catalysts,
            risks=risks,
            ai_score=round(ai_score, 1)
        )
    
    @classmethod
    def generate_market_summary(cls, all_insights: List[AIInsight]) -> str:
        """Generate overall market summary"""
        if not all_insights:
            return "Market analysis in progress. Please check back shortly."
        
        buy_signals = sum(1 for i in all_insights if i.action == 'buy')
        sell_signals = sum(1 for i in all_insights if i.action == 'sell')
        watch_signals = sum(1 for i in all_insights if i.action == 'watch')
        
        avg_confidence = sum(i.confidence for i in all_insights) / len(all_insights)
        
        intro = random.choice(cls.COACH_PERSONALITIES)
        
        if buy_signals > sell_signals * 1.5 and avg_confidence > 60:
            return f"{intro}, I'm seeing a favorable risk/reward environment. {buy_signals} quality setups identified with strong technical convergence. Favor longs with tight risk management."
        elif sell_signals > buy_signals * 1.5 and avg_confidence > 60:
            return f"{intro}, defensive positioning warranted. {sell_signals} assets showing distribution patterns. Raise cash and wait for better entries."
        elif avg_confidence < 45:
            return f"{intro}, market is in a choppy, low-conviction phase. Mixed signals across sectors suggest patience. Focus on high-conviction setups only."
        else:
            return f"{intro}, market is showing balanced conditions. Opportunities exist on both sides but selectivity is key. {buy_signals} bullish setups, {sell_signals} bearish. Stick to your process."
    
    @classmethod
    def get_coach_advice(cls, symbol: Optional[str] = None) -> Dict:
        """Get personalized coaching advice"""
        
        advice_templates = {
            'risk_management': [
                "Never risk more than 2% of your portfolio on a single trade",
                "Use position sizing based on setup quality - higher conviction = larger position",
                "Always have a stop loss before entering a position"
            ],
            'psychology': [
                "Don't chase moves - wait for your setup to come to you",
                "The best trades often feel uncomfortable at entry",
                "Missing a move is better than losing money on a forced trade"
            ],
            'technical': [
                "Volume confirms price - low volume breakouts often fail",
                "The trend is your friend until it ends",
                "Confluence of indicators > single indicator accuracy"
            ],
            'process': [
                "Journal every trade - the lessons are in the losses",
                "Review your winners too - understand what you did right",
                "Focus on execution, not outcomes"
            ]
        }
        
        category = random.choice(list(advice_templates.keys()))
        advice = random.choice(advice_templates[category])
        
        return {
            'category': category,
            'advice': advice,
            'timestamp': datetime.now().isoformat()
        }


# Create singleton instance
ai_coach = AICoachService()
