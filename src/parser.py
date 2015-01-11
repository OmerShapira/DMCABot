from __future__ import division
import json
import re
from urlparse import urlparse
import logging
from itertools import imap, ifilter
from collections import Counter

from sys import argv

def get_tokens(s):
	pre_split = re.split(r'\W', s)
	#remove empty strings
	clean_split = ifilter (lambda x : x, pre_split) 
	return set(clean_split)


class NoticeProcessor(object):
	def __init__(self, notice):
		self.notice = notice

	def process(self):
		''' 
		we first want to see that the domains 
		in the list are varied (over space or over time.)
		'''
		try:
			for work in self.notice['dmca']['works']:
				urls = imap(lambda x: x['url'], work['infringing_urls'])
				parsed_urls = map(urlparse, urls)
				
				token_lists = imap(lambda x : get_tokens(x.path), parsed_urls)
				all_tokens = reduce(lambda x, y: x + y, imap(Counter, token_lists), Counter())
				print (all_tokens.most_common(5))

				all_sites = map(lambda x : x.netloc, parsed_urls)
				diversity = len(set(all_sites)) / len(all_sites)
				# all_sites = Counter(all_sites_tokenized)
				# print (all_sites)
				print("Diversity : %s" % diversity)

		except Exception as e:
			raise (e)

def main():
	filename = argv[1]
	with open(filename) as f:
		jf = json.load(f)
		proc = NoticeProcessor(jf)
		proc.process()

if __name__ == '__main__':
	main()