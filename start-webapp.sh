#!/bin/bash

# Procurement Agent Web App Startup Script

echo "================================================"
echo "  Procurement Agent Web Application"
echo "================================================"
echo ""

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose detected"
    echo ""
    echo "Starting with Docker Compose..."
    echo ""
    docker-compose up --build
else
    echo "⚠ Docker Compose not found. Starting manually..."
    echo ""

    # Start backend
    echo "Starting backend on port 8000..."
    cd "$(dirname "$0")"

    # Check if backend dependencies are installed
    if ! python3 -c "import fastapi" &> /dev/null; then
        echo "Installing backend dependencies..."
        pip install -r requirements.txt
        pip install -r backend/requirements.txt
    fi

    # Start backend in background
    cd backend
    python3 api.py &
    BACKEND_PID=$!
    cd ..

    echo "✓ Backend started (PID: $BACKEND_PID)"

    # Start frontend
    echo "Starting frontend on port 3000..."
    cd frontend

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi

    # Start frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo "✓ Frontend started (PID: $FRONTEND_PID)"
    echo ""
    echo "================================================"
    echo "  Application Ready!"
    echo "================================================"
    echo ""
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""

    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
fi
