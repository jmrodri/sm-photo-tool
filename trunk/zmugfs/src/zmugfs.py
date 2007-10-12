import fuse
from fuse import Fuse
from datetime import *
import os, stat, errno, time
import zmugjson
from config import Config
import logging
import logging.config
import httplib

fuse.fuse_python_api = (0, 2)

# smugmug api key which identifies this application
apikey = "xbBmfRgR1whEAOv9QRh687GGP6Ow0IM6"

# configure the logging system for the module
logging.config.fileConfig("logger.conf")
log = logging.getLogger("zmugfs")

def _convert_date(datestr):
    # smugmug returns date in the following format: "%Y-%m-%d %H:%M:%S"
    return int(time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S")))

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_dev = 0
        self.st_mode = 0
        self.st_ino = 0
        self.st_nlink = 0
        # default user and groupid to the user running the program
        self.st_uid = os.getuid()
        self.st_gid = os.getgid()
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class Node(object):
    def __init__(self, path, id, inode=MyStat(), children=None):
        self.id = id
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

class ZmugFS(Fuse):
    """
    Need to implement Fuse api
    """

    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        self._config = Config('/etc/zmugfs/zmugfs.conf', '.zmugfsrc')
        self._nodes_by_path = {}
        self._indexTree()
        self._imgdata_by_path = {}

    #
    # should probably find a cleaner way to group the
    # _inode_from_xxx methods
    #
    def _inode_from_root(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_ino = 0
        st.st_nlink = 0
        st.st_atime = int(time.time())
        st.st_mtime = int(time.time())
        st.st_ctime = int(time.time())
        st.st_size = 0
        return st

    def _inode_from_image(self, image):
        st = MyStat()
        st.st_mode = stat.S_IFREG | 0644
        st.st_ino = image['id']
        st.st_nlink = 0
        # no atime from smugmug available, use last updated
        st.st_atime = _convert_date(image['LastUpdated'])
        st.st_mtime = _convert_date(image['LastUpdated'])
        st.st_ctime = _convert_date(image['Date'])
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
        # no atime from smugmug available, use last updated
        st.st_atime = _convert_date(album['LastUpdated'])
        st.st_mtime = _convert_date(album['LastUpdated'])
        st.st_ctime = _convert_date(album['LastUpdated'])
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
        sm = zmugjson.Smugmug(apikey)
        sessionid = sm.loginWithPassword(self._config['smugmug.username'],
                                         self._config['smugmug.password'])
        tree = sm.getTree(sessionid, 1)

        # handle the root node case

        self._nodes_by_path['/'] = Node('/', 0, self._inode_from_root())

        for cat in tree.children():
            catpath = '/' + cat.name
            log.debug("cat path: [" + catpath + "]")
            catnode = self._create_node(cat, catpath)
            self._nodes_by_path[catpath] = catnode
            self._nodes_by_path['/'].children.append(catnode)
            log.debug("before adding children: %s" % len(self._nodes_by_path[catpath].children))
            for subcat in cat.categories:
                subpath = catpath + '/' + subcat.name
                log.debug("subcat path: [" + subpath + "]")
                snode = self._create_node(subcat, '/' + subcat.name)
                self._nodes_by_path[subpath] = snode
                self._nodes_by_path[catpath].children.append(snode)
                log.debug("%s: after adding child: %s" % (catpath, len(self._nodes_by_path[catpath].children)))
                for album in subcat.albums:
                    apath = subpath + '/' + album['Title']
                    log.debug("album path: [" + apath + "]")
                    anode = self._create_node(album, '/' + album['Title'])
                    self._nodes_by_path[apath] = anode
                    self._nodes_by_path[subpath].children.append(anode)
                    log.debug("%s: after adding child: %s" % (subpath, len(self._nodes_by_path[subpath].children)))
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
                log.debug("album path: [" + apath + "]")
                anode = self._create_node(album, '/' + album['Title'])
                self._nodes_by_path[apath] = anode
                self._nodes_by_path[catpath].children.append(anode)
                log.debug("%s: after adding child: %s" % (catpath, len(self._nodes_by_path[catpath].children)))
                # get all of the image information we need to avoid making
                # n + 1 trips
                images = sm.getImages(sessionid, album['id'])
                for image in images:
                    ipath = apath + '/' + image['FileName']
                    imgnode = self._create_node(image, '/' + image['FileName'])
                    self._nodes_by_path[ipath] = imgnode
                    self._nodes_by_path[apath].children.append(imgnode)
            
        sm.logout(sessionid)

        # DEBUG CODE
        log.debug("begin nodes by path -----------------------------------")
        for k in self._nodes_by_path.keys():
            log.debug(k)
        log.debug("end nodes by path -----------------------------------")

    def _create_node(self, item, path):
        node = None

        if isinstance(item, zmugjson.Album):
            node = Node(path, item['id'], self._inode_from_album(item))
        elif isinstance(item, zmugjson.Category):
            node = Node(path, item.id, self._inode_from_category(item))
        else:
            node = Node(path, item['id'], self._inode_from_image(item))

        return node

    def getattr(self, path):
        """
        we need an inode cache for the files we have.
        """
        log.debug("getattr [" + str(path) + "]")
        if self._nodes_by_path.has_key(path):
            log.debug("returning inode for (%s)" % str(path))
            return self._nodes_by_path[path].inode
        else:
            return -errno.ENOENT

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
        log.debug("readdir (%s) (%d)" % (str(path), int(offset)))

        node = self._nodes_by_path[path]

        for n in node.get_nodes():
            log.debug("would return (%s) for path (%s)" % (n.path, path))
            yield fuse.Direntry(n.path.strip('/').encode('ascii'))

    def open(self, path, flags):
        log.debug("open (%s): flags = %s" % (str(path), str(flags)))
        node = self._nodes_by_path[path]

        # um what the heck are you looking for?
        if node == None:
            return -errno.ENOENT

        # see if we already got it
        if not self._imgdata_by_path.has_key(path):
            sm = zmugjson.Smugmug(apikey)
            sessionid = sm.loginWithPassword(self._config['smugmug.username'],
                                             self._config['smugmug.password'])
            urls = sm.getImageUrls(sessionid, node.id);
            sm.logout(sessionid)

            parts = urls['OriginalURL'].split('/')
            conn = httplib.HTTPConnection(parts[2])
            conn.request("GET",  '/' + '/'.join(parts[3:]))
            resp = conn.getresponse()
            imgdata = resp.read()
            conn.close()

            self._imgdata_by_path[path] = imgdata

    def read(self, path, size, offset):
        log.debug("read (%s): %d:%d)" % (str(path), int(size), int(offset)))
        imgdata = self._imgdata_by_path[path]
        imglen = len(imgdata)
        if offset < imglen:
            if offset + size > imglen:
                size = imglen - offset
            buf = imgdata[offset:offset+size]
        else:
            buf = ''
        return buf

    #def flush(self, path, flags):
    #    log.debug("flush (%s): flags = %s" % (str(path), str(flags)))
    #    # we're done with the file for now. Figure out a better way
    #    # to cache images in the future.
    #    if self._imgdata_by_path(path):
    #        self._imgdata_by_path[path] = None

    def release(self, path, flags):
        log.debug("release (%s): flags = %s" % (str(path), str(flags)))
        # we're done with the file for now. Figure out a better way
        # to cache images in the future.
        if self._imgdata_by_path.has_key(path) and self._imgdata_by_path[path]:
            del self._imgdata_by_path[path]


#
#    comment out mkdir for now, as we're only going to support
#    readonly version at first.
#
#    def mkdir(self, path, mode):
#        log.warning("mkdir: (%s): (%o)" % (str(path), mode))
#        log.warning("create gallery (%s) on smugmug" % str(path))
#
#        # split the path along the '/'.  the last one is
#        # an album. The other levels are categories.
#        dirs = path.split('/')
#        log.warning(dirs)
#
#        # get the octal of the mode to see if the album
#        # should be public or not. Need to define a
#        # whether g+r makes it public or not. u+r only
#        # makes it private
#        omode = oct(mode)
#
#        # add inode
#        st = MyStat()
#        st.st_mode = stat.S_IFDIR | mode
#        st.st_ino = 2
#        st.st_nlink = 1
#        st.st_atime = int(time.time())
#        st.st_mtime = int(time.time())
#        st.st_ctime = int(time.time())
#        self._inodes[path] = st
#
#        """
#        sm = zmugjson.Smugmug()
#        sessionid = sm.loginWithPassword(self._config['smugmug.username'],
#                                         self._config['smugmug.password'])
#        sm.createAlbum(sessionid, path, Public=0)
#        sm.logout(sessionid)
#        """
#        return -errno.ENOSYS

def main():
    usage = """
zmugfs: smugmug filesystem
    """ + Fuse.fusage
    server = ZmugFS(version="%prog " + fuse.__version__,
                    usage=usage,
                    dash_s_do='setsingle')
    server.parse(errex=1)
    log.warning("Hey there")
    server.main()

if __name__ == '__main__':
    main()
