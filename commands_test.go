package main

import (
	"testing"

	"github.com/pborman/getopt"
)

func TestBulidCommand(t *testing.T) {

	testBuildCommand("create", t)
	testBuildCommand("update", t)
	testBuildCommand("full_update", t)
	testBuildCommand("upload", t)
	testBuildCommand("list", t)
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
