#!/usr/bin/python
import urllib
from xml.dom.ext.reader import Sax2
#url?method=<name>&param1=value1....
#
#map = {param1=>value1,param2=>value2}
#Smugmug.method(map)

class _Method:
    # some magic to bind an XML-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, **args):
        print "__name: %s" % self.__name
        print "args: " + str(args)
        return self.__send(self.__name, args)

class Smugmug:
    def __init__(self):
        self.url="https://api.smugmug.com/hack/rest/1.1.1/"
        self.apikey="4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ"
        print self.url

    def addKey(self, call):
        return call + "&APIKey=" + self.apikey

    def __getattr__(self, name):
        # magic method dispatcher
        print "__getattr__(%s)" % name
        return _Method(self.__invoke, name)

    def __invoke(self, method, args):
        print "invoke.args: " + str(args)
        call = self.url + "?method="+ str(method)
        for k, v in args.iteritems():
            call = call + "&" + str(k) + "=" + str(v)
        call = self.addKey(call)
        print call
        rsp = urllib.urlopen(call).read()
        print rsp
        reader = Sax2.Reader()
        return rsp

if __name__ == "__main__":
    sm = Smugmug()
    sm.smugmug.login.withPassword(EmailAddress="jmrodri@gmail.com",
                                  Password="****");
