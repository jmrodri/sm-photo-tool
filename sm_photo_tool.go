/*
 * sm_photo_tool.go - update and create smugmug galleries from the
 *                    command line
 *
 * Copyright (C) 2016 Jesus M. Rodriguez
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

package main

import (
	"fmt"
	"os"

	"github.com/pborman/getopt"
)

func usage() {
	fmt.Println("\nUsage: PROG MODULENAME [options] --help")
	fmt.Println("Supported modules:")
	commands := GetCommands()
	for k, v := range commands {
		fmt.Printf("\t%-14s %-25s\n", k, v.GetShortDesc())
	}
}

func main() {
	getopt.Parse()
	args := getopt.Args()

	if len(args) < 2 {
		usage()
		os.Exit(1)
	}

	fmt.Println("Getting command")
	cmd := GetCommands()[args[1]]
	cmd.Go(args)
	fmt.Println("Did doCommand get called?")
}
