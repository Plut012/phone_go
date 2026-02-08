#!/data/data/com.termux/files/usr/bin/bash
# Run script for Phone Go (Termux)

echo "=== Starting Phone Go ==="
echo ""
echo "🚀 Starting proxy server..."
echo ""

# Start proxy in background
python proxy.py &
PROXY_PID=$!

# Wait for proxy to start
sleep 2

# Try to open the URL in browser
URL="http://localhost:5000"

if command -v termux-open &> /dev/null; then
    echo "📱 Opening $URL in browser..."
    termux-open "$URL"
    echo "✓ Browser launched"
elif command -v am &> /dev/null; then
    echo "📱 Opening $URL in browser..."
    am start -a android.intent.action.VIEW -d "$URL" &> /dev/null
    echo "✓ Browser launched"
else
    echo "⚠️  Could not auto-open browser"
    echo "   Please manually open: $URL"
fi

echo ""
echo "✓ Proxy running on $URL"
echo "  Press Ctrl+C to stop"
echo ""

# Wait for proxy process
wait $PROXY_PID
