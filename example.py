from server import host
import requests

ip_address = '1.0.0.1'
url = 'http://{}:{}/?ip={}'.format(host[0], host[1], ip_address)
data = requests.get(url=url).json()

print(data)
