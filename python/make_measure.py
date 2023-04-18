#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

import os

import yaml

from kernel.measure import Measure

if __name__ == "__main__":
    with open(os.path.join(os.getcwd(), "..", "conf", "rlx.yml")) as fp:
        conf = yaml.safe_load(fp)

    m = Measure(conf)
    print(m)
    print(m.state)
