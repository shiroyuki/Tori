# Tori Framework

Tori is a light-weight full-stack framework based on Facebook's Tornado framework 2.x. It aims to

1. Ease the setup process.
2. Support both as regular WSGI application or Google App Engine.

<table>
	<tr><th>Version</th><th>Release Status</th><th>Note</th></tr>
	<tr>
		<td>2.0-DEV</td>
		<td>
			**Unstable**
		</td>
		<td>
			This version is for technology preview only. The documents on the framework will be fully provided upon the stable release.
		</td>
	</tr>
</table>

## Dependencies

- Python 2.7.x
- Tornado 2.x

## How to use (by example)

_Note: Tori only simplifies the process for configuration, setup and initialization._

First, check out or clone the code. Then, make sure that `tori` (from `tori`, `doc` and `demo`) is in the path that Python can reach.

Suppose we have the following file structure:

	project/
		app/
			__init__.py
			controller.py
			view.html
		tori/ # only for development
			__init__.py

where `app/controller.py` contains:

	from tornado import web
	class MainController(web.RequestHandler):
		def get(self):
			self.render(
				'views/index.html',
				title="Testing Ground",
				uri=self.request.uri
			)

Now, we write a bootstrap `server.py`:

	import tori
	from app import controller
	controller_routing = {
		r'/': MainHandler
	}
	application = tori.Application(controller_routing)
	application.listen(8000).start()

Then, we can start the WSGI server by executing:

	python server.py

Please note that the current release only supports for the server mode.
