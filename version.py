version_code = "1.0"
version_name = "Revive " + version_code

def migrate_loaded_save(save):
    changed = False
    if "version" not in save or save["version"] is None:
        changed, save["version"] = True, "1.0"
    if save["version"] == "0.01a":
        if save["userInfo"]["player"]["lonelyAnimalCode"] == 0:
            changed, save["userInfo"]["player"]["lonelyAnimalCode"] = True, ""
        save["version"] = "1.0"
        changed = True
    return changed