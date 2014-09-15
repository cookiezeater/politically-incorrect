#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initiates database with some cards."""
import os
import sys
import json
import requests


def main(location):
    white_cards_file = os.path.join(os.path.dirname(__file__),
                       "../cards/white.txt")
    black_cards_file = os.path.join(os.path.dirname(__file__),
                       "../cards/black.txt")
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}

    with open(white_cards_file, "r") as white_cards, \
         open(black_cards_file, "r") as black_cards:
        for card_text in white_cards:
            requests.post(location,
                          data=json.dumps({"text": card_text.strip(),
                                           "white": True}),
                          headers=headers)
        for card_text in black_cards:
            answers = card_text.count("████")
            requests.post(location,
                          data=json.dumps({"text": card_text.strip(),
                                           "white": False,
                                           "answers": answers
                                                      if answers
                                                      else 1}),
                          headers=headers)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        main("http://stormy-forest-6794.herokuapp.com/cards")
    else:
        main(sys.argv[1])
