import unittest
import bootstrap

from tori.common import Console

Console.disable_logging()

suite = unittest.TestLoader().discover(
    bootstrap.testing_base_path,
    pattern='test_*.py'
)
unittest.TextTestRunner(verbosity=1).run(suite)
