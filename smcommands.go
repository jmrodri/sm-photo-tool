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

	"github.com/pborman/getopt"
)

//var commands []CLI
var commands map[string]CLI

func GetCommands() map[string]CLI {
	if len(commands) < 1 {
		commands = make(map[string]CLI)
		addCommand(commands, NewUploadCommand())
		addCommand(commands, NewListCommand())
		addCommand(commands, NewCreateCommand())
	}
	return commands
}

func addCommand(c map[string]CLI, cli CLI) {
	c[cli.GetName()] = cli
}

type CLI interface {
	GetName() string
	GetShortDesc() string
	Go([]string)
}

type CliCommand struct {
	name      string
	usage     string
	shortdesc string
	desc      string
}

func (cc *CliCommand) addCommonOptions() {
	getopt.StringLong("login", 'l', "", "smugmug.com username")
	getopt.StringLong("password", 'p', "", "smugmug.com password")
	getopt.BoolLong("quiet", 'q', "Don't tell us what you are doing")
	getopt.StringLong("log", 0, "", "log file name (will be overwritten)")
	getopt.StringLong("log-level", 0, "critical", "log level (debug/info/warning/error/critical")
}

/************************
 * CreateCommand
 ************************/
type CreateCommand struct {
	cli CliCommand
}

func NewCreateCommand() *CreateCommand {
	usage := "usage: PROG create [options] <gallery_name> [files...]"
	shortdesc := "creates a new gallery and uploads the given files."
	desc := "creates a new gallery and uploads the given files to it, " +
		"ignoring any previous upload state.\n" +
		"Use the --upload option if you want to do a one-time upload " +
		"to a new gallery without messing up future updates."
	c := CliCommand{"create", usage, shortdesc, desc}
	c.addCommonOptions()

	return &CreateCommand{c}
}

func (cc *CreateCommand) Go(args []string) {
	fmt.Println("Running create command")
}

func (cc *CreateCommand) GetName() string {
	return cc.cli.name
}

func (cc *CreateCommand) GetShortDesc() string {
	return cc.cli.shortdesc
}

/************************
 * UploadCommand
 ************************/
type UploadCommand struct {
	cli CliCommand
}

func NewUploadCommand() *UploadCommand {
	usage := "usage: PROG upload <gallery_id> [options] <file...>"
	shortdesc := "Upload the given files to the given gallery_id."
	desc := "Simply upload the listed files to the gallery with the " +
		"given gallery_id. Unlike the above command, does not " +
		"require or update any local information."

	c := CliCommand{"upload", usage, shortdesc, desc}
	c.addCommonOptions()

	getopt.IntLong("max_size", 0, 800000000, "Maximum file size (bytes) to upload.")
	getopt.BoolLong("filenames_default_captions", 0,
		"Filenames should be used as the default caption.")

	return &UploadCommand{c}
}

func (uc *UploadCommand) doCommand(args []string) {
	album_id := args[1]
	files := args[2:]
	fmt.Println("upload_files(%d)", album_id)
	fmt.Println(files)
}

func (uc *UploadCommand) validOptions(args []string) {
	if len(args) < 3 {
		fmt.Println("ERROR: requires album_id and filenames.")
		os.Exit(1)
	}
}
func (uc *UploadCommand) Go(args []string) {
	fmt.Println("Running upload command")
}

func (uc *UploadCommand) GetName() string {
	return uc.cli.name
}

func (uc *UploadCommand) GetShortDesc() string {
	return uc.cli.shortdesc
}

/************************
 * ListCommand
 ************************/
type ListCommand struct {
	cli           CliCommand
	valid_options []string
}

func NewListCommand() *ListCommand {
	usage := "usage: PROG list <album [albumid] | galleries>"
	desc := "Lists the files in an ablum, or lists available galleries"
	c := CliCommand{"list", usage, desc, desc}
	c.addCommonOptions()
	return &ListCommand{c, []string{"album", "galleries"}}
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
		oid = args[2]
	}

	fmt.Println("cmd = " + cmd)

	if cmd == "album" {
		fmt.Println("list_files(" + oid + ")")
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

func (lc *ListCommand) GetName() string {
	return lc.cli.name
}

func (lc *ListCommand) GetShortDesc() string {
	return lc.cli.shortdesc
}
