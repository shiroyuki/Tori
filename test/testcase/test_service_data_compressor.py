#-*- coding: utf-8 -*-

import unittest

from tori.exception               import *
from tori.service.data.base       import ResourceEntity
from tori.service.data.compressor import CSSCompressor

class TestDefaultRenderer(unittest.TestCase):
    ''' Test the CSS compressor '''
    def setUp(self):    pass
    def tearDown(self): pass

    def test_css_compressor(self):
        entity     = ResourceEntity('data/test.css')
        compressor = CSSCompressor()

        original_content = entity.content()
        updated_content  = compressor.execute(entity).content()

        original_size = len(original_content)
        updated_size  = len(updated_content)

        #print updated_content
        #print '%.3f%% reduced' % ((original_size - updated_size) * 100.0 / original_size)
        #print '%.3f KB reduced' % ((original_size - updated_size) / 1024.0)

        self.assertTrue(original_size > updated_size, 'The data should be smaller.')