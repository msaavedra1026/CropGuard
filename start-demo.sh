#!/usr/bin/env bash
# CropGuard Demo Launcher
# Starts FastAPI backend + FiftyOne App side by side

set -e

echo "🌱 Starting CropGuard demo..."

# Start FastAPI server in background
echo "→ Starting FastAPI on port 8000..."
cd backend
uvicorn server:app --reload --port 8000 &
FASTAPI_PID=$!
cd ..

# Start FiftyOne App in background
echo "→ Starting FiftyOne App on port 5151..."
python -c "import fiftyone as fo; dataset = fo.load_dataset('cropguard'); session = fo.launch_app(dataset, port=5151); session.wait()" &
FIFTYONE_PID=$!

echo ""
echo "✅ CropGuard is running:"
echo "   FastAPI  → http://localhost:8000/docs"
echo "   FiftyOne → http://localhost:5151"
echo ""
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C to kill both processes
trap "kill $FASTAPI_PID $FIFTYONE_PID 2>/dev/null; echo ''; echo 'Demo stopped.'" EXIT

wait
