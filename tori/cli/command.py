from tori.cli.exception import InterfaceException

class Command(object):
    """ Abstract class for all Tori-based commands """
    def define_arguments(self, argument_parser):
        """ Define the arguments """
        raise InterfaceException('Arguments are not defined.')

    def execute(self, args):
        """ Execute the command """
        raise InterfaceException('The interface does not know how to execute the command.')