#!/usr/bin/env python

# sm_photo_tool.py - update and create smugmug galleries from the command line
#
# Run sm_photo_tool --help for more info
# 
# Copyright (C) 2004 John C. Ruttenberg
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
import os

sys.path.insert(0, '.')
sys.path.insert(0, '/usr/share/sm-photo-tool')
sys.path.insert(0, os.path.dirname(sys.argv[0]))

from cli import CLI

if __name__ == "__main__":
    CLI().main()
