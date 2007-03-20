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
    
class Image:
    def __init__(self):
        self.id = 10

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
        print dir(node)
        print node.nodeName
        clazz = eval(node.nodeName)
        obj = clazz()
        
        """
        need to process attributes of the tag
        for each child node, get any attributes, then data
        interface Node {
  // NodeType
  const unsigned short      ELEMENT_NODE       = 1;
  const unsigned short      ATTRIBUTE_NODE     = 2;
  const unsigned short      TEXT_NODE          = 3;
  const unsigned short      CDATA_SECTION_NODE = 4;
  const unsigned short      ENTITY_REFERENCE_NODE = 5;
  const unsigned short      ENTITY_NODE        = 6;
  const unsigned short      PROCESSING_INSTRUCTION_NODE = 7;
  const unsigned short      COMMENT_NODE       = 8;
  const unsigned short      DOCUMENT_NODE      = 9;
  const unsigned short      DOCUMENT_TYPE_NODE = 10;
  const unsigned short      DOCUMENT_FRAGMENT_NODE = 11;
  const unsigned short      NOTATION_NODE      = 12;

  readonly attribute  DOMString            nodeName;
           attribute  DOMString            nodeValue;
                                                 // raises(DOMException) on setting
                                                 // raises(DOMException) on retrieval
  readonly attribute  unsigned short       nodeType;
  readonly attribute  Node                 parentNode;
  readonly attribute  NodeList             childNodes;
  readonly attribute  Node                 firstChild;
  readonly attribute  Node                 lastChild;
  readonly attribute  Node                 previousSibling;
  readonly attribute  Node                 nextSibling;
  readonly attribute  NamedNodeMap         attributes;
  readonly attribute  Document             ownerDocument;
  Node                      insertBefore(in Node newChild, 
                                         in Node refChild)
                                         raises(DOMException);
  Node                      replaceChild(in Node newChild, 
                                         in Node oldChild)
                                         raises(DOMException);
  Node                      removeChild(in Node oldChild)
                                        raises(DOMException);
  Node                      appendChild(in Node newChild)
                                        raises(DOMException);
  boolean                   hasChildNodes();
  Node                      cloneNode(in boolean deep);
};
        """
        print node.attributes
        return obj
        
class Smugmug:
    def __init__(self):
        self.sm = SmREST()
    
    def loginWithPassword(self, username, password):
        rsp = self.sm.smugmug.login.withPassword(EmailAddress=username,
                                      Password=password,
                                      APIKey="4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ")
        rsp = self.sm.findValue(rsp, "rsp/Login/SessionID")
        sessionid = rsp[0].firstChild.data
        print "rc: " + str(sessionid)
        return sessionid
    
    def logout(self, sessionid):
        rsp = self.sm.smugmug.logout(SessionID=sessionid)
        
    def getImageInfo(self, sessionid, imageId):
        rsp = self.sm.smugmug.images.getInfo(SessionID=sessionid,ImageID=imageId)
        # should return an Image object
        rsp = self.sm.findValue(rsp, "rsp/Info/Image")
        print rsp[0]
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
    
if __name__ == "__main__":
    # 1.1.1
    #sm = SmREST()

    sm1 = Smugmug()
    sessionid = sm1.loginWithPassword("jmrodri@gmail.com", "*****")
    print "Smugmug returned: " + str(sessionid)
    
    print "getimages"
    images = sm1.getImages(sessionid, 2559293)
    print "images: " + str(images)
    
    print "getimageinfo"
    imgInfo = sm1.getImageInfo(sessionid, images[0])
    print "imageinfo: " + str(imgInfo)
    
    print "logout"
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


    

    """

