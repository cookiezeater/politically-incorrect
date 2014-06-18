# Friends Against Humanity
A card game for Android

## Development Setup
Make a new virtual env. Then,
<pre><code>(venv) $ pip install -r requirements.txt</code></pre>

Make sure postgres.app is open.
<pre><code>(venv) $ createdb fah_dev
(venv) $ export DATABASE_URL=postgresql://localhost/fah_dev
(venv) $ export APP_SETTINGS=config.DevelopmentConfig</code></pre>

Make the app executable. (less typing)
<pre><code>(venv) $ chmod +x views.py</code></pre>

Run the app:
<pre><code>(venv) $ ./views.py</code></pre>

## What Works Right Now
- create a card
- get all cards as json
- get a card with its id

## Todo
- secret key for auth
- add all core features
- add oauth and social signup

## Directory Structure
- /android/: contains Android app
- /views.py: view controllers and routes
- /models.py: contains ORM models

## API Architecture
### Models
- [] denotes MTM relationship
- *[] denotes OTM relationship
- []* denotes MTO relationship

#### Cards
|text|rank|meta|white
|----|----|----|----
|String|Integer|Object|Boolean

#### Player
|username|password|email|first_name|last_name|matches|friends|wins|losses
|----|----|----|----|----|----|----|----|----
|String|Hash|String|String|String|[Match]|[Player]|Integer|Integer

#### Match
|status|state|pending|table|winner
|----|----|----|----|----|----|----
|String: PENDING/ONGOING/ENDED|*[State]|[Player]|Table|[Player]*

#### Table
|deck|black
|----|----
|[Cards]|Cards

#### State
|player|match|score  |hand   |played|judged
|------|-----|-------|-------|------|-------
|Player|Match|Integer|[Cards]|*[Cards]|Integer

### Routes
#### Cards
|url|verb|description
|---|----|-----
|/cards/new|POST|create a new card
|/cards/id|GET|retrieve card info
|/cards/id|DELETE|remove card
|/cards/|GET|retrieve a list of all cards (this is temporary)

#### Player
|url|verb|description
|---|----|-----
|/players/new|POST|create a new player
|/players/id|GET|get player info
|/players/id|PUT|update player info
|/players/id|DELETE|delete a player

#### Match
|url|verb|description
|---|----|-----
|/match/new|POST|create a new match
|/match/id|GET|get match info
|/match/id|PUT|update match
