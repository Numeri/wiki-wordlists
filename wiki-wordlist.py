#!/bin/python
"""Wiki Wordlists

Usage:
  wiki-wordlists.py <file> [options]
  wiki-wordlists.py -h

Options:
  -h --help                       Show this screen.
  -n <number>, --number <number>  Specify number of words [default: 1000]
  -c <config>, --config <config>  Use config file

"""

import xml.etree.ElementTree as etree
from collections import Counter
import regex
import string
from sys import argv, maxunicode
from os import fstat
import unicodedata
import logging
import json
from docopt import docopt

logging.basicConfig(format='%(message)s')

arguments = docopt(__doc__, version='Wiki Wordlists 0.5')

words_to_output = int(arguments['--number'])
if words_to_output < 1:
	logging.warning('Error: The number of words to output must be more than 0')
	exit()

config_filename = arguments['--config']
if config_filename != None:
	try:
		config_file = open(config_filename, 'r')
		config = json.load(config_file)
	except:
		logging.warning("Error: {0} could not be opened as a config file".format(config_filename))
		exit()
else:
	config = { 'excluded': ['Wikipedia'] }

punc = ''
for i in range(maxunicode):
	char = chr(i)
	if unicodedata.category(char)[0] in 'NPS': # All numbers, punctuation or symbols
		punc += char

punctuation = set(punc)
punctuation.remove("'") # Dumb apostrophe
punctuation.remove("’") # Smart apostrophe

try:
	xmlfile = open(arguments['<file>'])
	context = etree.iterparse(xmlfile, events=('start', 'end'))
except IOError:
	logging.warning('Error: {:s} could not be read'.format(argv[1]))
	exit()

whitespace_regex = regex.compile('\s+')
quotes_regex = regex.compile(r'\'\'\'?|\n+')
cleanup_regex = regex.compile(r"""\[\[.+?\]\]|\{\{.+?\}\}	# markup tags like [[]] or {{}}
                                  | ^[ |*{!=}].*?$		# tables, links and headers
				  | <!--.*?-->			# comment tags
                                  | <.*?>.*?</.*?>		# reference tags
                                  | <.*?>.*?$			# reference tags spanning a line
                                  | .*?</.*?>			# reference tags spanning a line
                                  | &lt;.*?&gt;.*?&lt;/.*?&gt;	# reference tags
                                  | &lt;.*?&gt;.*?\n		# reference tags spanning a line
                                  | .*?&lt;/.*?&gt;		# reference tags spanning a line
                               """, regex.VERBOSE | regex.M)

counter = Counter()

event, root = next(context)

url_length = root.tag.find('}') + 1
tags_found = 0
xmlfilesize = float(fstat(xmlfile.fileno()).st_size)
update_interval = 100 if xmlfilesize < 1e7 else 250 if xmlfilesize < 1e9 else 500

for event, elem in context:
	if event == 'end' and elem.tag[url_length:] == 'text' and elem.text != None:
		text = elem.text
		text = cleanup_regex.sub('', text)
		text = quotes_regex.sub(' ', text)
		text = ''.join([ch for ch in text if ch not in punctuation])
		text = whitespace_regex.sub('\n', text)

		words = regex.split('\n+', text)

		for word in words:
			counter[word] += 1

		tags_found += 1

		if tags_found % update_interval == 0:
			logging.warning("Tags found: {0:8n}    Progress: {1:6.4f}".format(tags_found, float(xmlfile.tell())/xmlfilesize))

		root.clear()

config['excluded'].extend(['', "''", "'"])

for word in config['excluded']:
	del counter[word]

for keypair in counter.most_common(words_to_output):
	print(keypair[0])

