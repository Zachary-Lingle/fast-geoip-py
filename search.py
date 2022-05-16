from process import ip_str_to_int
import json


def read_json(filename, path='data'):
    with open('{}/{}.json'.format(path, filename), 'r') as r_file:
        data = json.load(fp=r_file)
    return data


def extract_key(ip_list, i):
    if type(ip_list[i]) is list:
        return ip_list[i][0]
    else:
        return ip_list[i]


def binary_search(ip_list, ip):
    length = len(ip_list)
    low = 0
    high = length - 1
    while extract_key(ip_list, 0) <= ip <= extract_key(ip_list, length - 1):
        i = int((high - low) / 2) + low
        if ip < extract_key(ip_list, i):
            if i == high and i == low:
                return -1
            elif i == high:
                high = low
            else:
                high = i
        elif ip >= extract_key(ip_list, i) and (i == (length - 1) or ip < extract_key(ip_list, i + 1)):
            return i
        else:
            low = i
    return -1


def search_ip(ip_address: str, cache=None, location_list=None):
    ip_int = ip_str_to_int(ip_address)
    params = read_json('params', path='conf')
    ip_range_list = read_json('index')
    x, y = binary_search(ip_range_list, ip_int), -1
    if x >= 0:
        ip_range_list = read_json('i{}'.format(x))
        y = binary_search(ip_range_list, ip_int)
    if x * y >= 0:
        index = x * params.get('NUMBER_NODES_PER_MIDINDEX') + y
        if cache and cache.find(index) >= 0:
            ip_info_list = cache.get(index)
        else:
            ip_info_list = read_json('{}'.format(index))

        ip_info_index = binary_search(ip_info_list, ip_int)
        ip_info = ip_info_list[ip_info_index]
        if not location_list:
            location_list = read_json('locations')
        ip_geo = location_list[ip_info[1]]
        geo_info = {
            'country': ip_geo[0],
            'state': ip_geo[1],
            'eu': ip_geo[5],
            'timezone': ip_geo[4],
            'city': ip_geo[2],
            'lat': ip_info[2],
            'lon': ip_info[3],
            'metro': ip_geo[3],
            'area': ip_info[4]
        }
        return geo_info
    else:
        return {
            'country': 'not found',
            'state': 'not found',
            'eu': 'not found',
            'timezone': 'not found',
            'city': 'not found',
            'lat': 'not found',
            'lon': 'not found',
            'metro': 'not found',
            'area': 'not found'
        }


if __name__ == '__main__':
    ip_address = '118.238.204.216'
    print(search_ip(ip_address))
