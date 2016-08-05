package main

import "github.com/pborman/getopt"
import "fmt"
import "os"
import "sort"

type ListCommand struct {
	usage         string
	desc          string
	valid_options []string
}

func main() {
	//CLI{}.run()
	optName := getopt.StringLong("name", 'n', "", "Your name")
	optHelp := getopt.BoolLong("help", 0, "Help")

	getopt.Parse()
	args := getopt.Args()

	if *optHelp {
		getopt.Usage()
		os.Exit(0)
	}

	fmt.Println("Hello " + *optName + "!")
	validOptions := []string{"album", "galleries"}
	lcmd := ListCommand{usage: "Usage", desc: "the list command", valid_options: validOptions}
	lcmd.validOptions(args)
	lcmd.doCommand(args)
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

	/*
		in python this is
		if args[1] not in valid_options
	*/
	i := sort.SearchStrings(lc.valid_options, args[1])
	if i < len(lc.valid_options) && lc.valid_options[i] != args[1] {
		fmt.Println("ERROR: valid options are %s", lc.valid_options)
		os.Exit(1)
	}
}

func (lc *ListCommand) doCommand(args []string) {
	var oid string
	cmd := args[0]

	if len(args) > 2 {
		oid = args[1]
	}

	if cmd == "album" {
		fmt.Println("list_files(%s)", oid)
	} else if cmd == "galleries" {
		fmt.Println("list_galleries()")
	} else {
		os.Exit(1)
	}
}
