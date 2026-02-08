# Flow + OGS Bot Sparring

Play Go against OGS bots from your phone with a custom UI.

## Quick Start

**On Termux (Android):**
```bash
./setup.sh  # First time only
./run.sh    # Start proxy
```

**On desktop/laptop:**

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the proxy
```bash
python proxy.py
```

The proxy runs on `http://localhost:5000`

### 3. Open the UI
Open `http://localhost:5000` in your browser (Chrome recommended)

### 4. Play!
- Click "Play Bot"
- Choose opponent (Amy Bot SDK recommended for learning)
- Select board size (9x9, 13x13, or 19x19)
- Select your color (Black or White)
- Click "Start Game"
- Tap board to preview, tap golden bar to submit move
- Use Pass or Resign buttons as needed

## Features

- **5 Bot Opponents**: Choose from beginner to advanced (Amy Bots, KataGo, NightlyKataGo)
- **3 Board Sizes**: 9x9, 13x13, or 19x19
- **Color Selection**: Play as Black or White
- **Visual Submit**: Preview move with semi-transparent stone, tap bar to confirm
- **Pass & Resign**: Full game control
- **5-Minute Games**: Comfortable thinking time (Fischer: 5min + 30s/move)
- **Review SGF**: Load and navigate through SGF files

## How it works

```
Browser (localhost:5000) ↔ Proxy Server ↔ OGS Server
```

The proxy server:
- Serves the HTML UI at `http://localhost:5000`
- Bypasses CORS restrictions
- Forwards REST API calls (login, challenge, game details)
- Forwards WebSocket messages (real-time moves)

## Termux Setup (Android)

**Quick setup:**
```bash
./setup.sh  # One-time setup
./run.sh    # Auto-opens browser and starts proxy
```

**Manual setup:**
```bash
pkg install python
pip install -r requirements.txt
python proxy.py
```

Then open `http://localhost:5000` in your browser

## Available Bots

- **Amy Bot Beginner** (~25k) - Basic, always available
- **Amy Bot DDK** (~15k) - Solid play, always available
- **Amy Bot SDK** (~5k) - Tactical, always available ⭐ Default
- **NightlyKataGo** (Very Strong) - Fighting style, usually available
- **KataGo** (Strong) - Modern AI, intermittent

## Current Settings

- **Time Control**: Fischer (5min + 30s/move, max 10min)
- **Board Sizes**: 9x9, 13x13, 19x19
- **Colors**: Black or White (no random)

## Notes

- Requires valid OGS account
- Games are unranked
- Uses legacy cookie authentication
- Keep-alive pings every 20 seconds

## Troubleshooting

**"Connection failed"**: Make sure proxy.py is running
**"Login error"**: Check your OGS credentials
**Board not showing**: Check browser console for errors
