#-*- coding: utf-8 -*-

import unittest

from jinja2 import FileSystemLoader, PackageLoader

from tori.template.renderer  import DefaultRenderer
from tori.exception import *

class TestDefaultRenderer(unittest.TestCase):
    ''' Test default renderer '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_intercept_error_without_referers(self):
        try:
            r = DefaultRenderer()
            self.assertTrue(False, 'No referer should cause exception thrown.')
        except RendererSetupError:
            pass

    def test_intercept_error_with_invalid_referer(self):
        try:
            r = DefaultRenderer('shiroyuki')
            self.assertTrue(False, 'No referer should cause exception thrown.')
        except RendererSetupError:
            pass

        try:
            r = DefaultRenderer('data', '../demo/app/google')
            self.assertTrue(False, 'No referer should cause exception thrown.')
        except RendererSetupError:
            pass

    def test_filesystem_loader_single(self):
        r = DefaultRenderer('data')
        self.assertIsInstance(r.loader, FileSystemLoader);

        r = DefaultRenderer('../demo/app/views')
        self.assertIsInstance(r.loader, FileSystemLoader);

    def test_filesystem_loader_multiple(self):
        r = DefaultRenderer('data', '../demo/app/views')
        self.assertIsInstance(r.loader, FileSystemLoader);

    def test_package_loader(self):
        r = DefaultRenderer('demo.app.views')
        self.assertIsInstance(r.loader, PackageLoader);

    def test_basic_template(self):
        r = DefaultRenderer('data')
        self.assertEqual(r.render('basic_template.html'), u'Hello, world.');

    def test_unicode_template(self):
        r = DefaultRenderer('data')
        self.assertEqual(r.render('unicode_template.html'), u'こんにちは、みんな。');

    def test_dynamic_template(self):
        r = DefaultRenderer('data')
        self.assertEqual(r.render('dynamic_template.html', name='Juti'), u'Hello, Juti.');
