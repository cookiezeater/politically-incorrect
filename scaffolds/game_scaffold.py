#!/usr/bin/env python
import json
import requests
from requests.auth import HTTPBasicAuth
from card_scaffold import main

headers = {"Content-type": "application/json",
           "Accept": "application/json"}
cards_location = "http://localhost:5000/cards"
players_location = "http://stormy-forest-6794.herokuapp.com/players"
matches_location = "http://stormy-forest-6794.herokuapp.com/matches"
match_location = "http://stormy-forest-6794.herokuapp.com/matches/1"

players = [
    {
        "username"   : "obama",
        "email"      : "obama@whitehouse.gov",
        "password"   : "pass",
        "first_name" : "Barack",
        "last_name"  : "Obama",
        "player_type": "default"
    },
    {
        "username"   : "nietzsche",
        "email"      : "nietzsche@monsters.com",
        "password"   : "pass",
        "first_name" : "Friedrich",
        "last_name"  : "Nietzsche",
        "player_type": "default"
    },
    {
        "username"   : "kim",
        "email"      : "kim@nation.nk",
        "password"   : "pass",
        "first_name" : "Kim",
        "last_name"  : "Jong Un",
        "player_type": "default"
    },
    {
        "username"   : "hitler",
        "email"      : "adolf@thirdreich.com",
        "password"   : "pass",
        "first_name" : "Adolf",
        "last_name"  : "Hitler",
        "player_type": "default"
    },
    {
        "username"   : "dostoevsky",
        "email"      : "fyodor@russia.ru",
        "password"   : "pass",
        "first_name" : "Fyodor",
        "last_name"  : "Dostoevsky",
        "player_type": "default"
    },
    {
        "username"   : "zuckerberg",
        "email"      : "mark@facebook.com",
        "password"   : "pass",
        "first_name" : "Mark",
        "last_name"  : "Zuckerberg",
        "player_type": "default"
    }
]

for index in xrange(len(players)):
    response = requests.post(players_location,
                             data=json.dumps(players[index]),
                             headers=headers)
    assert response.status_code == 200, \
           "Stopped. Recieved status code {} when posting {}" \
           .format(response.status_code, player)

    players[i]["token"] = response["token"]

response = request.post(players_location + "/befriend",
                        data=json.dumps({"username": players[1]["username"]}),
                        headers=headers)
response = request.post(players_location + "/befriend",
                        data=json.dumps({"username": players[2]["username"]}),
                        headers=headers)

response = request.post(players_location + "/accept",
                        data=json.dumps({"username": players[0]["username"]}),
                        headers=headers)
response = request.post(players_location + "/accept",
                        data=json.dumps({"username": players[0]["username"]}),
                        headers=headers)

main(cards_location)

response = request.post(matches_location,
                        data=json.dumps({"name": "test",
                                          "max_players": 3,
                                          "max_score": 20}),
                        headers=headers)

response = request.post(matches_location + "/1/invite",
                        data=json.dumps({"username": players[1]["username"]}),
                        headers=headers)
response = request.post(matches_location + "/1/invite",
                        data=json.dumps({"username": players[2]["username"]}),
                        headers=headers)

response = request.get(matches_location + "/1/accept", headers=headers)
response = request.get(matches_location + "/1/accept", headers=headers)
