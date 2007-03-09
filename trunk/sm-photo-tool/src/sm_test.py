import unittest
import sys

import sm_photo_tool
from sm_photo_tool import *

class TestSmPhotoTool(unittest.TestCase):
    def testToBool(self):
        self.assertTrue(sm_photo_tool.to_bool("true"))
        self.assertTrue(sm_photo_tool.to_bool("yes"))
        self.assertFalse(sm_photo_tool.to_bool("false"))
        self.assertFalse(sm_photo_tool.to_bool("no"))
        self.assertFalse(sm_photo_tool.to_bool("nO"))
        try:
            self.assertFalse(sm_photo_tool.to_bool("foo"))
            self.fail("to_bool should throw an error with unknown boolean")
        except:
            self.assertEqual('text bool conversation', sys.exc_info()[0])
        
if __name__ == '__main__':
    unittest.main()