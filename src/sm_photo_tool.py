# sm_photo_tool.py - Smugmug API wrapper
#
# Copyright (C) 2007-2009 Jesus M. Rodriguez
# Copyright (C) 2004 John C. Ruttenberg
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from sys import stderr, exit
import string
import re
from xmlrpclib import *
import httplib, mimetypes
import hashlib
import os
from os import path

version = "1.13"
# sm_photo_tool offical key:
key = "4XHW8Aw7BQqbkGszuFciGZH4hMynnOxJ"

def error(string):
    from sys import exit, stderr
    stderr.write(string + "\n")
    exit(1)

def message(opts, string):
    from sys import stdout
    if opts:
        if not opts.quiet:
            stdout.write(string)
    else:
        stdout.write(string)

def minutes_seconds(seconds):
    if seconds < 60:
        return "%d" % seconds
    else:
        return "%d:%02d" % (seconds / 60, seconds % 60)

def filename_get_line(name):
    f = file(name, "rU")
    l = f.readline()
    f.close()
    return l[:-1]

def filename_get_data(name):
    f = file(name, "rb")
    d = f.read()
    f.close()
    return d

def filename_put_string(filename, string):
    f = file(filename, "w")
    f.write(string)
    f.close()

class LocalInformation:
    def __init__(self, dir):
        self.dir = dir
        self.smdir = path.join(dir, "SMUGMUG_INFO")

    def exists(self):
        return path.isdir(self.smdir) and path.isfile(path.join(self.smdir, "gallery"))

    def create(self, gallery):
        if not path.isdir(self.smdir):
            os.mkdir(self.smdir)
        gallery_file = path.join(self.smdir, "gallery")
        if not path.isfile(gallery_file):
            filename_put_string(gallery_file, "%s\n" % gallery)
        self.created = True

    def gallery_id(self):
        if not self.exists():
            raise "No Localinformation for %s" % (dir)
        l = filename_get_line(path.join(self.smdir, "gallery"))
        return l

    def file_needs_upload(self, filename):
        try:
            if not self.exists():
                return False
            head, tail = path.split(filename)
            infofile = path.join(self.smdir, tail)
            if not path.isfile(infofile):
                return True
            l = filename_get_line(infofile)
            utime_s, size_s, count_s = string.split(l)
            if path.getmtime(filename) > int(utime_s):
                return True
            if os.stat(filename).st_size != int(size_s):
                return True
            return False
        except:
            return True

    def file_uploaded(self, filename):
        from time import time

        head, tail = path.split(filename)
        infofile = path.join(self.smdir, tail)

        if not path.isfile(infofile):
            count = 1
        else:
            l = filename_get_line(infofile)
            try:
                utime_s, size_s, count_s = string.split(l)
                count = int(count_s) + 1
            except:
                count = 1

        filename_put_string(infofile, "%d %d %d\n" % (time(),
            os.stat(filename).st_size, count))

    def file_upload_count(self, filename):
        head, tail = path.split(filename)
        infofile = path.join(self.smdir, tail)

        if not path.isfile(infofile):
            return 0
        else:
            l = filename_get_line(infofile)
            utime_s, size_s, count_s = string.split(l)
            return int(count_s)

#
# Get the caption for a given filename.  If a ".caption" file exists
# for the file to upload, use the contents of that file.  Otherwise,
# if the filenames-are-default-captions bool is set, use the name of the
# file as the caption.
#
# Alternatively, instead of doing captioning through this tool, once
# an image is uploaded to smugmug, the smugmug system will use the
# "IPTC:Caption-Abstract" EXIF header field as a default caption.
# (Try 'exiftool -Caption-Abstract="this is a test caption" foo.jpg.)
#
def caption(filename, filenames_default_captions):
    head, ext = path.splitext(filename)
    capfile = head + ".caption"
    if path.isfile(capfile):
        result = filename_get_data(capfile)
        return result
    if filenames_default_captions:
        head, tail = path.split(head)
        return tail
    return None

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

