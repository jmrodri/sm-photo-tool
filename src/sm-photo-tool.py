#!/usr/bin/env python

# smugmug - update and create smugmug galleries from the command line
# Use smugmug --help for more info
# 
# Copyright (C) 2004 John C. Ruttenberg
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# A copy of the GNU General Public License should be included at the bottom of
# this program text; if not, write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA 02111-1307 USA

from sys import version_info, stderr, exit
if not (version_info[0] >= 2 and version_info[1] >= 3):
  stderr.write("Requires python 2.3 or more recent.  You have python %d.%d.\n"
               % (version_info[0], version_info[1]))
  stderr.write("Consider upgrading.  See http://www.python.org\n")
  exit(1)

from optparse import OptionParser, OptionGroup
import string
import re
from xmlrpclib import *
import httplib, mimetypes
import os
from os import path

version = "1.10"

# Changes:
#   1.10 Small bug fix for Windows (open file with "rb" mode)
#   1.9 Handle corrupt data files, add forced upload option.
#   1.8 Update .JPG and .GIF by default as well
#   1.7 Follow new API documentation.  Create properties work!  Send byte count
#       so incomplete uploads don't get processed.  XXX What about checksums?
#   1.6 Fix bug with listdir
#   1.5 Fix bug with --public and --no-public
#   1.4 Fix bug with boolean options and gallery creation
#   1.3 Document Title feature

def error(string):
  from sys import exit, stderr
  stderr.write(string + "\n")
  exit(1)

def message(opts,string):
  from sys import stderr
  if not opts.quiet:
    stderr.write(string)

def minutes_seconds(seconds):
    if seconds < 60:
        return "%d" % seconds
    else:
        return "%d:%02d" % (seconds / 60, seconds % 60)

def filename_get_line(name):
  f = file(name,"rU")
  l = f.readline()
  f.close()
  return l[:-1]

def filename_get_data(name):
  f = file(name,"rb")
  d = f.read()
  f.close()
  return d

def filename_put_string(filename,string):
  f = file(filename,"w")
  f.write(string)
  f.close()

class LocalInformation:
  def __init__(self,dir):
    self.dir = dir
    self.smdir = path.join(dir,"SMUGMUG_INFO")

  def exists(self):
    return path.isdir(self.smdir) and path.isfile(path.join(self.smdir,"gallery"))

  def create(self,gallery):
    if not path.isdir(self.smdir):
      os.mkdir(self.smdir)
    gallery_file = path.join(self.smdir,"gallery")
    if not path.isfile(gallery_file):
      filename_put_string(gallery_file,"%s\n" % gallery)
    self.created = True

  def gallery_id(self):
    if not self.exists():
      raise "No Localinformation for %s" % (dir)
    l = filename_get_line(path.join(self.smdir,"gallery"))
    return l

  def file_needs_upload(self,filename):
    try:
      if not self.exists():
        return False
      head,tail = path.split(filename)
      infofile = path.join(self.smdir,tail)
      if not path.isfile(infofile):
        return True
      #print "Checking %s... " % (infofile)
      l = filename_get_line(infofile)
      utime_s, size_s, count_s = string.split(l)
      if path.getmtime(filename) > int(utime_s):
        return True
      if os.stat(filename).st_size != int(size_s):
        return True
      return False
    except:
      return True

  def file_uploaded(self,filename):
    from time import time

    head,tail = path.split(filename)
    infofile = path.join(self.smdir,tail)

    if not path.isfile(infofile):
      count = 1
    else:
      l = filename_get_line(infofile)
      try:
        utime_s, size_s, count_s = string.split(l)
        count = int(count_s) + 1
      except:
        count = 1

    filename_put_string(infofile,"%d %d %d\n" % (time(),
                                                 os.stat(filename).st_size,
                                                 count))

  def file_upload_count(self,filename):
    head,tail = path.split(filename)
    infofile = path.join(self.smdir,tail)

    if not path.isfile(infofile):
      return 0
    else:
      l = filename_get_line(infofile)
      utime_s, size_s, count_s = string.split(l)
      return int(count_s)


def caption(filename,opts):
  head,ext = path.splitext(filename)
  capfile = head + ".caption"
  if path.isfile(capfile):
    result = filename_get_data(capfile)
    return f.read()
  if opts.filenames_default_captions:
    head,tail = path.split(head)
    return tail
  return None

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

