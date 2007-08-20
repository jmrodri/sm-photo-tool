import fuse
from fuse import Fuse

fuse.fuse_python_api = (0, 2)

class ZmugFS(Fuse):
    """
    Need to implement Fuse api
    """
    pass

def main():
    zfs = ZmugFS()
    print "Hey there"

if __name__ == '__main__':
    main()
