from processGeoIpCsv import ipStr2Int
import json


def read_json(filename):
    with open('data/{}.json'.format(filename), 'r') as r_file:
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
    while True:
        i = int((high - low) / 2) + low
        if ip < extract_key(ip_list, i):
            if i == high and i == low:
                return - 1
            elif i == high:
                high = low
            else:
                high = i
        elif ip >= extract_key(ip_list, i) and (i == (length - 1) or ip < extract_key(ip_list, i + 1)):
            return i
        else:
            low = i


def search_ip(ip_address: str):
    ip_int = ipStr2Int(ip_address)
    params = read_json('params')
    ip_range_list = read_json('index')
    x = binary_search(ip_range_list, ip_int)
    ip_range_list = read_json('i{}'.format(x))
    y = binary_search(ip_range_list, ip_int)
    index = x * params.get('NUMBER_NODES_PER_MIDINDEX') + y
    # print(x, y, x * params.get('NUMBER_NODES_PER_MIDINDEX') + y)
    ip_info_list = read_json('{}'.format(index))
    ip_info_index = binary_search(ip_info_list, ip_int)
    # print(ip_info_list[ip_info_index])
    ip_info = ip_info_list[ip_info_index]
    location_list = read_json('locations')
    ip_geo = location_list[ip_info[1]]
    geo_info = {
        'country': ip_geo[0],
        'region': ip_geo[1],
        'eu': ip_geo[5],
        'timezone': ip_geo[4],
        'city': ip_geo[2],
        'lat': ip_info[2],
        'lon': ip_info[3],
        'metro': ip_geo[3],
        'area': ip_info[4]
    }
    return geo_info


if __name__ == '__main__':
    ip_address = '118.238.204.216'
    print(search_ip(ip_address))
