from tori.controller           import Controller
from tori.decorator.controller import renderer
from tori.exception            import *

@renderer('app.views')
class MainController(Controller):
    def get(self):
        self.render('index.html', title="Testing Ground", uri=self.request.uri)
