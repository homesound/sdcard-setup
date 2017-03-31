import os,sys,argparse
import hashid

from common import run

def hostname(config):
	prefix = config['prefix']
	gen = config['generator']
	if gen['type'] == 'hashid':
		suffix = hashid.hashid(gen['size'])
	elif gen['type'] == 'randint':
		suffix = '{}'.format(random.randint(gen['min'], gen['max']))
	#elif gen['type'] == 'uuid':

	hostname = prefix + config.get('join', '.') + suffix

	# Now update /etc/hostname
	with open(os.path.join(config['path'], 'etc/hostname'), 'wb') as f:
		f.write(hostname)

	# Now update /etc/hosts
	path = os.path.join(config['path'], 'etc/hosts')
	ret, stdout, stderr = run(r'''sed -i 's/\(127.0.1.1\s\+\).*/\1{}/g' {}'''.format(hostname, path))
	if ret != 0:
		raise Exception('Failed to update /etc/hosts: {}'.format(stderr))
