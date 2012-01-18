from tori.application import Application
from tornado import web

class MainHandler(web.RequestHandler):
    def get(self):
        self.render('views/index.html', title="Testing Ground", uri=self.request.uri)

application = Application(
    {r'/': MainHandler}
)
application.listen().start()
