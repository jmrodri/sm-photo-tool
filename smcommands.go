/*
 * smcommands.go
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
	"sort"
)

type CliCommand struct {
	usage     string
	shortdesc string
	desc      string
	name      string
}

/*
func Init(name string, usage string, shortdesc string, description string) *CliCommand {
	return nil
}*/

func (cc *CliCommand) addCommonOptions() {

}

/************************
 * UploadCommand
 ************************/
type UploadCommand struct {
	usage     string
	shortdesc string
	desc      string
}

/************************
 * ListCommand
 ************************/
type ListCommand struct {
	usage         string
	desc          string
	valid_options []string
}

func NewListCommand() *ListCommand {
	usage := "usage: PROG list <album [albumid] | galleries>"
	desc := "Lists the files in an ablum, or lists available galleries"
	return &ListCommand{usage, desc, []string{"album", "galleries"}}
}

func (lc *ListCommand) validOptions(args []string) {
	if len(args) < 2 {
		fmt.Println(len(args))
		fmt.Println("print help")
		os.Exit(1)
	}

	if len(args) < 3 {
		if args[1] != "galleries" {
			fmt.Println("ERROR: requires album or galleries")
			os.Exit(1)
		}
	}

	// in python this is
	// if args[1] not in valid_options
	i := sort.SearchStrings(lc.valid_options, args[1])
	if i < len(lc.valid_options) && lc.valid_options[i] != args[1] {
		fmt.Println("ERROR: valid options are %s", lc.valid_options)
		os.Exit(1)
	}
	fmt.Println("Leaving validOptions")
}

func (lc *ListCommand) doCommand(args []string) {
	var oid string
	cmd := args[1]

	if len(args) > 2 {
		oid = args[1]
	}

	fmt.Println("cmd = " + cmd)

	if cmd == "album" {
		fmt.Println("list_files(%s)", oid)
	} else if cmd == "galleries" {
		fmt.Println("list_galleries()")
	} else {
		fmt.Println("Um why didn't we call one of the above?")
		os.Exit(1)
	}
}

func (lc *ListCommand) Go(args []string) {
	fmt.Println("Entered Go")
	lc.validOptions(args)
	lc.doCommand(args)
	fmt.Println("Leaving Go")
}
