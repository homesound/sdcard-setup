import os,sys,argparse

from common import run
import hashid

def chroot(config):
	# First, we copy qemu-arm-static
	ret, stdout, stderr = run('sudo cp /usr/bin/qemu-arm-static {}/usr/bin'.format(config['bindfs-path']))
	if ret != 0:
		raise Exception('''Failed to copy qemu-arm-static binary: {}'''.format(stderr))

	# Now, we move ld.so.preload
	path = os.path.join(config['bindfs-path'], 'etc', 'ld.so.preload')
	if os.path.exists(path):
		ret, stdout, stderr = run('sudo mv {} {}.bk'.format(path, path))
		if ret != 0:
			raise Exception('''Failed to move ld.so.preload: {}'''.format(stderr))

	script_name = config.get('name', 'chroot-{}'.format(hashid.hashid()))

	path = os.path.join(config['bindfs-path'], 'usr', 'local', 'bin', script_name)
	with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, 0o774), 'w') as f:
		f.write('#!/bin/bash\n')
		for line in config['commands']:
			f.write(line + '\n')

	#pwd = os.getcwd()
	#os.chdir(config['path'])
	ret, stdout, stderr = run('sudo chroot {} bin/bash -c "/usr/local/bin/{}"'.format(config['path'], script_name))
	# Regardless of error, first change back the current working directory
	#os.chdir(pwd)

	if ret != 0:
		raise Exception('''Failed to execute chroot script '{}': {}'''.format(path, stderr))
	os.remove(path)
