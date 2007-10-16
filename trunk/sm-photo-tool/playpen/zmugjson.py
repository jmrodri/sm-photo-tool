#!/usr/bin/python
import httplib, urllib
import md5
from time import time
import simplejson
from config import Config
import logging
import logging.config

# configure the logging system for the module
logging.config.fileConfig("logger.conf")
log = logging.getLogger("zmugjson")

def filename_get_data(name):
  f = file(name,"rb")
  d = f.read()
  f.close()
  return d

#####################################################################
# Supporting classes for Smugmug data objects
#####################################################################
class BaseDict:
    def __init__(self, data={}):
        self.data = data
        
    def __setitem__(self, key, value):
        self.data[key] = value
    def __getitem__(self, key):
        return self.data[key]
    def __str__(self):
        return str(self.data)

class Image(BaseDict):
    pass

class Album(BaseDict):

    def __getattr__(self, name):
        if name == "name":
            return self.data['Title']
        else:
            return self.data[name]

    def children(self):
        return None
        

class Category(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.albums = []
        self.categories = []

    def children(self):
        return self.categories + self.albums

class Tree(object):
    def __init__(self):
        self.nodes = []

    def children(self):
        return self.nodes

    def print_tree(self):
        for cat in self.nodes:
            print "Category: %d - %s" % (cat.id, cat.name)
            print "\t%d albums" % len(cat.albums)
            print "\t%d subcats" % len(cat.categories)
            for scat in cat.categories:
                print "\tCategory: %d - %s" % (scat.id, scat.name)
                print "\t\t%d albums" % len(scat.albums)

def create_tree(nodes):
    if nodes.has_key('Categories'):
        tree = Tree()
        for node in nodes['Categories']:
            cat = Category(node['id'], node['Name'])
            if node.has_key('SubCategories'):
                for subcat in node['SubCategories']:
                    child = Category(subcat['id'], subcat['Name'])
                    if subcat.has_key('Albums'):
                        for a in subcat['Albums']:
                            album = Album(a)
                            child.albums.append(album)
                    cat.categories.append(child)
            if node.has_key('Albums'):
                for a in node['Albums']:
                    album = Album(a)
                    cat.albums.append(album)

            tree.nodes.append(cat)

        return tree
    else:
        return nodes

#####################################################################
# JSON-PRC proxy
#####################################################################

class _Method:
    """
    some magic to bind an XML-RPC method to an RPC server.
    supports "nested" methods (e.g. examples.getStateName)
    """
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, **args):
        return self.__send(self.__name, args)

class ZmugJSON:
    def __init__(self,version="1.2.1"):
        self.url="https://api.smugmug.com/services/api/json/%s/" % str(version)
        log.debug(self.url)

    def __getattr__(self, name):
        # magic method dispatcher
        #log.debug("__getattr__(%s)" % name)
        return _Method(self.__invoke, name)

    def __invoke(self, method, args):
        #log.debug("invoke.args: " + str(args))
        call = self.url + "?method="+ str(method)
        for k, v in args.iteritems():
            call = call + "&" + str(k) + "=" + str(v)
        log.debug(call)
        rsp = urllib.urlopen(call).read()
        log.debug("urlopen returned: " + str(rsp))
        return rsp
            
class Exception:
    def __init__(self, code, msg):
        self.code = code
        self.message = msg
        
    def __str__(self):
        return "%s: %s" % (str(self.code), str(self.message))
    
