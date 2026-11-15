# M-Alloy-CAL

A simple browser-based master-alloy and charge calculator built with Python and Streamlit.

## Current prototype

The guided workflow currently includes a starter set of registered aluminium casting alloy records:
- 3xx.x: A356.0, 356.0, 319.0
- 4xx.x: B413.0, 443.0
- 5xx.x: 535.0

The alloy series follow the Aluminum Association cast-alloy designation system. This is **not yet a complete catalogue of every registered casting alloy**. In particular, 2xx.x, 7xx.x, 8xx.x, 9xx.x, and additional 1xx.x / 3xx.x / 4xx.x / 5xx.x grades still need to be added and checked.

## Run locally

Requires Python 3.9 or newer.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Run the calculation-engine tests:

```powershell
python -m unittest discover -s tests -v
```

## Units and displayed precision

- Charge masses are displayed in **kg**, rounded to 0.01 kg for readability.
- Composition values are entered and displayed in **wt.%**.
- The calculation engine retains full floating-point precision internally; displayed rounding does not change the calculation.
- Always use plant-approved weighing increments and validated process recoveries.

## Data sources and standard links

The starter chemistry entries are transcribed from The Aluminum Association's *Designations and Chemical Composition Limits for Aluminum Alloys in the Form of Castings and Ingot* (Pink Sheets, revised August 2025):
https://www.aluminum.org/sites/default/files/2025-10/Pink%20Sheets%202025.pdf

The Pink Sheets are a registration record maintained by The Aluminum Association. **They are not ASTM standards.** The UI links to ASTM's official catalogue pages for the product route selected:

- [ASTM B26/B26M-25 — Aluminum-Alloy Sand Castings](https://store.astm.org/b0026_b0026m-25.html)
- [ASTM B108/B108M-25 — Aluminum-Alloy Permanent Mold Castings](https://store.astm.org/b0108_b0108m-25.html)
- [ASTM B85/B85M-25 — Aluminum-Alloy Die Castings](https://store.astm.org/b0085_b0085m-25.html)
- [ASTM B179-26 — Aluminum Alloys in Ingot and Molten Forms](https://store.astm.org/b0179-26.html)

These links open ASTM's official catalogue pages; the full standards may require purchase or authorized access. The current database entries are **not ASTM-verified**. Do not infer that the Pink Sheets chemistry alone establishes conformance to a product specification. Confirm the exact grade, process route, edition, full table, footnotes, trace elements, mechanical properties, sampling, testing, and purchaser/producer requirements against the applicable standard.

## Calculation model and limitations

For a final batch mass `M`, base-metal composition `b_j`, target composition `t_j`, and selected master-alloy compositions `a_ij`, the engine solves:

```
sum_i m_i (a_ij - b_j) = M (t_j - b_j)
```

Compositions are wt.% and masses are kg. The engine searches exact square subsets of the selected master alloys and accepts a non-negative solution that leaves non-negative base metal. If no exact feasible combination exists, it reports an error.

The current model does not account for element recovery, oxidation, dross/slag losses, melt loss, charge contamination, unentered trace elements, assay uncertainty, or economic optimization. It also solves only the elements selected by the operator. A result is not a complete chemistry compliance certificate or a production instruction.

## Planned next steps

1. Complete the cast-alloy family catalogue across 1xx, 2xx, 3xx, 4xx, 5xx, 7xx, 8xx, and 9xx groups.
2. Verify each grade against the applicable licensed current ASTM specification and record exact edition/year, table, footnotes, and product route.
3. Add master-alloy catalogue records with supplier assay and lot traceability.
4. Add element recovery factors, melt-loss/yield corrections, and process-specific controls.
5. Add charge-sheet export, operator language support, and plant validation.

The project is a prototype for education and workflow development. It must undergo metallurgical review and plant validation before production use.
