# -*- coding: utf-8 -*-

'''
:Author: Juti Noppornpitaks

This package is used for rendering.
'''

from os import path
import re

from jinja2         import Environment, FileSystemLoader, PackageLoader
from tori.centre    import settings as AppSettings
from tori.exception import *

from tori.bundle.template.repository import Repository

class Renderer(object):
    '''
    The abstract renderer for Tori framework.

    .. warning::
        This is not a working renderer. To use the built-in renderer (using Jinja2), try :class:`DefaultRenderer`.
        Otherwise, you should be expecting :class:`tori.exception.FutureFeatureException`.
    '''
    def __init__(self, *args, **kwargs):
        raise FutureFeatureException, "Need to implement."

    def render(self, template_path, **contexts):
        '''
        Render a template with context variables.

        *contexts* is a dictionary of context variables.

        Example::

            renderer = Renderer()
            renderer.render('dummy.html', appname='ikayaki', version=1.0)

        '''
        raise FutureFeatureException, "Need to implement."

class DefaultRenderer(Renderer):
    '''
    The default renderer with Jinja2

    `referers` is either the template module path or multiple base paths of Jinja templates (based on the current
    working directory).

    For example::

        # Instantiate with the module path.
        renderer = DefaultRenderer('app.views')
        # Instantiate with multiple base paths of Jinja templates.
        renderer = DefaultRenderer('/opt/app/ui/template', '/usr/local/tori/module/template')

    '''

    def __init__(self, *referers):
        if len(referers) == 0:
            raise RendererSetupError, 'Require either one resource module or multiple file paths to the templates.'

        debug_mode = 'debug' in AppSettings and AppSettings['debug'] or False

        self.name     = ':'.join(referers)
        self.referers = referers
        self.loader   = (len(self.referers) == 1 and not path.exists(self.referers[0])) \
            and self._get_package_loader() \
            or  self._get_filesystem_loader()
        self.storage  = Environment(
            loader      = self.loader,
            trim_blocks = not debug_mode,
            auto_reload = debug_mode
        )

    def _get_filesystem_loader(self):
        '''
        Get the file-system loader for the renderer.

        .. warning::
            This is for internal use and only accessible for overriding purposes.
        '''
        for location in self.referers:
            if not path.exists(location):
                raise RendererSetupError, '%s is not found on this system.' % location

        return FileSystemLoader(self.referers)

    def _get_package_loader(self):
        '''
        Get the package loader for the renderer.

        .. warning::
            This is for internal use and only accessible for overriding purposes.
        '''

        module_name_chunks       = re.split('\.', self.name)
        module_name              = '.'.join(module_name_chunks[:-1])
        template_sub_module_name = module_name_chunks[-1]

        if len(module_name_chunks) <= 1:
            raise RendererSetupError, 'Could not instantiate the package loader. (%s)' % module_name_chunks

        return PackageLoader(module_name, template_sub_module_name)

    def render(self, template_path, **contexts):
        ''' See :meth:`Renderer.render` for more information. '''
        template = self.storage.get_template(template_path)

        return template.render(**contexts)