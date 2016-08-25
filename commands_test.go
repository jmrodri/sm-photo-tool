package main

import (
	"os"
	"os/exec"
	"testing"

	"github.com/pborman/getopt"
)

func aTestBuildCommand(t *testing.T) {

	testBuildCommand("create", t)
	testBuildCommand("update", t)
	testBuildCommand("full_update", t)
	testBuildCommand("upload", t)
	testBuildCommand("list", t)
}

func TestListCommandValidOptions(t *testing.T) {

	switch {
	case os.Getenv("TEST_EXIT") == "less_than_2":
		lcmd := NewListCommand()
		args := []string{"program"}
		lcmd.validOptions(args)
		return
	case os.Getenv("TEST_EXIT") == "album":
		lcmd := NewListCommand()
		args := []string{"program", "album"}
		lcmd.validOptions(args)
		return
	case os.Getenv("TEST_EXIT") == "invalid_option_between":
		lcmd := NewListCommand()
		args := []string{"list", "blah", "blah"}
		lcmd.validOptions(args)
		return
	case os.Getenv("TEST_EXIT") == "invalid_option_outside":
		lcmd := NewListCommand()
		args := []string{"list", "invalid", "blah"}
		lcmd.validOptions(args)
		return
	}

	handleExit("TestListCommandValidOptions", "less_than_2", t)
	handleExit("TestListCommandValidOptions", "album", t)
	handleExit("TestListCommandValidOptions", "invalid_option_between", t)
	handleExit("TestListCommandValidOptions", "invalid_option_outside", t)
}

func handleExit(test string, envvar string, t *testing.T) {
	cmd := exec.Command(os.Args[0], "-test.run="+test)
	cmd.Env = append(os.Environ(), "TEST_EXIT="+envvar)
	err := cmd.Run()
	if e, ok := err.(*exec.ExitError); ok && !e.Success() {
		return
	}
	t.Fatalf("%s ran with err %v, want exit status 1", envvar, err)
}

func testBuildCommand(name string, t *testing.T) {
	cmd := BuildCommand(name)
	if cmd.GetName() != name {
		t.Error("BuildCommand failed to create ListCommand")
	}

	reset()
}

func reset() {
	getopt.CommandLine = getopt.New()
}
