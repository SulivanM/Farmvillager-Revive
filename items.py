import os, zlib, pyamf, json
from pyamf.amf3 import Decoder, TYPE_OBJECT
from bundle import XML_DIR, CACHE_DIR

ITEMS_AMF = os.path.join(XML_DIR, "gz", "v855038", "items_opt.amf")
CACHE_ITEMS_JSON = os.path.join(CACHE_DIR, "gz_v855038_items_opt.json")
_cached_items = None

def _cache_items():
    obj_decomp = zlib.decompress(open(ITEMS_AMF, 'rb').read())
    assert obj_decomp[:1] == TYPE_OBJECT
    dec = pyamf.get_decoder(pyamf.AMF3, obj_decomp)
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump(dec.readElement(), open(CACHE_ITEMS_JSON, 'w'))

def load_items():
    global _cached_items
    if not os.path.exists(CACHE_ITEMS_JSON): _cache_items()
    _cached_items = json.load(open(CACHE_ITEMS_JSON, 'r'))

def get_items(): return _cached_items["settings"]["items"]["item"]
def get_item_by_name(name):
    for item in get_items():
        if item["name"] == name: return item
    return None
def get_item_by_code(code):
    for item in get_items():
        if item["code"] == code: return item
    return None