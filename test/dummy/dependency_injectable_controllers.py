from tori.controller           import Controller
from tori.decorator.controller import renderer
from tori.exception            import *

class PlainController(Controller):
    pass

@renderer('data')
class ControllerWithRenderer(Controller):
    pass

