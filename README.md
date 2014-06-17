# Friends Against Humanity
A card game for Android

# Directory Structure
- /android: contains Android app
- /views.py: view controllers and routes
- /models.py: contains ORM models

# API Architecture
## Models
- Cards:

|text|rank|meta
|----|----|----
|String|Integer|Object

- Player:

|username|password|email|first_name|last_name|matches|friends|wins|losses
|----|----|----|----|----|----|----|----|----
|String|Hash|String|String|String|[Match]|[Player]|Integer|Integer

- Match: 

|status|state|pending|participants|played|table|winner|judge
|----|----|----|----|----|----|----|----
|String: PENDING/JUDGE/OTHERS/ENDED|State|[Player]|[Player]|[Player]: Empty when status is JUDGE|Table|Player|Player


- Table:

|deck|black
|----|----
|[Cards]|Cards

- State:

|player|match|score
|----|----|----
|Player|Match|Integer


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
