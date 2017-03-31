import os,sys,argparse
import subprocess
import time

def run(cmd, stdout=None, stderr=None):
	print '${}'.format(cmd)
	p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, shell=True)
	p.wait()
	stdout, stderr = p.communicate()
	time.sleep(0.1)
	return p.returncode, stdout, stderr
