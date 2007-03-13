#!/usr/bin/python
import urllib
from xml.dom.ext.reader import Sax2
#url?method=<name>&param1=value1....
#
#map = {param1=>value1,param2=>value2}
#Smugmug.method(map)

class Smugmug:
    def __init__(self):
        self.url="https://api.smugmug.com/hack/rest/1.1.1/"
        self.apikey="4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ"
        print self.url

    def addKey(self, call):
        return call + "&APIKey=" + self.apikey

    def invoke(self, method, args):
        call = self.url + "?method="+ str(method)
        for k, v in args.iteritems():
            call = call + "&" + str(k) + "=" + str(v)
        call = self.addKey(call)
        print call
        rsp = urllib.urlopen(call).read()
        print rsp
        reader = Sax2.Reader()
        #doc = reader.fromString(rsp)
        return rsp

if __name__ == "__main__":
    sm = Smugmug()
    args = {"EmailAddress":"jmrodri@gmail.com",
            "Password":"luvLiz69"}
    sm.invoke("smugmug.login.withPassword", args)
