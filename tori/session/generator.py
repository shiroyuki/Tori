from time import time

from tori.decorator.common import singleton
from tori.centre import settings as AppSettings
from tori.common import Enigma

@singleton
class GuidGenerator(object):
    def generate(self):
        key = '%s/%s' % (AppSettings['cookie_secret'], time())\
            if 'cookie_secret' in AppSettings\
            else str(time())

        return Enigma.instance().hash(key)
