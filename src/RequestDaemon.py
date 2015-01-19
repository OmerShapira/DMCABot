import pycurl
import logging
import ijson
import itertools
from io import StringIO
import time
import parser

curl = pycurl.Curl()
URL_ROOT = "https://chillingeffects.org/"
PATH_NOTICES = "notices/"
PATH_SEARCH = "notices/search"
# curl.set


class Request(object):
    
    def __init__(self, **kwargs):
        self.params = kwargs

    def execute(self, request_next_page=True):
        # TODO: Make requests, parse page information from JSON, recursively make more requests    
        self.buffer = StringIO()
        if not self.curl:
            self.curl = pycurl.Curl()
            self.curl.setopt(pycurl.HTTPHEADER, [
                "Accept: application/json",
                "Content-type: application/json"
                ])

        url = URL_ROOT + PATH_SEARCH +"?"+ '&'.join([x+"="+y for x,y in self.params.iteritems()])
        self.curl.setopt(pycurl.URL,url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.perform()
        curl.close()

    def getNoticeStream(self):
        if self.buffer:
            return NoticeStream(self.buffer)
        else:
            return null


class NoticeStream(object):

    def __init__(self, buffer):
        self.buffer = buffer
        self.jsonstream = ijson.items(buffer, 'notices.item')

    def __iter__(self):
        return self.jsonstream.__iter__()


class Daemon(object):

    def __init__(self):
        pass

    def request_time(self, time_in, time_out):
        request = Request(
                date_received=time_in+".."+time_out,
                per_page=100
            )
        request.execute()
        # TOOD: make future
        return request.getNoticeStream()


if __name__ == '__main__':
    rightnow =  int(time.time() *10e6)
    earlier =  int((time.time()-3600) *10e6)
    d = Daemon()
    evts = d.request_time(earlier, rightnow)
    for v in evts:
        print (v)