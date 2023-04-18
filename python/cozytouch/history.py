#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

import json
import os
from datetime import datetime
from typing import List

from cozytouch.snapshot import Snapshot
from meta import SingletonMeta


class History(metaclass=SingletonMeta):
    def __init__(self):
        self.root_path = os.path.join(os.getcwd(), "..", "history")
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)

    def _get_snapshot_dir(self, snapshot) -> str:
        return os.path.join(self.root_path, str(snapshot.ts.year), str(snapshot.ts.month), str(snapshot.ts.day))

    def get_last_snapshot(self) -> Snapshot:
        year = max(os.listdir(self.root_path))
        month = max(os.listdir(os.path.join(self.root_path, year)))
        day = max(os.listdir(os.path.join(self.root_path, year, month)))
        snapshot_file_name = max(os.listdir(os.path.join(self.root_path, year, month, day)))
        return History.snapshot_from_path(os.path.join(self.root_path, year, month, day, snapshot_file_name))

    @staticmethod
    def snapshot_from_path(path) -> Snapshot:
        with open(path, "r") as fp:
            snapshot_data = json.load(fp)
        breadcrumbs = path.split(os.path.sep)
        ts = datetime(
            int(breadcrumbs[-4]),
            int(breadcrumbs[-3]),
            int(breadcrumbs[-2]),
            int(breadcrumbs[-1][:2]),
            int(breadcrumbs[-1][2:4])
        )
        return Snapshot(snapshot_data, ts)


    def add_snapshot(self, snapshot: Snapshot):
        path = self._get_snapshot_dir(snapshot)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, f"{snapshot.ts.strftime('%H%M%S')}.json"), "w") as fp:
            json.dump(snapshot.data, fp)

    def get_today_s_snapshots(self) -> List[Snapshot]:
        year = max(os.listdir(self.root_path))
        month = max(os.listdir(os.path.join(self.root_path, year)))
        day = max(os.listdir(os.path.join(self.root_path, year, month)))
        snapshots = []
        for snapshot_file_name in sorted(os.listdir(os.path.join(self.root_path, year, month, day))):
            snapshots.append(History.snapshot_from_path(os.path.join(self.root_path, year, month, day, snapshot_file_name)))
        return snapshots
