#!/data/data/com.termux/files/usr/bin/bash
# Run script for Phone Go (Termux)

echo "=== Starting Phone Go ==="
echo ""

# Get the absolute path to the HTML file
HTML_FILE="$(pwd)/go-flow.html"

# Try to open the HTML file in browser
if command -v termux-open &> /dev/null; then
    echo "📱 Opening go-flow.html in browser..."
    termux-open "$HTML_FILE"
    echo "✓ Browser launched"
elif command -v am &> /dev-null; then
    echo "📱 Opening go-flow.html in browser..."
    am start -a android.intent.action.VIEW -d "file://$HTML_FILE" -t "text/html" &> /dev/null
    echo "✓ Browser launched"
else
    echo "⚠️  Could not auto-open browser"
    echo "   Please manually open: file://$HTML_FILE"
fi

echo ""
echo "🚀 Starting proxy on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

python proxy.py
