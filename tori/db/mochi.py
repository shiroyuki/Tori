"""
Mochi Non-relational Database Library
#####################################

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>

This library is designed to work like SQLite but be compatible with MongoDB instructions (and PyMongo interfaces).
"""

import codecs
import json

class Mochi(dict):
    def __init__(self, location=None):
        self.__location = location

        with codecs.open(self.__location, 'r', 'utf-8') as fp:
            db_map = json.load(fp)

        for id in db_map:
            self[id] = Database(db_map[id])

class Database(dict):
    def __init__(self, initial_data_map={}):
        for id in initial_data_map:
            self[id] = Collection(initial_data_map[id])

class Collection(dict):
    def insert(self, data_set={}):
        pass

    def remove(self, criteria={}):
        pass

    def update(self, criteria={}, update_instructions={}, upsert=False):
        pass
