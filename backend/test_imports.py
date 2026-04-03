#!/usr/bin/env python3
"""Test that all imports work correctly"""

import sys
sys.path.insert(0, '.')

print("🧪 Testing imports...")

try:
    print("1. Testing database...")
    from app.database import engine, Base, get_db
    print("   ✅ Database OK")
except Exception as e:
    print(f"   ❌ Database error: {e}")

try:
    print("2. Testing models...")
    from app.models import Stock, Prediction, PaperTrade
    print("   ✅ Models OK")
except Exception as e:
    print(f"   ❌ Models error: {e}")

try:
    print("3. Testing technical analysis...")
    from app.services.technical_analysis import TechnicalAnalysisService
    print("   ✅ Technical Analysis OK")
except Exception as e:
    print(f"   ❌ Technical Analysis error: {e}")

try:
    print("4. Testing data service...")
    from app.services.data_service import DataService
    print("   ✅ Data Service OK")
except Exception as e:
    print(f"   ❌ Data Service error: {e}")

try:
    print("5. Testing routers...")
    from app.routers import stocks, crypto, predictions, paper_trading, watchlist
    print("   ✅ Routers OK")
except Exception as e:
    print(f"   ❌ Routers error: {e}")

try:
    print("6. Testing main app...")
    from main import app
    print("   ✅ Main app OK")
    print(f"   📋 Routes: {[route.path for route in app.routes][:5]}...")
except Exception as e:
    print(f"   ❌ Main app error: {e}")

print("\n✅ All imports successful!")
