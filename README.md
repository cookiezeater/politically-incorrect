# Friends Against Humanity
A card game for Android

# Directory Structure
- /android/: contains Android app
- /views.py: view controllers and routes
- /models.py: contains ORM models

# API Architecture
## Models
- [] denotes MTM relationship
- *[] denotes OTM relationship

### Cards
|text|rank|meta|white
|----|----|----|----
|String|Integer|Object|Boolean

### Player
|username|password|email|first_name|last_name|matches|friends|wins|losses
|----|----|----|----|----|----|----|----|----
|String|Hash|String|String|String|[Match]|[Player]|Integer|Integer

### Match
|status|state|pending|table|winner
|----|----|----|----|----|----|----
|String: PENDING/ONGOING/ENDED|*[State]|[Player]|Table|Player

### Table
|deck|black
|----|----
|[Cards]|Cards

### State
|player|match|score  |hand   |played|judged |
|------|-----|-------|-------|------|-------|
|Player|Match|Integer|[Cards]|Cards |Integer|

## Routes
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
