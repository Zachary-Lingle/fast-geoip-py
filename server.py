import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from search import search_ip

host = ('localhost', 21700)


class Cache:
    length = 10
    cache_list = []

    def __init__(self, length=10):
        self.length = length

    def find(self, key):
        for index in range(len(self.cache_list)):
            k, v = self.cache_list[index]
            if k == key:
                return index
        return -1

    def put(self, key, value):
        index = self.find(key)
        if index < 0:
            self.cache_list.pop(0)
            self.cache_list.append((key, value))
        else:
            self.cache_list[index] = (key, value)

    def get(self, key, default=None):
        index = self.find(key)
        if index < 0:
            return default
        else:
            _, value = self.cache_list[index]
            return value


class Resquest(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "Apache"
    cache = Cache(10)

    def response_data(self, info: str):
        self.wfile.write(info.encode())

    def do_GET(self):
        querys = urlparse(self.path).query
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        if querys:
            querys = querys.split('&')
            params = {}
            for qc in querys:
                k, v = qc.split("=")
                params[k] = v
            if params.get('ip'):
                geo_info = search_ip(ip_address=params.get('ip'), cache=self.cache)
                self.response_data(json.dumps(geo_info))
            else:
                self.response_data('Error')
        else:
            self.response_data('Error')


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting fast-geoip-py server, listen at: %s:%s" % host)
    server.serve_forever()
