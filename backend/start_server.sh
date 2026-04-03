#!/bin/bash
# Start Chartwise AI Backend Server

cd "$(dirname "$0")"
source venv/bin/activate

echo "🚀 Starting Chartwise AI Backend..."
echo "📊 API will be available at: http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