#####################################################################
# Smugmug API wrapper, uses ZmugJSON as the RPC proxy
#####################################################################
class Smugmug:
    def __init__(self,key):
        self.sm = ZmugJSON("1.2.1")
        self.key = key
    
    def loginWithPassword(self, username, password):
        rsp = self.sm.smugmug.login.withPassword(EmailAddress=username,
                                      Password=password,
                                      APIKey=self.key)
        session = simplejson.loads(rsp)
        # TODO: handle error cases
        #    * 1 - "invalid login"
        #    * 5 - "system error"
        #    * 11 - "ancient version"
        if session['stat'] == "ok":
            return session['Login']['Session']['id']
        else:
            raise Exception(session['code'], session['message'])

    def loginAnonymously(self):
        rsp = self.sm.smugmug.login.anonymously(APIKey=self.key)
        session = simplejson.loads(rsp)
        if session['stat'] == "ok":
            return session['Login']['Session']['id']
        else:
            raise Exception(session['code'], session['message'])
        
    
    def logout(self, sessionid):
        rsp = self.sm.smugmug.logout(SessionID=sessionid)
        rsp = simplejson.loads(rsp)

        if rsp['stat'] == "fail":
            raise Exception(rsp['code'], rsp['message'])

        # TODO: handle error cases
        #    * 3 - "invalid session"
        #    * 5 - "system error"
        
    def getImageInfo(self, sessionid, imageId):
        rsp = self.sm.smugmug.images.getInfo(SessionID=sessionid,ImageID=imageId)
        rsp = simplejson.loads(rsp)
        # TODO: handle error cases
        #    * 4 - "invalid user (message)"
        #    * 5 - "system error"
        return Image(rsp['Image'])

    def getImageUrls(self, sessionid, imageId):
        rsp = self.sm.smugmug.images.getURLs(SessionID=sessionid,ImageID=imageId)
        rsp = simplejson.loads(rsp)
        log.debug(rsp)
        return Image(rsp['Image'])
       
    def getImages(self, sessionid, albumId, heavy=1):
        """
        returns list of imageids for the given albumId
        """
        imageids = []
        rsp = self.sm.smugmug.images.get(SessionID=sessionid,AlbumID=albumId,Heavy=heavy)
        rsp = simplejson.loads(rsp)
        # TODO: handle error cases
        #    * 4 - "invalid user (message)"
        #    * 5 - "system error"
        #    * 15 - "empty set"
        log.debug(rsp)
        if rsp['stat'] == "fail":
            if rsp['code'] == 15:
                return [] # empty list
            else:
                raise rsp['message']

        return rsp['Images']

    def getImageIds(self, sessionid, albumId):
        """
        returns list of imageids for the given albumId
        """
        imageids = []
        rsp = self.sm.smugmug.images.get(SessionID=sessionid,AlbumID=albumId)
        rsp = simplejson.loads(rsp)
        # TODO: handle error cases
        #    * 4 - "invalid user (message)"
        #    * 5 - "system error"
        #    * 15 - "empty set"
        log.debug(rsp)
        return [img['id'] for img in rsp['Images']] # list of ids
    
    def getAlbumInfo(self, sessionid, albumId):
        rsp = self.sm.smugmug.albums.getInfo(SessionID=sessionid,AlbumID=albumId)
        rsp = simplejson.loads(rsp)
        # TODO: handle error cases
        #    * 4 - "invalid user (message)"
        #    * 5 - "system error"
        return Album(rsp['Album'])
    
    def createAlbum(self, sessionid, title, categoryId=0, **kargs):
        rsp = self.sm.smugmug.albums.create(SessionID=sessionid, Title=title, CategoryID=categoryId, **kargs)
        # TODO: deal with error conditions
        #    * 10 - "invalid title"
        #    * 3 - "invalid session"
        #    * 5 - "system error"
        # should return an id
        rsp = simplejson.loads(rsp)
        return rsp['Album']['id'] # albumid
    
    def deleteAlbum(self, sessionid, albumid):
        rsp = self.sm.smugmug.albums.delete(SessionID=sessionid, AlbumID=albumid)
        rsp = simplejson.loads(rsp)
        # TODO: deal with error conditions
        #     * 4 - "invalid user"
        #     * 5 - "system error"
        return rsp['Album'] # returns true or false

       
    def getTree(self, sessionid, heavy=0):
        """
        returns a Tree object
        """
        rsp = self.sm.smugmug.users.getTree(SessionID=sessionid, Heavy=heavy)
        # returns array of categories
        return simplejson.loads(rsp, object_hook=create_tree)

    
    def uploadImage(self, sessionid, albumid, filename):
        imageid = 0
        log.debug("uploadImage -----------------------------------------------------")
        
        data = filename_get_data(filename)
        headers = {
            "Content-Transfer-Encoding":'binary',
            "Content-MD5":md5.new(data).hexdigest(),
            "X-Smug-SessionID":sessionid,
            "X-Smug-Version":'1.1.1',
            "X-Smug-ResponseType": 'JSON',
            "X-Smug-AlbumID": albumid,
            "X-Smug-FileName": filename
        }
        
        conn = httplib.HTTPConnection("upload.smugmug.com", 80)
        conn.connect()
        conn.request("PUT", '/' + filename, data, headers)
        response = conn.getresponse()
        print response.status, response.reason
        rsp = response.read()
        log.debug(rsp)
        rsp = simplejson.loads(rsp)

        if rsp.has_key('stat') and rsp['stat'] == "ok":
            log.debug("we're ok")
            imageid = rsp['Image']['id']
        conn.close()
        log.debug("uploadImage -------------------------------------------------")
        return imageid
        
        
