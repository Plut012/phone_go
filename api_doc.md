# OGS (Online-Go.com) API Documentation

## Overview

OGS uses a hybrid API:
- **REST API**: Authentication, game creation, challenges
- **WebSocket API**: Real-time game play, moves, chat (via Socket.IO)

**Base URLs:**
- REST: `https://online-go.com/api/`
- WebSocket: `wss://online-go.com/socket.io/?transport=websocket`
- Real-time endpoint: `https://ggs.online-go.com`

---

## Authentication

### Method 1: Legacy (Web Client)

**Step 1: Login**
```http
POST https://online-go.com/api/v0/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```
- Returns cookies (`sessionid`, `csrftoken`)
- Must send these cookies with all subsequent requests

**Step 2: Get Config & Auth Tokens**
```http
GET https://online-go.com/api/v1/ui/config
Cookie: sessionid=...; csrftoken=...
```

**Response:**
```json
{
  "user": {
    "id": 123456,
    "username": "your_username",
    "ranking": 15.5
  },
  "chat_auth": "abc123...",
  "notification_auth": "def456..."
}
```

### Method 2: OAuth2 (Recommended for Apps)

```http
POST https://online-go.com/oauth2/token/
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=USER&password=PASS&client_id=CLIENT_ID&client_secret=CLIENT_SECRET
```

**To get client credentials:**
1. Visit https://online-go.com/oauth2/applications/
2. Create a new application
3. Save `client_id` and `client_secret`

**Use token in headers:**
```http
Authorization: Bearer {access_token}
```

**Refresh token:**
```http
POST https://online-go.com/oauth2/token/
grant_type=refresh_token&refresh_token=REFRESH_TOKEN&client_id=CLIENT_ID&client_secret=CLIENT_SECRET
```

---

## REST API Endpoints

### CSRF Protection
For POST requests, include:
```http
X-CSRFToken: {csrftoken_from_cookie}
Referer: https://online-go.com/
```

### Challenge a Bot

```http
POST https://online-go.com/api/v1/players/{bot_id}/challenge/
Authorization: Bearer {token}
Content-Type: application/json

{
  "game": {
    "name": "Sparring Session",
    "rules": "chinese",
    "ranked": false,
    "width": 9,
    "height": 9,
    "handicap": 0,
    "komi_auto": "automatic",
    "disable_analysis": false,
    "initial_state": null,
    "private": false,
    "time_control": "fischer",
    "time_control_parameters": {
      "system": "fischer",
      "time_increment": 30,
      "initial_time": 120,
      "max_time": 300
    }
  },
  "challenger_color": "automatic",
  "min_ranking": -1000,
  "max_ranking": 1000,
  "initialized": false
}
```

**Response:**
```json
{
  "game": 987654,
  "challenge_id": 123456
}
```

**Common Bot IDs:**
- `605979` - amybot-beginner (~25k)
- `431859` - amybot-ddk (~15k)
- `424928` - amybot-sdk (~5k)

### Get Game Details

```http
GET https://online-go.com/api/v1/games/{game_id}
Authorization: Bearer {token}
```

**Returns:** Game state including `auth` token for WebSocket game operations

### Accept Challenge

```http
POST https://online-go.com/api/v1/me/challenges/{challenge_id}/accept
Authorization: Bearer {token}
```

---

## WebSocket API (Socket.IO)

### Connection

```javascript
// Using socket.io-client
const socket = io('https://online-go.com', {
  transports: ['websocket']
});

// Or raw WebSocket
const ws = new WebSocket('wss://online-go.com/socket.io/?transport=websocket');
```

### Message Format

Socket.IO messages use the format: `42["event_name", {payload}]`

**Example:**
```
42["game/move",{"game_id":123456,"move":"dd"}]
```

### Initial Connection Sequence

**1. Authenticate with notification system:**
```javascript
42["notification/connect",{
  "player_id": "123456",
  "username": "your_username",
  "auth": "notification_auth_from_config"
}]
```

**2. Connect to chat:**
```javascript
42["chat/connect",{
  "player_id": "123456",
  "username": "your_username",
  "auth": "chat_auth_from_config"
}]
```

**3. General authentication:**
```javascript
42["authenticate",{
  "player_id": "123456",
  "username": "your_username",
  "auth": "chat_auth_from_config"
}]
```

**4. Keep-alive ping (every 20 seconds):**
```javascript
42["net/ping",{"client": Date.now()}]
```

### Game Operations

**Connect to game:**
```javascript
42["game/connect",{
  "player_id": "123456",
  "game_id": "987654",
  "chat": true
}]
```

**Server responds with:**
```javascript
42["game/987654/gamedata", {
  "game_id": 987654,
  "players": {
    "black": {...},
    "white": {...}
  },
  "width": 9,
  "height": 9,
  "moves": [[x1,y1,time1], [x2,y2,time2], ...],
  "clock": {...},
  "phase": "play"
}]
```

**Submit a move:**
```javascript
42["game/move",{
  "auth": "game_auth_token",
  "game_id": "987654",
  "player_id": "123456",
  "move": "dd"  // or [3,3]
}]
```

