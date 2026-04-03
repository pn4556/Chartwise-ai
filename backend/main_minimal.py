"""
Chartwise AI - Minimal API for testing Render deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(
    title="Chartwise AI API",
    description="AI-powered trading analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chartwise AI API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/predictions/top")
async def get_top_picks():
    """Return mock top picks for testing"""
    return {
        "stocks": [
            {"symbol": "AAPL", "name": "Apple Inc.", "score": 85, "recommendation": "BUY"},
            {"symbol": "NVDA", "name": "NVIDIA Corp", "score": 92, "recommendation": "STRONG_BUY"},
            {"symbol": "MSFT", "name": "Microsoft", "score": 78, "recommendation": "BUY"},
        ]
    }
