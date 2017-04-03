import os,sys,argparse
import json
import yaml
import requests
import pycommons
import hashlib
import time
import subprocess

import mount

from common import run
from setup_sdcard import default_config, setup_parser, parse_config

def main(argv):
	parser = setup_parser()
	args = parser.parse_args(argv[1:])

	config = dict(default_config, **parse_config(args.config))

	for m in config['mounts'][::-1]:
		mount.unmount(m, False)

if __name__ == '__main__':
	main(sys.argv)

