#!/bin/python

import xml.etree.ElementTree as etree
from collections import Counter
import regex
import string
from sys import argv, maxunicode
from os import fstat
import unicodedata
import logging

logging.basicConfig(format='%(message)s')

#Check that arguments were provided
words_to_output = 1000
if len(argv) < 2:
	logging.warning('Error: Provide a filename to read and optionally the number of words to output')
	exit()
if len(argv) == 3:
	words_to_output = int(argv[2])
	if words_to_output < 1:
		logging.warning('Error: The number of words to output must be more than 0')
		exit()

punc = '=|+<>^'

for i in range(maxunicode):
	char = chr(i)
	if unicodedata.category(char).startswith('P'):
		punc += char
punctuation = set(punc)
punctuation.remove("'")

try:
	xmlfile = open(argv[1])
	context = etree.iterparse(xmlfile, events=('start', 'end'))
except IOError:
	logging.warning('Error: {:s} could not be read'.format(argv[1]))
	exit()

whitespace_regex = regex.compile('\s+')
quotes_regex = regex.compile(r'\'\'\'?')
cleanup_regex = regex.compile(r"""\[\[.+\]\]|\{\{.+\}\}		# markup tags like [[]] or {{}}
                                  | (\n|^)[ |*{!=}].*		# tables, links and headers
                                  | <.*>.*</.*>			# reference tags
                                  | <.*>.*\n			# reference tags spanning a line
                                  | .*</.*>			# reference tags spanning a line
                                  | [0-9۰-۹]			# numbers
                               """, regex.VERBOSE)

counter = Counter()

event, root = next(context)

url_length = root.tag.find('}') + 1
tags_found = 0
xmlfilesize = float(fstat(xmlfile.fileno()).st_size)
update_interval = 250 if xmlfilesize > 1e7 else 100

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

counter[''] = 0
counter["''"] = 0
counter["'"] = 0

for keypair in counter.most_common(words_to_output):
	print(keypair[0])
