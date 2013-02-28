import parser
from unittest import TestCase

class TestSandbox(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sandbox(self):
        code = """print('Compiled Scope:', __name__)

class Association(object):
    def __init__(self, name):
        self.name = name"""

        code = code.strip()
        bytecode = compile(code, '<string>', 'exec')

        exec(bytecode, globals())

        print('Globals:', globals().keys())
        print('Locals:', locals().keys())
        print('Dir:', dir(self))

        a = globals()['Association']('abc')

        self.assertEqual('abc', a.name)