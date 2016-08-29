package main

import (
	"io/ioutil"
	"os"
	"strconv"
	"testing"
)

func TestGetIntReturnsInt(t *testing.T) {
	c := Config{make(map[string]string)}
	c.SetProperty("age", "30")
	if c.GetInt("age", 0) != 30 {
		t.Error("expected 30")
	}
}

func TestGetIntReturnsDefaultValue(t *testing.T) {
	c := Config{make(map[string]string)}
	c.SetProperty("age", "30")
	if c.GetInt("number", 0) != 0 {
		t.Error("expected 0")
	}
}

func TestHandlesTypeMismatch(t *testing.T) {
	c := Config{make(map[string]string)}
	c.SetProperty("age", "u")
	if c.GetInt("age", 0) != 0 {
		t.Error("expected 0")
	}
}

func TestGetProperty(t *testing.T) {
	c := Config{make(map[string]string)}
	c.SetProperty("name", "joe")
	if c.GetProperty("name", "buck") != "joe" {
		t.Error("expected joe")
	}
}

func TestGetPropReturnsDefault(t *testing.T) {
	c := Config{make(map[string]string)}
	if c.GetProperty("last", "buck") != "buck" {
		t.Error("expected buck")
	}
}

func TestGetBool(t *testing.T) {
	c := Config{make(map[string]string)}
	c.SetProperty("lowercasetrue", "true")
	c.SetProperty("yes", "y")
	c.SetProperty("fullyes", "yes")
	c.SetProperty("no", "n")
	c.SetProperty("initialcap", "True")
	c.SetProperty("allcaps", "TRUE")
	c.SetProperty("one", "1")
	c.SetProperty("zero", "0")
	c.SetProperty("justt", "t")
	c.SetProperty("justf", "f")

	verifyBool(c, "lowercasetrue", true, t)
	verifyBool(c, "yes", false, t)
	verifyBool(c, "fullyes", false, t)
	verifyBool(c, "initialcap", true, t)
	verifyBool(c, "allcaps", true, t)
	verifyBool(c, "one", true, t)
	verifyBool(c, "zero", false, t)
	verifyBool(c, "no", false, t)
	verifyBool(c, "justt", true, t)
	verifyBool(c, "justf", false, t)
}

func verifyBool(c Config, property string, expected bool, t *testing.T) {

	if c.GetBool(property, false) != expected {
		t.Error(property + " expected " + strconv.FormatBool(expected))
	}
}

func TestReadFile(t *testing.T) {
	tmpdir := os.TempDir()
	conffile, _ := ioutil.TempFile(tmpdir, "smugmug_test_config")
	ioutil.WriteFile(conffile.Name(), []byte("login=username\npublic=False\noriginals_allowed=True\n#comment\n"), os.FileMode(644))
	config := New(conffile.Name(), "")
	if config.GetProperty("login", "") != "username" {
		t.Error("expected username")
	}
	if config.GetBool("public", true) {
		t.Error("expected false")
	}
}
