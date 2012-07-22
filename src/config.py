import errno
import os
import stat
import time


class Config:
    def __init__(self, global_conf, local_conf):
        self._config = {}

        # read global config
        self._readfile(global_conf)

        # read local overrides
        homedir = os.environ.get('HOME')
        if homedir is not None and local_conf is not None:
            l_config = os.path.join(homedir, local_conf)
            self._readfile(l_config)

    def __setitem__(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return self._config[key]

    def __str__(self):
        return str(self._config)

    def _readfile(self, config):
        if os.path.isfile(config):
            f = open(config, "r")
            while f:
                rawline = f.readline()
                line = rawline.strip()
                if len(line) == 0:
                    break
                if line[0] == "#":
                    # ignore comment lines
                    continue
                pairs = line.split('=')
                self._config[pairs[0]] = pairs[1]

    def get_int(self, property, default=0):
        return int(self.get_property(property, default))

    def get_property(self, property, default=None):
        return self._config.get(property, default)

    def set_property(self, name, value):
        self.__setitem__(name, value)

    def get_as_dict(self):
        return self._config