class Smugmug:
    def __init__(self, account, passwd):
        self.account = account
        self.password = passwd
        self.sp = ServerProxy("https://api.smugmug.com/services/api/xmlrpc/1.2.1/")
        self.categories = None
        self.subcategories = None
        self.login()

    def __del__(self):
        self.logout()

    def login(self):
        rc = self.sp.smugmug.login.withPassword(self.account, self.password, key)
        self.session = rc["Session"]["id"]

    def logout(self):
        self.sp.smugmug.logout(self.session)

    def _set_property(self, props, name, opt):
        if opt != None:
            props[name] = opt

    def create_album(self, name, opts):
        properties = {}

        if opts != None:
            if not opts.category or opts.category == '0':
                category = 0
            else:
                category = self.get_category(opts.category)
                if opts.subcategory:
                    subcat = self.get_subcategory(category, opts.subcategory)
                    properties["SubCategoryID"] = subcat

            self._set_property(properties, "Description", opts.description)
            self._set_property(properties, "Keywords", opts.keywords)
            self._set_property(properties, "Password", opts.gallery_password)
            self._set_property(properties, "Public", opts.public)
            self._set_property(properties, "Filenames", opts.show_filenames)
            self._set_property(properties, "Comments", opts.comments_allowed)
            self._set_property(properties, "External", opts.external_links_allowed)
            self._set_property(properties, "EXIF", opts.show_camera_info)
            self._set_property(properties, "Share", opts.easy_sharing_allowed)
            self._set_property(properties, "Printable", opts.print_ordering_allowed)
            self._set_property(properties, "Originals", opts.originals_allowed)
            self._set_property(properties, "CommunityID", opts.community)

        rsp = self.sp.smugmug.albums.create(self.session, name, category, properties)
        return rsp['Album']['id']

    def get_categories(self):
        categories = self.sp.smugmug.categories.get(self.session)
        self.categories = {}
        for category in categories['Categories']:
            self.categories[category['Name']] = category['id']

    def get_category(self, category_string):
        if re.match("\d+$", category_string):
            return string.atoi(category_string)
        if not self.categories:
            self.get_categories()

        if not self.categories.has_key(category_string):
            error("Unknown category " + category_string)
        else:
            return self.categories[category_string]

    def get_subcategory(self, category, subcategory_string):
        if re.match("\d+$", subcategory_string):
            return string.atoi(subcategory_string)
        if not self.subcategories:
            self.subcategories = {}
        if not self.subcategories.has_key(category):
            subcategories = self.sp.smugmug.subcategories.get(self.session, category)
            subcategory_map = {}
            for subcategory in subcategories:
                subcategory_map[subcategory['Title']] = subcategory['SubCategoryID']
            self.subcategories[category] = subcategory_map

        if not self.subcategories[category].has_key(subcategory_string):
            error("Unknown subcategory " + subcategory_string)
        else:
            return self.subcategories[category][subcategory_string]

    def upload_files(self, albumid, opts, args, local_information=None):
        from time import time
        from os import stat
        from string import atoi

        max_size = atoi(opts.max_size)

        total_size = 0
        sizes = {}
        files = []
        for file in args:
            if not path.isfile(file):
                message(opts,"%s is not a file.  Not uploading.\n" % file)
                continue
            size = stat(file).st_size
            if size > max_size:
                message(opts, "%s size %d greater than %d.  Not uploading\n" %
                    (file, size, max_size))
            else:
                files.append(file)
                sizes[file] = size
                total_size += size

        t = time()
        total_xfered_bytes = 0

        for file in files:
            t0 = time()
            message(opts, file + "...")
            self.upload_file(albumid, file, caption(file, False))
            t1 = time()
            if local_information:
                local_information.file_uploaded(file)
            seconds = t1 - t0
            try:
                bytes_per_second = sizes[file] / seconds
                total_xfered_bytes += sizes[file]
                estimated_remaining_seconds = \
                    (total_size - total_xfered_bytes) / bytes_per_second
                message(opts, "[OK] %d bytes %d seconds %dKB/sec ETA %s\n" % (
                    sizes[file],
                    seconds,
                    bytes_per_second / 1000,
                    minutes_seconds(estimated_remaining_seconds)))
            except:
                pass

        total_seconds = time() - t
        try:
            message(opts, "%s %d bytes %dKB/sec\n" % (
                minutes_seconds(total_seconds),
                total_size,
                (total_size / total_seconds) / 1000))
        except:
            pass

    # List all the images in the given album
    def list_files(self, albumid, opts, args):
        # Get IDs in album
        resp = self.sp.smugmug.images.get(self.session, albumid)
        imageIDs = resp['Images']

        for imgHandle in imageIDs:
            imgID = imgHandle['id']
            imgKey = imgHandle['Key']
            resp = self.sp.smugmug.images.getInfo(self.session, imgID, imgKey)
            img = resp['Image']
            message(opts, "%d: %s (%d x %d):%s\n" %
                (imgID, img['FileName'], img['Width'], img['Height'],
                 img['Caption']))

    # List all the albums/galleries the current user has
    def list_galleries(self, opts, arg):
        # Get IDs in album
        resp = self.sp.smugmug.albums.get(self.session)
        albums = resp['Albums']

        for alb in albums:
            message(opts, "%9d: %s\n" % (alb['id'], alb['Title']))

    def upload_file(self, albumid, filename, caption=None):
        fields = []
        data = filename_get_data(filename)
        fields.append(['ByteCount', str(len(data))])
        #fields.append(['MD5Sum', md5.new(data).hexdigest()])
        fields.append(['MD5Sum', hashlib.md5(data).hexdigest()])
        fields.append(['AlbumID', str(albumid)])
        fields.append(['SessionID', self.session])
        fields.append(['ResponseType', 'XML-RPC'])
        if caption:
            fields.append(['Caption', caption])

        file = ['Image', filename, data]
        self.post_multipart("upload.smugmug.com", "/photos/xmladd.mg", fields, [file])
    def post_multipart(self, host, selector, fields, files):
        """
        Post fields and files to an http host as multipart/form-data. fields is a
        sequence of (name, value) elements for regular form fields. files is a
        sequence of (name, filename, value) elements for data to be uploaded as
        files. Returns the server's response page.
        """
        content_type, body = self.encode_multipart_formdata(fields, files)
        h = httplib.HTTP(host)
        h.putrequest('POST', selector)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.endheaders()
        h.send(body)
        errcode, errmsg, headers = h.getreply()
        result = h.file.read()
        h.close()
        return result

    def encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
        uploaded as files Return (content_type, body) ready for httplib.HTTP
        instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"'
                             % (key, filename))
            L.append('Content-Type: %s' % get_content_type(filename))
            L.append("content-length: %d" % (len(value)))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
