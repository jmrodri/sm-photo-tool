import unittest
import os
from config import Config

class TestConfig(unittest.TestCase):

    def _writeouttestconf(self):
        f = open('test.conf', 'w')
        f.writelines(['some.namespace=10\n', 'another.namespace=sm_json\n'])
        f.flush()
        f.close()

    def setUp(self):
        self._writeouttestconf()
        self.config = Config('test.conf', None)

    def testgetproperty(self):
        i = self.config.get_property('some.namespace')
        self.assertEquals('10', i)

    def testgetint(self):
        i = self.config.get_int('some.namespace')
        self.assertEquals(10, i)

    def testsetproperty(self):
        self.config.set_property('foo', 'bar')
        result = self.config.get_property('foo')
        self.assertEquals('bar', result)

    def tearDown(self):
        os.remove('test.conf')

if __name__ == '__main__':
    unittest.main()
