# M-Alloy-CAL Desktop

This is the separate Windows desktop interface. It deliberately reuses the root-level
`calculator.py` calculation engine and `data/aluminium_cast_alloys.json` database.
The Streamlit web interface remains in `app.py` and is not replaced by this desktop app.

## Development setup (Windows)

Use Python 3.10 or newer:

```powershell
py -m venv .venv-desktop
.\.venv-desktop\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-desktop.txt
python -m desktop.main
```

## Build a Windows executable

From the repository root, with the desktop environment activated:

```powershell
pyinstaller --clean packaging/m_alloy_cal.spec
```

The executable is written under `dist\M-Alloy-CAL.exe`.

## Offline design

- The alloy database is loaded from the local repository/bundle.
- The calculation engine is imported from the local `calculator.py`.
- No web server, hosted database, API, or runtime package download is used by the desktop shell.

## Current implementation status

The initial desktop foundation includes the application shell, local alloy database browser,
and a shared-engine smoke test. The full multi-element calculator workflow, process-adjusted
inputs, audit view, PDF export, installer signing, MSIX packaging and clean-machine offline
validation are still planned work. Do not treat this initial shell as a production-ready release.
