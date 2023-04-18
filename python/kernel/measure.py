#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

from datetime import datetime

from kernel.cozytouch import Cozytouch


class Measure:
    def __init__(self, conf):
        self.ts = datetime.now()
        self.state = Cozytouch(conf).get_state()

    def __str__(self):
        return f"Measure from {self.ts.strftime('%y/%m/%d-%H:%M')}"
