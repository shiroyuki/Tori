# Tori Framework

Tori is a light-weight framework based on Facebook's Tornado framework 2.x. It aims to

1. Ease the setup process.
2. Make everything driven by configuration.
3. Extendable, scalable and customizable.
4. Free to design the structure of the application in the way everyone wants.
5. Support both as regular WSGI application or Google App Engine.

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

## Concepts

Tori borrows:

1. the concept of the dependency injection and the aspect-oriented programming from Spring Framework and Java Bean
2. the concept of object alteration using annotations or decorators from Symfony 2 and Doctrine 2.

## Dependencies

First, this requires Python 2.7. It may work with the older version of Python but it isn't tested at this point.

<table>
	<tr><th>Package</th><th>Minimum version</th><th>Note</th></tr>
	<tr>
		<td>setuptools</td>
		<td>the latest version</td>
		<td>This is for `easy_install`.</td>
	</tr>
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
		<td>Yotsuba (yotsuba)</td>
		<td>3.1</td>
		<td>XML parser for `tori.application.Application`</td>
	</tr>
</table>

## How to use (by example)

This section is now moved to [the official documentation](https://github.com/shiroyuki/Tori/tree/master/docs/build/html/getting_started.html).

## Status

### Complete:

- tori.decorator.common.singleton
- tori.decorator.common.singleton_with
- tori.application
- tori.renderer
- tori.template
- tori.controller (not testible)

### Scheduled for unit testing:

- tori.decorator.controller.renderer

### Scheduled for field testing

- tori.decorator.controller.disable_access

### Incomplete

- tori.service
- tori.developer.profiler
- tori.developer.monitor