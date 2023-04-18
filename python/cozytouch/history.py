#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

from cozytouch.snapshot import Snapshot
from meta import SingletonMeta


class History(metaclass=SingletonMeta):
    def get_last_snapshot(self) -> Snapshot:
        return Snapshot()

    def add_snapshot(self, snapshot: Snapshot):
        pass
