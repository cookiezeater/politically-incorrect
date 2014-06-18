# Friends Against Humanity
A card game for Android

# Development Setup
Make sure postgres.app is open.
<pre><code>$ createdb fah_dev
$ export DATABASE_URL=postgresql://localhost/fah_dev
$ export APP_SETTINGS=config.DevelopmentConfig</code></pre>

Run the app:
<pre><code>$ python views.py</code></pre>

# Directory Structure
- /android/: contains Android app
- /views.py: view controllers and routes
- /models.py: contains ORM models

# API Architecture
## Models
- [] denotes MTM relationship
- *[] denotes OTM relationship
- []* denotes MTO relationship

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
|String: PENDING/ONGOING/ENDED|*[State]|[Player]|Table|[Player]*

### Table
|deck|black
|----|----
|[Cards]|Cards

### State
|player|match|score  |hand   |played|judged
|------|-----|-------|-------|------|-------
|Player|Match|Integer|[Cards]|*[Cards]|Integer

## Routes
### Cards
|url|verb|description
|---|----|-----
|/cards/new|POST|create a new card
|/cards/id|GET|retrieve card info
|/cards/id|DELETE|remove card
|/cards/|GET|retrieve a list of all cards

### Player
|url|verb|description
|---|----|-----
|/players/new|POST|create a new player
|/players/id|GET|get player info
|/players/id|PUT|update player info
|/players/id|DELETE|delete a player
|/players/id/befriend|GET|send or accept a friend request

### Match
|url|verb|description
|---|----|-----
|/match/new|POST|create a new match
|/match/id|GET|get match info
|/match/id|PUT|update match
|/match/id/join|GET|join a match after being given an invite
