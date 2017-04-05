import os,sys,argparse
import re

from common import run

def expand(config, image):

	bs = int(config['bs'])
	count = int(config['count'])

	total = bs * count
	unit = config['unit']
	ret, stdout, stderr = run('''dd if=/dev/zero bs={}{} count={} >> {}'''.format(bs, unit, count, image))
	if ret != 0:
		raise Exception('Failed to extend image: {}'.format(stderr))

	# Get new size
	size_pattern = re.compile('Disk .*: (?P<size>(?P<size_num>\d+)..)$')

	ret, stdout, stderr = run('''parted {} print'''.format(image))
	if ret != 0:
		raise Exception('Failed to extend image using parted: {}'.format(stderr))

	for line in stdout.split('\n'):
		m = size_pattern.match(line)
		if m:
			d = m.groupdict()
			ret, stdout, stderr = run('''parted --script {} resizepart {} \{}'''.format(image, config['partition'], d['size']))
			if ret != 0:
				raise Exception('Failed to resize partition using parted: {}'.format(stderr))
			break

	# Find a loop device to use
	for i in range(8):
		loop_device = '/dev/loop{}'.format(i)

		ret, stdout, stderr = run('''sudo losetup -o 70254592 {} {}'''.format(loop_device, image))
		if ret != 0:
			continue
		else:
			ret, stdout, stderr = run('''sudo resize2fs {}'''.format(loop_device))
			if ret != 0:
				raise Exception('Failed to extend image using resize2fs: {}'.format(stderr))
			ret, stdout, stderr = run('''sudo losetup -d {}'''.format(loop_device))
			if ret != 0:
				raise Exception('Failed to delete loopback device')
			break

