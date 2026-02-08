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
Open `go-flow.html` in your browser (Chrome recommended)

### 4. Play!
- Click "Play Bot"
- Select board size (9x9, 13x13, or 19x19)
- Click "Start Game"
- Tap the board to place stones
- Use Pass or Resign buttons as needed

## Features

- **Play Bot**: Challenge amybot-beginner (25k) on 9x9, 13x13, or 19x19 boards
- **Pass & Resign**: Proper game control buttons
- **Review SGF**: Load and navigate through SGF files

## How it works

```
Browser (go-flow.html) ↔ Proxy (localhost:5000) ↔ OGS Server
```

The proxy bypasses CORS restrictions and forwards:
- REST API calls (login, challenge, game details)
- WebSocket messages (real-time moves)

## Termux Setup (Android)

**Quick setup:**
```bash
./setup.sh
./run.sh
```

**Manual setup:**
```bash
pkg install python
pip install -r requirements.txt
python proxy.py
```

Then open `go-flow.html` in Chrome at `file:///...`

## Configuration

Edit `go-flow.html` to change:
- `BOT_ID`: Default is 605979 (amybot-beginner)
  - 431859: amybot-ddk (~15k)
  - 424928: amybot-sdk (~5k)
- Board size (currently 9x9)
- Time controls (currently Fischer: 120s + 30s/move, max 300s)

## Notes

- Requires valid OGS account
- Games are unranked
- Uses legacy cookie authentication
- Keep-alive pings every 20 seconds

## Troubleshooting

**"Connection failed"**: Make sure proxy.py is running
**"Login error"**: Check your OGS credentials
**Board not showing**: Check browser console for errors
