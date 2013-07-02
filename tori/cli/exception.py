class InterfaceException(Exception):
    """ Interface Exception. Require implementation """

class TerminationSignal(RuntimeError):
    """ Termination Signal """

class CommandNotFound(RuntimeError):
    """ Command Not Found """

class NotConfigured(Exception):
    """ Not-configured exception """