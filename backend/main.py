"""
Chartwise AI - Backend API
FastAPI application for trading analysis and predictions
"""

from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import asyncio
import uvicorn
import os

from app.database import engine, Base, get_db
from app.routers import stocks, crypto, predictions, paper_trading, watchlist
from app.routers import enhanced_predictions
from app.routers import auth
from app.routers import ai_coach
from app.services.data_service import DataService
from app.services.prediction_service import PredictionService

# Create FastAPI app
app = FastAPI(
    title="Chartwise AI API",
    description="AI-powered trading analysis and predictions",
    version="1.0.0"
)

# CORS configuration - allow all origins for Render deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(crypto.router, prefix="/api/crypto", tags=["crypto"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(paper_trading.router, prefix="/api/paper-trading", tags=["paper-trading"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
app.include_router(enhanced_predictions.router)
app.include_router(ai_coach.router)

# Global scheduler reference
scheduler = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Chartwise AI API starting up...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
    
    # Initialize data service
    try:
        DataService.initialize()
        print("✅ Data service initialized")
    except Exception as e:
        print(f"⚠️ Data service init error: {e}")
    
    # Start scheduler only if enabled
    if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
        try:
            from app.scheduler import scheduler as sched
            global scheduler
            scheduler = sched
            scheduler.start()
            print("✅ Scheduler started")
        except Exception as e:
            print(f"⚠️ Scheduler start error: {e}")
    else:
        print("ℹ️ Scheduler disabled (set ENABLE_SCHEDULER=true to enable)")

@app.get("/")
async def root():
    return {
        "message": "Chartwise AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scheduler": "running" if scheduler and scheduler.running else "disabled"
    }

# WebSocket placeholder (simplified for deployment)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"type": "connected", "message": "WebSocket connected"})
    # Keep connection alive
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "data": data})
    except:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
