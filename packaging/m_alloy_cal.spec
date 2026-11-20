# PyInstaller spec for the Windows desktop build.
# Run from the repository root:
#   pyinstaller --clean packaging/m_alloy_cal.spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

# Resolve safely whether SPECPATH is provided as the spec directory or file path.
_spec_location = Path(SPECPATH).resolve()
_candidates = [_spec_location, _spec_location.parent, _spec_location.parent.parent]
ROOT = next((path for path in _candidates if (path / "desktop" / "main.py").is_file()), None)
if ROOT is None:
    raise RuntimeError("Could not locate the M-Alloy-CAL repository root from the spec file.")
hiddenimports = collect_submodules("PySide6")

a = Analysis(
    [str(ROOT / "desktop" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "data" / "aluminium_cast_alloys.json"), "data"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["streamlit"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="M-Alloy-CAL",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
