import sys
import httplib
from xmlrpclib import *
import hashlib

if len(sys.argv) < 3:
    print("testupload.py username password albumid")
    sys.exit(1)

#albumid = 10116334
albumid = sys.argv[3]
filename = 'test.jpg'

client = ServerProxy("https://api.smugmug.com/services/api/xmlrpc/1.2.1/")
session = client.smugmug.login.withPassword(sys.argv[1], sys.argv[2],
    "4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ")

# read in image file
f = file(filename, "rb")
data = f.read()
f.close()

# prep HTTP PUT to upload image
#h = httplib.HTTP("upload.smugmug.com")
h = httplib.HTTPConnection("upload.smugmug.com")
h.connect()
h.putrequest('PUT', "/" + filename)
print("Content-Length: %s" % str(len(data)))
print("Content-MD5: %s" % hashlib.md5(data).hexdigest())
print("X-Smug-SessionID: %s" % session["Session"]["id"])
print("X-Smug-Version: 1.2.1")
print("X-Smug-ResponseType: XML-RPC")
print("X-Smug-AlbumID: %s" % str(albumid))
print("X-Smug-FileName: %s" % filename)

h.putheader('Content-Length', str(len(data)))
h.putheader('Content-MD5', hashlib.md5(data).hexdigest())
h.putheader('X-Smug-SessionID', session['Session']['id'])
h.putheader('X-Smug-Version', '1.2.1')
h.putheader('X-Smug-ResponseType', 'XML-RPC')
h.putheader('X-Smug-AlbumID', str(albumid))
h.putheader('X-Smug-FileName', filename)
h.endheaders()
h.send(data)

# response output
resp = h.getresponse()
print("%s: %s" % (resp.status, resp.reason))
result = resp.read()
h.close()
print("PUT: result: %s" % result)
