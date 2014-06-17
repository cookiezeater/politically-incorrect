# Friends Against Humanity
A card game for Android

# Directory Structure
- /android: contains Android app
- /views.py: view controllers and routes
- /models.py: contains ORM models

# API Architecture
## Models
- Cards:
<pre><code>{text: String,
rank: Integer,
meta: Object}</code></pre>

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

- Match: (column "played" should equal "participants" when status is "JUDGE")
<pre><code>{status: String, (PENDING | JUDGE | OTHERS | ENDED)
pending: [Player], (Many-to-many relationship)
participants: [Player], (Many-to-many relationship)
played: [Player], (Many-to-many relationship)
table: Table, (One-to-one relationship)
winner: Player,
judge: Player}</code></pre>

- Table:
<pre><code>
{deck: [Cards], (Many-to-many relationship)
black: Cards}


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
