import os, sys, json, copy, uuid
from engine import timestamp_now
from bundle import VILLAGES_DIR, SAVES_DIR
from version import migrate_loaded_save

__villages, __saves = {}, {}
__initial_village = json.load(open(os.path.join(VILLAGES_DIR, "initial.json")))

def load_saves():
    global __saves
    __saves = {}
    os.makedirs(SAVES_DIR, exist_ok=True)
    for f in os.listdir(SAVES_DIR):
        try:
            save = json.load(open(os.path.join(SAVES_DIR, f)))
            uid = str(save["userInfo"]["player"]["userId"])
            __saves[uid] = save
            if migrate_loaded_save(save): save_session(uid)
        except: continue

def load_static_villages():
    global __villages
    __villages = {}
    for f in os.listdir(VILLAGES_DIR):
        if f == "initial.json" or not f.endswith(".json"): continue
        v = json.load(open(os.path.join(VILLAGES_DIR, f)))
        __villages[str(v["userInfo"]["player"]["userId"])] = v

def new_village():
    uid, ts = str(uuid.uuid4()), timestamp_now()
    v = copy.deepcopy(__initial_village)
    v["version"] = None
    v["userInfo"]["player"]["userId"] = uid
    v["flashHotParams"]["ZYNGA_USER_ID"] = uid
    v["world"]["id"], v["world"]["uid"] = 1, str(uuid.uuid4())
    v["userInfo"]["worldSummaryData"]["farm"]["firstLoaded"] = v["userInfo"]["worldSummaryData"]["farm"]["lastLoaded"] = ts
    v["userInfo"]["is_new"] = v["userInfo"]["firstDay"] = True
    v["userInfo"]["firstDayTimestamp"] = ts
    migrate_loaded_save(v)
    __saves[uid] = v
    save_session(uid)
    return uid

def all_saves_uids(): return list(__saves.keys())
def all_uids(): return list(__villages.keys()) + list(__saves.keys())
def session(uid): return __saves.get(uid)

def get_player(uid):
    s = session(uid)
    s["userInfo"]["worldSummaryData"]["farm"]["lastLoaded"] = timestamp_now()
    s["userInfo"]["player"]["neighbors"] = []
    return s

def save_info(uid):
    s = __saves[uid]
    return {"uid": uid, "name": s["userInfo"]["attr"]["name"], "xp": s["userInfo"]["player"]["xp"]}

def all_saves_info(): return [save_info(uid) for uid in __saves]

def save_session(uid):
    v = copy.deepcopy(session(uid))
    for obj in v["world"]["objectsArray"]:
        if "tempId" in obj: del obj["tempId"]
    with open(os.path.join(SAVES_DIR, f"{uid}.save.json"), 'w') as f: json.dump(v, f, indent=4)