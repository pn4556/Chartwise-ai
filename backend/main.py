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
from app.services.data_service import DataService
from app.services.prediction_service import PredictionService
from app.scheduler import scheduler
from app.websocket import manager, handle_websocket

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chartwise AI API",
    description="AI-powered trading analysis and predictions",
    version="1.0.0"
)

# CORS configuration - use FRONTEND_URL env var for production
# Allow multiple origins for local development and production
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Chartwise AI API starting up...")
    # Initialize data service
    DataService.initialize()
    print("✅ Data service initialized")
    
    # Start scheduler for automatic updates
    scheduler.start()
    print("✅ Scheduler started")

@app.get("/")
async def root():
    return {
        "message": "Chartwise AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scheduler": scheduler.get_status(),
        "websocket_connections": len(manager.active_connections)
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
