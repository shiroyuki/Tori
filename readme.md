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

First, this requires Python 2.7. It may work with the older version of Python but it isn't tested at this point.

<table>
	<tr><th>Package</th><th>Minimum version</th><th>Note</th></tr>
	<tr>
		<td>jinja2</td>
		<td>the latest version</td>
		<td>The default template system.</td>
	</tr>
	<tr>
		<td>Tornado Framework (tornado)</td>
		<td>2.1</td>
		<td>The base framework</td>
	</tr>
    <tr>
		<td>Kotoba (kotoba)</td>
		<td>3.0-DEV</td>
		<td>XML parser for `tori.application.Application`. Currently available from https://github.com/shiroyuki/Kotoba.</td>
	</tr>
    <tr>
		<td>Imagination (imagination)</td>
		<td>1.0-DEV</td>
		<td>Component Controller. Currently available from https://github.com/shiroyuki/Imagination.</td>
	</tr>
    <tr>
		<td>SQLAlchemy (sqlalchemy)</td>
		<td>0.7.8+</td>
		<td>For session management.</td>
	</tr>
</table>

## Status

### Complete:

- tori.decorator.common.singleton
- tori.decorator.common.singleton_with
- tori.application
- tori.renderer
- tori.template
- tori.controller (not testible)

### Scheduled for field testing

- tori.decorator.controller.disable_access

### Incomplete

- tori.developer.profiler
- tori.developer.monitor