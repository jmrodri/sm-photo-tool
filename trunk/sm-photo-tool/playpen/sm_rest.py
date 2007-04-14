#!/usr/bin/python
import httplib, urllib
import md5
from xml import xpath
from xml.dom.minidom import parseString
from time import time

#url?method=<name>&param1=value1....
#
#map = {param1=>value1,param2=>value2}
#Smugmug.method(map)

def filename_get_data(name):
  f = file(name,"rb")
  d = f.read()
  f.close()
  return d

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
        elif node.nodeType == node.ELEMENT_NODE:
            rc = getText(node[0].childNodes)
        return rc
    
class Image:
    def __init__(self):
        self.data = {}
        
    def __setitem__(self, key, value):
        #print "__setitem__(%s:%s)" % (key,value)
        self.data[key.lower()] = value
    def __getitem__(self, key):
        #print "__getitem__(%s)" % (key)
        return self.data[key.lower()]
    def __str__(self):
        return str(self.data)

class Album:
    def __init__(self):
        self.data = {}
        
    def __setitem__(self, key, value):
        #print "__setitem__(%s:%s)" % (key,value)
        self.data[key.lower()] = value
    def __getitem__(self, key):
        #print "__getitem__(%s)" % (key)
        return self.data[key.lower()]
    def __str__(self):
        return str(self.data)

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
        self.url="https://api.smugmug.com/hack/rest/%s/" % str(version)
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

    def findValue(self, doc, path):
        dom1 = parseString(doc)
        nodes = xpath.Evaluate(path, dom1)
        return nodes
        #return getText(nodes[0].childNodes)
        
    def createObject(self, nodeList):
        print "createObj: " + str(dir(nodeList))
        node = nodeList[0]
        print "Creating class of type: " + str(node.nodeName)
        clazz = eval(node.nodeName)
        obj = clazz()
       
        # gather the attributes of the node
        self.__processAttributes(obj, node.tagName, node.attributes)
        self.__processNodes(obj, node.childNodes)
            
        return obj
        
    def __processNodes(self, obj, nodes):
        for n in nodes:
            if n.nodeType == n.TEXT_NODE:
                obj[n.parentNode.tagName] = n.data
            elif n.nodeType == n.ELEMENT_NODE:
                #print n.tagName
                if n.hasAttributes:
                    self.__processAttributes(obj, n.tagName, n.attributes)
                if n.hasChildNodes:
                    self.__processNodes(obj, n.childNodes)
                        
    def __processAttributes(self, obj, tagName, attributes):
        for i in range(attributes.length):
            attr = attributes.item(i)
            #print str(attr.name) + " " + str(attr.value)
            obj[tagName + attr.name] = attr.value
            
class Exception:
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        
    def __str__(self):
        return "%s: %s" % (str(self.code), str(self.msg))
    
