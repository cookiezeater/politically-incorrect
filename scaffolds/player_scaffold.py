#!/usr/bin/env python
import json
import requests

headers = {"Content-type": "application/json",
           "Accept": "application/json"}
location = "http://stormy-forest-6794.herokuapp.com/players"

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
    response = requests.post(location,
                             data=json.dumps(players[index]),
                             headers=headers)
    assert response.status_code == 200, \
           "Stopped. Recieved status code {} when posting {}" \
           .format(response.status_code, player)

    players[i]["token"] = response["token"]
