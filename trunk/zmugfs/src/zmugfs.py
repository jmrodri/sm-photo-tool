import fuse
from fuse import Fuse
from datetime import *
import os, stat, errno, time
import sm_json

fuse.fuse_python_api = (0, 2)

def _convert_date(dt):
    ds = dt.replace(' ', '-').replace(':', '-').split('-')
    d = map(int, ds) # convert all strings in ds to ints
    return datetime(d[0], d[1], d[2], d[3], d[4], d[5])

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_dev = 0
        self.st_mode = 0
        self.st_ino = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class ZmugFS(Fuse):
    """
    Need to implement Fuse api
    """

    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        self._config = Config()
        self._inodes= {}
        self._indexTree()

    def _inode_from_category(self, cat):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_ino = cat['id']
        st.st_nlink = 0
        st.st_atime = int(time.time()) # no time from smugmug available
        st.st_mtime = int(time.time())
        st.st_ctime = int(time.time())
        st.st_size = 0
        return st

    def _inode_from_subcat(self, subcat):
        return self._inode_from_category(subcat)


    def _inode_from_album(self, album):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_ino = album['id']
        st.st_nlink = 0
        st.st_atime = int(time.time()) # no time from smugmug available
        st.st_mtime = _convert_date(album['LastUpdated']).time()
        st.st_ctime = _convert_date(album['LastUpdated']).time()
        st.st_size = album['ImageCount']
        return st

    def _indexTree(self):
        sm = sm_json.Smugmug()
        sessionid = sm.loginWithPassword(self._config['smugmug.username'],
                                         self._config['smugmug.password'])
        tree = sm.getTree(sessionid, 1)
        for cat in tree:
            path = '/' + cat['Name']
            print "cat path: " + path
            self._inodes[path] = self._inode_from_category(cat)
            if cat.has_key('SubCategories'):
                for subcat in cat['SubCategories']:
                    path += '/' + subcat['Name']
                    print "subcat path: " + path
                    self._inodes[path] = self._inode_from_subcat(subcat)
                    if subcat.has_key('Albums'):
                        for album in subcat['Albums']:
                            path += '/' + album['Title']
                            print "album path: " + path
                            self._inodes[path] = self._inode_from_album(album)
            if cat.has_key('Albums'):
                for album in cat['Albums']:
                    path += '/' + album['Title']
                    print "album path: " + path
                    self._inodes[path] = self._inode_from_album(album)
            
        sm.logout(sessionid)

    def getattr(self, path):
        """
        we need an inode cache for the files we have.
        """
        print "getattr " + str(path)
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_ino = 2
            st.st_nlink = 1
            st.st_atime = int(time.time())
            st.st_mtime = int(time.time())
            st.st_ctime = int(time.time())
        elif path == '/foobar':
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_atime = int(time.time())
            st.st_mtime = int(time.time())
            st.st_ctime = int(time.time())
            st.st_size = len(path)
        elif self._inodes.has_key(path):
            return self._inodes[path]
        else:
            return -errno.ENOENT

        return st

    def readdir(self, path, offset):
        print "readdir (%s) (%d)" % (str(path), int(offset))
        yield fuse.Direntry(path)

    def read(self, path, size, offset):
        print "read (%s): %d:%d)" % (str(path), int(size), int(offset))
        return 'foo'

    def mkdir(self, path, mode):
        print "mkdir: (%s): (%o)" % (str(path), mode)
        print "create gallery (%s) on smugmug" % str(path)

        # split the path along the '/'.  the last one is
        # an album. The other levels are categories.
        dirs = path.split('/')
        print dirs

        # get the octal of the mode to see if the album
        # should be public or not. Need to define a
        # whether g+r makes it public or not. u+r only
        # makes it private
        omode = oct(mode)

        # add inode
        st = MyStat()
        st.st_mode = stat.S_IFDIR | mode
        st.st_ino = 2
        st.st_nlink = 1
        st.st_atime = int(time.time())
        st.st_mtime = int(time.time())
        st.st_ctime = int(time.time())
        self._inodes[path] = st

        """
        sm = sm_json.Smugmug()
        sessionid = sm.loginWithPassword(self._config['smugmug.username'],
                                         self._config['smugmug.password'])
        sm.createAlbum(sessionid, path, Public=0)
        sm.logout(sessionid)
        """
        return -errno.ENOSYS

class Config:
    def __init__(self):
        self._config = {}

        # read global config
        self._readfile('/etc/zmugfs', 'zmugfs.conf')

        # read local overrides
        homedir = os.environ.get('HOME')
        if homedir is not None:
            self._readfile(homedir, '.zmugfsrc')

    def __setitem__(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return self._config[key]

    def __str__(self):
        return str(self._config)

    def _readfile(self, path, file):
        config = os.path.join(path, file)
        if os.path.isfile(config):
            f = open(config, "r")
            while f:
                line = f.readline()
                if len(line) == 0:
                    break
                pairs = line.strip().split('=')
                self._config[pairs[0]] = pairs[1]
        else:
            print "can't find " + str(config)

def main():
    usage = """
zmugfs: smugmug filesystem
    """ + Fuse.fusage
    server = ZmugFS(version="%prog " + fuse.__version__,
                    usage=usage,
                    dash_s_do='setsingle')
    server.parse(errex=1)
    print "Hey there"
    server.main()

if __name__ == '__main__':
    main()
