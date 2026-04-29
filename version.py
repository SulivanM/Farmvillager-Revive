version_code = "1.2"
version_name = f"Revive {version_code}"

def migrate_loaded_save(save):
    changed = False
    
    if save.get("version") == "0.01a":
        try:
            if save["userInfo"]["player"]["lonelyAnimalCode"] == 0:
                save["userInfo"]["player"]["lonelyAnimalCode"] = ""
        except KeyError:
            pass

    if save.get("version") != version_code:
        save["version"] = version_code
        changed = True

    return changed