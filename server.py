import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from search import search_ip

data = {'result': 'this is a test'}
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
    server_version = "Apache"  # 设置服务器返回的的响应头
    cache = Cache(10)

    def response_data(self, info: str):
        self.wfile.write(info.encode())

    def do_GET(self):
        querys = urlparse(self.path).query
        self.send_response(200)
        self.send_header("Content-type", "text/json")  # 设置服务器响应头
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

    # def do_POST(self):
    #     path = self.path
    #     print(path)
    #     # 获取post提交的数据
    #     datas = self.rfile.read(int(self.headers['content-length']))  # 固定格式，获取表单提交的数据
    #     # datas = urllib.unquote(datas).decode("utf-8", 'ignore')
    #
    #     self.send_response(200)
    #     self.send_header("Content-type", "text/html")  # 设置post时服务器的响应头
    #     self.send_header("test", "This is post!")
    #     self.end_headers()
    #
    #     html = '''<!DOCTYPE HTML>
    #     <html>
    #         <head>
    #             <title>Post page</title>
    #         </head>
    #         <body>
    #             Post Data:%s  <br />
    #             Path:%s
    #         </body>
    #     </html>''' % (datas, self.path)
    #     self.wfile.write(html.encode())  # 提交post数据时，服务器跳转并展示的页面内容


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
