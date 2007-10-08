import fuse
from fuse import Fuse
from datetime import *
import os, stat, errno, time
import zmugjson
from config import Config

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

class Node(object):
    def __init__(self, path, inode=MyStat(), children=None):
        self.path = path
        self.inode = inode
        if children is None:
            self.children = []
        else:
            self.children = children

    def get_nodes(self):
        return self.children

    def add_node(self, node):
        self.children.append(node)

#class TreeIndex(object):
#    def __init__(self, tree):
#        self.tree = tree
#        self.nodes_by_path = {}
#        self.child_to_parent_map = {}
#        self.depth_map = {}
#        self.node_levels = []
#        self._indexTree()
#
#    def _indexTree(self):
#        depth = 0
#        nodesAtCurrentDepth = self.tree.children()
#        self.node_levels.insert(depth, nodesAtCurrentDepth)
#
#        for n in nodesAtCurrentDepth:
#            self._indexCat(n, depth + 1)
#
#    def _indexCat(self, node, depth):
#        self.depth_map[node] = depth
#        current_depth = node.children()
#        self.node_levels.insert(depth, current_depth)
#        self.nodes_by_path[node.path] = node
#        for n in current_depth:
#            self.child_to_parent_map[n] = node
#            self._indexCat(n, depth + 1)

        
class ZmugFS(Fuse):
    """
    Need to implement Fuse api
    """

    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        self._config = Config('/etc/zmugfs/zmugfs.conf', '.zmugfsrc')
        self._nodes_by_path = {}
        self._indexTree()

    def _inode_from_image(self, image):
        st = MyStat()
        st.st_mode = stat.S_IFREG | 0744
        st.st_ino = image['id']
        st.st_nlink = 0
        st.st_atime = int(time.time()) # no time from smugmug available
        st.st_mtime = int(time.time()) # image['LastUpdated']
        st.st_ctime = int(time.time()) # image['Date']
        st.st_size = image['Size']
        return st

    def _inode_from_category(self, cat):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_ino = cat.id
        st.st_nlink = 0
        st.st_atime = int(time.time()) # no time from smugmug available
        st.st_mtime = int(time.time())
        st.st_ctime = int(time.time())
        st.st_size = len(cat.categories) + len(cat.albums)
        return st

    def _inode_from_subcat(self, subcat):
        return self._inode_from_category(subcat)


    def _inode_from_album(self, album):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_ino = album['id']
        st.st_nlink = 0
        st.st_atime = int(time.time()) # no time from smugmug available
        st.st_mtime = int(time.time()) # no time from smugmug available
        st.st_ctime = int(time.time()) # no time from smugmug available
        #st.st_mtime = _convert_date(album['LastUpdated']).time()
        #st.st_ctime = _convert_date(album['LastUpdated']).time()
        st.st_size = album['ImageCount']
        return st

    def _split_path(self, path):
        splitpath = path.strip('/').split('/')
        pathprefixes = []
        for i in reversed(range(1, len(splitpath) + 1)):
            p = "/"
            p = p.join(splitpath[:i])
            pathprefixes.append(p)
        pathprefixes.append('/')
        return pathprefixes

    def find_best_node(self, path):
        paths = self._split_path(path)
        for p in paths:
            if self._nodes_by_path.has_key(p):
                return self._nodes_by_path[p]

    def _indexTree(self):
        sm = zmugjson.Smugmug()
        sessionid = sm.loginWithPassword(self._config['smugmug.username'],
                                         self._config['smugmug.password'])
        tree = sm.getTree(sessionid, 1)

        for cat in tree.children():
            catpath = '/' + cat.name
            print "cat path: [" + catpath + "]"
            self._nodes_by_path[catpath] = self._create_node(cat, catpath)
            print "before adding children: %s" % len(self._nodes_by_path[catpath].children)
            for subcat in cat.categories:
                subpath = catpath + '/' + subcat.name
                print "subcat path: [" + subpath + "]"
                snode = self._create_node(subcat, '/' + subcat.name)
                self._nodes_by_path[subpath] = snode
                self._nodes_by_path[catpath].children.append(snode)
                print "%s: after adding child: %s" % (catpath, len(self._nodes_by_path[catpath].children))
                for album in subcat.albums:
                    apath = subpath + '/' + album['Title']
                    print "album path: [" + apath + "]"
                    anode = self._create_node(album, '/' + album['Title'])
                    self._nodes_by_path[apath] = anode
                    self._nodes_by_path[subpath].children.append(anode)
                    print "%s: after adding child: %s" % (subpath, len(self._nodes_by_path[subpath].children))
                    # get all of the image information we need to avoid making
                    # n + 1 trips
                    images = sm.getImages(sessionid, album['id'])
                    for image in images:
                        ipath = apath + '/' + image['FileName']
                        imgnode = self._create_node(image, '/' + image['FileName'])
                        self._nodes_by_path[ipath] = imgnode
                        self._nodes_by_path[apath].children.append(imgnode)
                        
            for album in cat.albums:
                apath = catpath + '/' + album['Title']
                print "album path: [" + apath + "]"
                anode = self._create_node(album, '/' + album['Title'])
                self._nodes_by_path[apath] = anode
                self._nodes_by_path[catpath].children.append(anode)
                print "%s: after adding child: %s" % (catpath, len(self._nodes_by_path[catpath].children))
                # get all of the image information we need to avoid making
                # n + 1 trips
                images = sm.getImages(sessionid, album['id'])
                for image in images:
                    ipath = apath + '/' + image['FileName']
                    imgnode = self._create_node(image, '/' + image['FileName'])
                    self._nodes_by_path[ipath] = imgnode
                    self._nodes_by_path[apath].children.append(imgnode)
            
        sm.logout(sessionid)

        print "begin nodes by path -----------------------------------"
        for k in self._nodes_by_path.keys():
            print k
        print "end nodes by path -----------------------------------"

    def _create_node(self, item, path):
        node = None

        if isinstance(item, zmugjson.Album):
            node = Node(path, self._inode_from_album(item))
        elif isinstance(item, zmugjson.Category):
            node = Node(path, self._inode_from_category(item))
        else:
            node = Node(path, self._inode_from_image(item))

        return node

    def getattr(self, path):
        """
        we need an inode cache for the files we have.
        """
        print "getattr [" + str(path) + "]"
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
        elif self._nodes_by_path.has_key(path):
            print "returnining inode for (%s)" % str(path)
            return self._nodes_by_path[path].inode
        else:
            return -errno.ENOENT

        return st

    #def opendir(self, path):
    #    # prepare a directory for reading
    #    print "opendir (%s)" % str(path)

    #def releasedir(self, path):
    #    # a process has closed the directory, and is no longer reading from it.
    #    print "releasedir (%s)" % str(path)

    #def fsyncdir(self, path, sync):
    #    # flush a directory to permanent storage
    #    pass
    
    def readdir(self, path, offset):
        # read the next directory entry
        print "readdir (%s) (%d)" % (str(path), int(offset))

        node = self._nodes_by_path[path]

        for n in node.get_nodes():
            print "would return (%s) for path (%s)" % (n.path, path)
            yield fuse.Direntry(n.path.strip('/').encode('ascii'))

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
        sm = zmugjson.Smugmug()
        sessionid = sm.loginWithPassword(self._config['smugmug.username'],
                                         self._config['smugmug.password'])
        sm.createAlbum(sessionid, path, Public=0)
        sm.logout(sessionid)
        """
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
