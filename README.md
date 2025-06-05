# 🛡️ File Integrity Monitoring (FIM) Tool

A lightweight, customizable, and user-friendly CLI-based File Integrity Monitoring Tool developed in Python to detect unauthorized changes in system files. This tool helps in ensuring system security and data integrity by tracking content.

## 🔍 Features

- 📁 Scan and monitor selected directories
- 🔐 Detect unauthorized modifications using SHA-256 hashing
- 📊 Display file change alert
- 🧠 CLI with options to add/view/delete monitored paths
- 🔁 Background monitoring for real-time protection

## 🧪 How It Works

1. **Baseline Creation**: The tool stores SHA-256 hashes and permissions of files in selected directories.
2. **Monitoring**: On subsequent scans or in background mode, it compares current file states with the baseline.
3. **Alerting**: If any changes are found (content), it prints alerts on the console.
4. **CLI Menu**: Users can interactively choose options to scan, add paths, view/delete saved paths, or run in background mode.

## ⚙️ Technology Stack

- **Language**: Python 3.x
- **Hashing**: SHA-256 from `hashlib`
- **OS Integration**: `os`, `stat`
- **Data Handling**: JSON files for saving path info and baselines
- **CLI Interaction**: Built-in input/output, cross-platform compatibility
- 
## 🚀 Installation & Usage

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/file-integrity-monitor.git
cd file-integrity-monitor
```

### Step 2: Open the folder via Command prompt
```bash
python fim.py
```
