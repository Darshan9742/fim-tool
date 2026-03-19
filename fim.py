import json
import time
from utils import scan_directory, detect_changes
from pathlib import Path
from utils import scan_directory
from config_manager import load_config
from report_manager import generate_report, save_report

CONFIG_PATH = "config.json"

def get_baseline_path(folder_path):
    safe_name = folder_path.replace(":", "").replace("\\", "_").replace("/", "_")
    return f"baseline_{safe_name}.json"

def load_baseline(path):
    from utils import calculate_baseline_hash

    if not Path(path).exists():
        return {}

    with open(path) as f:
        data = json.load(f)

    # 🔐 Verify integrity
    meta_path = path + ".meta"

    if Path(meta_path).exists():
        with open(meta_path) as f:
            meta = json.load(f)

        current_hash = calculate_baseline_hash(data)

        if meta.get("hash") != current_hash:
            print("[🚨] WARNING: Baseline file may have been tampered!")

    else:
        print("[!] No integrity metadata found for baseline.")

    return data

def save_baseline(data, path):
    import json
    from utils import calculate_baseline_hash

    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

    # 🔐 Create meta file
    meta_path = path + ".meta"
    baseline_hash = calculate_baseline_hash(data)

    with open(meta_path, 'w') as f:
        json.dump({"hash": baseline_hash}, f)

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
                    report = generate_report(path, changes)
                    report_file = save_report(report)

                    print(f"[⚠️] Changes detected in {path}. Report saved at: {report_file}")

                    for change in changes:
                        print("   ", change["type"], ":", change["file"])

                    # 🔥 also update baseline (same fix as CLI)
                    save_baseline(current, baseline_path)
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
            report = generate_report(monitor_path, changes)
            report_file = save_report(report)

            print(f"[⚠️] Changes detected. Report saved at: {report_file}")

            for change in changes:
                print("!!", change["type"], ":", change["file"])

            save_baseline(all_current_hashed, baseline_path)
        else:
            print("[✓] No changes detected")

if __name__ == "__main__":
    main()