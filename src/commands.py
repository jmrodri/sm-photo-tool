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
from sm_photo_tool import Smugmug
from os import environ, path
from config import Config

class CliCommand(object):
    """ common """

    def __init__(self, name="cli", usage=None):
        self.parser = OptionParser(usage)
        self._add_common_options()
        self.name = name

    def _load_defaults_from_rc(self, options):
        config = Config('/etc/sm-photo-tool/sm.conf', '.smugmugrc')
        for (k,v) in config.get_as_dict().items():
            options.__dict__[k] = v

    def _add_common_options(self):
        # add options that apply to ALL of them.
        self.parser.add_option("--login", dest="login", metavar="LOGIN",
                help="login")
        self.parser.add_option("--password", dest="password",
                metavar="PASSWORD", help="password")

    def _add_subcommand_options(self):
        # add options that apply to ALL of them.
        pass

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
        usage = "usage: %prog build [options]"
        CliCommand.__init__(self, "create", usage)

class CreateUploadCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog build [options]"
        CliCommand.__init__(self, "create_upload", usage)

class UpdateCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog build [options]"
        CliCommand.__init__(self, "update", usage)

class FullUpdateCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog build [options]"
        CliCommand.__init__(self, "full_update", usage)

class UploadCommand(CliCommand):
    def __init__(self):
        usage = "usage: %prog build [options]"
        CliCommand.__init__(self, "upload", usage)

class ListCommand(CliCommand):
    """ List commands """

    def __init__(self):
        usage = "usage: %prog build [options]"
        CliCommand.__init__(self, "list", usage)
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
            print("foobar")

    def _validate_options(self):
        if len(self.args) < 3:
            if self.args[1] != "galleries":
                print("ERROR: requires album or galleries")
                sys.exit(1)

        if self.args[1] not in self.valid_options:
            print("ERROR: valid options are %s" % self.valid_options)
            sys.exit(1)

class GalleriesCommand(CliCommand):
    pass
