from sys                       import modules as system_modules
from tori.controller           import Controller
from tori.decorator.controller import renderer

@renderer('tori.developer.profiler.views')
class MainController(Controller):
    def get(self):
        modules = system_modules.keys()
        modules.sort()
        
        self.render('modules.html', location=__file__, modules=modules)