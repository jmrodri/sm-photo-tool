package main

import "testing"

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
