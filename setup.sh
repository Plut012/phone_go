#!/data/data/com.termux/files/usr/bin/bash
# Setup script for Phone Go (Termux)

echo "=== Phone Go Setup for Termux ==="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "📦 Installing Python..."
    pkg install python -y
else
    echo "✓ Python already installed"
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install Python first."
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Setting up credentials..."
    echo "Enter your OGS username (or press Enter to skip):"
    read -r username

    if [ -n "$username" ]; then
        echo "Enter your OGS password:"
        read -rs password
        echo ""

        echo "OGS_USERNAME=$username" > .env
        echo "OGS_PASSWORD=$password" >> .env
        echo "✓ Credentials saved to .env"
    else
        echo "⚠️  Skipped credential setup. You'll need to login manually."
    fi
else
    echo "✓ .env file already exists"
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start the proxy:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  python proxy.py"
echo ""
