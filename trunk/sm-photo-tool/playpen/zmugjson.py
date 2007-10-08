#!/usr/bin/python
import httplib, urllib
import md5
from time import time
import simplejson
from config import Config
#from elementtree.ElementTree import ElementTree

#url?method=<name>&param1=value1....
#
#map = {param1=>value1,param2=>value2}
#Smugmug.method(map)

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
        #print "__setitem__(%s:%s)" % (key,value)
        self.data[key] = value
    def __getitem__(self, key):
        #print "__getitem__(%s)" % (key)
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
    tree = Tree()
    if nodes.has_key('Categories'):
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
        #print "__name: %s" % self.__name
        #print "args: " + str(args)
        return self.__send(self.__name, args)

class ZmugJSON:
    def __init__(self,version="1.2.1"):
        self.url="https://api.smugmug.com/services/api/json/%s/" % str(version)
        self.apikey="4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ"
        print self.url

    def __addKey(self, call):
        return call + "&APIKey=" + self.apikey

    def __getattr__(self, name):
        # magic method dispatcher
        #print "__getattr__(%s)" % name
        return _Method(self.__invoke, name)

    def __invoke(self, method, args):
        #print "invoke.args: " + str(args)
        call = self.url + "?method="+ str(method)
        for k, v in args.iteritems():
            call = call + "&" + str(k) + "=" + str(v)
        #call = self.__addKey(call)
        print call
        rsp = urllib.urlopen(call).read()
        print "urlopen returned: " + str(rsp)
        return rsp
            
class Exception:
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        
    def __str__(self):
        return "%s: %s" % (str(self.code), str(self.msg))
    
#####################################################################
# Smugmug API wrapper, uses ZmugJSON as the RPC proxy
#####################################################################
class Smugmug:
    def __init__(self):
        self.sm = ZmugJSON("1.2.1")
    
    def loginWithPassword(self, username, password):
        rsp = self.sm.smugmug.login.withPassword(EmailAddress=username,
                                      Password=password,
                                      APIKey="4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ")
        session = simplejson.loads(rsp)
        # TODO: handle error cases
        #    * 1 - "invalid login"
        #    * 5 - "system error"
        #    * 11 - "ancient version"
        if session['stat'] == "ok":
            return session['Login']['Session']['id']
        else:
            raise Exception(session['code'], session['message'])
    
    def logout(self, sessionid):
        rsp = self.sm.smugmug.logout(SessionID=sessionid)
        rsp = simplejson.loads(rsp)
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
        print rsp
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
        print rsp
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
        print rsp
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
        print "uploadImage -----------------------------------------------------"
        
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
        print rsp
        rsp = simplejson.loads(rsp)

        if rsp.has_key('stat') and rsp['stat'] == "ok":
            print "we're ok"
            imageid = rsp['Image']['id']
        conn.close()
        print "uploadImage -------------------------------------------------"
        return imageid
        
        
#####################################################################
# MAIN
#####################################################################
if __name__ == "__main__":
    config = Config('/etc/zmugjson/zmugjson.conf', '.zmugjsonrc')
    sm1 = Smugmug()
    sessionid = sm1.loginWithPassword(config.get_property('smugmug.username'),
                                      config.get_property('smugmug.password'))
    print "Smugmug returned: " + str(sessionid)
    print "createalbum"
    albumid = sm1.createAlbum(sessionid, "testalbum" + str(time()), Public=0)
    print "albumid: " + str(albumid)
    print "getalbuminfo"
    albuminfo = sm1.getAlbumInfo(sessionid, albumid)
    print "albuminfo: " + str(albuminfo)
    if albuminfo['Public']:
        print "this album is Public"
    else:
        print "this album is PRIVATE"
    
    #try:
    #    sm1.uploadImage(sessionid, albumid, "test.jpg")    
    #finally:
    #    print "upload image failed"

    
    print "getimageids"
    images = sm1.getImageIds(sessionid, 3167690)
    print "imageids: " + str(images)
    
    print "getimageinfo ---------------------------------------"
    imgInfo = sm1.getImageInfo(sessionid, images[0])
    print "imageinfo: " + str(imgInfo)
    print "TinyURL = " + imgInfo['TinyURL']
    print "imageid = " + str(imgInfo['id'])
    print "albumId = " + str(imgInfo['Album']['id'])

    print "getimageurls ---------------------------------------"
    urls = sm1.getImageUrls(sessionid, images[0])
    print urls['ThumbURL']

    rc = sm1.deleteAlbum(sessionid, albumid)
    if rc:
        print "album (%d) deleted" % albumid
    else:
        print "could not delete album (%d)" % albumid
    print "gettree ------------------------------------------"
    tree = sm1.getTree(sessionid, 1)
    print tree.print_tree()
    """
    for cat in rc:
        print "Category: (%s:%s) path:(/%s)" % (str(cat['id']), str(cat['Name']), str(cat['Name']))
        if cat.has_key('SubCategories'):
            for subcat in cat['SubCategories']:
                print "\tSubcat: (%s:%s) path:(/%s/%s)" % (str(subcat['id']), str(subcat['Name']), str(cat['Name']), str(subcat['Name']))
                #print subcat
                for album in subcat['Albums']:
                    print "\t\tAlbum: (%s:%s) path:(/%s/%s/%s)" % (str(album['id']), str(album['Title']), str(cat['Name']), str(subcat['Name']), str(album['Title']))
                    #print album
        if cat.has_key('Albums'):
            for album in cat['Albums']:
                print "\tAlbum: (%s:%s) path:(/%s/%s)" % (str(album['id']), str(album['Title']), str(cat['Name']), str(album['Title']))
                #print album
    """
    
    print "logout -------------------------------------------"
    rc = sm1.logout(sessionid)
    print "logout returned: " + str(rc)
    
    classobj = eval("Image")
    classinstance = classobj()
    print classinstance.__class__

    print type(classinstance)
    print dir(classinstance)
