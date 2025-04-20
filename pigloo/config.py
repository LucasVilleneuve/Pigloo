import os
from configparser import ConfigParser

config = ConfigParser(os.environ)
config.read("pigloo.conf")
