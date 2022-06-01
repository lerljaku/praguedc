import os
import sys
import argparse
import logging
import fitz
import re

logger = logging.Logger("")
logger.setLevel('INFO')

class Score:
    def __init__(self, order: str, name: str, points: str):
        self.order = int(order)
        self.name = name.strip()
        self.points = int(points)

def export_bodu(file_path: str):
    logger.info(f'body {file_path}')
    with fitz.open(file_path) as f:
        text = ''
        for page in f:
            text += page.get_text()
    
    scores: list[Score] = []
    scrore_points = False
    p = re.compile(r'^(?P<order>\d+)[  \s]+(?P<name>.*)[  \s]+(?P<points>\d+)[  \s]+(?P<ow>\d+)[  \s]+(?P<gw>\d+)[  \s]+(?P<ogw>\d+)[  \s]*$')
    for line in text.split('\n'):
        matches = p.search(line) 
        if matches:
            order = matches.group('order')
            name = matches.group('name')
            points = matches.group('points')
            score = Score(order, name, points)
            scores.append(score)
            print(f"{score.name};{score.points}")

if __name__ == '__main__':
    args = sys.argv[1:]
    file_path = args[0]
    export_bodu(file_path=file_path)

