import csv, os, json, shutil
from math import sqrt, floor, ceil

CSV_DATABASE_DIR = "csv/"
DATA_DIR = "data"
PARAMS_FILE = 'conf'
BLOCK_SIZE = 2 ** 12  # = 4KB, the storage block size on almost all new OSes
FILE_SIZE = BLOCK_SIZE * 12 - 100  # File size is made to be lower than the size of 12 storage blocks (minus a few bytes to account for overheads) in order to make sure that all the file's contents are directly addressed from the file's inode (preventing indirect access to storage blocks)


def remove_old_data():
    shutil.rmtree(DATA_DIR, ignore_errors=True)  # Clean directory
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(PARAMS_FILE):
        os.mkdir(PARAMS_FILE)


def jsonify(item):
    return json.dumps(item).encode('utf-8')


def store_file(filename, content, binary=False):
    if binary:
        mode = "wb"
    else:
        mode = "w"
    with open(os.path.join(DATA_DIR, filename), mode) as newFile:
        newFile.write(content)


def parse_number(num, parser):
    return 0 if num == "" else parser(num)


def extract_location_attrs(row):
    # The only data from the locations file that is returned by neode-geoip is:
    # - country_iso_code (row 4)
    # - subdivision_1_iso_code (row 6)
    # - city_name (row 10)
    # - metro_code (row 11)
    # - time_zone (row 12)
    # - is_in_european_union (row 13)
    return [row[4], row[6], row[10], parse_number(row[11], int), row[12], row[13]]


def generate_locations_file(lang='en'):
    geoname_ids = {}
    location_items = []
    max_item_length = 0
    folders = list(os.listdir(CSV_DATABASE_DIR))
    folders.sort()
    with open(CSV_DATABASE_DIR + folders[-1] + '/' + "GeoLite2-City-Locations-{}.csv".format(lang)) as locations_file:
        locations = csv.reader(locations_file, delimiter=',')
        next(locations)  # Ignore first line (headers)
        counter = 0
        for row in locations:
            current_geoname_id = row[0]
            geoname_ids[current_geoname_id] = counter
            counter += 1
            stored_attrs = jsonify(extract_location_attrs(row))
            location_items.append(stored_attrs)
            max_item_length = max(max_item_length, len(stored_attrs))

    location_items = map(lambda item: item.rjust(max_item_length, b' '), location_items)
    new_location_file_content = b'[' + b','.join(
        location_items) + b']'  # Make it into a json even if it will not be used that way
    store_file("locations.json", new_location_file_content, True)

    return [geoname_ids, max_item_length + 1]


def extract_block_attrs(row, geoname_ids):
    # Attrs used by node-geoip:
    # - range (will be derived from the ip being searched) [0]
    # - geoname_id (needs to be transformed to match the ids generated before for the locations file) [1]
    # - latitude [7]
    # - longitude [8]
    # - accuracy_radius [9]
    try:
        locations_id = geoname_ids[row[1]]
    except:
        locations_id = geoname_ids.get(row[2], None)
    return [locations_id, parse_number(row[7], float), parse_number(row[8], float), parse_number(row[9], int)]


def store_ips(ips, counter, ip_index):
    ips = ips[:-1] + b']'  # Remove the trailing comma and add ]
    ip_index.append(json.loads(ips.decode('utf-8'))[0][0])  # Store the first IP of the set into the index
    store_file("%d.json" % counter, ips, True)


def ip_str_to_int(str_ip):
    ip = [int(e) for e in str_ip.split('.')]
    return ip[0] * 256 ** 3 + ip[1] * 256 ** 2 + ip[2] * 256 ** 1 + ip[3]


def generate_block_files(geoname_ids):
    counter = 0
    ips = b'['
    ipIndex = []
    folders = list(os.listdir(CSV_DATABASE_DIR))
    folders.sort()
    with open(CSV_DATABASE_DIR + folders[-1] + '/' + "GeoLite2-City-Blocks-IPv4.csv") as blocks_file:
        blocks = csv.reader(blocks_file, delimiter=',')
        next(blocks)  # Skip headers
        for row in blocks:
            [ip, mask] = row[0].split('/')
            mask = int(mask)
            ip = ip_str_to_int(ip)
            attrs = jsonify([ip] + extract_block_attrs(row, geoname_ids)) + b','
            if len(ips + attrs) > FILE_SIZE:
                store_ips(ips, counter, ipIndex)
                counter += 1
                ips = b'[' + attrs
            else:
                ips += attrs

    store_ips(ips, counter, ipIndex)
    return ipIndex


def generate_indexes(ip_index):
    root_ip_index = []
    ROOT_NODES = int(floor(sqrt(len(ip_index))))  # See readme for the rationale behind this formula
    MID_NODES = int(ceil(len(ip_index) / ROOT_NODES))
    for i in range(ROOT_NODES):
        root_ip_index.append(ip_index[i * MID_NODES])
        store_file("i%d.json" % i, json.dumps(ip_index[i * MID_NODES:(i + 1) * MID_NODES]))

    store_file("index.json", json.dumps(root_ip_index))
    return MID_NODES


def store_dynamic_params(location_record_length, num_mid_nodes):
    with open(PARAMS_FILE + '/params.json', "w") as params_file:
        params = {
            "LOCATION_RECORD_SIZE": location_record_length,
            "NUMBER_NODES_PER_MIDINDEX": num_mid_nodes
        }
        json.dump(params, fp=params_file, indent=2)  # Pretty-printed json


def main():
    remove_old_data()
    [geoname_ids, location_record_length] = generate_locations_file()
    ip_index = generate_block_files(geoname_ids)
    num_mid_nodes = generate_indexes(ip_index)
    store_dynamic_params(location_record_length, num_mid_nodes)


if __name__ == '__main__':
    main()
