# 3DP Cost Calculator

A Tkinter desktop app for estimating 3D print pricing, managing filament materials, previewing receipts, and exporting order reports.

## Features

- Calculate print price from material, weight in grams, and print time in hours.
- Store editable filament profiles with wattage and price-per-gram values.
- Configure electricity rate and setup fee.
- Preview calculated pricing before export.
- Export receipts as PNG or PDF files.
- Generate monthly revenue reports as CSV files.
- Reload the most recent receipt inputs.
- Toggle between light and dark UI themes.

## Requirements

- Python 3.10 or newer
- Tkinter, usually included with standard Python desktop installs
- Pillow for image handling
- ReportLab for PDF generation

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running Locally

Start the app from the repository root:

```bash
python main.py
```

On startup, the app initializes its SQLite database and creates these runtime folders when missing:

- `Data/` for `3DP_Database.db`
- `Receipts/` for exported PNG and PDF receipts
- `Reports/` for monthly CSV reports

These folders contain generated local data and should not be treated as source files.

## Project Structure

```text
.
├── main.py                # Main Tkinter application
├── logic.py               # Pricing calculation logic
├── database.py            # SQLite schema and data access
├── config.py              # Runtime and asset paths
├── export.py              # PNG, PDF, and CSV export helpers
├── report_handler.py      # Monthly report workflow
├── settings.py            # Settings window
├── material_manager.py    # Material add/delete window
├── preview.py             # Receipt preview window
└── Assets/                # Logo and toolbar icons
```

## Quick Checks

Run a syntax check across the Python modules:

```bash
python -m compileall main.py logic.py database.py config.py export.py report_handler.py settings.py material_manager.py preview.py tests
```

Run the automated tests:

```bash
python -m pytest
```

The current tests focus on pricing logic. For UI or export changes, manually run the app, calculate a sample order, export a receipt, and generate a report when records are available.

## Continuous Integration

GitHub Actions runs on pull requests and pushes to `main` or `master`. The CI checks Windows and Linux with Python 3.10 and 3.12, then runs an additional Fedora container job to stay close to the Fedora development environment.

Each job installs `requirements.txt`, compiles the Python modules, and runs `pytest`. Keep shared validation in CI so contributors on Fedora and Windows catch the same issues before merging.

## Packaging

The code includes PyInstaller-compatible resource path handling. A typical one-file desktop build is:

```bash
pyinstaller --onefile --windowed --add-data "Assets:assets" main.py
```

On Windows, use a semicolon in `--add-data`:

```bash
pyinstaller --onefile --windowed --add-data "Assets;assets" main.py
```

## Building a Linux Executable and Launcher Shortcut

From a Linux system such as Fedora, install the app dependencies and PyInstaller:

```bash
python -m pip install -r requirements.txt pyinstaller
```

Build the executable from the repository root:

```bash
pyinstaller --onefile --windowed --name 3dp-cost-calculator --add-data "Assets:assets" main.py
```

The executable will be created at:

```text
dist/3dp-cost-calculator
```

Run it with:

```bash
./dist/3dp-cost-calculator
```

Install it into your user app launcher:

```bash
bash scripts/install-linux-desktop.sh
```

This copies the executable to `~/.local/share/3dp-cost-calculator/`, installs the icon, and creates a `.desktop` entry under `~/.local/share/applications/`. After that, search for `3DP Cost Calculator` from the desktop application launcher.

When launched, the installed executable creates `Data/`, `Receipts/`, and `Reports/` beside itself. Build artifacts such as `build/`, `dist/`, and `.spec` files are ignored by Git.

## Building a Windows Executable and Shortcuts

From PowerShell on Windows, install dependencies and PyInstaller:

```powershell
python -m pip install -r requirements.txt pyinstaller
```

Build the executable:

```powershell
pyinstaller --onefile --windowed --name 3dp-cost-calculator --add-data "Assets;assets" main.py
```

The executable will be created at:

```text
dist\3dp-cost-calculator.exe
```

Create Start Menu and Desktop shortcuts:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-windows-shortcut.ps1
```

After that, search for `3DP Cost Calculator` in the Windows Start Menu or launch it from the Desktop shortcut.

The script copies the executable to `%LOCALAPPDATA%\3DP Cost Calculator\` before creating shortcuts, so the shortcut does not depend on the repository `dist\` folder staying in place.

## Notes

Default materials and settings are inserted automatically when the database is empty. Keep new filesystem paths in `config.py` so script and packaged-executable behavior stays consistent.
