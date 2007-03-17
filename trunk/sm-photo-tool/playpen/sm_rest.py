#!/usr/bin/python
import urllib
from xml import xpath
from xml.dom.minidom import parseString
from time import time

#url?method=<name>&param1=value1....
#
#map = {param1=>value1,param2=>value2}
#Smugmug.method(map)


def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
        elif node.nodeType == node.ELEMENT_NODE:
            rc = getText(node[0].childNodes)
        return rc

class Album:
    def __init__(self, id, title, category, categoryid, subcategory='', subcategoryid=''):
        self.id = id
        self.title = title
        self.category = category
        self.categoryid = categoryid
        self.subcategory = subcategory
        self.subcategoryid = subcategoryid

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

class Smugmug:
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

if __name__ == "__main__":
    # 1.1.1
    sm = Smugmug()
    rsp = sm.smugmug.login.withPassword(EmailAddress="jmrodri@gmail.com",
                                  Password="****", APIKey=sm.apikey)
    rsp = sm.findValue(rsp, "rsp/Login/SessionID")
    sessionid = rsp[0].firstChild.data
    print "rc: " + str(sessionid)
    

    print "calling albums.create"
    rsp = sm.smugmug.albums.create(SessionID=sessionid, Title="testalbum" + str(time()), CategoryID=0)
    # should return an id
    rsp = sm.findValue(rsp, "rsp/Create/Album/@id")
    albumid = rsp[0].value
    print albumid
    
    print "getinfo"
    rsp = sm.smugmug.albums.getInfo(SessionID=sessionid,AlbumID=albumid)
    rsp = sm.findValue(rsp, "rsp/Albums/Album")
    # should build an Album objects
    print rsp[0]
    
    print "delete"
    rsp = sm.smugmug.albums.delete(SessionID=sessionid,AlbumID=albumid)
    rsp = sm.findValue(rsp, "rsp/Delete/Album/Successful");
    print rsp[0].tagName


    print "getimages for album: 2559293"
    rsp = sm.smugmug.images.get(SessionID=sessionid,AlbumID=2559293)
    rsp = sm.findValue(rsp, "rsp/Images/Image/@id")
    # should return array of ids
    print "count: " + str(len(rsp))
    print rsp[0].value

    print "getimageinfo"
    rsp = sm.smugmug.images.getInfo(SessionID=sessionid,ImageID=rsp[0].value)
    # should return an Image object
    rsp = sm.findValue(rsp, "rsp/Info/Image")
    print rsp[0]
    
    print "logout"
    rsp1 = sm.smugmug.logout(SessionID=sessionid)
    print rsp1

