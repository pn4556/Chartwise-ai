#!/bin/bash
# Render.com startup script for Chartwise AI Backend

set -e

echo "🚀 Starting Chartwise AI Backend on Render.com..."

# Check required environment variables
echo "🔍 Checking environment variables..."

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
fi

echo "✅ DATABASE_URL is configured"

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  WARNING: SECRET_KEY is not set. Using default (not recommended for production)"
fi

if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  WARNING: FRONTEND_URL is not set. CORS may not work correctly."
fi

# Handle Render's postgres:// URL format (SQLAlchemy requires postgresql://)
if [[ "$DATABASE_URL" == postgres://* ]]; then
    echo "🔄 Converting postgres:// to postgresql://..."
    export DATABASE_URL="${DATABASE_URL/postgres:\/\//postgresql:\/\/}"
fi

# Log configuration (without sensitive data)
echo ""
echo "📊 Configuration:"
echo "  - Host: 0.0.0.0"
echo "  - Port: ${PORT:-8000}"
echo "  - Database: PostgreSQL (configured via DATABASE_URL)"
echo "  - Frontend URL: ${FRONTEND_URL:-not set}"
echo "  - Scheduler: ${ENABLE_SCHEDULER:-true}"
echo ""

# Start the application
echo "🌟 Starting Uvicorn server..."
exec uvicorn main:app \
    --host "0.0.0.0" \
    --port "${PORT:-8000}" \
    --workers 1 \
    --access-log \
    --log-level info
