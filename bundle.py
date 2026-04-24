import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_BUNDLED_DIR = BASE_DIR

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    TMP_BUNDLED_DIR = sys._MEIPASS
    BASE_DIR = os.path.dirname(BASE_DIR)

PATCHED_ASSETS_DIR = os.path.join(TMP_BUNDLED_DIR, "patched")
TEMPLATES_DIR = os.path.join(TMP_BUNDLED_DIR, "templates")
VILLAGES_DIR = os.path.join(TMP_BUNDLED_DIR, "villages")
XML_DIR = os.path.join(TMP_BUNDLED_DIR, "xml")
EMBEDS_DIR = os.path.join(TMP_BUNDLED_DIR, "embeds")
ASSETHASH_DIR = os.path.join(TMP_BUNDLED_DIR, "assethash")

SAVES_DIR = os.path.join(BASE_DIR, "saves")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
TMP_DIR = os.path.join(BASE_DIR, "tmp")
