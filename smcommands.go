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

/*
 Maybe what I should do is create a factory function, given a command, return
 the class that is associated. For example:
*/
func BuildCommand(name string) CLI {
	switch name {
	case "create":
		return NewCreateCommand()
	case "update":
		return NewUpdateCommand()
	case "full_update":
		return NewFullUpdateCommand()
	case "upload":
		return NewUploadCommand()
	case "list":
		return NewListCommand()
	default:
		//return NewListCommand()
		return NewCreateCommand()
	}
}

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

/************************
 * CLI interface
 ************************/
type CLI interface {
	GetName() string
	GetShortDesc() string
	Go([]string)
}

/************************
 * CliCommand
 ************************/
type CliCommand struct {
	name      string
	usage     string
	shortdesc string
	desc      string
}

func (cc *CliCommand) loadDefaultsFromRc() {
	fmt.Println("LOAD DEFAULTS FROM LOCAL CONFIG")
}

func (cc *CliCommand) addCommonOptions() {
	fmt.Println("entered addCommonOptions")
	getopt.StringLong("login", 0, "", "smugmug.com username")
	getopt.StringLong("password", 'p', "", "smugmug.com password")
	getopt.BoolLong("quiet", 'q', "Don't tell us what you are doing")
	getopt.StringLong("log", 0, "", "log file name (will be overwritten)")
	getopt.StringLong("log-level", 0, "critical", "log level (debug/info/warning/error/critical")
}

func (cc *CliCommand) GetName() string {
	return cc.name
}

func (cc *CliCommand) GetShortDesc() string {
	return cc.shortdesc
}

/************************
 * CreateCommand
 ************************/
type CreateCommand struct {
	CliCommand
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

	getopt.StringLong("category", 0, "", "Parent category for album")
	getopt.StringLong("subcategory", 0, "", "Parent category for album")
	getopt.StringLong("description", 0, "", "Gallery description")
	getopt.StringLong("keywords", 0, "", "Gallery description")
	getopt.StringLong("gallery_password", 0, "", "Gallery password")
	getopt.BoolLong("private", 0, "", "make gallery private, [default: public]")
	getopt.BoolLong("showfilenames", 0, "", "show filenames in the gallery, [default: true]")
	getopt.BoolLong("squarethumbs", 0, "", "square thumbs in the gallery,, [default: false]")
	getopt.BoolLong("hideowner", 0, "", "hide ownership, [default: false]")
	getopt.StringLong("sortmethod", 0, "", "define sort method, [default: Position]")
	getopt.BoolLong("no-comments", 0, "", "disallow comments")
	getopt.BoolLong("no-external-links", 0, "", "disallow external links")
	getopt.BoolLong("no-camera-info", 0, "", "do not show camera info")
	getopt.BoolLong("no-easy-sharing", 0, "", "disable easy sharing")
	getopt.BoolLong("no-print-ordering", 0, "", "disable print ordering")
	getopt.BoolLong("no-originals", 0, "", "disable originals")
	getopt.BoolLong("no-world-searchable", 0, "", "disable world searchability")
	getopt.BoolLong("no-smug-searchable", 0, "", "disable smug searchability")
	getopt.StringLong("community", 0, "", "specifies the gallery's community")
	filter_regex_default := ".*\\.(jpg|gif|avi|m4v|mp4|JPG|GIF|AVI|M4V|MP4)"
	getopt.StringLong("filter-regex", 0, filter_regex_default,
		"Only upload files that match. [default: %s]", filter_regex_default)
	getopt.BoolLong("upload", 0, "", "upload images, ignoring previous upload state")
	getopt.IntLong("max_size", 0, 800000000, "Maximum file size (bytes) to upload. [default: 800000000]")

	return &CreateCommand{c}
}

func (cc *CreateCommand) Go(args []string) {
	getopt.CommandLine.Parse(args)
	fmt.Println(args)
	fmt.Println("Running create command")
	fmt.Println(getopt.GetValue("category"))
}

/************************
 * UpdateCommand
 ************************/
type UpdateCommand struct {
	CliCommand
}

