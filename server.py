import os, sys, json, pyamf, copy, uuid, math
from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, Response, redirect, session
from pyamf import remoting
import commands, engine
from engine import timestamp_now
from version import version_name
from bundle import BASE_DIR, ASSETS_DIR, EMBEDS_DIR, ASSETHASH_DIR, PATCHED_ASSETS_DIR, TEMPLATES_DIR, XML_DIR
from player import save_session, load_saves, load_static_villages, all_saves_info, all_saves_uids, save_info, new_village
from assets import check_assets
from game_settings import load_game_settings
from items import load_items

if os.name == 'nt':
    os.system("color")
    os.system("title FarmVille Revive Server")
else:
    sys.stdout.write("\x1b]2;FarmVille Revive Server\x07")

check_assets()
load_game_settings()
load_items()
load_saves()
load_static_villages()

BIND_IP, BIND_PORT = "127.0.0.1", 5500
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def login():
    session.pop('UID', default=None)
    load_saves()
    if request.method == 'POST':
        session['UID'] = request.form['UID']
        return redirect("/play.html")
    return render_template("login.html", saves_info=all_saves_info(), version=version_name)

@app.route("/play.html")
def play():
    uid = session.get('UID')
    if not uid or uid not in all_saves_uids(): return redirect("/")
    info = save_info(uid)
    return render_template("play.html", version=version_name, base_url=f"http://{BIND_IP}:{BIND_PORT}", server_time=timestamp_now(), debug="true", user={"uid": uid, "name": info["name"]}, save_info=info)

@app.route("/new.html")
def new():
    session['UID'] = new_village()
    return redirect("play.html")

@app.route("/img/<path:path>")
def img(path): return send_from_directory(TEMPLATES_DIR + "/img", path)
@app.route("/css/<path:path>")
def css(path): return send_from_directory(TEMPLATES_DIR + "/css", path)
@app.route("/crossdomain.xml")
def crossdomain(): return send_from_directory(TEMPLATES_DIR, "crossdomain.xml")
@app.route("/embeds/Flash/v855097-855094/FV_Preloader.swf")
def patched_preloader(): return send_from_directory(PATCHED_ASSETS_DIR, "FV_Preloader_mod.swf")
@app.route("/embeds/<path:path>")
def embeds(path): return send_from_directory(EMBEDS_DIR, path)
@app.route("/assethash/<path:path>")
def assethash_path(path): return send_from_directory(ASSETHASH_DIR, path, mimetype="application/x-amf")
@app.route("/xml/<path:path>")
def xml(path): return send_from_directory(XML_DIR, path, mimetype='text/xml')
@app.route("/assets/Environment/grass_themeBackground_7.swf")
def stub_grass_themeBackground_7(): return send_from_directory(ASSETS_DIR, "Environment/02de7becb766242e421e1430176f55a2.swf", mimetype='text/xml')
@app.route("/assets/<path:path>")
def assets(path): return send_from_directory(ASSETS_DIR, path)
@app.route("/report_exception.php", methods=['POST'])
def report_exception(): return "{}"
@app.route("/record_stats.php", methods=['POST'])
def record_stats():
    for i in json.loads(request.data).get("stats", []): print(f" * {i['statfunction']}: {i['data']}")
    return "{}"
@app.route("/report_log.php", methods=['POST'])
def report_log(): return "{}"
@app.route("/cb.php", methods=['POST'])
def cb(): return "{}"
@app.route("/sn_app_url/index.php")
def sn_app_url_index(): return redirect("/")

HANDLERS = {
    'UserService.initUser': lambda u, p: commands.init_user(u),
    'UserService.postInit': lambda u, p: commands.post_init_user(u),
    'FriendSetService.getBatchFriendSetData': lambda u, p: [],
    'UserService.r2InterstitialPostInit': lambda u, p: {"r2InterstitialItems":[], "r2InterstitialFeedItems":[], "r2InterstitialMinigameIndex":[], "r2InterstitialTypeIndex":None, "r2InterstitialFriendCount":None},
    'FriendListService.getFriendsForR2FlashNeighborFlow': lambda u, p: {"requestedFriends":{"GhostNeighbor":[], "FarmVille":[], "Facebook":[], "PossibleCommunity":[], "CurrentAllNeighbor":[]}},
    'UserService.incrementActionCount': lambda u, p: commands.increment_action_count(u, p[0]),
    'UserService.resetActionCount': lambda u, p: commands.reset_action_count(u, p[0]),
    'UserService.setSeenFlag': lambda u, p: commands.set_seen_flag(u, p[0]),
    'UserService.resetSystemNotifications': lambda u, p: None,
    'UserContentService.onCreateImage': lambda u, p: commands.set_avatar_appearance(u, p[0], p[1], p[2]) if p[0] == "avatar_appearance" else None,
    'UserService.saveOptions': lambda u, p: commands.save_options(u, p[0]),
    'WorldService.performAction': lambda u, p, r: (lambda obj_id: (r.update({"id": obj_id}), {"id": obj_id})[1])(commands.world_perform_action(u, p[0], p[1], p[2])),
    'UserService.updateFeatureFrequencyTimestamp': lambda u, p: commands.update_feature_frequency_timestamp(u, p[0]),
    'UserService.publishUserAction': lambda u, p: commands.publish_user_actions(u, p[0], p[1])
}

@app.route("/flashservices/gateway.php", methods=['POST'])
def flashservices_gateway():
    resp_msg = remoting.decode(request.data)
    resps, body = [], resp_msg.bodies[0][1].body
    h = body[0] if isinstance(body, (list, tuple)) else body.get(0)
    reqs = body[1] if isinstance(body, (list, tuple)) else body.get(1)
    if isinstance(reqs, dict): reqs = list(reqs.values())
    uid = h["uid"] if isinstance(h, dict) else getattr(h, 'uid', None)
    for reqq in reqs:
        n = getattr(reqq, 'functionName', reqq.get('functionName') if isinstance(reqq, dict) else "Unknown")
        p = getattr(reqq, 'params', reqq.get('params') if isinstance(reqq, dict) else [])
        s = getattr(reqq, 'sequence', reqq.get('sequence') if isinstance(reqq, dict) else 0)
        res = {"errorType":0, "errorData":None, "isDST":0, "sequenceNumber":s, "worldTime":timestamp_now(), "metadata":{"QuestComponent":{}}, "data":None}
        handler = HANDLERS.get(n)
        if handler: res["data"] = handler(uid, p, res) if n == 'WorldService.performAction' else handler(uid, p)
        resps.append(res)
    save_session(uid)
    ev = remoting.Envelope(pyamf.AMF0)
    ev[resp_msg.bodies[0][0]] = remoting.Response({"serverTime":timestamp_now(), "errorType":0, "data":resps})
    return Response(remoting.encode(ev, strict=True, logger=True).getvalue(), mimetype='application/x-amf')

@app.route("/sn_app_url/gifts.php")
def sn_app_url_gifts(): return "{}"

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.root_path, app.template_folder, app.static_folder = BASE_DIR, TEMPLATES_DIR, TEMPLATES_DIR
    app.run(host=BIND_IP, port=BIND_PORT, threaded=True)
