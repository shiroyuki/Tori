# Tori Framework

See [the official documentation](http://readthedocs.org/docs/tori-framework/) for more information.

<table>
	<tr><th>Version</th><th>Release Status</th><th>Note</th></tr>
	<tr>
		<td>2.0-DEV</td>
		<td>
			**Unstable**
		</td>
		<td>
            This is for technology preview only. The installation script and documents
            on the framework will be fully provided upon the stable release.
		</td>
	</tr>
</table>

## Dependencies

First, this requires **Python 2.7**. It may work with the older version of Python but it isn't tested at this point.
It may work in **Python 3.3** but some required libraries don't support that version at the moment.

<table>
	<tr><th>Package</th><th>Minimum version</th><th>Note</th></tr>
	<tr>
		<td>jinja2</td>
		<td>2.6+</td>
		<td>
			The default template system. (Incompatible with Python 3.3)
		</td>
	</tr>
	<tr>
		<td>Tornado Framework (tornado)</td>
		<td>2.4+</td>
		<td>The base framework</td>
	</tr>
	<tr>
		<td>Kotoba (kotoba)</td>
		<td>3.0</td>
		<td>XML parser for `tori.application.Application`. Currently available from https://github.com/shiroyuki/Kotoba.</td>
	</tr>
	<tr>
		<td>Imagination (imagination)</td>
		<td>1.5+</td>
		<td>Component Controller. The current prerequisite is only available from https://github.com/shiroyuki/Imagination.</td>
	</tr>
	<tr>
		<td>SQLAlchemy (sqlalchemy)</td>
		<td>0.7.x</td>
		<td>Used by any relational database components if required. (optional)</td>
	</tr>
	<tr>
		<td>PyMongo (pymongo)</td>
		<td>2.3.x</td>
		<td>Used by MongoDB database components if required. (optional)</td>
	</tr>
	<tr>
		<td>Redis (redis-py)</td>
		<td>2.7.x</td>
		<td>Used by relational database components if required. (optional)</td>
	</tr>
</table>
