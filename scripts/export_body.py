import os
import sys
import argparse
import logging
import fitz
import requests
import csv
import re
import tempfile

logger = logging.Logger("")
logger.setLevel('INFO')

csv_url = 'https://docs.google.com/spreadsheets/d/1IjrWe_b-Wk5n9hD2CJl5yiS_BoN9wU203jpGx4qfP6Q/export?format=csv'
headers_count = 2


class Player:
    def __init__(self, name: str):
        self.name = name


class Score:
    def __init__(self, order: str, name: str, points: str):
        self.order = int(order)
        self.name = name.strip()
        self.points = int(points)


def export_bodu(file_path: str):
    logger.info(f'pulling data from {csv_url}')
    sheet_csv_data =  requests.get(csv_url).content.decode('utf-8')
    tmp = tempfile.NamedTemporaryFile()
    players: list[Player] = []
    with open(tmp.name, 'w') as f:
        f.write(sheet_csv_data)
    with open(tmp.name, 'r') as f:
        readCSV = csv.reader(f, delimiter=',', quotechar='"')
        for row in list(readCSV)[headers_count:]:
            player_name = row[14].strip()
            if player_name:
                players.append(Player(name=player_name))

            
    logger.info(f'parsing data from {file_path}')
    with fitz.open(file_path) as f:
        text = ''
        for page in f:
            text += page.get_text()

    scores: dict[str, Score] = {}
    p = re.compile(r'^(?P<order>\d+)[  \s]+(?P<name>.*)[  \s]+(?P<points>\d+)[  \s]+(?P<ow>\d+)[  \s]+(?P<gw>\d+)[  \s]+(?P<ogw>\d+)[  \s]*$')
    for line in text.split('\n'):
        matches = p.search(line) 
        if matches:
            order = matches.group('order')
            name = matches.group('name').strip()
            points = matches.group('points')
            score = Score(order, name, points)
            scores[name] = score
    
    missing_players = []
    source_players = list(map(lambda p: p.name, players))
    for player_name in scores:
        if player_name not in source_players:
            missing_players.append(player_name)

    if missing_players:
         print('--- players missing in source sheet ---')
         for player_name in missing_players:
             print(player_name)
    else:
        logger.info(f'paste this to source sheet score column:')
        for player in players:
            if player.name in scores:
                score = scores[player.name]
                print(f"{score.name};{score.points}")
                scores.pop(player.name)
            else:
                print(f" ")


if __name__ == '__main__':
    args = sys.argv[1:]
    file_path = args[0]
    export_bodu(file_path=file_path)

