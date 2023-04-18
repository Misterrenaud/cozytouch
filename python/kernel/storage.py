#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

import os
import shelve
from typing import Any


class Storage:
    def __init__(self):
        self.path = os.path.join(os.getcwd(), "..", "data")

    def get(self, name: str, default=None) -> Any:
        with shelve.open(self.path) as s:
            return s.get(name, default)

    def set(self, name: str, value: Any):
        with shelve.open(self.path) as s:
            s[name] = value
