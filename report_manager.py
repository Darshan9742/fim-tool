import json
from datetime import datetime
from pathlib import Path

REPORTS_DIR = "reports"

def generate_report(path, changes):
    return {
        "timestamp": datetime.now().isoformat(),
        "path": path,
        "changes": changes
    }

def save_report(report):
    Path(REPORTS_DIR).mkdir(exist_ok=True)

    filename = f"{REPORTS_DIR}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump(report, f, indent=4)

    return filename