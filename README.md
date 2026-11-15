# M-Alloy-CAL

A simple, browser-based master-alloy charge calculator built with Python and Streamlit.

## Current prototype

The guided workflow currently supports a starter aluminium casting alloy database:

1. Select an alloy (currently A356.0, 356.0, or 319.0).
2. Choose a casting/supply route.
3. Enter the required final batch weight.
4. Select target chemistry within the displayed registered ranges.
5. Enter the measured chemistry of base metal/returns.
6. Enter the assay of available master alloys.
7. Calculate master-alloy additions and remaining base-metal mass.

The calculation engine uses only the Python standard library. Streamlit is the only application dependency.

## Run locally

Requires Python 3.9 or newer.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Aluminium database scope and source discipline

The initial casting-grade records are transcribed from The Aluminum Association's *Designations and Chemical Composition Limits for Aluminum Alloys in the Form of Castings and Ingot* (Pink Sheets, revised August 2025). The public source is linked in `data/aluminium_cast_alloys.json`.

Important: the Aluminum Association Pink Sheets are not ASTM standards. ASTM product specifications depend on product form/process route. Candidate routes shown in the interface are ASTM B26/B26M for sand castings, ASTM B108/B108M for permanent-mold castings, and ASTM B179 for ingot/molten alloy supply. The current licensed ASTM editions must be checked for exact grade chemistry, mechanical/property requirements, sampling, testing, and all applicable notes before the database can be labelled ASTM-verified.

The starter records contain selected chemistry fields and do not yet reproduce every trace-element limit or every footnote. They are for prototype and educational testing only, not production charge instructions. ASTM and Aluminum Association publications are copyrighted; use authorized copies and do not scrape or redistribute complete standards.

## Calculation model and limitations

For a final batch mass \(M\), base-metal composition \(b_j\), target composition \(t_j\), and selected master-alloy compositions \(a_{ij}\), the engine solves:

\[
\sum_i m_i(a_{ij}-b_j)=M(t_j-b_j)
\]

Compositions are wt.% and additions are kg. The engine searches exact square subsets of the selected master alloys and accepts a non-negative solution that leaves non-negative base metal. If no exact feasible combination exists, it reports an error.

The current model does not account for element recovery, oxidation, dross/slag losses, melt loss, charge contamination, unentered trace elements, or uncertainty in assay. It also does not yet optimize among multiple feasible solutions.

## Planned next steps

- Cross-check each grade against the applicable licensed current ASTM specification and record edition/year and exact clause/table.
- Expand cast alloy coverage (e.g., A380, 413, 535) and add wrought alloys as a separate product-form family.
- Add a master-alloy catalogue (Al-Si, Al-Cu, Al-Mg, Al-Mn, Al-Ti-B, Al-Sr, etc.) with supplier assay and lot traceability.
- Add recovery factors per element and process, plus melt-loss/yield corrections.
- Add a constrained optimization engine to choose economical additions from multiple available materials.
- Add charge-sheet export, language support, operator-friendly icons, and plant validation.
- Complete metallurgical review and validation before production use.
