import os,sys,argparse
import subprocess

def script(config):
	for cmd in config['commands']:
		ret, stdout, stderr = run(cmd)
		if ret != 0:
			raise Exception('''Failed to run '{}': {}'''.format(cmd, stderr))

