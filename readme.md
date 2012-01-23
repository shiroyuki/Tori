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
- `setuptools` for `easy_install`
- Tornado 2.x (installed by using `sudo easy_install -U tornado`)
- Yotsuba 3.1 (installed by using `sudo easy_install -U yotsuba`)

## How to use (by example)

_Note: Tori only simplifies the process for configuration, setup and initialization._

First, check out or clone the code. Then, make sure that `tori` (from `tori`, `doc` and `demo`) is in the path that Python can reach.

Suppose we have the following file structure:

	project/
		app/
			__init__.py
			controller.py
			views/
				index.html
		server.py
		server.xml

where `app/controller.py` contains:

	from tornado import web
	
	@renderer('app.views')
	class MainController(web.RequestHandler):
		def get(self):
			self.render(
				'index.html',
				title="Testing Website",
				uri=self.request.uri
			)

Then, we write a configuration file `server.xml`:

	<?xml version="1.0" encoding="utf-8"?>
	<application>
	    <server>
	        <port>8000</port>
	    </server>
	    <routes>
	        <route type="controller" pattern="/">app.controller.main.MainController</route>
	    </routes>
	</application>

where `<port/>` is the port number and `<route/>` is dealing with controller, static content (not supported yet) and redirection (not supported yet).

Now, we write a bootstrap `server.py`:

	import os
	import sys
	
	app_path = os.path.abspath(os.path.join(os.path.dirname(
		os.path.abspath(__file__)), '..'
	))
	
	sys.path.append(app_path)
	
	from tori.application import DIApplication
	
	application = Application(server.xml)
	application.start()

Then, we can start the WSGI server by executing:

	python server.py

Now, you should be able to access http://127.0.0.1:8000.

Please note that the current release only supports for the server mode.

## Status

### Complete:

- tori.decorator.common.singleton
tori.decorator.common.singleton_with

### Scheduled for unit testing:

- tori.decorator.controller.renderer
- tori.application
- tori.controller
- tori.renderer
- tori.template

### Scheduled for field testing

- tori.decorator.controller.disable_access

### Incomplete

- tori.service