func NewUpdateCommand() *UpdateCommand {
	usage := "usage: PROG update [options]"
	shortdesc := "Updates gallery with any new or modified images."
	desc := "Updates the gallery associated with the current " +
		"working directory with any new or modified images."

	c := CliCommand{"update", usage, shortdesc, desc}
	c.addCommonOptions()

	getopt.StringLong("filter-regex", 0,
		".*\\.(jpg|png|gif|avi|m4v|mp4|JPG|PNG|GIF|AVI|M4V|MP4)",
		"Only upload files that match.")

	return &UpdateCommand{c}
}

func (uc *UpdateCommand) doCommand(args []string) {
	fmt.Println("update command called")
}

func (uc *UpdateCommand) Go(args []string) {
	getopt.CommandLine.Parse(args)
	fmt.Println("Running update command")
}

/************************
 * FullUpdateCommand
 ************************/
type FullUpdateCommand struct {
	CliCommand
}

func NewFullUpdateCommand() *FullUpdateCommand {
	usage := "usage: PROG full_update [options]"
	shortdesc := "Mirror an entire directory tree."
	desc := shortdesc + "The current working directory and all its " +
		"subdirectories are examined for suitable image files. " +
		"Directories already corresponding to galleries, an update " +
		"is performed. Directories not already known to be created on " +
		"smugmug, are created there and all the appropriate image " +
		"files are uploaded. The new gallery is named with the " +
		"corresponding directory's relative path to the working " +
		"directory where the command was invoked. This can be " +
		"overridden with a file named Title in the relevant " +
		"directory. If this exists, its contents are used to name " +
		"the new gallery."

	c := CliCommand{"full_update", usage, shortdesc, desc}
	c.addCommonOptions()

	getopt.StringLong("category", 0, "", "Parent category for album")
	getopt.StringLong("subcategory", 0, "", "Parent category for album")
	getopt.StringLong("description", 0, "", "Gallery description")
	getopt.StringLong("keywords", 0, "", "Gallery description")
	getopt.StringLong("gallery_password", 0, "", "Gallery password")
	getopt.BoolLong("private", 0, "", "make gallery private, [default: public]")
	getopt.BoolLong("showfilenames", 0, "", "show filenames in the gallery, [default: true]")
	getopt.BoolLong("squarethumbs", 0, "", "square thumbs in the gallery,, [default: false]")
	getopt.BoolLong("hideowner", 0, "", "hide ownership, [default: false]")
	getopt.StringLong("sortmethod", 0, "", "define sort method, [default: Position]")
	getopt.BoolLong("no-comments", 0, "", "disallow comments")
	getopt.BoolLong("no-external-links", 0, "", "disallow external links")
	getopt.BoolLong("no-camera-info", 0, "", "do not show camera info")
	getopt.BoolLong("no-easy-sharing", 0, "", "disable easy sharing")
	getopt.BoolLong("no-print-ordering", 0, "", "disable print ordering")
	getopt.BoolLong("no-originals", 0, "", "disable originals")
	getopt.BoolLong("no-world-searchable", 0, "", "disable world searchability")
	getopt.BoolLong("no-smug-searchable", 0, "", "disable smug searchability")
	getopt.StringLong("community", 0, "", "specifies the gallery's community")
	filter_regex_default := ".*\\.(jpg|gif|avi|m4v|mp4|JPG|GIF|AVI|M4V|MP4)"
	getopt.StringLong("filter-regex", 0, filter_regex_default,
		"Only upload files that match. [default: %s]", filter_regex_default)
	getopt.BoolLong("upload", 0, "", "upload images, ignoring previous upload state")

	return &FullUpdateCommand{c}
}

func (fc *FullUpdateCommand) doCommand(args []string) {
	fmt.Println("full update command called")
}

func (fc *FullUpdateCommand) Go(args []string) {
	getopt.CommandLine.Parse(args)
	fmt.Println("Running full update command")
}

/************************
 * UploadCommand
 ************************/
type UploadCommand struct {
	CliCommand
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
	getopt.CommandLine.Parse(args)
	fmt.Println("Running upload command")
}

/************************
 * ListCommand
 ************************/
type ListCommand struct {
	CliCommand
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
	getopt.CommandLine.Parse(args)
	fmt.Println("Entered Go")
	lc.validOptions(args)
	lc.doCommand(args)
	fmt.Println("Leaving Go")
}
