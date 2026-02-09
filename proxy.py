#!/usr/bin/env python3
"""
Minimal proxy for OGS API - bypasses CORS for local HTML files
Runs on phone via Termux: python proxy.py
"""

import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import socketio
import threading
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
from websockets.sync.client import connect as ws_connect

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from file:// origins

# WebSocket clients: {client_sid: {'ogs_ws': websocket, 'thread': thread}}
ws_clients = {}

# OGS endpoints
OGS_BASE = "https://online-go.com"
OGS_WS_URL = "wss://online-go.com/socket.io/?transport=websocket"

# Persistent HTTP session (handles cookies automatically)
http_session = requests.Session()


def log(msg):
    print(f"[PROXY] {msg}")


def auto_login():
    """Auto-login using credentials from environment variables"""
    username = os.getenv('OGS_USERNAME')
    password = os.getenv('OGS_PASSWORD')

    if not username or not password:
        log("No credentials in environment - manual login required")
        return False

    log(f"Auto-login for user: {username}")

    try:
        # Login
        resp = http_session.post(
            f"{OGS_BASE}/api/v0/login",
            json={"username": username, "password": password},
            headers={'Content-Type': 'application/json'}
        )

        if resp.status_code != 200:
            log(f"Auto-login failed: {resp.status_code}")
            return False

        log(f"Auto-login successful!")
        if http_session.cookies:
            log(f"Cookies stored: {list(http_session.cookies.keys())}")

        return True

    except Exception as e:
        log(f"Auto-login error: {e}")
        return False


# ============================================================================
# Serve HTML UI
# ============================================================================

@app.route('/')
def serve_html():
    """Serve the go-flow.html file"""
    from flask import make_response
    response = make_response(send_file('go-flow.html'))
    # Disable caching for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/manifest.json')
def serve_manifest():
    """Serve the PWA manifest"""
    return send_file('manifest.json', mimetype='application/json')

@app.route('/icon-192.png')
def serve_icon_192():
    """Serve the 192x192 icon"""
    return send_file('icon-192.png', mimetype='image/png')

@app.route('/icon-512.png')
def serve_icon_512():
    """Serve the 512x512 icon"""
    return send_file('icon-512.png', mimetype='image/png')


