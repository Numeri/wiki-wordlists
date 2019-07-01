#!/bin/python

from bs4 import BeautifulSoup, Tag
from collections import Counter
import regex
import string
from sys import argv, maxunicode
import unicodedata

#Check that arguments were provided
words_to_output = 1000
if len(argv) < 2:
	print('Error: Provide a filename to read and optionally the number of words to output')
	exit()
if len(argv) == 3:
	words_to_output = int(argv[2])
	if words_to_output < 1:
		print('Error: The number of words to output must be more than 0')
		exit()

punc = '=|'

for i in range(maxunicode):
	char = chr(i)
	if unicodedata.category(char).startswith('P'):
		punc += char
punctuation = set(punc)
punctuation.remove("'")

try:
	with open(argv[1]) as xmlfile:
		xml = xmlfile.read()
except IOError:
	print('Error: {:s} could not be read'.format(argv[1]))
	exit()

soup = BeautifulSoup(xml, 'lxml')
text_tags = soup.find_all('text')

text = ''

for tag in text_tags:
	text += tag.get_text()

whitespace_regex = regex.compile('\s+')
triplequotes_regex = regex.compile(r'\'\'\'')
cleanup_regex = regex.compile(r"""\[\[.+\]\]|\{\{.+\}\}		# markup tags like [[]] or {{}}
                                  | (\n|^)[ |*{!=}].*		# tables, links and headers
                                  | <.*>.*</.*>			# reference tags
                                  | <.*>.*\n			# reference tags spanning a line
                                  | .*</.*>			# reference tags spanning a line
                                  | [0-9]			# numbers
                               """, regex.VERBOSE)

text = cleanup_regex.sub('', text)
text = triplequotes_regex.sub(' ', text)
text = ''.join([ch for ch in text if ch not in punctuation])
text = whitespace_regex.sub('\n', text)

words = regex.split('\n+', text)

counter = Counter()
for word in words:
	counter[word] += 1

counter[''] = 0
counter["''"] = 0
counter["'"] = 0

for keypair in counter.most_common(words_to_output):
	print(keypair[0])
