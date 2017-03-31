import os,sys,argparse


def append(config):
	with open(config['target'], 'r') as f:
		data = f.read()
	if config.get('before', None):
		# We need to add the lines *before* a string
		before_str = config['before']
		if before_str not in data:
			print '''Did not find string '{}'in '{}' '''.format(before_str, config['target'])
		else:
			idx = data.index(before_str)
			new_data = '\n'.join(['\n'] + config['data'])
			data = data[:idx] + new_data + data[idx:]

		with open(config['target'], 'wb') as f:
			f.write(data)
		return

	with open(config['target'], 'a') as f:
		lines = []
		for line in config['data']:
			if line != '' and not line in data:
				lines.append(line)
		if len(lines) > 0:
			lines.insert(0, '\n')
			f.write('\n'.join(lines))

