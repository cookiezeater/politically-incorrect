#!/usr/bin/env python
"""Initiates database with some cards."""
import json
import requests


if __name__ == "__main__":
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}
    location = "http://localhost:5000/cards"

    with open("white.txt", "r") as white_cards, \
         open("black.txt", "r") as black_cards:
        for card_text in white_cards:
            requests.post(location,
                          data=json.dumps({"text": card_text.strip(),
                                           "white": True}),
                          headers=headers)
        for card_text in black_cards:
            requests.post(location,
                          data=json.dumps({"text": card_text.strip(),
                                           "white": False}),
                          headers=headers)
