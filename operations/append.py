import os,sys,argparse
import re

def append(config):
	with open(config['target'], 'r') as f:
		data = f.read()
	if config.get('before', None):
		# We need to add the lines *before* a string
		before_pattern = (config['before'])
		res = re.findall(before_pattern, data)
		if len(res) == 0:
			print '''Did not find pattern '{}'in '{}' '''.format(before_pattern.pattern, config['target'])
		else:
			m = re.finditer(before_pattern, data).next()
			idx = m.start()
			new_data = '\n'.join(['\n'] + config['data'] + ['\n'])
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

