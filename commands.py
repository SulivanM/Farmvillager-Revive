import math
from player import session
from engine import timestamp_now
import engine
from items import get_item_by_name
from game_settings import level_to_xp

def init_user(UID): return session(UID)
def post_init_user(UID):
    return {
        "postInitTimestampMetric": timestamp_now(), "friendsFertilized": [], "totalFriendsFertilized": 0, "friendsFedAnimals": [],
        "totalFriendsFedAnimals": 0, "showBookmark": True, "showToolbarThankYou": True, "toolbarGiftName": True,
        "isAbleToPlayMusic": True, "FOFData": [], "prereqDSData": [], "neighborCount": 1, "hudIcons": ["scratchCard"],
        "completedQuests": [], "lastPphActionType": "PphAction", "turtleInnovationData": [], "worldCurrencies": [], "lotteryData": [], "popupTwitterDialog": False
    }

def increment_action_count(UID, action):
    save = session(UID)
    counts = save["userInfo"]["player"]["actionCounts"]
    counts[action] = counts.get(action, 0) + 1

def reset_action_count(UID, action):
    save = session(UID)
    if action in save["userInfo"]["player"]["actionCounts"]: save["userInfo"]["player"]["actionCounts"][action] = 0

def set_seen_flag(UID, flag): session(UID)["userInfo"]["player"]["seenFlags"][flag] = True
def save_options(UID, options):
    save = session(UID)
    save["userInfo"]["player"]["options"] = options.copy()
    save["options"] = options

def set_avatar_appearance(UID, name, png_b64, feed_post): return {}

def world_perform_action(UID, actionName, m_save, params):
    save = session(UID)
    obj_id = m_save["id"]
    if engine.world_object_id_is_temporary(obj_id):
        temp_id = obj_id
        already_gen = False
        for obj in save["world"]["objectsArray"]:
            if obj.get("tempId") == temp_id:
                obj_id = obj["id"]
                already_gen = True
                break
        if not already_gen: obj_id = engine.get_new_world_object_id(save["world"]["objectsArray"])
        m_save["tempId"], m_save["id"] = temp_id, obj_id

    for k in ["plantTime", "tempId", "buildTime"]:
        if k in m_save and isinstance(m_save[k], (int, float)) and math.isnan(m_save[k]): m_save[k] = None

    if actionName == 'plow':
        engine.world_update_or_add_object(save["world"]["objectsArray"], m_save)
        engine.apply_gold_diff(save, -15)
        engine.apply_xp_increment(save, 1)
    elif actionName == 'place':
        item = get_item_by_name(m_save["itemName"])
        engine.world_update_or_add_object(save["world"]["objectsArray"], m_save)
        p = params[0] if params else {}
        is_storage = p.get("isStorageWithdrawal", 0) != 0
        is_inv = p.get("isInventoryWithdrawal", False)
        is_gift = p.get("isGift", False)
        if is_storage: engine.storage_withdrawal(save, m_save["itemName"], 1)
        if not (is_gift or is_inv or is_storage):
            engine.apply_item_cost(save, item, currency=p.get("currency"))
        if m_save.get("state") == "planted" and item.get("plantXp"):
            engine.apply_xp_increment(save, item["plantXp"])
        elif not (is_gift or is_inv or is_storage):
            xp = int(item.get("buyXp") or (int(item.get("cost") or 0) // 100))
            engine.apply_xp_increment(save, xp)
    elif actionName == 'harvest':
        engine.apply_item_yield_reward(save, get_item_by_name(m_save["itemName"]))
        engine.world_update_or_add_object(save["world"]["objectsArray"], m_save)
    elif actionName == 'move':
        engine.world_replace_object(save["world"]["objectsArray"], m_save)
    return obj_id

def update_feature_frequency_timestamp(UID, feature):
    session(UID)["userInfo"]["player"]["featureFrequency"][feature] = timestamp_now()

def publish_user_actions(UID, action, params):
    save = session(UID)
    if action == "LevelUp":
        lvl = int(params["level_number"])
        min_xp = int(level_to_xp(lvl))
        if int(save["userInfo"]["player"]["xp"]) < min_xp: save["userInfo"]["player"]["xp"] = min_xp