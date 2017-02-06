from gallium.interface import ICommand, alias


@alias('tori.ws')
class WebServiceStartCommand(ICommand):
    def identifier(self):
        return 'tori.webservice'

    def define(self, parser):
        pass

    def execute(self, args):
        pass
