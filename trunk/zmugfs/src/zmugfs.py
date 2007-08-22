import fuse
from fuse import Fuse
import os, stat, errno

fuse.fuse_python_api = (0, 2)

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
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
            st.st_nlink = 2
        else:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = 10

        return st

    def readdir(self, path, offset):
        print "readdir (%s) (%d)" % (str(path), int(offset))
        yield fuse.Direntry(path)

    def read(self, path, size, offset):
        print "read (%s): %d:%d)" % (str(path), int(size), int(offset))
        return 'foo'

    def mkdir(self, path, mode):
        print "mkdir: (%s): (%s)" % (str(path), str(mode))

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