#####################################################################
# MAIN
#####################################################################
if __name__ == "__main__":
    config = Config('/etc/zmugjson/zmugjson.conf', '.zmugjsonrc')
    sm1 = Smugmug("4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ")
    sessionid = sm1.loginWithPassword(config.get_property('smugmug.username'),
                                      config.get_property('smugmug.password'))
    log.debug("Smugmug returned: " + str(sessionid))
    log.info("createalbum -------------------------------")
    albumid = sm1.createAlbum(sessionid, "testalbum" + str(time()), Public=0)
    log.debug("albumid: " + str(albumid))
    log.info("getalbuminfo -------------------------------")
    albuminfo = sm1.getAlbumInfo(sessionid, albumid)
    log.debug("albuminfo: " + str(albuminfo))
    log.debug("lastupdated: " + str(albuminfo['LastUpdated']))
    if albuminfo['Public']:
        log.debug("this album is Public")
    else:
        log.debug("this album is PRIVATE")
    
    #try:
    #    sm1.uploadImage(sessionid, albumid, "test.jpg")    
    #finally:
    #    log.debug("upload image failed")

    
    log.info("getimageids -------------------------------")
    images = sm1.getImageIds(sessionid, 3167690)
    log.debug("imageids: " + str(images))
    
    log.info("getimageinfo ---------------------------------------")
    imgInfo = sm1.getImageInfo(sessionid, images[0])
    log.debug("imageinfo: " + str(imgInfo))
    log.debug("TinyURL = " + imgInfo['TinyURL'])
    log.debug("lastupdate = " + imgInfo['LastUpdated'])
    log.debug("date = " + imgInfo['Date'])
    log.debug("imageid = " + str(imgInfo['id']))
    log.debug("albumId = " + str(imgInfo['Album']['id']))

    log.info("getimageurls ---------------------------------------")
    urls = sm1.getImageUrls(sessionid, images[0])
    log.debug(urls['ThumbURL'])

    rc = sm1.deleteAlbum(sessionid, albumid)
    if rc:
        log.debug("album (%d) deleted" % albumid)
    else:
        log.debug("could not delete album (%d)" % albumid)
    log.info("gettree ------------------------------------------")
    tree = sm1.getTree(sessionid, 1)
    #tree.print_tree()
    
    log.info("logout -------------------------------------------")
    rc = sm1.logout(sessionid)
    log.debug("logout returned: " + str(rc))
    
    classobj = eval("Image")
    classinstance = classobj()
    log.debug(classinstance.__class__)

    log.debug(type(classinstance))
    log.debug(dir(classinstance))
