#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

from datetime import datetime
from typing import Optional


class Snapshot:
    def __init__(self, data, ts: Optional[datetime] = None):
        self.data = data
        self.ts = datetime.now() if ts is None else ts

    def __repr__(self):
        return f"Snapshot({self.ts})"

    def get_temps(self):
        places = {}
        for place in self.data["setup"]["rootPlace"]["subPlaces"]:
            places[place["oid"]] = place["label"]
        temps = {}
        for device in self.data["setup"]["devices"]:
            if device["uiClass"] == "TemperatureSensor":
                for state in device["states"]:
                    if state["name"] == "core:TemperatureState":
                        temps[places.get(device["placeOID"])] = state["value"]
                        break
        return temps
