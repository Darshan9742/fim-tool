import json
import time
from pathlib import Path
from utils import scan_directory

CONFIG_PATH = "config.json"

def get_baseline_path(folder_path):
    safe_name = folder_path.replace(":", "").replace("\\", "_").replace("/", "_")
    return f"baseline_{safe_name}.json"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def load_baseline(path):
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_baseline(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def update_config(new_path):
    config = load_config()
    if new_path not in config["monitor_paths"]:
        config["monitor_paths"].append(new_path)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    else:
        print("[!] Path already exists in configuration.")

def background_scan_all(interval=60):
    config = load_config()
    monitor_paths = config["monitor_paths"]

    if not monitor_paths:
        print("[!] No saved paths to scan.")
        return

    print(f"\n[✓] Starting background scan every {interval} seconds for paths:")
    for p in monitor_paths:
        print(" -", p)

    try:
        while True:
            print("\n[⏳] Scanning all paths...")
            for path in monitor_paths:
                if not Path(path).exists():
                    print(f"[!] Skipping missing path: {path}")
                    continue

                baseline_path = get_baseline_path(path)
                current = scan_directory(path, config["excluded_extensions"], config["hash_algo"])
                baseline = load_baseline(baseline_path)

                if not baseline:
                    print(f"[+] No baseline for {path}. Saving...")
                    save_baseline(current, baseline_path)
                    continue

                changes = detect_changes(current, baseline)
                if changes:
                    print(f"[⚠️] Changes detected in {path}:")
                    for c in changes:
                        print("   ", c)
                else:
                    print(f"[✓] No changes in {path}.")

            print(f"[⏳] Sleeping for {interval} seconds...\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[!] Background scanning stopped by user.")

def user_menu():
    config = load_config()
    while True:
        print("\nSelect an option:")
        print("[1] Scan a saved path")
        print("[2] Add a new path")
        print("[3] View all saved paths")
        print("[4] Delete a saved path")
        print("[5] Start background scan on all saved paths")
        print("[6] Exit")

        choice = input("Enter choice [1-6]: ")

        if choice == "1":
            if not config["monitor_paths"]:
                print("No saved paths found. Please add one first.")
                continue
            print("Choose a path to scan:")
            for idx, path in enumerate(config["monitor_paths"], 1):
                print(f"{idx}. {path}")
            index = int(input("Enter number: ")) - 1
            return config["monitor_paths"][index]

        elif choice == "2":
            new_path = input("Enter full path to monitor: ").strip()
            if Path(new_path).exists():
                update_config(new_path)
                return new_path
            else:
                print("[!] Path doesn't exist.")

        elif choice == "3":
            if config["monitor_paths"]:
                print("Saved paths:")
                for i, p in enumerate(config["monitor_paths"], 1):
                    print(f"{i}. {p}")
            else:
                print("No paths saved yet.")

        elif choice == "4":
            if not config["monitor_paths"]:
                print("No paths to delete.")
                continue
            print("Select a path to delete:")
            for idx, path in enumerate(config["monitor_paths"], 1):
                print(f"{idx}. {path}")
            to_delete = int(input("Enter number: ")) - 1
            removed_path = config["monitor_paths"].pop(to_delete)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"[✓] Removed {removed_path}")

        elif choice == "5":
            interval = input("Enter scan interval in seconds (default 60): ").strip()
            interval = int(interval) if interval.isdigit() else 60
            background_scan_all(interval)

        elif choice == "6":
            exit()

        else:
            print("[!] Invalid choice. Try again.")

def detect_changes(current, baseline):
    changes = []
    for path, meta in current.items():
        if path not in baseline:
            changes.append(f"[NEW FILE] {path}")
        else:
            if baseline[path]["hash"] != meta["hash"]:
                changes.append(f"[MODIFIED CONTENT] {path} (Last modified: {meta['last_modified']})")
    for path in baseline:
        if path not in current:
            changes.append(f"[DELETED] {path}")
    return changes

def main():
    print("\n--- File Integrity Monitor ---")
    monitor_path = user_menu()
    monitor_paths = [monitor_path]
    baseline_path = get_baseline_path(monitor_path)

    all_current_hashed = {}
    for path in monitor_paths:
        all_current_hashed.update(scan_directory(
            path, load_config()["excluded_extensions"], load_config()["hash_algo"]
        ))

    baseline = load_baseline(baseline_path)

    if not baseline:
        print("[+] No baseline found. Saving current state.")
        save_baseline(all_current_hashed, baseline_path)
    else:
        print("[*] Comparing with baseline...")
        changes = detect_changes(all_current_hashed, baseline)
        if changes:
            for c in changes:
                print("!!", c)
        else:
            print("[✓] No changes detected")

if __name__ == "__main__":
    main()