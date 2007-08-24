import fuse
from fuse import Fuse
import os, stat, errno, time
import sm_json

fuse.fuse_python_api = (0, 2)

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

    def getattr(self, path):
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
        # get the octal of the mode to see if the album
        # should be public or not. Need to define a
        # whether g+r makes it public or not. u+r only
        # makes it private
        omode = oct(mode)
        sm = sm_json.Smugmug()
        sessionid = sm.loginWithPassword("jmrodri@gmail.com", "***")
        sm.createAlbum(sessionid, path, Public=0)
        sm.logout(sessionid)
        return -errno.ENOSYS

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
