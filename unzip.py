import urllib.request, os, zipfile, shutil
import process as geoip

ZIP_DIR = "zip/"
TEMPORAL_EXTRACTED_DIR = "csv"

# urllib.request.urlretrieve(
#     "https://geoip.maxmind.com/app/geoip_download?edition_id=GeoLite2-City-CSV&suffix=zip&license_key=" + os.environ[
#         "MAXMIND_LICENSE_KEY"], ZIP_FILENAME)

shutil.rmtree(geoip.CSV_DATABASE_DIR, ignore_errors=True)
if not os.path.exists(TEMPORAL_EXTRACTED_DIR):
    os.mkdir(TEMPORAL_EXTRACTED_DIR)

zipfiles = list(os.listdir('zip'))
zipfiles.sort()
with zipfile.ZipFile(ZIP_DIR + zipfiles[-1], 'r') as zip_ref:
    zip_ref.extractall(TEMPORAL_EXTRACTED_DIR)