class Smugmug:
    def __init__(self):
        self.sm = SmREST()
    
    def loginWithPassword(self, username, password):
        rsp = self.sm.smugmug.login.withPassword(EmailAddress=username,
                                      Password=password,
                                      APIKey="4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ")
        # handle invalid login
        r = self.sm.findValue(rsp, "rsp/err")
        if len(r) != 0:
            msg = r[0].attributes["msg"].value
            code = r[0].attributes["code"].value
            
            raise Exception(code, msg)
        
        rsp = self.sm.findValue(rsp, "rsp/Login/SessionID")
        if rsp is None:
            print "rsp is none"
        sessionid = rsp[0].firstChild.data
        print "rc: " + str(sessionid)
        return sessionid
    
    def logout(self, sessionid):
        rsp = self.sm.smugmug.logout(SessionID=sessionid)
        
    def getImageInfo(self, sessionid, imageId):
        rsp = self.sm.smugmug.images.getInfo(SessionID=sessionid,ImageID=imageId)
        # should return an Image object
        rsp = self.sm.findValue(rsp, "rsp/Info/Image")
        #print rsp[0]
        return self.sm.createObject(rsp)
        
    def getImages(self, sessionid, albumId):
        """
        returns list of imageids for the given albumId
        """
        imageids = []
        rsp = self.sm.smugmug.images.get(SessionID=sessionid,AlbumID=albumId)
        rsp = self.sm.findValue(rsp, "rsp/Images/Image/@id")
        # should return array of ids
        for id in rsp:
            imageids.append(id.value)
        return imageids
    
    def getAlbumInfo(self, sessionid, albumId):
        rsp = self.sm.smugmug.albums.getInfo(SessionID=sessionid,AlbumID=albumId)
        rsp = self.sm.findValue(rsp, "rsp/Albums/Album")
        return self.sm.createObject(rsp)
    
    def createAlbum(self, sessionid, title, categoryId=0, **kargs):
        rsp = self.sm.smugmug.albums.create(SessionID=sessionid, Title=title, CategoryID=categoryId, **kargs)
        # should return an id
        rsp = self.sm.findValue(rsp, "rsp/Create/Album/@id")
        return int(rsp[0].value) # albumid
    
    def deleteAlbum(self, sessionid, albumid):
        rsp = self.sm.smugmug.albums.delete(SessionID=sessionid, AlbumID=albumid)
        rsp = self.sm.findValue(rsp, "rsp/Delete/Album/Successful");
        return rsp[0].tagName
    
    def uploadImage(self, sessionid, albumid, filename):
        print "uploadImage -----------------------------------------------------"
        """
            print "upload"
    filename = "test.jpg"
    data = filename_get_data(filename)
    len = len(data)
    
    headers = {
        "Content-Length":,
        "Content-MD5":,
        "X-Smug-SessionID":sessionid,
        "X-Smug-Version":'1.1.1',
        "X-Smug-ResponseType": 'REST',
        "X-Smug-AlbumID": albumid,
        "X-Smug-FileName": filename
        }
    filename = "photo.jpg"
    conn = httplib.HTTPConnection("http://upload.smugmug.com/")
    conn.request("PUT", filename, {}, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    print data
    conn.close()
    print "delete"
    rsp = sm.smugmug.albums.delete(SessionID=sessionid,AlbumID=albumid)
    rsp = sm.findValue(rsp, "rsp/Delete/Album/Successful");
    print rsp[0].tagName
        """
        data = filename_get_data(filename)
        size = len(data)
        headers = {
            "Content-Length":size,
            "Content-MD5":md5.new(data).hexdigest(),
            "X-Smug-SessionID":sessionid,
            "X-Smug-Version":'1.1.1',
            "X-Smug-ResponseType": 'REST',
            "X-Smug-AlbumID": albumid,
            "X-Smug-FileName": filename
        }
        
        conn = httplib.HTTPConnection("upload.smugmug.com")
        conn.request("PUT", filename, data, headers)
        response = conn.getresponse()
        print response.status, response.reason
        print response.read()
        conn.close()
        print "uploadImage -------------------------------------------------"
        
        
if __name__ == "__main__":
    # 1.1.1
    #sm = SmREST()

    sm1 = Smugmug()
    sessionid = sm1.loginWithPassword("jmrodri@gmail.com", "Wakt$iaS")
    print "Smugmug returned: " + str(sessionid)
    
    print "createalbum"
    albumid = sm1.createAlbum(sessionid, "testalbum" + str(time()), Public=0)
    print "albumid: " + str(albumid)
    print "getalbuminfo"
    #albuminfo = sm1.getAlbumInfo(sessionid, 2559293)
    albuminfo = sm1.getAlbumInfo(sessionid, albumid)
    print "albuminfo: " + str(albuminfo)
    if albuminfo['public']:
        print "this album is public"
    else:
        print "this album is PRIVATE"
    
    sm1.uploadImage(sessionid, albumid, "test.jpg")    
    
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
    print "imageid = " + imgInfo['imageid']
    print "albumId = " + imgInfo['albumId']
    
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

