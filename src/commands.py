# commands.py - commands used to by sm_photo_tool
#
# Copyright (C) 2007-2009 Jesus M. Rodriguez
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

import sys
from optparse import OptionParser
from sm_photo_tool import Smugmug, LocalInformation
from os import environ, path
import os
from config import Config
import re

def _set_option(options, parser, key, value):
    defval = None
    curval = None

    if parser.get_default_values().__dict__.has_key(key):
        defval = parser.get_default_values().__dict__[key]
    if options.__dict__.has_key(key):
        curval = options.__dict__[key]

    if curval == defval:
        options.__dict__[key] = value

class CliCommand(object):
    """ common """

    def __init__(self, name="cli", usage=None, shortdesc=None,
            description=None):

        self.shortdesc = shortdesc
        if shortdesc is not None and description is None:
            description = shortdesc
        self.parser = OptionParser(usage=usage, description=description)
        self._add_common_options()
        self.name = name

    def _load_defaults_from_rc(self, options):
        config = Config('/etc/sm-photo-tool/sm.conf', '.smugmugrc')
        for (k,v) in config.get_as_dict().items():
            # if config overrides an options default value, use it.
            # if the option was passed in use it to override config.
            _set_option(options, self.parser, k, v)

    def _add_common_options(self):
        # add options that apply to ALL of them.
        self.parser.add_option("--login", dest="login", metavar="LOGIN",
                help="smugmug.com username")
        self.parser.add_option("--password", dest="password",
                metavar="PASSWORD", help="smugmug.com password")
        self.parser.add_option("--quiet", dest="quiet",
                action="store_true", help="Don't tell us what you are doing")

    def _validate_options(self):
        pass

    def _do_command(self):
        pass

    def get_name(self):
        return self.name

    def main(self):
        (self.options, self.args) = self.parser.parse_args()

        self._load_defaults_from_rc(self.options)

        self._validate_options()

        if len(sys.argv) < 2:
            print(parser.error("Please enter at least 2 args"))

        # do the work
        self._do_command()

    def _get_defaults(self):
        pass

class CreateCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog create [options] <gallery_name> [files...]"
        CliCommand.__init__(self, "create", usage,
            "creates a new gallery and uploads give files to it.")

        self.parser.add_option("--category", dest="category", metavar="CATEGORY",
                help="Parent category for album")
        self.parser.add_option("--subcategory", dest="subcategory",
                metavar="SUBCATEGORY", help="Parent category for album")
        self.parser.add_option("--description", dest="description",
                metavar="DESCRIPTION", help="Gallery description")
        self.parser.add_option("--keywords", dest="keywords",
                metavar="KEYWORDS", help="Gallery description")
        self.parser.add_option("--gallery_password", dest="gallery_password",
                metavar="GALLERY_PASSWORD", help="Gallery password")
        self.parser.add_option("--private", dest="public",
                action="store_false",
                help="make gallery private, [default: public]")
        self.parser.add_option("--showfilenames", dest="show_filenames",
                action="store_true", 
                help="show filenames in the gallery, [default: %default]")
        self.parser.add_option("--no-comments", dest="comments_allowed",
                action="store_false", 
                help="disallow comments")
        self.parser.add_option("--no-external-links", 
                dest="external_links_allowed", action="store_false",
                help="disallow external links")
        self.parser.add_option("--no-camera-info", dest="show_camera_info",
                action="store_false", 
                help="do not show camera info")
        self.parser.add_option("--no-easy-sharing", dest="easy_sharing_allowed",
                action="store_false",  help="disable easy sharing")
        self.parser.add_option("--no-print-ordering", 
                dest="print_ordering_allowed", action="store_false",
                help="disable print ordering")
        self.parser.add_option("--no-originals", dest="originals_allowed",
                action="store_false",  help="disallow originals")
        self.parser.add_option("--community", dest="community",
                metavar="COMMUNITY", help="specifies the gallery's community")
        self.parser.add_option("--filter-regex",
                dest="filter_regex", metavar="REGEX",
                help="Only upload files that match. [default: %default]")

        self.parser.set_defaults(public=True)
        self.parser.set_defaults(show_filenames=False)
        self.parser.set_defaults(comments_allowed=True)
        self.parser.set_defaults(external_links_allowed=True)
        self.parser.set_defaults(show_camera_info=True)
        self.parser.set_defaults(eash_sharing_allowed=True)
        self.parser.set_defaults(print_ordering_allowed=True)
        self.parser.set_defaults(originals_allowed=True)
        self.parser.set_defaults(filter_regex =".*\\.(jpg|gif|avi|JPG|GIF|AVI)")

    def _process_files(self, local, files):
        files_to_upload = []
        for f in files:
            if re.match(self.options.filter_regex, f):
                file = path.join(local.dir, f)
                if local.file_needs_upload(file):
                    files_to_upload.append(file)
        if len(files_to_upload) > 0:
            files_to_upload.sort()
        return files_to_upload

    def _do_command(self):
        # connect to smugmug.com
        self.smugmug = Smugmug(self.options.login, self.options.password)
        name = self.args[1]
        # TODO: get options to album from CLI
        album_id = self.smugmug.create_album(name, self.options)
        print("[%s] created with id [%s]" % (name, album_id))
        li = LocalInformation(".")
        li.create(album_id)

        # first 2 args are create & album name, the rest will
        # be optional files
        if len(self.args) > 2:
            to_upload = self._process_files(li, self.args[2:])
            if len(to_upload) > 0:
                self.smugmug.upload_files(li.gallery_id(), self.options,
                    to_upload, local_information=li)


    def _validate_options(self):
        if len(self.args) < 2:
            print("ERROR: requires album name")
            sys.exit(1)


class CreateUploadCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog create_upload [options] [files...]"
        shortdesc = "creates a new gallery and uploads the given files."
        desc = "creates a new gallery and uploads the given files to it, " + \
            "ignoring any previous upload state. Use this if you want to " + \
            "do a one-time upload to a new gallery without messing up " + \
            "future updates."
        CliCommand.__init__(self, "create_upload", usage, shortdesc, desc)

class UpdateCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog update [options]"
        shortdesc = "Updates gallery with any new or modified images."
        description = "Updates the gallery associated with the current " + \
            "working directory with any new or modified images."
        CliCommand.__init__(self, "update", usage, shortdesc, description)

        self.parser.add_option("--filter-regex",
                dest="filter_regex", metavar="REGEX",
                help="Only upload files that match. [default: %default]")
        self.parser.set_defaults(filter_regex =".*\\.(jpg|gif|avi|JPG|GIF|AVI)")

    def _process_files(self, local, files):
        files_to_upload = []
        for f in files:
            if re.match(self.options.filter_regex, f):
                file = path.join(local.dir, f)
                if local.file_needs_upload(file):
                    files_to_upload.append(file)
        if len(files_to_upload) > 0:
            files_to_upload.sort()
        return files_to_upload

    def _do_command(self):
        # connect to smugmug.com
        self.smugmug = Smugmug(self.options.login, self.options.password)

        li = LocalInformation(".")
        to_upload = self._process_files(li, os.listdir("."))
        if len(to_upload) > 0:
            self.smugmug.upload_files(li.gallery_id(), self.options,
                to_upload, local_information=li)

class FullUpdateCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog full_update [options]"
        shortdesc = "Mirror an entire directory tree."
        desc = shortdesc + "The current working directory and all its " + \
            "subdirectories are examined for suitable image files. " + \
            "Directories already corresponding to galleries, an update " + \
            "is performed. Directories not already known to be created on " + \
            "smugmug, are created there and all the appropriate image " + \
            "files are uploaded. The new gallery is named with the " + \
            "corresponding directory's relative path to the working " + \
            "directory where the command was invoked. This can be " + \
            "overridden with a file named Title in the relevant directory. " + \
            "If this exists, its contents are used to name the new gallery."
        CliCommand.__init__(self, "full_update", usage, shortdesc, desc)

class UploadCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog upload <gallery_id> [options] <file...>"
        shortdesc = "Upload the given files to the given gallery_id."
        desc = "Simply upload the listed files to the gallery with the " + \
            "given gallery_id. Unlike the above command, does not " + \
            "require or update any local information."
        CliCommand.__init__(self, "upload", usage, shortdesc, desc)

        self.parser.add_option("--max_size", dest="max_size",
                metavar="MAX_SIZE", type="int",
                help="Maximum file size (bytes) to upload. [default: %default]")
        self.parser.add_option("--filenames_default_captions",
                dest="filenames_default_captions",
                action="store_true", 
                help="Filenames should be used as the default caption.")

        self.parser.set_defaults(max_size=800000000)
        self.parser.set_defaults(filenames_default_captions=False)

    def _do_command(self):
        album_id = self.args[1]
        files = self.args[2:]
        # connect to smugmug.com
        self.smugmug = Smugmug(self.options.login, self.options.password)
        self.smugmug.upload_files(album_id, self.options, files)

    def _validate_options(self):
        if len(self.args) < 3:
            print("ERROR: requires album_id and filenames.")
            sys.exit(1)

class ListCommand(CliCommand):
    """ List commands """

    def __init__(self):
        usage = "usage: %prog list <album [albumid] | galleries>"
        desc = "Lists the files in an album, or lists available galleries"
        CliCommand.__init__(self, "list", usage, desc)
        self.valid_options = ["album", "galleries"]

        # add the list options here
        #self.parser.add_option("--album", dest="album", metavar="ALBUM",
        #    help="List the contents of an album")
        #self.parser.add_option("--galleries", dest="gallery", metavar="GALLERY",
        #    help="List the contents of a galleries")

    def _do_command(self):
        # do the list work
        print(self.options)

        # connect to smugmug.com
        self.smugmug = Smugmug(self.options.login, self.options.password)

        cmd = self.args[1]
        if len(self.args) > 2:
            id = self.args[2]

        if cmd == "album":
            self.smugmug.list_files(id, None, None)
        elif cmd == "galleries":
            self.smugmug.list_galleries(None, None)
        else:
            # bail
            sys.exit(1)

    def _validate_options(self):
        if len(self.args) < 3:
            if self.args[1] != "galleries":
                print("ERROR: requires album or galleries")
                sys.exit(1)

        if self.args[1] not in self.valid_options:
            print("ERROR: valid options are %s" % self.valid_options)
            sys.exit(1)
