from tornado import web

class Controller(web.RequestHandler):
	def get(self):
		self.render('views/index.html', title="Testing Ground", uri=self.request.uri)
