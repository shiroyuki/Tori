from gallium.interface import IExtension


class Extension(IExtension):
    def default_settings(self):
        return None

    def config_key(self):
        return None

    def initialize(self, core, config = None):
        core.set_entity('app', 'tori.application.Application')
