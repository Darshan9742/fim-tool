import json
import argparse
from pathlib import Path

from utils import scan_directory, detect_changes, calculate_baseline_hash
from config_manager import load_config, save_config
from report_manager import generate_report, save_report


def get_baseline_path(folder_path):
    safe_name = folder_path.replace(":", "").replace("\\", "_").replace("/", "_")
    return f"baseline_{safe_name}.json"


# 🔐 UPDATED — WITH INTEGRITY CHECK
def load_baseline(path):
    if not Path(path).exists():
        return {}

    with open(path) as f:
        data = json.load(f)

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
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

    meta_path = path + ".meta"
    baseline_hash = calculate_baseline_hash(data)

    with open(meta_path, 'w') as f:
        json.dump({"hash": baseline_hash}, f)


def update_config(new_path):
    config = load_config()
    if new_path not in config["monitor_paths"]:
        config["monitor_paths"].append(new_path)
        save_config(config)
        print(f"[✓] Added {new_path}")
    else:
        print("[!] Path already exists.")


def delete_path(del_path):
    config = load_config()
    if del_path in config["monitor_paths"]:
        config["monitor_paths"].remove(del_path)
        save_config(config)
        print(f"[✓] Removed {del_path}")
    else:
        print("[!] Path not found.")


# 🔥 FIXED scan_path
def scan_path(path):
    if not Path(path).exists():
        print(f"[!] Path does not exist: {path}")
        return

    config = load_config()

    current = scan_directory(path, config["excluded_extensions"], config["hash_algo"])
    baseline_path = get_baseline_path(path)
    baseline = load_baseline(baseline_path)

    if not baseline:
        print("[+] No baseline found. Saving current state.")
        save_baseline(current, baseline_path)
        return

    print(f"[*] Comparing {path} with baseline...")
    changes = detect_changes(current, baseline)

    if changes:
        report = generate_report(path, changes)
        report_file = save_report(report)

        print(f"[⚠️] Changes detected. Report saved at: {report_file}")

        for change in changes:
            print("!!", change["type"], ":", change["file"])

        # 🔥 update baseline
        save_baseline(current, baseline_path)

    else:
        print("[✓] No changes detected")


def scan_all():
    config = load_config()
    for path in config["monitor_paths"]:
        print(f"\n[🔍] Scanning: {path}")
        scan_path(path)


def view_paths():
    config = load_config()
    for p in config["monitor_paths"]:
        print("-", p)


def main():
    parser = argparse.ArgumentParser(description="File Integrity Monitoring Tool")

    parser.add_argument("--add")
    parser.add_argument("--delete")
    parser.add_argument("--view", action="store_true")
    parser.add_argument("--scan")
    parser.add_argument("--scan-all", action="store_true")

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