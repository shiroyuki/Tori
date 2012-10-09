import logging
import unittest

import bootstrap

from tori import common

common.default_logging_level = logging.ERROR

suite = unittest.TestLoader().discover(
    bootstrap.testing_base_path,
    pattern='test_*.py'
)
unittest.TextTestRunner(verbosity=1).run(suite)
