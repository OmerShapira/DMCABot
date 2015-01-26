import pycurl
import ijson
from io import BytesIO
import time
import RequestParser
from pprint import pprint
import logging

curl = pycurl.Curl()
URL_ROOT = "https://chillingeffects.org/"
PATH_NOTICES = "notices/"
PATH_SEARCH = "notices/search"

log = logging.getLogger("RequestDaemon")


class Request(object):

    def __init__(self, **kwargs):
        self.params = kwargs

    def execute(self, request_next_page=True):
        # TODO: Make requests, parse page information from JSON, recursively make more requests    
        self.buffer = BytesIO()
        if not hasattr(self, "curl"):
            self.curl = pycurl.Curl()
            self.curl.setopt(pycurl.HTTPHEADER, [
                "Accept: application/json",
                "Content-type: application/json"
            ])

        url = URL_ROOT + PATH_SEARCH + "?" + '&'.join(
            [str(x) + "=" + str(y) for x, y in self.params.items()])
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEDATA, self.buffer)
        log.info("Request: "+url)
        self.curl.perform()
        self.curl.close()

    def getNoticeStream(self):
        if self.buffer:
            self.buffer.seek(0)
            return NoticeStream(self.buffer)
        else:
            return None


class NoticeStream(object):

    def __init__(self, buffer):
        self.jsonstream = ijson.items(buffer, 'notices.item')

    def __iter__(self):
        return self.jsonstream.__iter__()


class Daemon(object):

    def __init__(self):
        pass

    def request_time(self, time_in, time_out):
        request = Request(
            date_received=repr(time_in) + ".." + repr(time_out),
            per_page=100
        )
        request.execute()
        # TOOD: make future
        return request.getNoticeStream()


if __name__ == '__main__':
    rightnow = int((time.time()) * 10e6)
    earlier  =  int((time.time() - 3600) * 10e6)
    d = Daemon()
    evts = d.request_time(earlier, rightnow)
    parsed_evts = (RequestParser.NoticeProcessor(v).get_report() for v in evts)
    for evt in parsed_evts:
        if evt:
            pprint(evt)
