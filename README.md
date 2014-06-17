# Friends Against Humanity
A card game for Android

# Directory Structure
- /android: contains Android app
- /views.py: view controllers and routes
- /models.py: contains ORM models

# API Architecture
## Models
- Cards:
<pre><code>{text: String}</code></pre>

- Player:
<pre><code>{username: String,
password: Hash,
email: String,
first_name: String,
last_name: String,
matches: [Match], (Many-to-many relationship)
friends: [Player], (Many-to-many relationship)
wins: Integer,
losses: Integer}</code></pre>

- Match:
<pre><code>{status: String, (PENDING | ONGOING | ENDED)
participants: [Player], (Many-to-many relationship)
winner: Player,
judge: Player}</code></pre>

## URLs
### Cards
- POST /cards/new
- GET /cards/id
- DELETE /cards/id

### Player
- POST /players/new
- GET /players/id
- DELETE /players/id
- GET /players/id/befriend (accept or send a friend request)

### Match
- POST /match/new
- GET /match/id
- DELETE /match/id
- GET /match/id/join (join a match after being given an invite)
