#!/usr/bin/python
class Album:
    def __init__(self):
        self.data = {}
        
    def __setitem__(self, key, value):
        #print "__setitem__(%s:%s)" % (key,value)
        self.data[key] = value
    def __getitem__(self, key):
        #print "__getitem__(%s)" % (key)
        return self.data[key]

if __name__ == "__main__":
    b = 'bar'
    a = Album()
    #print dir(a)
    a.foo = 'hello'
    #a['bar'] = 30
    a[b] = 20
    a['album'] = Album()
    a['album'].b = 10
    print a.foo
    print a['bar']
    print a['album'].b
    #print dir(a)
