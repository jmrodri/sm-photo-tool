"""
Borrowed from the Python Cookbook:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149368
"""

import string
from xml.parsers import expat
from xml import xpath
from xml.dom.minidom import parseString
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            print "we have a TEXT_NODE"
            rc = rc + node.data
        return rc

class Element:
    'A parsed XML element'
    def __init__(self,name,attributes):
        'Element constructor'
        # The element's tag name
        self.name = name
        # The element's attribute dictionary
        self.attributes = attributes
        # The element's cdata
        self.cdata = ''
        # The element's child element list (sequence)
        self.children = []
        
    def addChild(self,element):
        'Add a reference to a child element'
        self.children.append(element)
        
    def getAttribute(self,key):
        'Get an attribute value'
        return self.attributes.get(key)
    
    def getData(self):
        'Get the cdata'
        return self.cdata
        
    def getElements(self,name=''):
        'Get a list of child elements'
        #If no tag name is specified, return the all children
        if not name:
            return self.children
        else:
            # else return only those children with a matching tag name
            elements = []
            for element in self.children:
                if element.name == name:
                    elements.append(element)
            return elements

    def getElement(self,path):
        print path
        if path == None:
            return path
        newpath = path.split('/')
        elem = None
        for p in newpath:
            elem = self.getElements(p)
        print type(elem)
        print "dir(elem): " + str(dir(elem))
        return elem[0].getData()

class Xml2Obj:
    'XML to Object'
    def __init__(self):
        self.root = None
        self.nodeStack = []
        
    def startElement(self,name,attributes):
        'SAX start element even handler'
        # Instantiate an Element object
        print "name: %s; attributes: %s" % (name,str(attributes))
        element = Element(name.encode(),attributes)
        
        # Push element onto the stack and make it a child of parent
        if len(self.nodeStack) > 0:
            parent = self.nodeStack[-1]
            parent.addChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)
        
    def endElement(self,name):
        'SAX end element event handler'
        print "name: %s" % name
        self.nodeStack = self.nodeStack[:-1]

    def characterData(self,data):
        'SAX character data event handler'
        if string.strip(data):
            data = data.encode()
            element = self.nodeStack[-1]
            element.cdata += data
            return

    def parse(self,document):
        # Create a SAX parser
        parser = expat.ParserCreate()

        # SAX event handlers
        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characterData

        # Parse the XML File
        status = parser.Parse(document, 1)
        
        return self.root
   
if __name__ == "__main__":
    parser = Xml2Obj()
    sample = """<?xml version="1.0"?>
<foo>
  <bar name="jar">
      cat
  </bar>
</foo>
"""
    #element = parser.parse(sample)
    #print "foo/bar: " + element.getElement("foo/bar")
    #print "foo: " + element.getElement("foo")
    #print "foo/fee: " + element.getElement("foo/fee")

    dom1 = parseString(sample)
    nodes = xpath.Evaluate("foo/bar", dom1)
    #print dir(nodes)
    #print type(nodes)
    #print len(nodes)
    #print getText(nodes)
    #print dir(nodes[0].childNodes)
    print "text: " + getText(nodes[0].childNodes)
