# Repository Guidelines

## Project Structure & Module Organization

This is a small Tkinter desktop app for calculating 3D print prices. Core modules live at the repository root:

- `main.py` starts the UI and wires windows together.
- `logic.py` contains pricing calculations.
- `database.py` manages SQLite access and default data.
- `export.py` and `report_handler.py` generate receipts and monthly CSV reports.
- `settings.py`, `material_manager.py`, and `preview.py` define secondary windows.
- `config.py` centralizes paths for runtime folders and bundled assets.
- `Assets/` stores UI images such as `Logo.png` and toolbar icons.

At runtime, the app creates `Data/`, `Receipts/`, and `Reports/` beside the script or executable. Treat these as generated output, not source code.

## Build, Test, and Development Commands

- `python main.py` runs the desktop app locally.
- `python -m compileall main.py logic.py database.py config.py export.py report_handler.py settings.py material_manager.py preview.py tests` performs a cross-platform syntax check.
- `python -m pip install -r requirements.txt` installs app and test dependencies.
- `pyinstaller --onefile --windowed --add-data "Assets:assets" main.py` builds a standalone app on Linux/macOS-style shells. On Windows, use `Assets;assets` for the `--add-data` separator.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Keep module names lowercase with underscores when needed. Use `snake_case` for functions and variables, and `PascalCase` for Tkinter window classes such as `CalculatorApp` and `SettingsWindow`. Prefer central path constants from `config.py` over hardcoded paths. Keep UI callbacks short; move reusable calculation, persistence, or export logic into the existing helper modules.

## Testing Guidelines

Automated tests use `pytest` and currently focus on pricing logic under `tests/`. For logic changes, add focused tests using names like `test_logic.py` and `test_calculates_total_cost()`. For UI or export changes, at minimum run `python main.py`, calculate a sample receipt, export PNG/PDF output, and generate a monthly report when records exist.

## Commit & Pull Request Guidelines

Existing commits use short, imperative summaries, for example `Create README.md` and `Ready to deploy as .exe`. Follow that style with concise subject lines that describe the user-visible change. Pull requests should include a brief description, manual test steps, screenshots for visible UI changes, and notes about any generated files or packaging changes.

## Security & Configuration Tips

Do not commit generated `Data/`, `Receipts/`, or `Reports/` contents. Keep database writes parameterized as in `database.py`, and route new filesystem paths through `config.py` so development and PyInstaller builds behave consistently.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
