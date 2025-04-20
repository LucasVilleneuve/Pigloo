from configparser import ConfigParser
import os

config = ConfigParser(os.environ)
config.read('pigloo.conf')
