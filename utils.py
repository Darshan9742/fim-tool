import hashlib
import os
import json
from pathlib import Path
from datetime import datetime

def calculate_baseline_hash(data):
    data_string = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(data_string).hexdigest()

def calculate_hash(file_path, algo='sha256'):
    h = hashlib.new(algo)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def detect_changes(current, baseline):
    changes = []

    for path, meta in current.items():
        if path not in baseline:
            changes.append({"type": "NEW", "file": path})

        elif baseline[path]["hash"] != meta["hash"]:
            changes.append({
                "type": "MODIFIED",
                "file": path,
                "last_modified": meta["last_modified"]
            })

    for path in baseline:
        if path not in current:
            changes.append({"type": "DELETED", "file": path})

    return changes

def scan_directory(path, exclude_exts, algo):
    file_info = {}

    for root, _, files in os.walk(path):
        for file in files:
            if any(file.endswith(ext) for ext in exclude_exts):
                continue

            full_path = Path(root) / file

            try:
                normalized_path = str(full_path.resolve())
                stat = full_path.stat()

                file_info[normalized_path] = {
                    "hash": calculate_hash(full_path, algo),
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }

            except Exception as e:
                print(f"Error reading {full_path}: {e}")

    return file_info