# -*- coding: utf-8 -*-

"""
:Author: Juti Noppornpitak

This package is used for rendering.
"""

from os import path, getcwd
import re

from jinja2         import Environment, FileSystemLoader, PackageLoader
from tori.centre    import settings as AppSettings
from tori.exception import *

from tori.template.repository import Repository

class Renderer(object):
    """
    The abstract renderer for Tori framework.

    .. warning::
        This is a non-working renderer. To use the built-in renderer (with
        Jinja2), try :class:`DefaultRenderer`. Otherwise, you should be
        expecting :class:`tori.exception.FutureFeatureException`.
    """
    def __init__(self, *args, **kwargs):
        raise FutureFeatureException("Need to implement.")

    def render(self, template_path, **contexts):
        """
        Render a template with context variables.

        :param template_path: a path to the template
        :type template_path: string or unicode
        :param contexts: a dictionary of context variables.
        :rtype: string or unicode

        Example::

            renderer = Renderer()
            renderer.render('dummy.html', appname='ikayaki', version=1.0)

        """
        raise FutureFeatureException("Need to implement.")

class DefaultRenderer(Renderer):
    """
    The default renderer with Jinja2

    :param `referers`: the template module path (e.g., com.shiroyuki.view)
                        or multiple base paths of Jinja templates based on the
                        current working directory.

    For example::

        # Instantiate with the module path.
        renderer = DefaultRenderer('app.views')

        # Instantiate with multiple base paths of Jinja templates.
        renderer = DefaultRenderer('/opt/app/ui/template', '/usr/local/tori/module/template')

    """

    def __init__(self, *referers):
        if len(referers) == 0:
            raise RendererSetupError('Require either one resource module or multiple file paths to the templates.')

        debug_mode = 'debug' in AppSettings and AppSettings['debug'] or False

        self.name     = ':'.join(referers)
        self.referers = referers
        self.loader   = self._get_package_loader() \
            if   (len(self.referers) == 1 and not path.exists(self.referers[0])) \
            else self._get_filesystem_loader()
        self.storage  = Environment(
            loader      = self.loader,
            trim_blocks = not debug_mode,
            auto_reload = debug_mode,
            extensions  = [
                'jinja2.ext.do',
                'jinja2.ext.i18n',
                'jinja2.ext.loopcontrols',
                'jinja2.ext.autoescape',
            ]
        )

    def _get_filesystem_loader(self):
        """
        Get the file-system loader for the renderer.

        :rtype: FileSystemLoader
        """
        for location in self.referers:
            if path.exists(location):
                continue

            backup_location = path.join(getcwd(), location)

            # unused logic
            #if backup_location:
            #    continue

            raise RendererSetupError('{} or {} is not found on this system.'.format(location, backup_location))

        return FileSystemLoader(self.referers)

    def _get_package_loader(self):
        """
        Get the package loader for the renderer.

        :rtype: PackageLoader
        """

        module_name_chunks       = re.split('\.', self.name)
        module_name              = '.'.join(module_name_chunks[:-1])
        template_sub_module_name = module_name_chunks[-1]

        if len(module_name_chunks) <= 1:
            raise RendererSetupError('Could not instantiate the package loader. (%s)' % '.'.join(module_name_chunks))

        return PackageLoader(module_name, template_sub_module_name)

    def render(self, template_path, **contexts):
        """
        See :meth:`Renderer.render` for more information.
        """

        template = self.storage.get_template(template_path)

        return template.render(**contexts)