import unittest
import zmugjson
import sys
from config import Config

class TestTree(unittest.TestCase):
    def testTree(self):
        tree = zmugjson.Tree()
        self.assertEquals(0, len(tree.children()))

class TestCategory(unittest.TestCase):
    def testCategory(self):
        cat = zmugjson.Category(10, "foo")
        self.assertEquals(10, cat.id)
        self.assertEquals("foo", cat.name)
        self.assertEquals(0, len(cat.albums))
        self.assertEquals(0, len(cat.categories))
        self.assertEquals(cat.children(), cat.categories + cat.albums)

#class TestAlbum(unittest.TestCase):
#    def testAlbum(self):
#        album = zmugjson.Album("foo")
#        self.assertEquals("foo", album.name)
#        self.assertEquals(None, album.children())

class TestSmugmug(unittest.TestCase):

    def setUp(self):
        self.sm = zmugjson.Smugmug()
        self.config = Config('/etc/zmugjson/zmugjson.conf', '.zmugjsonrc')

    def testLoginWithPasswordInvalid(self):
        try:
            self.sm.loginWithPassword("foo", "baz")
        except zmugjson.Exception, e:
            self.assertEquals(1, e.code)
            self.assertEquals("invalid login", e.message)
            

    def testLoginWithPassword(self):
        sessionid = self.sm.loginWithPassword(
                                  self.config.get_property('smugmug.username'),
                                  self.config.get_property('smugmug.password'))

        self.assert_(sessionid != None)

    def testLoginAnonymously(self):
        sessionid = self.sm.loginAnonymously()
        print sessionid
        self.assert_(sessionid != None)

    def testLogoutInvalidSession(self):
        # invalid session
        try:
            self.sm.logout("fefifofum")
        except zmugjson.Exception, e:
            self.assertEquals(18, e.code)
            self.assertEquals("invalid API key", e.message)

    def testLogout(self):
        # assume login works
        sessionid = self._login()
        self.sm.logout(sessionid)

    def testGetImageInfo(self):
        pass

    def _login(self):
        return self.sm.loginWithPassword(self.config.get_property('smugmug.username'),
                                         self.config.get_property('smugmug.password'))

    def _logout(self, sessionid):
            self.sm.logout(sessionid)


if __name__ == '__main__':
    unittest.main()
