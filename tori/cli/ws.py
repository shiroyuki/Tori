from gallium.interface import ICommand, alias


@alias('run')
class WebServiceStartCommand(ICommand):
    """ Start the web service process """
    def identifier(self):
        return 'tori.ws.start'

    def define(self, parser):
        parser.add_argument(
            '--debug',
            '-d',
            help     = 'The debug mode flag',
            action   = 'store_true',
            required = False,
        )
        parser.add_argument(
            '--bind-address',
            '-b',
            help     = 'The binding IP address',
            required = False,
            default  = '0.0.0.0',
        )
        parser.add_argument(
            '--port',
            '-p',
            help     = 'The listening port',
            type     = int,
            required = False,
            default  = 8000,
        )

    def execute(self, args):
        print(args)
