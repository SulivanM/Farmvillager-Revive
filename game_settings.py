import os, zlib, json, xmltodict
from bundle import XML_DIR, CACHE_DIR

CONFIG_XML = os.path.join(XML_DIR, "gz", "v855098", "gameSettings.xml.gz")
CACHE_CONFIG_JSON = os.path.join(CACHE_DIR, "gz_v855098_gameSettings.json")
_cached_game_settings = None
_xp_level_map = None
_level_xp_map = None

def _cache_game_settings():
    obj = zlib.decompress(open(CONFIG_XML, 'rb').read())
    arr = xmltodict.parse(obj)
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump(arr, open(CACHE_CONFIG_JSON, 'w'))

def load_game_settings():
    global _cached_game_settings
    if not os.path.exists(CACHE_CONFIG_JSON): _cache_game_settings()
    _cached_game_settings = json.load(open(CACHE_CONFIG_JSON, 'r'))
    _xp_level_map_init()

def get_game_settings(): return _cached_game_settings["settings"]

def _xp_level_map_init():
    global _xp_level_map, _level_xp_map
    _xp_level_map, _level_xp_map = {}, {}
    for level in get_game_settings()["levels"]["level"]:
        _xp_level_map[level["@requiredXP"]] = level["@num"]
        _level_xp_map[level["@num"]] = level["@requiredXP"]

def xp_to_level(xp):
    xp = int(xp)
    for x in sorted(_xp_level_map.keys(), key=int, reverse=True):
        if xp >= int(x): return int(_xp_level_map[str(x)])
    return None

def level_to_xp(level): return int(_level_xp_map[str(level)])
