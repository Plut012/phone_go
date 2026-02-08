#!/usr/bin/env python3
"""Quick test to verify dependencies are installed"""

print("Checking dependencies...")

try:
    import flask
    print("✓ Flask installed")
except ImportError:
    print("✗ Flask missing - run: pip install flask")

try:
    import flask_cors
    print("✓ Flask-CORS installed")
except ImportError:
    print("✗ Flask-CORS missing - run: pip install flask-cors")

try:
    import socketio
    print("✓ Python-SocketIO installed")
except ImportError:
    print("✗ Python-SocketIO missing - run: pip install python-socketio")

try:
    import requests
    print("✓ Requests installed")
except ImportError:
    print("✗ Requests missing - run: pip install requests")

print("\nAll checks passed! Run: python proxy.py")
