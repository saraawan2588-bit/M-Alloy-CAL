# Desktop conversion architecture

## Branch and compatibility strategy

The desktop conversion is developed on `desktop-conversion`. The `main` branch remains
the existing Streamlit web application. The desktop app is a separate entry point and does
not replace `app.py`.

## Shared components

- Calculation logic: root-level `calculator.py`
- Alloy reference data: `data/aluminium_cast_alloys.json`
- Desktop UI: `desktop/` (PySide6)
- Web UI: `app.py` (Streamlit)
- Desktop packaging: `packaging/` (PyInstaller)

Both interfaces must call the same tested calculation functions. Do not fork or duplicate
the mass-balance equations into the GUI layer.

## Release direction

1. Port the complete multi-element workflow to PySide6.
2. Add automated tests that run against the shared engine independently of either UI.
3. Bundle all runtime dependencies and reference data.
4. Build and test a Windows installer on a clean offline Windows machine.
5. Add MSIX packaging and Microsoft Store submission assets after the desktop workflow
   and offline acceptance tests pass.

## Scientific-data caution

The current starter alloy records are explicitly marked as not yet fully cross-checked
against every applicable ASTM product specification. The desktop interface must preserve
those warnings and must not imply standards certification.
