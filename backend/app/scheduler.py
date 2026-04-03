"""
Scheduler for automatic data updates
Runs every 15 minutes to refresh predictions
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import asyncio

from app.services.technical_analysis import TechnicalAnalysisService
from app.services.prediction_service import PredictionService
from app.websocket import manager

# Get event loop for async operations
_loop = None

def get_event_loop():
    global _loop
    if _loop is None:
        try:
            _loop = asyncio.get_running_loop()
        except RuntimeError:
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
    return _loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default symbols to track
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

class UpdateScheduler:
    """Manages scheduled updates for predictions"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Add job to update predictions every 15 minutes
        self.scheduler.add_job(
            self.update_predictions,
            trigger=IntervalTrigger(minutes=15),
            id='update_predictions',
            name='Update Stock/Crypto Predictions',
            replace_existing=True
        )
        
        # Add job to clear old cache every hour
        self.scheduler.add_job(
            self.clear_old_cache,
            trigger=IntervalTrigger(hours=1),
            id='clear_cache',
            name='Clear Old Cache',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("✅ Scheduler started - Updates every 15 minutes")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def update_predictions(self):
        """Update all predictions and broadcast via WebSocket"""
        logger.info(f"🔄 Starting prediction update at {datetime.now()}")
        
        all_symbols = DEFAULT_STOCKS + DEFAULT_CRYPTOS
        updated = 0
        failed = 0
        updated_predictions = []
        
        for symbol in all_symbols:
            try:
                # This will trigger prediction calculation and caching
                prediction = PredictionService.get_prediction(symbol)
                if prediction:
                    updated_predictions.append(prediction)
                updated += 1
            except Exception as e:
                logger.error(f"Failed to update {symbol}: {e}")
                failed += 1
        
        logger.info(f"✅ Updated {updated} predictions, {failed} failed")
        
        # Broadcast updates via WebSocket
        if updated_predictions:
            self._broadcast_updates(updated_predictions)
    
    def _broadcast_updates(self, predictions: list):
        """Broadcast prediction updates to subscribed clients"""
        try:
            loop = get_event_loop()
            
            for prediction in predictions:
                symbol = prediction.get('symbol', '')
                if symbol:
                    message = {
                        'type': 'prediction_update',
                        'symbol': symbol,
                        'data': prediction,
                        'timestamp': datetime.now().isoformat()
                    }
                    # Broadcast to symbol subscribers
                    if symbol in manager.subscriptions:
                        asyncio.run_coroutine_threadsafe(
                            manager.broadcast_to_symbol(symbol, message),
                            loop
                        )
            
            # Also broadcast summary to all connected clients
            summary_message = {
                'type': 'predictions_refreshed',
                'count': len(predictions),
                'timestamp': datetime.now().isoformat()
            }
            asyncio.run_coroutine_threadsafe(
                manager.broadcast_to_all(summary_message),
                loop
            )
            
            logger.info(f"📡 Broadcasted updates for {len(predictions)} predictions via WebSocket")
        except Exception as e:
            logger.error(f"Failed to broadcast WebSocket updates: {e}")
    
    def clear_old_cache(self):
        """Clear old cached predictions"""
        logger.info("🧹 Clearing old cache")
        PredictionService.clear_cache()
        logger.info("✅ Cache cleared")
    
    def get_status(self):
        """Get scheduler status"""
        jobs = self.scheduler.get_jobs()
        return {
            'is_running': self.is_running,
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }

# Global scheduler instance
scheduler = UpdateScheduler()
