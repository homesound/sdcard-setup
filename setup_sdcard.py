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

from operations import append, script, hostname, chroot, expand

default_config_str = '''
download:
  force: false
  name: ''
  unzip: true
  result: result
'''

default_config = yaml.load(default_config_str)

def setup_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('config', type=str, help='Config YAML file')
	return parser

def parse_config(config):
	with open(config, 'rb') as f:
		return yaml.load(f.read())

def download(config):
	assert config.get('url', None), 'No URL specified'

	r = requests.get(config['url'], allow_redirects=True, stream=True)
	url = r.url
	r.close()

	filename = os.path.basename(url)
	name, ext = os.path.splitext(filename)
	dirname = os.path.dirname(url)

	def __download():
		run('aria2c -x 16 {} -o {}'.format(url, config['name']))

	if config['name'] == '':
		config['name'] = filename
	print 'filename={}'.format(filename)
	exists = os.path.exists(config['name'])
	if not exists:
		print 'Downloading {}'.format(url)
		__download()
	elif exists:
		if config['force']:
			print 'Force downloading {}'.format(url)
		else:
			checksum_url = os.path.join(dirname, filename + '.sha1')
			r = requests.get(checksum_url)
			url_checksum = r.text.strip().split(' ')[0]

			sha1 = hashlib.sha1()
			with open(config['name'], 'rb') as f:
				while True:
					data = f.read(4096)
					if not data:
						break
					sha1.update(data)
			file_checksum = sha1.hexdigest()
			if url_checksum != file_checksum:
				print '''Checksums don't match..Downloading ...'''
				__download()
			else:
				print 'Checksums match. Not downloading'

	# Now handle unzip
	if ext == '.zip':
		ret, stdout, stderr = run('zipinfo -1 {}'.format(filename), stdout=subprocess.PIPE)
		unzipped_filename = stdout.strip()
		if not os.path.exists(unzipped_filename) or config['unzip']:
			ret, stdout, stderr = run('unzip {}'.format(filename))
		return unzipped_filename
	else:
		return filename


def main(argv):
	parser = setup_parser()
	args = parser.parse_args(argv[1:])

	config = dict(default_config, **parse_config(args.config))
	print json.dumps(config, indent=2)

	image = download(config['download'])
	config[config['download']['result']] = image

	if config.get('expand', None):
		expand.expand(config['expand'], image)

	for m in config.get('mounts', []):
		mount.mount(m, image)

	for entry in config.get('operations', []):
		if entry['operation'] == 'append':
			append.append(entry)
		elif entry['operation'] == 'hostname':
			hostname.hostname(entry)
		elif entry['operation'] == 'chroot':
			chroot.chroot(entry)

	for m in config.get('mounts', [])[::-1]:
		mount.unmount(m)
if __name__ == '__main__':
	main(sys.argv)
