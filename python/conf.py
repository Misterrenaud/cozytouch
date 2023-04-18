#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

from collections import UserDict

import yaml

from meta import SingletonMeta


class Conf(metaclass=SingletonMeta):
    def __init__(self):
        self.data = {}

    def setup(self, path):
        with open(path) as fp:
            self.data = yaml.safe_load(fp)

    def get_conf(self):
        return self.data