# ============================================================================
# REST API Proxy
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """Forward login request to OGS"""
    data = request.json
    log(f"Login request for user: {data.get('username')}")

    try:
        resp = http_session.post(
            f"{OGS_BASE}/api/v0/login",
            json=data,
            headers={'Content-Type': 'application/json'}
        )

        # Session automatically stores cookies
        log(f"Login response: {resp.status_code}")
        if resp.cookies:
            log(f"Cookies received: {list(resp.cookies.keys())}")

        return jsonify(resp.json() if resp.text else {}), resp.status_code

    except Exception as e:
        log(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get UI config with auth tokens"""
    log("Getting config")

    try:
        resp = http_session.get(
            f"{OGS_BASE}/api/v1/ui/config"
        )

        config = resp.json()
        log(f"Got config for user: {config.get('user', {}).get('username')}")
        return jsonify(config), resp.status_code

    except Exception as e:
        log(f"Config error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/challenge/<int:bot_id>', methods=['POST'])
def challenge_bot(bot_id):
    """Challenge a bot"""
    data = request.json
    log(f"Challenging bot {bot_id}")

    try:
        # Log all cookies in session
        log(f"Session cookies: {list(http_session.cookies.keys())}")

        # Get CSRF token from session cookies
        csrf_token = http_session.cookies.get('csrftoken', '')
        sessionid = http_session.cookies.get('sessionid', '')
        log(f"CSRF token: {csrf_token[:20] + '...' if csrf_token else 'MISSING'}")
        log(f"Session ID: {sessionid[:20] + '...' if sessionid else 'MISSING'}")

        resp = http_session.post(
            f"{OGS_BASE}/api/v1/players/{bot_id}/challenge/",
            json=data,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token,
                'Referer': 'https://online-go.com/'
            }
        )

        if resp.status_code >= 400:
            log(f"Challenge failed: {resp.status_code} - {resp.text[:200]}")
            return jsonify({"error": f"HTTP {resp.status_code}", "details": resp.text[:200]}), resp.status_code

        result = resp.json()
        log(f"Challenge created: game_id={result.get('game')}")
        return jsonify(result), resp.status_code

    except Exception as e:
        log(f"Challenge error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/game/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Get game details"""
    log(f"Getting game {game_id}")

    try:
        resp = http_session.get(
            f"{OGS_BASE}/api/v1/games/{game_id}"
        )

        return jsonify(resp.json()), resp.status_code

    except Exception as e:
        log(f"Get game error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# WebSocket Proxy
# ============================================================================

sio_server = socketio.Server(
    async_mode='threading',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)

# Wrap Flask app with Socket.IO
app.wsgi_app = socketio.WSGIApp(sio_server, app.wsgi_app)


@sio_server.event
def connect(sid, environ):
    log(f"Client connected: {sid}")


@sio_server.event
def disconnect(sid):
    log(f"Client disconnected: {sid}")
    if sid in ws_clients:
        try:
            ws_clients[sid]['ogs_ws'].close()
        except:
            pass
        del ws_clients[sid]


def ogs_receiver_thread(sid, ogs_ws):
    """Thread to receive messages from OGS and forward to client"""
    try:
        for message in ogs_ws:
            log(f"OGS -> Client: {message[:100]}")
            # Parse Socket.IO message and forward to client
            try:
                # Socket.IO messages are like: 42["event",{data}]
                if message.startswith('42'):
                    # Parse the event and data
                    msg = message[2:]  # Remove '42' prefix
                    parsed = json.loads(msg)
                    if len(parsed) >= 2:
                        event = parsed[0]
                        data = parsed[1] if len(parsed) > 1 else None
                        sio_server.emit(event, data, room=sid)
                elif message.startswith('0'):
                    # Connection success
                    log(f"OGS WebSocket connected")
                    sio_server.emit('ogs_connected', room=sid)
                elif message.startswith('2'):
                    # Ping - respond with pong
                    ogs_ws.send('3')
            except Exception as e:
                log(f"Error parsing message: {e}")
    except Exception as e:
        log(f"OGS receiver error: {e}")
    finally:
        log(f"OGS connection closed for {sid}")
        sio_server.emit('ogs_disconnected', room=sid)


@sio_server.event
def connect_ogs(sid):
    """Client requests connection to OGS WebSocket"""
    log(f"Client {sid} connecting to OGS")

    try:
        # Connect raw WebSocket to OGS
        log(f"Connecting to {OGS_WS_URL}")
        ogs_ws = ws_connect(OGS_WS_URL)

        # Start receiver thread
        receiver = threading.Thread(target=ogs_receiver_thread, args=(sid, ogs_ws), daemon=True)
        receiver.start()

        ws_clients[sid] = {'ogs_ws': ogs_ws, 'thread': receiver}
        log(f"WebSocket connected for client {sid}")

    except Exception as e:
        log(f"OGS connection error: {e}")
        import traceback
        traceback.print_exc()
        sio_server.emit('error', {'message': str(e)}, room=sid)


@sio_server.on('*')
def catch_all_from_client(event, sid, data=None):
    """Forward all client events to OGS"""
    # Skip our internal events
    if event in ['connect', 'disconnect', 'connect_ogs']:
        return

    log(f"Client -> OGS: {event}")

    if sid in ws_clients:
        try:
            # Format as Socket.IO message: 42["event",data]
            if data is not None:
                msg = f'42{json.dumps([event, data])}'
            else:
                msg = f'42{json.dumps([event])}'

            ws_clients[sid]['ogs_ws'].send(msg)
            log(f"Sent to OGS: {msg[:100]}")
        except Exception as e:
            log(f"Error forwarding {event}: {e}")
            import traceback
            traceback.print_exc()
    else:
        log(f"No OGS connection for client {sid}")


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    log("Starting OGS proxy on http://localhost:5000")
    log("Serving UI at http://localhost:5000/")

    # Try auto-login if credentials are in environment
    auto_login()

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
