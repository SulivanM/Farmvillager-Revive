from datetime import datetime
import constants
from items import get_item_by_name
from game_settings import xp_to_level, level_to_xp

def timestamp_now(): return int(datetime.now().timestamp())

def world_object_id_is_temporary(oid): return constants.TEMP_ID_START <= oid <= constants.TEMP_ID_END
def world_objects_equal(a, b): return a["id"] == b["id"]

def get_new_world_object_id(objects):
    ids = [obj["id"] for obj in objects]
    nxt = max(ids) + 1
    if world_object_id_is_temporary(nxt): nxt = constants.TEMP_ID_END + 1
    return nxt

def get_world_object_by_id(objects, oid):
    for obj in objects:
        if obj["id"] == oid: return obj
    return None

def world_replace_object(objects, new_obj):
    for i, obj in enumerate(objects):
        if obj["id"] == new_obj["id"]:
            objects[i] = new_obj
            return True
    return False

def world_update_or_add_object(objects, new_obj):
    if not world_replace_object(objects, new_obj): objects.append(new_obj)

def apply_xp_increment(save, val):
    val = int(val)
    if val <= 0: return
    old_xp = save["userInfo"]["player"]["xp"]
    new_xp = old_xp + val
    save["userInfo"]["player"]["xp"] = new_xp
    old_lvl, new_lvl = xp_to_level(old_xp), xp_to_level(new_xp)
    if old_lvl < new_lvl:
        diff = new_lvl - old_lvl
        apply_cash_diff(save, diff)

def apply_coins_diff(save, val):
    if val != 0: save["userInfo"]["player"]["gold"] = max(0, save["userInfo"]["player"]["gold"] + val)
def apply_gold_diff(save, val): apply_coins_diff(save, val)
def apply_cash_diff(save, val):
    if val != 0: save["userInfo"]["player"]["cash"] = max(0, save["userInfo"]["player"]["cash"] + val)

def apply_item_cost(save, item, currency=None):
    cost = int(item.get("cost") or 0)
    cash = int(item.get("cash") or 0)
    market = item.get("market")
    if not currency: currency = market if market in ["cash", "coins"] else "coins"
    
    val = cost if currency == "coins" else (cash if currency == "cash" else 0)
    if val > 0:
        if currency == "coins": apply_coins_diff(save, -val)
        elif currency == "cash": apply_cash_diff(save, -val)

def apply_item_yield_reward(save, item):
    yield_val = int(item.get("coinYield") or 0)
    if yield_val > 0: apply_coins_diff(save, yield_val)

def storage_withdrawal(save, name, amount=1):
    item = get_item_by_name(name)
    if not item or amount <= 0: return
    code, storage = item["code"], save["userInfo"]["player"]["storageData"]
    for group in storage:
        if code in storage[group]:
            storage[group][code][0] -= amount
            if storage[group][code][0] <= 0: del storage[group][code]
            return