#!/usr/bin/python
import httplib, urllib
import md5
from time import time
import simplejson
from elementtree.ElementTree import ElementTree

#url?method=<name>&param1=value1....
#
#map = {param1=>value1,param2=>value2}
#Smugmug.method(map)

def filename_get_data(name):
  f = file(name,"rb")
  d = f.read()
  f.close()
  return d

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
    pass


class _Method:
    # some magic to bind an XML-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, **args):
        #print "__name: %s" % self.__name
        #print "args: " + str(args)
        return self.__send(self.__name, args)

class SmREST:
    def __init__(self,version="1.1.1"):
        #http[s]://api.smugmug.com/hack/rest/1.2.0/
        #https://api.smugmug.com/hack/rest/1.1.1/
        #self.url="https://api.smugmug.com/hack/rest/%s/" % str(version)
        self.url="https://api.smugmug.com/hack/json/%s/" % str(version)
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
    
class Smugmug:
    def __init__(self):
        self.sm = SmREST("1.2.0")
    
    def loginWithPassword(self, username, password):
        rsp = self.sm.smugmug.login.withPassword(EmailAddress=username,
                                      Password=password,
                                      APIKey="4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ")
        session = simplejson.loads(rsp)
        if session['stat'] == "ok":
            return session['Login']['Session']['id']
        else:
            raise Exception(session['code'], session['message'])
    
    def logout(self, sessionid):
        rsp = self.sm.smugmug.logout(SessionID=sessionid)
        
    def getImageInfo(self, sessionid, imageId):
        rsp = self.sm.smugmug.images.getInfo(SessionID=sessionid,ImageID=imageId)
        rsp = simplejson.loads(rsp)
        return Image(rsp['Image'])
        
    def getImages(self, sessionid, albumId):
        """
        returns list of imageids for the given albumId
        """
        imageids = []
        rsp = self.sm.smugmug.images.get(SessionID=sessionid,AlbumID=albumId)
        rsp = simplejson.loads(rsp)
        return rsp['Images'].keys()
    
    def getAlbumInfo(self, sessionid, albumId):
        rsp = self.sm.smugmug.albums.getInfo(SessionID=sessionid,AlbumID=albumId)
        rsp = simplejson.loads(rsp)
        keys = rsp['Album'].keys()
        print Album(rsp['Album'][keys[0]])
        return Album(rsp['Album'][keys[0]])
    
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
    
    def uploadImage(self, sessionid, albumid, filename):
        print "uploadImage -----------------------------------------------------"
        
        data = filename_get_data(filename)
        headers = {
            "Content-Transfer-Encoding":'binary',
            "Content-MD5":md5.new(data).hexdigest(),
            "X-Smug-SessionID":sessionid,
            "X-Smug-Version":'1.1.1',
            "X-Smug-ResponseType": 'REST',
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

        if rsp.find('stat="ok"') > 0:
            print "we're ok"
        """
        <?xml version='1.0' encoding="iso-8859-1" ?>
            <rsp stat="fail">
                        <err code="4" msg="Wrong format. (ByteCount given: ,  received.  MD5Sum given: ,  actual.)" />

                    </rsp>
        """
        conn.close()
        print "uploadImage -------------------------------------------------"
        
        
if __name__ == "__main__":
    # 1.1.1
    #sm = SmREST()

    sm1 = Smugmug()
    sessionid = sm1.loginWithPassword("jmrodri@gmail.com", "****")
    print "Smugmug returned: " + str(sessionid)
    
    print "createalbum"
    albumid = sm1.createAlbum(sessionid, "testalbum" + str(time()), Public=0)
    print "albumid: " + str(albumid)
    print "getalbuminfo"
    #albuminfo = sm1.getAlbumInfo(sessionid, 2559293)
    albuminfo = sm1.getAlbumInfo(sessionid, albumid)
    print "albuminfo: " + str(albuminfo)
    if albuminfo['Public']:
        print "this album is Public"
    else:
        print "this album is PRIVATE"
    
    try:
        sm1.uploadImage(sessionid, albumid, "test.jpg")    
    finally:
        print "upload image failed"
    
    #rc = sm1.deleteAlbum(sessionid, albumid)
    #if rc:
    #    print "album (%d) deleted" % albumid
    #else:
    #    print "could not delete album (%d)" % albumid

    
    print "getimages"
    images = sm1.getImages(sessionid, 2559293)
    print "images: " + str(images)
    
    print "getimageinfo ---------------------------------------"
    imgInfo = sm1.getImageInfo(sessionid, images[0])
    print "imageinfo: " + str(imgInfo)
    print "TinyURL = " + imgInfo['TinyURL']
    print "imageid = " + str(imgInfo['id'])
    print "albumId = " + str(imgInfo['Album']['id'])
    
    print "logout -------------------------------------------"
    rc = sm1.logout(sessionid)
    print "logout returned: " + str(rc)
    
    classobj = eval("Image")
    classinstance = classobj()
    print classinstance.__class__

    print type(classinstance)
    print dir(classinstance)
    
    """
    print "calling albums.create"
    rsp = sm.smugmug.albums.create(SessionID=sessionid, Title="testalbum" + str(time()), CategoryID=0)
    # should return an id
    rsp = sm.findValue(rsp, "rsp/Create/Album/@id")
    albumid = rsp[0].value
    print albumid
    

   


    """

