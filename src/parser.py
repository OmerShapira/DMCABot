from __future__ import division
import json
import re
import operator
from urlparse import urlsplit
from itertools import imap, ifilter
from collections import Counter
from pprint import pprint 

from sys import argv

def get_tokens(s, prune=True):
    ## remove ['.html', '.html', '.php', '.py', 'erb'] etc
    pruned = re.sub(r'\.\w{1,4}$', '', s, flags=re.IGNORECASE) if prune else s
    pre_split = re.split(r'\W', pruned)
    ## remove empty strings
    clean_split = ifilter (lambda x : x, pre_split) 
    return set(clean_split)


class NoticeProcessor(object):
    def __init__(self, notice, token_threshold=5, common_proportion=0.25, diversity_threshold = 0.2, rules=None):
        self.notice = notice
        self.token_threshold = token_threshold
        self.common_proportion = common_proportion
        self.diversity_threshold = diversity_threshold
        self.rules = rules or {'disallowed_tokens':['index', 'rar', 'download', 'pirate', 'mp3', 'pdf', 'torrent', 'file', '4shared']}

    def apply_token_threshold(self, col):
        try:
            max_num = col.most_common(1)[0][1]
            
            def filter_func(x):
                cond = (x[1] >= max(self.token_threshold, max_num * self.common_proportion)) and (x[0] not in self.rules['disallowed_tokens'])
                return cond

            large_enough = filter(filter_func, col.viewitems())
            return large_enough
        except Exception as e:
            return []


    def make_report(self):
        ''' 
        we want to see that the domains 
        in the list are varied (over space or over time.)
        First we deal with space.
        '''
        for work in self.notice['dmca']['works']:
            try:
                report = {}
                urls = (x['url'] for x in work['infringing_urls'])
                parsed_urls = map(urlsplit, urls)

                ## Calculate Tokens
                token_list = (get_tokens(x.path) | get_tokens(x.query) for x in parsed_urls)   
                all_tokens = reduce(operator.add, imap(Counter, token_list))

                common_tokens = self.apply_token_threshold(all_tokens)
                if not common_tokens:
                    continue
                else: 
                    report['common_tokens'] = common_tokens

                ## Calculate Diversity
                sites = [x.hostname for x in parsed_urls]
                num_sites, num_urls = len(set(sites)), len(sites) 
                diversity = num_sites / num_urls
                
                if diversity < self.diversity_threshold:
                    continue
                else:
                    report['num_urls'] = num_urls
                    report['num_sites'] = num_sites
                    report['diversity'] = diversity

                yield report
            except Exception as e:
                print (e)


    def get_report(self):
        return list(self.make_report())


def main():
    filename = argv[1]
    with open(filename) as f:
        jf = json.load(f)
        proc = NoticeProcessor(jf)
        pprint(proc.get_report())

if __name__ == '__main__':
    main()