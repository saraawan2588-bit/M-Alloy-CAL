# M-Alloy-CAL

A browser-based master-alloy and charge calculator built with Python and Streamlit.

## Current prototype

The guided workflow includes a starter set of registered aluminium casting alloy records:
- 3xx.x: A356.0, 356.0, 319.0
- 4xx.x: B413.0, 443.0
- 5xx.x: 535.0

The calculator's **addition-element selector contains all 118 chemical elements**, including modifiers and microalloying elements such as Sr, Na, Sb, P, B, Ti, Zr and rare-earth elements. The operator selects the elements to balance, then enters target concentration, base-metal assay and supplier-certified master-alloy assays. This does not mean every element is suitable for aluminium foundry use or is available as a master alloy.

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

## Units and precision

- Charge masses are displayed in **kg**, rounded to 0.01 kg for readability.
- Composition values are entered in **wt.%**.
- Low-level elements not present in the selected grade's main chemistry table use four decimal places in input fields.
- 1 wt.% = 10,000 ppm. Convert ppm to wt.% before entry.
- The calculation engine retains full floating-point precision internally; displayed rounding does not change the calculation.
- Always use plant-approved weighing increments and validated process recoveries.

## Operator guidance and warnings

The application contains four tabs: Charge calculator, How to use, Warnings & troubleshooting, and Calculation audit. The audit tab documents the mass-balance equations, defines symbols and units, gives a worked Al–50Si example, independently reconstructs the latest result from its charge masses, and provides links to standards and technical references.

The current solver requires at least as many master alloys as controlled elements and searches exact square subsets. It may reject a blend if no non-negative, compositionally independent solution is available. A mathematically feasible result is not necessarily a metallurgically suitable treatment.

## Data sources and standard links

The starter chemistry entries are transcribed from The Aluminum Association's *Designations and Chemical Composition Limits for Aluminum Alloys in the Form of Castings and Ingot* (Pink Sheets, revised August 2025):
https://www.aluminum.org/sites/default/files/2025-10/Pink%20Sheets%202025.pdf

The Pink Sheets are a registration record maintained by The Aluminum Association. **They are not ASTM standards.** The UI links to ASTM's official catalogue pages for the product route selected:

- [ASTM B26/B26M-25 — Aluminum-Alloy Sand Castings](https://store.astm.org/b0026_b0026m-25.html)
- [ASTM B108/B108M-25 — Aluminum-Alloy Permanent Mold Castings](https://store.astm.org/b0108_b0108m-25.html)
- [ASTM B85/B85M-25 — Aluminum-Alloy Die Castings](https://store.astm.org/b0085_b0085m-25.html)
- [ASTM B179-26 — Aluminum Alloys in Ingot and Molten Forms](https://store.astm.org/b0179-26.html)

These links open ASTM's official catalogue pages; the full standards may require purchase or authorized access. The current database entries are **not ASTM-verified**. Confirm the exact grade, process route, edition, full table, footnotes, trace elements, mechanical properties, sampling, testing, and purchaser/producer requirements against the applicable standard.

## Calculation model and limitations

For a final batch mass `M`, base-metal composition `b_j`, target composition `t_j`, and selected master-alloy compositions `a_ij`, the engine solves:

```
sum_i m_i (a_ij - b_j) = M (t_j - b_j)
```

Compositions are wt.% and masses are kg. The engine searches exact square subsets of the selected master alloys and accepts a non-negative solution that leaves non-negative base metal. If no exact feasible combination exists, it reports an error.

The current model does not account for element recovery, oxidation, fading, dross/slag losses, melt loss, evaporation, charge contamination, unentered trace elements, assay uncertainty, or economic optimization. It balances only the elements selected by the operator. It does not certify full alloy chemistry compliance or determine whether a modifier treatment is effective or compatible with the process.

**Do not use the tool as a production charge instruction until the data, calculation model, recoveries, process controls and results have been reviewed and validated by qualified metallurgical personnel.**

## Planned next steps

1. Complete the cast-alloy family catalogue across 1xx, 2xx, 3xx, 4xx, 5xx, 7xx, 8xx, and 9xx groups.
2. Verify each grade against the applicable licensed current ASTM specification and record exact edition/year, table, footnotes, and product route.
3. Add a master-alloy catalogue with supplier assay and lot traceability.
4. Add element recovery factors, melt-loss/yield corrections, and process-specific controls.
5. Add charge-sheet export, operator language support, and plant validation.


## Calculation audit and weight-loss equations

The **Calculation audit** tab provides the equations needed to check the software's ideal charge calculation by hand:

- Total mass: `M = m0 + sum(mi)`
- Base-metal mass: `m0 = M - sum(mi)`
- Element mass from the base: `mE,base = m0 × bE / 100`
- Element mass from additions: `mE,additions = sum[mi × ai,E / 100]`
- Final element concentration: `CE = 100 × mE,total / M`
- Solver balance: `sum[mi × (ai,E - bE)] = M × (tE - bE)`

Here, M and mi are in kg; bE, ai,E, and tE are numerical wt.% values. The audit tab also stores the most recent calculation in the Streamlit session and independently reconstructs total charge mass and the mass/concentration of each selected element from the returned charge quantities.

### Weight loss and recovery are not included in the present solver

For a separately measured overall metal yield:

- `Y = recovered metal mass / charged mass`
- `metal loss (%) = 100 × (1 - Y)`
- `required charge mass = required recovered metal mass / Y`

For element-specific recovery:

- `RE = retained element mass in metal / charged element mass`
- `retained element mass = RE × charged element mass`

These equations are explanatory only. The current solver assumes ideal 100% retention and does **not** apply Y or RE. Metal yield and element-specific recovery are not interchangeable; use plant-validated data and a separately validated recovery-aware model before including them in production charge calculations.


## Production route and calculation basis

At the top of the calculator, the operator chooses two independent settings:

1. **Composition route**
   - **Registered grade target:** targets for listed grade elements are constrained to the chemistry ranges in the starter database. These records are sourced from The Aluminum Association Pink Sheets (August 2025); they are not independently certified as ASTM-compliant.
   - **Modified / custom composition:** permits user-entered targets outside the recorded ranges. This does not mean the modified chemistry complies with the alloy standard, customer specification or casting process requirements.

2. **Calculation basis**
   - **Ideal theoretical:** assumes 100% retention. The sum of base metal and master-alloy additions equals the required final batch mass.
   - **Actual process-adjusted:** treats the requested batch as recovered final metal. It calculates gross charge using a user-entered measured overall metal yield and uses a measured recovery percentage for each selected element. The operator must confirm that these values come from validated, comparable process data.

### Actual-mode equations and limitations

- Overall metal yield: `Y = final recovered metal mass / gross charged mass`
- Gross charge: `Mcharge = Mfinal / Y`
- Base-metal charge: `m0 = Mcharge - sum(master-alloy additions)`
- Element recovery: `RE = retained mass of element E / charged mass of element E`
- Final element concentration: `CE = 100 × RE × charged mass of E / Mfinal`

The measured overall yield is intended to include the combined net effect of metal losses such as oxidation, dross, slag removal/carry-over and transfer losses. Do **not** subtract those losses a second time if they are already included in the yield. Element-specific recovery is separate from overall metal yield.

This mode does not independently calculate the mass or chemistry of oxide, dross, slag or other individual loss streams, nor does it predict yield or recovery. It is a process-adjusted calculation based on user-provided measured factors. If suitable data are unavailable, use ideal mode for theoretical study only; do not guess actual-mode inputs.
