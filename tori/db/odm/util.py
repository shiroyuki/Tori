from time import time

from tori.common import Enigma

class GuidGenerator(object):
    def __init__(self):
        self.enigma = Enigma.instance()

    def generate(self):
        guid = self.enigma.hash('{}:{}'.format(
            time(),
            self.enigma.random_number() % 1024
        ))

        return guid