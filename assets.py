import os
import sys
import shutil
import threading
import requests
import tqdm
import hashlib
from bundle import ASSETS_DIR, TMP_DIR
from warc_extractor.warc_extractor import _main_interface

WARC_PATH = os.path.join(TMP_DIR, "warc")
EXTRACTION_PATH = os.path.join(TMP_DIR, "extracted")
EXTRACTED_INNER_ASSETS_PATH = os.path.join(EXTRACTION_PATH, "zynga1-a.akamaihd.net", "farmville", "assets", "hashed", "assets")
BASE_URL = "https://cdnalpha.ttron.eu/production/farmvillage/"
FILES = [
    {"filename": "urls-bluepload.unstable.life-farmvilleassets.txt-shallow-20201225-045045-5762m-00000.warc.gz", "hash": "d9a36e44e5361e3db6ce1457f74ddf89"},
    {"filename": "urls-bluepload.unstable.life-farmvilleassets.txt-shallow-20201225-045045-5762m-00001.warc.gz", "hash": "54a8d13a5dfe0b12b5a3e17e39167a1e"},
    {"filename": "urls-bluepload.unstable.life-farmvilleassets.txt-shallow-20201225-045045-5762m-00002.warc.gz", "hash": "04938bcbc6585858f88962e9af6232b1"},
    {"filename": "urls-bluepload.unstable.life-farmvilleassets.txt-shallow-20201225-045045-5762m-00003.warc.gz", "hash": "4bb8d8f949f2ecfdab395cd35c9a47e6"},
]

def __inner_assets_check():
    return os.path.exists(os.path.join(ASSETS_DIR, "Environment")) and os.path.exists(os.path.join(ASSETS_DIR, "xpromoSupport"))

def check_assets():
    if __inner_assets_check(): return
    if os.path.exists(ASSETS_DIR) and os.listdir(ASSETS_DIR): sys.exit(1)
    if os.path.exists(ASSETS_DIR): os.rmdir(ASSETS_DIR)
    if not os.path.exists(TMP_DIR): os.mkdir(TMP_DIR)
    if not os.path.exists(WARC_PATH) or not os.listdir(WARC_PATH): warc_download(FILES)
    
    missing = []
    for f_dict in FILES:
        loc = os.path.join(WARC_PATH, f_dict["filename"])
        if not os.path.exists(loc):
            missing.append(f_dict)
            continue
        with open(loc, 'rb') as f:
            md5 = hashlib.md5()
            for chunk in iter(lambda: f.read(4*1024*1024), b""): md5.update(chunk)
            if md5.hexdigest() != f_dict["hash"]: missing.append(f_dict)

    if missing:
        warc_download(missing)
        check_assets()
        return
    
    os.makedirs(EXTRACTION_PATH, exist_ok=True)
    _main_interface(path=WARC_PATH, output_path=EXTRACTION_PATH, dump="content", filter=["WARC-Target-URI:zynga1-a.akamaihd.net/farmville/assets/hashed/assets"], silence=False)
    if not os.path.exists(EXTRACTED_INNER_ASSETS_PATH): sys.exit(1)
    shutil.move(EXTRACTED_INNER_ASSETS_PATH, ASSETS_DIR)
    shutil.rmtree(TMP_DIR)

def warc_download(files_list):
    os.makedirs(WARC_PATH, exist_ok=True)
    threads = []
    def download(desc, link, loc):
        r = requests.get(link, stream=True)
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        with open(loc, 'wb') as f, tqdm.tqdm(desc=desc, total=total, unit='B', unit_scale=True) as pb:
            for chunk in r.iter_content(1024):
                if chunk:
                    f.write(chunk)
                    pb.update(len(chunk))
    for f_dict in files_list:
        loc = os.path.join(WARC_PATH, f_dict["filename"])
        t = threading.Thread(target=download, args=(f" * {f_dict['filename']}", BASE_URL + f_dict["filename"], loc))
        t.start()
        threads.append(t)
    for t in threads: t.join()
