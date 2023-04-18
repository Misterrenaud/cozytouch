#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

from datetime import datetime


class Snapshot:
    def __init__(self, data):
        self.ts = datetime.now()
        self.data = data

    def __repr__(self):
        return f"Snapshot({self.ts})"