class Smugmug:
  def __init__(self,account,passwd):
    self.account = account
    self.password = passwd
    self.sp = ServerProxy("https://upload.smugmug.com/xmlrpc/")
    self.api_version = "1.0"
    self.categories = None
    self.subcategories = None
    self.login()

  def __del__(self):
    self.logout()

  def login(self):
    rep = self.sp.loginWithPassword(self.account,self.password,self.api_version)
    self.session = rep['SessionID']

  def logout(self):
    self.sp.logout(self.session)

  def create_album(self,name,opts):
    properties = {}
    if not opts.category or opts.category == '0':
      category = 0
    else:
      category = self.get_category(opts.category)
      if opts.subcategory:
        properties["SubCategoryID"] = self.get_subcategory(category,
                                                           opts.subcategory)
    if opts.description != None:
      properties["Description"] = opts.description
    if opts.keywords != None:
      properties["Keywords"] = opts.keywords
    if opts.gallery_password != None:
      properties["Password"] = opts.gallery_password
    if opts.public != None:
      properties["Public"] = opts.public
    if opts.show_filenames != None:
      properties["Filenames"] = opts.show_filenames
    if opts.comments_allowed != None:
      properties["Comments"] = opts.comments_allowed
    if opts.external_links_allowed != None:
      properties["External"] = opts.external_links_allowed
    if opts.show_camera_info != None:
      properties["EXIF"] = opts.show_camera_info
    if opts.easy_sharing_allowed != None:
      properties["Share"] = opts.easy_sharing_allowed
    if opts.print_ordering_allowed != None:
      properties["Pritable"] = opts.print_ordering_allowed
    if opts.originals_allowed != None:
      properties["Originals"] = opts.originals_allowed
    if opts.community != None:
      properties["CommunityID"] = opts.community

    if opts.test:
      return 0
    else:
      return self.sp.createAlbum(self.session,name,category,properties)

  def get_categories(self):
    categories = self.sp.getCategories(self.session)
    self.categories = {}
    for category in categories:
      self.categories[category['Title']] = category['CategoryID']

  def get_category(self,category_string):
    if re.match("\d+$",category_string):
      return string.atoi(category_string)
    if not self.categories:
      self.get_categories()

    if not self.categories.has_key(category_string):
      error("Unknown category " + category_string)
    else:
      return self.categories[category_string]

  def get_subcategory(self,category,subcategory_string):
    if re.match("\d+$",subcategory_string):
      return string.atoi(subcategory_string)
    if not self.subcategories:
      self.subcategories = {}
    if not self.subcategories.has_key(category):
      subcategories = self.sp.getSubCategories(self.session,category)
      subcategory_map = {}
      for subcategory in subcategories:
        subcategory_map[subcategory['Title']] = subcategory['SubCategoryID']
      self.subcategories[category] = subcategory_map

    if not self.subcategories[category].has_key(subcategory_string):
      error("Unknown subcategory " + subcategory_string)
    else:
      return self.subcategories[category][subcategory_string]

  def upload_files(self,albumid,opts,args,local_information=None):
    from time import time
    from os import stat
    from string import atoi

    max_size = atoi(opts.max_size)

    total_size = 0
    sizes = {}
    files = []
    for file in args:
      if not path.isfile(file):
        message(opts,"%s not a file.  Not uploading\n")
        continue
      size = stat(file).st_size
      if size > max_size:
        message(opts,"%s size %d greater than %d.  Not uploading\n" %
                (file,size,max_size))
      else:
        files.append(file)
        sizes[file] = size
        total_size += size

    t = time()
    total_xfered_bytes = 0

    for file in files:
      t0 = time()
      message(opts,file + "...")
      if not opts.test:
        self.upload_file(albumid,file,caption(file,opts))
      t1 = time()
      if local_information:
        local_information.file_uploaded(file)
      seconds = t1 - t0
      try:
        bytes_per_second = sizes[file] / seconds
        total_xfered_bytes += sizes[file]
        estimated_remaining_seconds = \
                                    (total_size - total_xfered_bytes) / bytes_per_second
        message(opts,"[OK] %d bytes %d seconds %dKB/sec ETA %s\n" % (
          sizes[file],
          seconds,
          bytes_per_second / 1000,
          minutes_seconds(estimated_remaining_seconds)))
      except:
        pass      

    total_seconds = time() - t
    try:
      message(opts,"%s %d bytes %dKB/sec\n" % (
        minutes_seconds(total_seconds),
        total_size,
        (total_size / total_seconds) / 1000))
    except:
      pass

  def upload_file(self,albumid,filename,caption=None):
    fields = []
    fields.append(['AlbumID',albumid])
    fields.append(['SessionID',self.session])
    if caption:
      fields.append(['Caption',caption])

    data = filename_get_data(filename)
    fields.append(['ByteCount',str(len(data))])

    file = ['Image',filename,data]
    self.post_multipart("upload.smugmug.com","/photos/xmladd.mg",fields,[file])

  def post_multipart(self,host,selector,fields,files):
    """
    Post fields and files to an http host as multipart/form-data.  fields is a
    sequence of (name, value) elements for regular form fields.  files is a
    sequence of (name, filename, value) elements for data to be uploaded as
    files Return the server's response page.
    """
    content_type, body = self.encode_multipart_formdata(fields,files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    #print errcode
    #print errmsg
    #print headers
    result = h.file.read()
    #print result
    h.close()
    return result

  def encode_multipart_formdata(self,fields,files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files Return (content_type, body) ready for httplib.HTTP
    instance
    """
    #print fields
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


def defaults_from_rc():
  from os import environ, path

  result = {}
  rcfile = path.join(environ['HOME'],'.smugmugrc')
  if not path.isfile(rcfile):
    return result
  f = file(rcfile,"rU")
  try:
    option = None
    for lwithnl in f:
      l = lwithnl[:-1]
      if l[-1] != "\\":
        has_continuation = False
      else:
        has_continuation = True
        l = l[:-1]
      if option:
        value += l
      else:
        colon_index = string.find(l,":")
        if colon_index != -1:
          option = l[0:colon_index]
          value = l[colon_index+1:]
      if not has_continuation and option:
        result[string.strip(option)] = string.strip(value)
        option = None
  finally:
    f.close()
    return result

def to_bool(str):
  str = string.lower(str)
  if str == "true" or str == 'yes':
    return True
  elif str == 'false' or str == 'no':
    return False
  else:
    raise 'text bool conversation'


class Options:
  def __init__(self,argv):
    self.rcfile_options = defaults_from_rc()
    self.short_usage = \
      "sm-photo-tool create gallery_name [options] [file...]\n" \
      "       sm-photo-tool create_upload gallery_name [options] [file...]\n" \
      "       sm-photo-tool update [options]\n" \
      "       sm-photo-tool full_update [options]\n" \
      "       sm-photo-tool upload gallery_id [options] file...\n"
    self.parser = OptionParser(
      self.short_usage +
      "\n"
      "Create smugmug galleries and upload to them.  Mirror directory trees \n"
      "on smugmug and keep up to date.\n"
      "\n"
      "sm-photo-tool create gallery_name -- creates a new gallery and uploads the \n"
      "given files to it.\n"
      "\n"
      "sm-photo-tool create_upload gallery_name -- creates a new gallery and uploads the \n"
      "  given files to it, ignoring any previous upload state.  Use this if you\n"
      "  Want to do a 1-time upload to a new gallery without messing up future updates.\n"
      "\n"
      "sm-photo-tool update -- Updates the smugmug gallery associated with the \n"
      "working directory with any images that are either new or modified since\n"
      "creation or the last update\n"
      "\n"
      "sm-photo-tool full_update [options] -- Mirror an entire directory tree on \n"
      "smugmug.  The current working directory and all it's subdirectories are \n"
      "examined for image suitable image files.  Directories already \n"
      "corresponding to smugmug galleries, an update is performed.  Directories \n"
      "not already known to be created on smugmug, are created there and all \n"
      "the appropriate image files are uploaded.  The new gallery is named with \n"
      "the corresponding directory's relative path to the working directory where \n"
      "the command was invoked.  This can be overridden with a file named Title in the \n"
      "relevant directory.  If this exists, it's contents are used to name the new \n"
      "gallery.\n"
      "\n"
      "sm-photo-tool upload -- Simply upload the listed files to the smugmug \n"
      "gallery with the given gallery_id.  Unlike the above command, does not \n"
      "require or update any local information.\n"
      "\n\n"
      "sm-photo-tool accepts a number of command line options.  The default for \n"
      "any option can be specified in the a .smugmugrc file in the user's home \n"
      "directory.  The format of lines in that file is:\n"
      "  option_name: default\n"
      "For example:\n"
      "  login: joe@photographer.com\n"
      "  password: hotdog\n"
      "  public: True\n"
      "changes the default so that new galleries are public unless --no-public is \n"
      "given on the command line.  Notice that for boolean options, a default of \n"
      "True, yes, false, or no can be given  for the first given name of the \n"
      "option (the one without the ""no-"" prefix.).  Option values can cover \n"
      "more than one line.  \\ acts as a line continuation character."
      "\n\n"
      "Captions for specific images can be specified by files.  Suppose that \n"
      "xxxx.jpg is to be uploaded and that xxxx.caption exists in the same \n"
      "directory.  Then the contents of this file will be used to caption \n"
      "xxxx.jpg when it is uploaded")
      
    group = OptionGroup(self.parser,
                        "Common options",
                        "These apply to all functions")
    self.add_string_option(group,'login',help="REQUIRED")
    self.add_string_option(group,"password",help="REQUIRED")
    self.add_bool_option(group,"quiet",help="Don't tell us what you are doing")
    self.add_bool_option(group,"test",
                         help="Don't actually create galleries or upload files.")
    self.parser.add_option_group(group)

    group = OptionGroup(self.parser,
                        "Create options",
                        "Only relevant when albums are created")
    self.add_string_option(group,"category")
    self.add_string_option(group,"subcategory")
    self.add_string_option(group,"description")
    self.add_string_option(group,"keywords")
    self.add_string_option(group,"gallery_password")
    self.add_bool_option(group,"public")
    self.add_bool_option(group,"show_filenames")
    self.add_bool_option(group,"comments_allowed",default=True)
    self.add_bool_option(group,"external_links_allowed",default=True)
    self.add_bool_option(group,"show_camera_info",default=True)
    self.add_bool_option(group,"easy_sharing_allowed",default=True)
    self.add_bool_option(group,"print_ordering_allowed",default=True)
    self.add_bool_option(group,"originals_allowed")
    self.add_string_option(group,"community")
    self.parser.add_option_group(group)

    group = OptionGroup(self.parser,
                        "Upload options",
                        "Only relevant when files are uploaded")
    self.add_bool_option(group,"filenames_default_captions")
    self.add_string_option(group,"max_size",
                           default="8000000",
                           help="Only upload if file <= this. By default "
                                "8000000 bytes.")
    self.add_string_option(group,"filter_regular_expression",
                           help="Only upload files that match. "
                                "By default, all .jpg and .gif files are "
                                "eligible.",
                           default=".*\\.(jpg|gif|JPG|GIF)")
    self.parser.add_option_group(group)

    self.options, self.args = self.parser.parse_args(argv)
    if not (self.options.login and self.options.password):
      error("No login and/or password.  Both are required")


  def help(self):
    error("Usage: " + self.short_usage +
          "\n       sm-photo-tool --help for complete documentaton\n")

  def add_bool_option(self,x,name,*args,**kwargs):
    try:
      kwargs['default'] = to_bool(self.rcfile_options[name])
    except:
      pass
    if not kwargs.has_key("default"):
      kwargs['default'] = False
    kwargs['help'] = "Default: %s" % (kwargs['default'])
    kwargs['action'] = 'store_true'
    x.add_option('--'+name,*args,**kwargs)
    kwargs['action'] = 'store_false'
    del kwargs['help']
    x.add_option('--no-'+name,*args,**kwargs)

  def add_string_option(self,x,name,*args,**kwargs):
    try:
      kwargs['default'] = self.rcfile_options[name]
    except:
      pass
    x.add_option('--'+name,*args,**kwargs)

def create(smugmug,name,dir,opts):
  album_id = smugmug.create_album(name,opts)
  li = LocalInformation(dir)
  li.create(album_id)

def update_dir(smugmug,dir,opts,files):
  li = LocalInformation(dir)
  
  files_to_upload = []
  for f in files:
    if re.match(opts.filter_regular_expression,f):
      file = path.join(dir,f)
      if li.file_needs_upload(file):
        files_to_upload.append(file)
  if len(files_to_upload) > 0:
    files_to_upload.sort()
    smugmug.upload_files(li.gallery_id(),opts,files_to_upload,
                         local_information=li)


def create_update(name,options):
  opts = options.options
  smugmug = Smugmug(opts.login,opts.password)
  create(smugmug,name,".",opts)
  update_dir(smugmug,".",opts,options.args)
  
def create_upload(name,options):
  opts = options.options
  rest = options.args
  smugmug = Smugmug(opts.login,opts.password)
  album_id = "%d" % smugmug.create_album(name,opts)
  smugmug.upload_files(album_id,opts,rest)

def upload(album_id,options):
  opts = options.options
  rest = options.args
  smugmug = Smugmug(opts.login,opts.password)
  smugmug.upload_files(album_id,opts,rest)

def update(options):
  opts = options.options
  smugmug = Smugmug(opts.login,opts.password)
  update_dir(smugmug,".",opts,os.listdir("."))

def full_update(options):
  opts = options.options
  smugmug = Smugmug(opts.login,opts.password)
  opts = options.options
  for root, dirs, files in os.walk("."):
    try:
      dirs.remove("SMUGMUG_INFO")
    except:
      pass
    li = LocalInformation(root)
    # Look for at least one matching file before making directory
    for file in files:
      if re.match(opts.filter_regular_expression,file):
        if not li.exists():
          title_file = path.join(root,"Title")
          if path.isfile(title_file):
            name = filename_get_line(title_file)
          else:
            name = root[2:] # strip of initial ./ or .\
          create(smugmug,name,root,opts)
        update_dir(smugmug,root,opts,files)
        break

def main():
  from sys import argv, exit

  if len(argv) < 2:
    Options([]).help()
  elif argv[1] == 'create_upload':
    if len(argv) < 3:
      Options([]).help()
    create_upload(argv[2],Options(argv[3:]))
  elif argv[1] == 'create':
    if len(argv) < 3:
      Options([]).help()
    create_update(argv[2],Options(argv[3:]))
  elif argv[1] == 'upload':
    if len(argv) < 3:
      Options([]).help()
    upload(argv[2],Options(argv[3:]))
  elif argv[1] == 'update':
    update(Options(argv[2:]))
  elif argv[1] == 'full_update':
    full_update(Options(argv[2:]))
  elif argv[1] == '--help':
    Options(argv[1:])
  else:
    Options([]).help()

if __name__ == "__main__":
  main()


#		    GNU GENERAL PUBLIC LICENSE
#		       Version 2, June 1991
#
# Copyright (C) 1989, 1991 Free Software Foundation, Inc.
#                       59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
#			    Preamble
#
#   The licenses for most software are designed to take away your
# freedom to share and change it.  By contrast, the GNU General Public
# License is intended to guarantee your freedom to share and change free
# software--to make sure the software is free for all its users.  This
# General Public License applies to most of the Free Software
# Foundation's software and to any other program whose authors commit to
# using it.  (Some other Free Software Foundation software is covered by
# the GNU Library General Public License instead.)  You can apply it to
# your programs, too.
#
#   When we speak of free software, we are referring to freedom, not
# price.  Our General Public Licenses are designed to make sure that you
# have the freedom to distribute copies of free software (and charge for
# this service if you wish), that you receive source code or can get it
# if you want it, that you can change the software or use pieces of it
# in new free programs; and that you know you can do these things.
#
#   To protect your rights, we need to make restrictions that forbid
# anyone to deny you these rights or to ask you to surrender the rights.
# These restrictions translate to certain responsibilities for you if you
# distribute copies of the software, or if you modify it.
#
#   For example, if you distribute copies of such a program, whether
# gratis or for a fee, you must give the recipients all the rights that
# you have.  You must make sure that they, too, receive or can get the
# source code.  And you must show them these terms so they know their
# rights.
#
#   We protect your rights with two steps: (1) copyright the software, and
# (2) offer you this license which gives you legal permission to copy,
# distribute and/or modify the software.
#
#   Also, for each author's protection and ours, we want to make certain
# that everyone understands that there is no warranty for this free
# software.  If the software is modified by someone else and passed on, we
# want its recipients to know that what they have is not the original, so
# that any problems introduced by others will not reflect on the original
# authors' reputations.
#
#   Finally, any free program is threatened constantly by software
# patents.  We wish to avoid the danger that redistributors of a free
# program will individually obtain patent licenses, in effect making the
# program proprietary.  To prevent this, we have made it clear that any
# patent must be licensed for everyone's free use or not licensed at all.
#
#   The precise terms and conditions for copying, distribution and
# modification follow.
#
# 		    GNU GENERAL PUBLIC LICENSE
#    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#   0. This License applies to any program or other work which contains
# a notice placed by the copyright holder saying it may be distributed
# under the terms of this General Public License.  The "Program", below,
# refers to any such program or work, and a "work based on the Program"
# means either the Program or any derivative work under copyright law:
# that is to say, a work containing the Program or a portion of it,
# either verbatim or with modifications and/or translated into another
# language.  (Hereinafter, translation is included without limitation in
# the term "modification".)  Each licensee is addressed as "you".
#
# Activities other than copying, distribution and modification are not
# covered by this License; they are outside its scope.  The act of
# running the Program is not restricted, and the output from the Program
# is covered only if its contents constitute a work based on the
# Program (independent of having been made by running the Program).
# Whether that is true depends on what the Program does.
#
#   1. You may copy and distribute verbatim copies of the Program's
# source code as you receive it, in any medium, provided that you
# conspicuously and appropriately publish on each copy an appropriate
# copyright notice and disclaimer of warranty; keep intact all the
# notices that refer to this License and to the absence of any warranty;
# and give any other recipients of the Program a copy of this License
# along with the Program.
#
# You may charge a fee for the physical act of transferring a copy, and
# you may at your option offer warranty protection in exchange for a fee.
#
#   2. You may modify your copy or copies of the Program or any portion
# of it, thus forming a work based on the Program, and copy and
# distribute such modifications or work under the terms of Section 1
# above, provided that you also meet all of these conditions:
#
#     a) You must cause the modified files to carry prominent notices
#     stating that you changed the files and the date of any change.
#
#     b) You must cause any work that you distribute or publish, that in
#     whole or in part contains or is derived from the Program or any
#     part thereof, to be licensed as a whole at no charge to all third
#     parties under the terms of this License.
#
#     c) If the modified program normally reads commands interactively
#     when run, you must cause it, when started running for such
#     interactive use in the most ordinary way, to print or display an
#     announcement including an appropriate copyright notice and a
#     notice that there is no warranty (or else, saying that you provide
#     a warranty) and that users may redistribute the program under
#     these conditions, and telling the user how to view a copy of this
#     License.  (Exception: if the Program itself is interactive but
#     does not normally print such an announcement, your work based on
#     the Program is not required to print an announcement.)
# 
# These requirements apply to the modified work as a whole.  If
# identifiable sections of that work are not derived from the Program,
# and can be reasonably considered independent and separate works in
# themselves, then this License, and its terms, do not apply to those
# sections when you distribute them as separate works.  But when you
# distribute the same sections as part of a whole which is a work based
# on the Program, the distribution of the whole must be on the terms of
# this License, whose permissions for other licensees extend to the
# entire whole, and thus to each and every part regardless of who wrote it.
#
# Thus, it is not the intent of this section to claim rights or contest
# your rights to work written entirely by you; rather, the intent is to
# exercise the right to control the distribution of derivative or
# collective works based on the Program.
#
# In addition, mere aggregation of another work not based on the Program
# with the Program (or with a work based on the Program) on a volume of
# a storage or distribution medium does not bring the other work under
# the scope of this License.
#
#   3. You may copy and distribute the Program (or a work based on it,
# under Section 2) in object code or executable form under the terms of
# Sections 1 and 2 above provided that you also do one of the following:
#
#     a) Accompany it with the complete corresponding machine-readable
#     source code, which must be distributed under the terms of Sections
#     1 and 2 above on a medium customarily used for software interchange; or,
#
#     b) Accompany it with a written offer, valid for at least three
#     years, to give any third party, for a charge no more than your
#     cost of physically performing source distribution, a complete
#     machine-readable copy of the corresponding source code, to be
#     distributed under the terms of Sections 1 and 2 above on a medium
#     customarily used for software interchange; or,
#
#     c) Accompany it with the information you received as to the offer
#     to distribute corresponding source code.  (This alternative is
#     allowed only for noncommercial distribution and only if you
#     received the program in object code or executable form with such
#     an offer, in accord with Subsection b above.)
#
# The source code for a work means the preferred form of the work for
# making modifications to it.  For an executable work, complete source
# code means all the source code for all modules it contains, plus any
# associated interface definition files, plus the scripts used to
# control compilation and installation of the executable.  However, as a
# special exception, the source code distributed need not include
# anything that is normally distributed (in either source or binary
# form) with the major components (compiler, kernel, and so on) of the
# operating system on which the executable runs, unless that component
# itself accompanies the executable.
#
# If distribution of executable or object code is made by offering
# access to copy from a designated place, then offering equivalent
# access to copy the source code from the same place counts as
# distribution of the source code, even though third parties are not
# compelled to copy the source along with the object code.
# 
#   4. You may not copy, modify, sublicense, or distribute the Program
# except as expressly provided under this License.  Any attempt
# otherwise to copy, modify, sublicense or distribute the Program is
# void, and will automatically terminate your rights under this License.
# However, parties who have received copies, or rights, from you under
# this License will not have their licenses terminated so long as such
# parties remain in full compliance.
#
#   5. You are not required to accept this License, since you have not
# signed it.  However, nothing else grants you permission to modify or
# distribute the Program or its derivative works.  These actions are
# prohibited by law if you do not accept this License.  Therefore, by
# modifying or distributing the Program (or any work based on the
# Program), you indicate your acceptance of this License to do so, and
# all its terms and conditions for copying, distributing or modifying
# the Program or works based on it.
#
#   6. Each time you redistribute the Program (or any work based on the
# Program), the recipient automatically receives a license from the
# original licensor to copy, distribute or modify the Program subject to
# these terms and conditions.  You may not impose any further
# restrictions on the recipients' exercise of the rights granted herein.
# You are not responsible for enforcing compliance by third parties to
# this License.
#
#   7. If, as a consequence of a court judgment or allegation of patent
# infringement or for any other reason (not limited to patent issues),
# conditions are imposed on you (whether by court order, agreement or
# otherwise) that contradict the conditions of this License, they do not
# excuse you from the conditions of this License.  If you cannot
# distribute so as to satisfy simultaneously your obligations under this
# License and any other pertinent obligations, then as a consequence you
# may not distribute the Program at all.  For example, if a patent
# license would not permit royalty-free redistribution of the Program by
# all those who receive copies directly or indirectly through you, then
# the only way you could satisfy both it and this License would be to
# refrain entirely from distribution of the Program.
#
# If any portion of this section is held invalid or unenforceable under
# any particular circumstance, the balance of the section is intended to
# apply and the section as a whole is intended to apply in other
# circumstances.
#
# It is not the purpose of this section to induce you to infringe any
# patents or other property right claims or to contest validity of any
# such claims; this section has the sole purpose of protecting the
# integrity of the free software distribution system, which is
# implemented by public license practices.  Many people have made
# generous contributions to the wide range of software distributed
# through that system in reliance on consistent application of that
# system; it is up to the author/donor to decide if he or she is willing
# to distribute software through any other system and a licensee cannot
# impose that choice.
#
# This section is intended to make thoroughly clear what is believed to
# be a consequence of the rest of this License.
# 
#   8. If the distribution and/or use of the Program is restricted in
# certain countries either by patents or by copyrighted interfaces, the
# original copyright holder who places the Program under this License
# may add an explicit geographical distribution limitation excluding
# those countries, so that distribution is permitted only in or among
# countries not thus excluded.  In such case, this License incorporates
# the limitation as if written in the body of this License.
#
#   9. The Free Software Foundation may publish revised and/or new versions
# of the General Public License from time to time.  Such new versions will
# be similar in spirit to the present version, but may differ in detail to
# address new problems or concerns.
#
# Each version is given a distinguishing version number.  If the Program
# specifies a version number of this License which applies to it and "any
# later version", you have the option of following the terms and conditions
# either of that version or of any later version published by the Free
# Software Foundation.  If the Program does not specify a version number of
# this License, you may choose any version ever published by the Free Software
# Foundation.
#
#   10. If you wish to incorporate parts of the Program into other free
# programs whose distribution conditions are different, write to the author
# to ask for permission.  For software which is copyrighted by the Free
# Software Foundation, write to the Free Software Foundation; we sometimes
# make exceptions for this.  Our decision will be guided by the two goals
# of preserving the free status of all derivatives of our free software and
# of promoting the sharing and reuse of software generally.
#
# 			    NO WARRANTY
#
#   11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
# FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
# OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
# PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
# OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
# TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
# PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
# REPAIR OR CORRECTION.
#
#   12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
# WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
# REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
# INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
# OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
# TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
# YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
# PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGES.
#
# 		     END OF TERMS AND CONDITIONS
#
#  
