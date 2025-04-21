import json
import argparse
from pathlib import Path
from utils import scan_directory
from datetime import datetime

CONFIG_PATH = "config.json"

def get_baseline_path(folder_path):
    safe_name = folder_path.replace(":", "").replace("\\", "_").replace("/", "_")
    return f"baseline_{safe_name}.json"

def load_config():
    if not Path(CONFIG_PATH).exists():
        return {"monitor_paths": [], "excluded_extensions": [], "hash_algo": "sha256"}
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def load_baseline(path):
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_baseline(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def detect_changes(current, baseline):
    changes = []
    for path, meta in current.items():
        if path not in baseline:
            changes.append(f"[NEW FILE] {path}")
        elif baseline[path]["hash"] != meta["hash"]:
            changes.append(f"[MODIFIED CONTENT] {path} (Last modified: {meta['last_modified']})")
    for path in baseline:
        if path not in current:
            changes.append(f"[DELETED] {path}")
    return changes

def update_config(new_path):
    config = load_config()
    if new_path not in config["monitor_paths"]:
        config["monitor_paths"].append(new_path)
        save_config(config)
        print(f"[✓] Added {new_path}")
    else:
        print("[!] Path already exists in configuration.")

def delete_path(del_path):
    config = load_config()
    if del_path in config["monitor_paths"]:
        config["monitor_paths"].remove(del_path)
        save_config(config)
        print(f"[✓] Removed {del_path}")
    else:
        print("[!] Path not found in config.")

def scan_path(path):
    config = load_config()
    current = scan_directory(path, config["excluded_extensions"], config["hash_algo"])
    baseline_path = get_baseline_path(path)
    baseline = load_baseline(baseline_path)

    if not baseline:
        print("[+] No baseline found. Saving current state.")
        save_baseline(current, baseline_path)
    else:
        print(f"[*] Comparing {path} with baseline...")
        changes = detect_changes(current, baseline)
        if changes:
            for c in changes:
                print("!!", c)
        else:
            print("[✓] No changes detected")

def view_paths():
    config = load_config()
    if config["monitor_paths"]:
        print("Monitored Paths:")
        for p in config["monitor_paths"]:
            print(f" - {p}")
    else:
        print("No monitored paths.")

def scan_all():
    config = load_config()
    for path in config["monitor_paths"]:
        print(f"\n[🔍] Scanning: {path}")
        scan_path(path)

def main():
        parser = argparse.ArgumentParser(description="File Integrity Monitoring Tool")
        parser.add_argument("--add", help="Add a new path to monitor")
        parser.add_argument("--delete", help="Delete a monitored path")
        parser.add_argument("--view", action="store_true", help="View all monitored paths")
        parser.add_argument("--scan", help="Scan a specific path")
        parser.add_argument("--scan-all", action="store_true", help="Scan all monitored paths")

        args = parser.parse_args()

        if args.add:
            update_config(args.add)
        elif args.delete:
            delete_path(args.delete)
        elif args.view:
            view_paths()
        elif args.scan:
            scan_path(args.scan)
        elif args.scan_all:
            scan_all()
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
