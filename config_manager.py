import json
from pathlib import Path

CONFIG_PATH = "config.json"

def load_config():
    if not Path(CONFIG_PATH).exists():
        return {
            "monitor_paths": [],
            "excluded_extensions": [],
            "hash_algo": "sha256",
            "scan_interval": 60
        }

    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)