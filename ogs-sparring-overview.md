# Flow + OGS Bot Sparring

A minimal setup for playing Go against OGS bots from your phone, wrapped in your own UI.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│   flow.html     │ ◄─────► │   proxy.py      │ ◄─────► │   OGS Server    │
│   (browser)     │  local  │   (Termux)      │  https  │                 │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
      Your UI                 CORS bypass               Bots + game logic
```

## Why a proxy?

Browsers block cross-origin requests from local HTML files. OGS won't respond to `file://` origins. A tiny local proxy running on your phone (via Termux) forwards requests to OGS, bypassing CORS entirely.

## Components

| File | Purpose |
|------|---------|
| `flow.html` | Go board UI — displays game, handles input |
| `proxy.py` | ~50 lines — forwards REST/WebSocket to OGS |

## OGS API Flow

**1. Authenticate**
```
POST https://online-go.com/api/v0/login
Body: {"username": "...", "password": "..."}
→ Returns cookies
```

**2. Get tokens**
```
GET https://online-go.com/api/v1/ui/config
→ Returns chat_auth, notification_auth, user.id
```

**3. Open WebSocket**
```
Connect: wss://online-go.com/socket.io/?transport=websocket
Send: 42["authenticate", {"player_id": ..., "username": ..., "auth": ...}]
```

**4. Challenge a bot**
```
POST https://online-go.com/api/v1/players/{bot_id}/challenge/
Body: {
  "game": {
    "name": "Sparring",
    "rules": "chinese",
    "ranked": false,
    "width": 9,
    "height": 9,
    "time_control": "fischer",
    ...
  }
}
→ Returns game_id
```

**5. Connect to game**
```
Send: 42["game/connect", {"game_id": ..., "player_id": ...}]
Receive: 42["game/{id}/gamedata", {...}]  // full game state
```

**6. Play moves**
```
Send: 42["game/move", {"game_id": ..., "player_id": ..., "move": "cd"}]
Receive: 42["game/{id}/move", {"move": [2, 3]}]  // opponent's response
```

## Bot IDs (for challenges)

| Bot | ID | Strength | Availability |
|-----|----|----------|--------------|
| amybot-beginner | 605979 | ~25k | Always ✅ |
| amybot-ddk | 431859 | ~15k | Always ✅ |
| amybot-sdk | 424928 | ~5k | Always ✅ (Default) |
| NightlyKataGo | 530672 | Very Strong | Usually ✅ |
| kata-bot | 592684 | Strong | Intermittent ⚠️ |

**Note**: User-run bots (Leela Zero, etc.) often offline. Stick with Amy bots for reliability.

## Phone Setup (Termux)

```bash
pkg install python
pip install websockets requests flask
python proxy.py
```

Then open `flow.html` in Chrome. It talks to `localhost:5000`.

## Security Notes

- Your OGS credentials stay local (proxy only)
- Use an alt account if paranoid
- This is for personal use only

## Status

- [x] UI: go-flow.html with bot selection, board sizes, color choice
- [x] Proxy: proxy.py serving HTML at localhost:5000
- [x] Integration: WebSocket + REST API fully connected
- [x] Visual submit: Preview + confirmation bar
- [x] Time control: 5min Fischer games
- [x] Multiple bots: Amy series, KataGo, NightlyKataGo
