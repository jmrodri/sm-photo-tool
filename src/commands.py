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

class CliCommand(object):
    """ common """

    def __init__(self, usage=None):
        self.parser = OptionParser(usage)
        self._add_common_options()

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
        pass

    def main(self):
        (self.options, args) = self.parser.parse_args()

        self._validate_options()

        if len(sys.argv) < 2:
            print parser.error("Please enter at least 2 args")

        self._do_command()


class CreateCommand(CliCommand):
    pass

class CreateUploadCommand(CliCommand):
    pass

class UpdateCommand(CliCommand):
    pass

class FullUpdateCommand(CliCommand):
    pass

class UploadCommand(CliCommand):
    pass

class ListCommand(CliCommand):
    """ List commands """

    def __init__(self):
        usage = "usage: %prog build [options]"
        CliCommand.__init__(self, usage)

        # add the list options here

    def _do_command(self):
        # do the list work
        print("list")

    def get_name(self):
        return "list"

class GalleriesCommand(CliCommand):
    pass