**Move format options:**
- Letter notation: `"ab"`, `"dd"`, `"qq"` (like SGF: a-s for 19x19)
- Array notation: `[2,3]` (zero-indexed: [column, row])
- Pass: `".."` or `[-1,-1]`

**Receive opponent move:**
```javascript
42["game/987654/move",{
  "move_number": 5,
  "move": [3,3,1234567890]  // [x, y, time_elapsed_ms]
}]
```

**Other game events:**
```javascript
// Time updates
42["game/987654/clock",{...}]

// Phase changes
42["game/987654/phase","stone removal"]
42["game/987654/phase","finished"]

// Game reset (start/end)
42["game/987654/reset",{"gamestart_beep": true}]

// Chat messages
42["game/987654/chat",{
  "username": "player",
  "message": {...}
}]

// Errors
42["game/987654/error","This is a private game"]
```

**Game control:**
```javascript
// Resign
42["game/resign",{
  "auth": "game_auth",
  "game_id": "987654",
  "player_id": "123456"
}]

// Request undo
42["game/undo/request",{
  "auth": "game_auth",
  "game_id": "987654",
  "player_id": "123456",
  "move_number": 10
}]

// Pause/resume
42["game/pause",{...}]
42["game/resume",{...}]
```

---

## Authentication Tokens by Context

Different operations require different auth tokens:

| Operation | Token Source | Token Field |
|-----------|--------------|-------------|
| Notifications | `ui/config` | `notification_auth` |
| General chat | `ui/config` | `chat_auth` |
| Game moves | `games/{id}` | `auth` |
| Game chat | `games/{id}` | `game_chat_auth` |
| Reviews | `reviews/{id}` | `auth` |
| Review chat | `reviews/{id}` | `review_chat_auth` |

Tokens are reusable throughout the game/session duration.

---

## Coordinate Systems

**Board positions:**
- Zero-indexed: `[0,0]` = top-left, `[18,18]` = bottom-right (19x19)
- Letter notation: `a-s` for each axis (SGF format)
  - `aa` = top-left
  - `ss` = bottom-right
  - `dd` = (3,3) in zero-indexed

**Move format conversion:**
```javascript
// Letter to index
function letterToIndex(letter) {
  return letter.charCodeAt(0) - 97; // 'a' = 0
}

// Index to letter
function indexToLetter(index) {
  return String.fromCharCode(97 + index); // 0 = 'a'
}
```

---

## Automatch (Quick Play)

```javascript
42["automatch/find_match",{
  "uuid": "unique-request-id",
  "size_speed_options": [
    {"size": "9x9", "speed": "live"}
  ],
  "rules": {
    "condition": "preferred",
    "value": "chinese"
  }
}]
```

---

## Error Handling & Best Practices

1. **Rate Limiting**: Limit reconnection attempts to ~1 per minute
2. **Keep-Alive**: Send `net/ping` every 20 seconds
3. **Debugging**: Use browser DevTools Network tab to inspect traffic
4. **Bot-Specific**: Different bots may accept different challenge parameters
5. **Token Expiry**: Handle 401 responses by re-authenticating
6. **Connection Loss**: Implement reconnection logic with exponential backoff

---

## Time Control Systems

**Fischer (most common for quick games):**
```json
{
  "system": "fischer",
  "time_increment": 30,     // seconds added per move
  "initial_time": 120,      // starting seconds
  "max_time": 300          // maximum accumulated time
}
```

**Absolute:**
```json
{
  "system": "absolute",
  "total_time": 600        // total seconds for all moves
}
```

**Simple:**
```json
{
  "system": "simple",
  "per_move": 30           // seconds per move
}
```

**Canadian:**
```json
{
  "system": "canadian",
  "main_time": 600,        // initial seconds
  "period_time": 30,       // seconds per period
  "stones_per_period": 5   // moves in each period
}
```

---

## Implementation Checklist

- [ ] HTTP authentication (login + config)
- [ ] WebSocket connection with Socket.IO
- [ ] Send authentication messages (notification, chat, authenticate)
- [ ] Implement keep-alive ping
- [ ] Challenge bot endpoint
- [ ] Connect to game via WebSocket
- [ ] Parse gamedata (board state, moves)
- [ ] Submit moves
- [ ] Handle opponent moves
- [ ] Update UI on move events
- [ ] Handle phase changes (play → stone removal → finished)
- [ ] Error handling & reconnection

---

## Sources

- [OGS Developer Resources](https://docs.online-go.com/)
- [Real-time API Documentation](https://ogs.readme.io/docs/real-time-api)
- [OGS API Notes (Forum)](https://forums.online-go.com/t/ogs-api-notes/17136)
- [Challenge Bot Discussion](https://forums.online-go.com/t/challenge-a-bot-using-the-api/47479)
- [Python Implementation Example](https://github.com/acbraith/go_player/blob/master/ogs_api.py)
- [Python ogs_api Library](https://github.com/flovo/ogs_api)
- [Official Web Client Source](https://github.com/online-go/online-go.com)
- [gtp2ogs Bot Tool](https://github.com/online-go/gtp2ogs)
