import tori
from tornado import web

class MainHandler(web.RequestHandler):
	def get(self):
		self.render('views/index.html', title="Testing Ground", uri=self.request.uri)

application = tori.Application(
	{r'/': MainHandler}
)
application.listen().start()
