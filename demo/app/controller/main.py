from tori                      import Controller
from tori.decorator.controller import renderer
from tori.exception            import *

@renderer('demo.app.views')
class MainController(Controller):
    def get(self):
        try:
            self.render('index.html', title="Testing Ground", uri=self.request.uri)
        except Exception as e:
            print(e)
