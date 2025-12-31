#!/bin/bash

# ArtPriv API Test Runner Script
# This script starts the server, runs tests, and generates a report

echo "🚀 ArtPriv API Test Runner"
echo "================================"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating venv..."
    source venv/bin/activate
fi

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Server already running on port 8000"
    SERVER_RUNNING=true
else
    echo "🔄 Starting FastAPI server..."
    uvicorn main:app --reload > server.log 2>&1 &
    SERVER_PID=$!
    SERVER_RUNNING=false
    
    # Wait for server to start
    echo "⏳ Waiting for server to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Server is ready!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo "❌ Server failed to start after 30 seconds"
            cat server.log
            exit 1
        fi
    done
fi

echo ""
echo "🧪 Running API tests..."
echo "================================"
echo ""

# Run tests
python test_api.py
TEST_EXIT_CODE=$?

echo ""
echo "================================"

# Cleanup
if [ "$SERVER_RUNNING" = false ]; then
    echo "🛑 Stopping test server..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
fi

# Show results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Check test_report.json for details."
fi

echo ""
echo "📄 Test report: test_report.json"
echo "📋 Server logs: server.log"
echo ""

exit $TEST_EXIT_CODE
