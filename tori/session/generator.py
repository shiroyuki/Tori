from time import time

from tori.centre import settings as AppSettings
from tori.common import Enigma

class GuidGenerator(object):
    def generate(self):
        return Enigma.instance().hash(
            '%s/%s' % (AppSettings['cookie_secret'], time())
        )
