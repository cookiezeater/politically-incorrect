# Friends Against Humanity
A card game for Android

# Directory Structure
- /android: contains Android app
- /views.py: view controllers and routes
- /models.py: contains ORM models

# API Architecture
## Models
- Cards:

|Column Name|Value
|-----------|-----------
|text       |String
|rank       |Integer
|meta       |Object

- Player:

|Column Name|Value
|-----------|-----------
|username   |String
|password   |Hash
|email      |String
|first_name |String
|last_name  |String   
|matches    |[Match] Many-to-many relationship
|friends    |[Player] Many-to-many relationship
|wins       |Integer
|losses     |Integer

- Match: 

|Column Name |Value
|------------|------------
|status      |String
|pending     |[Player] Many-to-many relationship
|participants|[Player] Many-to-many relationship
|played      |[Player] This should equal "participants" when status is "JUDGE"
|table       |Table
|winner      |Player
|judge       |Player

- Table:

|Column Name |Value
|------------|------------
|deck        |[Cards]
|black       |Cards


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
