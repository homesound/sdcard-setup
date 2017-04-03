import os,sys,argparse

from common import run

def mount_pseudo(rootdir):
	ret, stdout, stderr = run('sudo mount --bind /dev {}/dev'.format(rootdir))
	if ret != 0:
		raise Exception('Failed to mount dev: {}'.format(stderr))

	ret, stdout, stderr = run('sudo mount --bind /proc {}/proc'.format(rootdir))
	if ret != 0:
		raise Exception('Failed to mount proc: {}'.format(stderr))

	ret, stdout, stderr = run('sudo mount --bind /sys {}/sys'.format(rootdir))
	if ret != 0:
		raise Exception('Failed to mount sys: {}'.format(stderr))

	ret, stdout, stderr = run('sudo mount --bind /dev/pts {}/dev/pts'.format(rootdir))
	if ret != 0:
		raise Exception('Failed to mount /dev/pts: {}'.format(stderr))

def unmount_pseudo(rootdir, fail_on_error=True):
	ret, stdout, stderr = run('sudo umount {}/dev/pts'.format(rootdir))
	if ret != 0 and fail_on_error:
		raise Exception('Failed to unmount /dev/pts: {}'.format(stderr))

	ret, stdout, stderr = run('sudo umount {}/dev'.format(rootdir))
	if ret != 0 and fail_on_error:
		raise Exception('Failed to unmount dev: {}'.format(stderr))

	ret, stdout, stderr = run('sudo umount {}/proc'.format(rootdir))
	if ret != 0 and fail_on_error:
		raise Exception('Failed to unmount proc: {}'.format(stderr))

	ret, stdout, stderr = run('sudo umount {}/sys'.format(rootdir))
	if ret != 0 and fail_on_error:
		raise Exception('Failed to unmount sys: {}'.format(stderr))


def mount(config, image):
	#sudo /sbin/losetup -o $((8192*512)) /dev/loop0 $1
	#sudo mount /dev/loop0 /mnt

	if config.get('losetup', None):
		losetup = config['losetup']
		ret, stdout, stderr = run('sudo /sbin/losetup -o {} {} {}'.format(losetup['offset'], losetup['dev'], image))
		if ret != 0:
			raise Exception('Failed to run losetup: {}'.format(stderr))
	input = config.get('losetup', {}).get('dev', None) or image
	ret, stdout, stderr = run('sudo mount {} {}'.format(input, config['mountpoint']))
	if ret != 0:
		raise Exception('Failed to run mount: {}'.format(stderr))
	if config.get('pseudofs', False):
		mount_pseudo(config['mountpoint'])

#	if config.get('chown', None):
#		ret, stdout, stderr = run('sudo chown {} {}'.format(config['chown'], config['mountpoint']))
#		if ret != 0:
#			raise Exception('Failed to run chown: {}'.format(stderr))
	if config.get('bindfs', None):
		bindfs = config['bindfs']
		if not os.path.exists(bindfs['mountpoint']):
			if bindfs['create']:
				ret, stdout, stderr = run('sudo mkdir -p {}'.format(bindfs['mountpoint']))
				if ret != 0:
					raise Exception('''Failed to create bindfs mountpoint: {}'''.format(stderr))
			else:
				raise Exception('Cannot run bindfs with non-existent mountpoint. Try again with create: true')

		cmd = 'sudo bindfs -u $(id -u {}) -g $(id -u {}) {} {}'.format(bindfs['user'], bindfs['group'], config['mountpoint'], bindfs['mountpoint'])
		ret, stdout, stderr = run(cmd)
		if ret != 0:
			raise Exception('''Failed to run '{}': {}'''.format(cmd, stderr))

		if config.get('pseudofs', False):
			mount_pseudo(config['bindfs']['mountpoint'])




def unmount(config, fail_on_error=True):
	if config.get('cleanup', True) is False:
		# Config tells us not to clean up
		return

	if config.get('pseudofs', False):
		unmount_pseudo(config['mountpoint'], fail_on_error)

	if config.get('bindfs', None):
		if config.get('pseudofs', False):
			unmount_pseudo(config['bindfs']['mountpoint'], fail_on_error)

		ret, stdout, stderr = run('sudo umount {}'.format(config['bindfs']['mountpoint']))
		if ret != 0 and fail_on_error:
			raise Exception('Failed to run umount: {}'.format(stderr))

	ret, stdout, stderr = run('sudo umount {}'.format(config['mountpoint']))
	if ret != 0 and fail_on_error:
		raise Exception('Failed to run umount: {}'.format(stderr))

	if config.get('losetup', None):
		ret, stdout, stderr = run('sudo losetup -d {}'.format(config['losetup']['dev']))
		if ret != 0 and fail_on_error:
			raise Exception('Failed to run losetup -d: {}'.format(stderr))



