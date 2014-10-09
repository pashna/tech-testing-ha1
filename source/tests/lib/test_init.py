__author__ = 'Admin'

#!/usr/bin/python

import unittest
import mock
from source import lib


class InitTestCase(unittest.TestCase):
    def test_start(self):
        assert 1==1