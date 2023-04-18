#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

import os
from time import sleep

from conf import Conf
from cozytouch.api import Api
from cozytouch.history import History

if __name__ == "__main__":
    Conf().setup(os.path.join(os.getcwd(), "..", "conf", "rlx.yml"))

    api = Api()
    while True:
        snap = api.get_snapshot()
        print(snap)
        History().add_snapshot(snap)
        sleep(60)
