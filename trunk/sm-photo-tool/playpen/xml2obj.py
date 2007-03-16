"""
Borrowed from the Python Cookbook:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149368
"""

import string
from xml.parsers import expat

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

class Xml2Obj:
    'XML to Object'
    def __init__(self):
        self.root = None
        self.nodeStack = []
        
    def startElement(self,name,attributes):
        'SAX start element even handler'
        # Instantiate an Element object
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
  <bar>
  cat
  </bar>
</foo>
"""
    element = parser.parse(sample)
    print element
