package main

import (
	"bufio"
	"log"
	"os"
	"strconv"
	"strings"
)

type Config struct {
	config map[string]string
}

func New(global_conf string, local_conf string) (c *Config) {
	return &Config{make(map[string]string)}
}

func (c *Config) readfile(configfn string) {
	if _, err := os.Stat(configfn); err == nil {
		// configfn exists
		file, err := os.Open(configfn)
		if err != nil {
			log.Fatal(err)
		}

		defer file.Close()

		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			rawline := scanner.Text()
			line := strings.TrimSpace(rawline)
			if len(line) == 0 {
				break
			}
			if strings.HasPrefix(line, "#") {
				continue
			}
			pairs := strings.Split(line, "=")
			c.config[pairs[0]] = pairs[1]
		}
	}
}

func (c *Config) GetInt(prop string, defval int) int {
	if i, err := strconv.Atoi(c.config[prop]); err == nil {
		return i
	}
	return defval
}

func (c *Config) GetProperty(prop string, defval string) string {
	return c.config[prop]
}

func (c *Config) SetProperty(name string, value string) {
	c.config[name] = value
}

func (c *Config) GetAsMap() map[string]string {
	return c.config
}
