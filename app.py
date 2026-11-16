import json
from pathlib import Path

import streamlit as st

from calculator import calculate_blend, CalculationError

st.set_page_config(
    page_title="M-Alloy-CAL | Foundry Charge Calculator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).parent / "data" / "aluminium_cast_alloys.json"
with DATA_PATH.open(encoding="utf-8") as data_file:
    database = json.load(data_file)

# Complete periodic-table selector: symbol and element name.
ELEMENTS = [
    ("H","Hydrogen"),("He","Helium"),("Li","Lithium"),("Be","Beryllium"),("B","Boron"),("C","Carbon"),("N","Nitrogen"),("O","Oxygen"),("F","Fluorine"),("Ne","Neon"),
    ("Na","Sodium"),("Mg","Magnesium"),("Al","Aluminium"),("Si","Silicon"),("P","Phosphorus"),("S","Sulfur"),("Cl","Chlorine"),("Ar","Argon"),("K","Potassium"),("Ca","Calcium"),
    ("Sc","Scandium"),("Ti","Titanium"),("V","Vanadium"),("Cr","Chromium"),("Mn","Manganese"),("Fe","Iron"),("Co","Cobalt"),("Ni","Nickel"),("Cu","Copper"),("Zn","Zinc"),
    ("Ga","Gallium"),("Ge","Germanium"),("As","Arsenic"),("Se","Selenium"),("Br","Bromine"),("Kr","Krypton"),("Rb","Rubidium"),("Sr","Strontium"),("Y","Yttrium"),("Zr","Zirconium"),
    ("Nb","Niobium"),("Mo","Molybdenum"),("Tc","Technetium"),("Ru","Ruthenium"),("Rh","Rhodium"),("Pd","Palladium"),("Ag","Silver"),("Cd","Cadmium"),("In","Indium"),("Sn","Tin"),
    ("Sb","Antimony"),("Te","Tellurium"),("I","Iodine"),("Xe","Xenon"),("Cs","Caesium"),("Ba","Barium"),("La","Lanthanum"),("Ce","Cerium"),("Pr","Praseodymium"),("Nd","Neodymium"),
    ("Pm","Promethium"),("Sm","Samarium"),("Eu","Europium"),("Gd","Gadolinium"),("Tb","Terbium"),("Dy","Dysprosium"),("Ho","Holmium"),("Er","Erbium"),("Tm","Thulium"),("Yb","Ytterbium"),
    ("Lu","Lutetium"),("Hf","Hafnium"),("Ta","Tantalum"),("W","Tungsten"),("Re","Rhenium"),("Os","Osmium"),("Ir","Iridium"),("Pt","Platinum"),("Au","Gold"),("Hg","Mercury"),
    ("Tl","Thallium"),("Pb","Lead"),("Bi","Bismuth"),("Po","Polonium"),("At","Astatine"),("Rn","Radon"),("Fr","Francium"),("Ra","Radium"),("Ac","Actinium"),("Th","Thorium"),
    ("Pa","Protactinium"),("U","Uranium"),("Np","Neptunium"),("Pu","Plutonium"),("Am","Americium"),("Cm","Curium"),("Bk","Berkelium"),("Cf","Californium"),("Es","Einsteinium"),("Fm","Fermium"),
    ("Md","Mendelevium"),("No","Nobelium"),("Lr","Lawrencium"),("Rf","Rutherfordium"),("Db","Dubnium"),("Sg","Seaborgium"),("Bh","Bohrium"),("Hs","Hassium"),("Mt","Meitnerium"),("Ds","Darmstadtium"),
    ("Rg","Roentgenium"),("Cn","Copernicium"),("Nh","Nihonium"),("Fl","Flerovium"),("Mc","Moscovium"),("Lv","Livermorium"),("Ts","Tennessine"),("Og","Oganesson")
]
ELEMENT_LABELS = [f"{symbol} — {name}" for symbol, name in ELEMENTS]
ELEMENT_NAME = dict(ELEMENTS)

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 1.8rem; padding-bottom: 3rem;}
.hero {padding: 1.35rem 1.5rem; border-radius: 16px; background: linear-gradient(115deg,#102b3f,#1d5266); color: white; margin-bottom: 1rem;}
.hero h1 {color: white; margin: 0 0 .25rem 0; font-size: 2rem;}
.hero p {color: #e5f1f5; margin: 0; font-size: 1rem;}
div[data-testid="stMetric"] {background: #f3f7f9; border: 1px solid #dce7ec; padding: .8rem 1rem; border-radius: 12px;}
div.stButton > button[kind="primary"] {min-height: 3.25rem; font-size: 1.08rem; font-weight: 700; border-radius: 10px;}
div[data-testid="stExpander"] {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>⚙️ M-Alloy-CAL</h1>'
    '<p>Master-alloy and charge calculator · Aluminium foundry edition</p></div>',
    unsafe_allow_html=True,
)
st.write("Calculate an ideal charge using your target chemistry, base-metal assay, and available master alloys.")

st.warning(
    "Prototype / educational use only. The alloy-grade chemistry records are transcribed from "
    "The Aluminum Association Pink Sheets (August 2025), not certified against the applicable ASTM edition. "
    "This calculator does not replace melt-treatment procedures or metallurgical approval."
)

calculator_tab, guide_tab, warnings_tab, audit_tab = st.tabs(
    ["⚙️  Charge calculator", "📘  How to use", "⚠️  Warnings & troubleshooting", "🧮  Calculation audit"]
)

with calculator_tab:
    alloys = database["alloys"]
    series_labels = sorted({a.get("series", "Other") for a in alloys})
    series_filter = st.selectbox("Filter by cast-alloy series", ["All series"] + series_labels)
    visible_alloys = alloys if series_filter == "All series" else [
        a for a in alloys if a.get("series", "Other") == series_filter
    ]
    selected = st.selectbox(
        "1 · Select the alloy to manufacture",
        visible_alloys,
        format_func=lambda a: f'{a["designation"]}  ·  {a["family"]}',
    )
    st.caption(
        f'Alloy series: {selected.get("series", "Not classified")}  |  '
        f'Product form: {selected["product_form"]}'
    )
    with st.expander("How cast-alloy series are grouped"):
        st.markdown("\n".join(
            f"- **{series}** — {description}"
            for series, description in database.get("series_reference", {}).items()
        ))

    standard_links = {
        "ASTM B26/B26M": "https://store.astm.org/b0026_b0026m-25.html",
        "ASTM B108/B108M": "https://store.astm.org/b0108_b0108m-25.html",
        "ASTM B85/B85M": "https://store.astm.org/b0085_b0085m-25.html",
        "ASTM B179": "https://store.astm.org/b0179-26.html",
    }
    route_options = selected.get("astm_route_candidates", [])
    if route_options:
        route = st.selectbox("Casting / supply route", route_options)
        route_code = route.split(" — ")[0]
        if route_code in standard_links:
            st.link_button(f"Open official {route_code} standard page", standard_links[route_code])
    else:
        st.info("No product route is recorded for this entry. Confirm the applicable specification with your metallurgist.")

    with st.expander("Registered alloy chemistry limits · wt.%", expanded=False):
        rows = [
            {"Element": element, "Min (wt.%)": limits["min"], "Max (wt.%)": limits["max"]}
            for element, limits in selected["elements"].items()
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.write(f'Aluminium: **{selected["aluminium"]}**')
        each_limit = selected.get("other_elements_each_max")
        each_text = f"each ≤ {each_limit} wt.%" if each_limit is not None else "individual limit not separately stated in this record"
        st.write(f'Other elements: {each_text}; total ≤ {selected["other_elements_total_max"]} wt.%.')
        st.caption(
            f'Source: {selected["chemistry_source"]}, page {selected["chemistry_source_page"]}. '
            f'{selected["notes"]}'
        )

    st.divider()
    st.markdown("### 2 · Required batch and target chemistry")
    left, right = st.columns([1, 2])
    with left:
        batch_kg = st.number_input(
            "Required finished batch (kg)", min_value=0.1, value=100.0,
            step=5.0, format="%.2f",
        )
        st.metric("Target batch", f"{batch_kg:,.2f} kg")
    with right:
        st.caption("Target values start at the midpoint of the registered range. Adjust to your approved melt target.")
        grade_target = {}
        target_cols = st.columns(3)
        for idx, (element, limits) in enumerate(selected["elements"].items()):
            midpoint = (limits["min"] + limits["max"]) / 2
            with target_cols[idx % 3]:
                grade_target[element] = st.number_input(
                    f"{element} target (wt.%)",
                    min_value=float(limits["min"]), max_value=float(limits["max"]),
                    value=float(midpoint), step=0.01, format="%.2f",
                    key=f'grade_target_{selected["designation"]}_{element}',
                )

    st.divider()
    st.markdown("### 3 · Select every element you want to adjust")
    st.info(
        "This list is the complete periodic table, not just the elements in the selected grade. "
        "You can therefore add modifiers or microalloying elements such as Sr, Na, Sb, P, B, Ti, Zr "
        "and rare-earth elements (La, Ce, mischmetal constituents, etc.)."
    )
    grade_symbols = list(selected["elements"])
    default_symbols = [e for e in ("Si", "Mg") if e in grade_symbols] or grade_symbols[:1]
    selected_labels = st.multiselect(
        "Elements to calculate from master-alloy additions",
        options=ELEMENT_LABELS,
        default=[f"{s} — {ELEMENT_NAME[s]}" for s in default_symbols],
        max_selections=20,
        help="Choose up to 20 elements whose final concentrations you want the mass balance to meet.",
    )
    controlled_elements = [label.split(" — ")[0] for label in selected_labels]

    if not controlled_elements:
        st.info("Select at least one element to continue to master-alloy entry.")
    else:
        st.caption(
            "For elements in the registered grade table, the initial target comes from the grade target above. "
            "For additional elements (for example Sr), enter a target approved by your foundry/metallurgist."
        )
        target = {}
        base = {}
        input_cols = st.columns(2)
        for idx, element in enumerate(controlled_elements):
            grade_limits = selected["elements"].get(element)
            default_target = grade_target[element] if element in grade_target else 0.0
            with input_cols[idx % 2]:
                target[element] = st.number_input(
                    f"{element} target (wt.%)",
                    min_value=0.0, max_value=100.0, value=float(default_target),
                    step=0.01 if grade_limits else 0.0001,
                    format="%.2f" if grade_limits else "%.4f",
                    key=f'controlled_target_{selected["designation"]}_{element}',
                )
                base[element] = st.number_input(
                    f"{element} in base metal / returns (wt.%)",
                    min_value=0.0, max_value=100.0, value=0.0,
                    step=0.01 if grade_limits else 0.0001,
                    format="%.2f" if grade_limits else "%.4f",
                    key=f'controlled_base_{selected["designation"]}_{element}',
                )

        st.divider()
        st.markdown("### 4 · Master alloys available")
        st.caption(
            "Enter each material's actual assay certificate values. A master alloy can contain more than one "
            "selected element; enter every relevant element shown on its certificate."
        )
        count = st.number_input(
            "Number of master alloys available",
            min_value=len(controlled_elements), max_value=20,
            value=len(controlled_elements), step=1,
            help="The current solver needs at least as many master alloys as controlled elements.",
        )
        master_alloys = []
        master_cols = st.columns(2)
        for i in range(int(count)):
            with master_cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**Master alloy {i + 1}**")
                    name = st.text_input(
                        "Name / grade", value=f"Addition {i + 1}",
                        key=f"master_name_{i}",
                    )
                    composition = {}
                    assay_cols = st.columns(2)
                    for idx, element in enumerate(controlled_elements):
                        with assay_cols[idx % 2]:
                            composition[element] = st.number_input(
                                f"{element} assay (wt.%)",
                                min_value=0.0, max_value=100.0, value=0.0,
                                step=0.01 if element in grade_symbols else 0.0001,
                                format="%.2f" if element in grade_symbols else "%.4f",
                                key=f"master_{i}_{element}",
                            )
                    master_alloys.append({"name": name, "composition": composition})

        st.divider()
        if st.button("⚙️  CALCULATE CHARGE", type="primary", use_container_width=True):
            try:
                result = calculate_blend(
                    batch_kg, controlled_elements, target, base, master_alloys
                )
                st.session_state["last_calculation_audit"] = {
                    "batch_kg": float(batch_kg),
                    "elements": list(controlled_elements),
                    "target": dict(target),
                    "base": dict(base),
                    "master_alloys": [
                        {"name": item["name"], "composition": dict(item["composition"])}
                        for item in master_alloys
                    ],
                    "result": result,
                }
                st.success("Ideal material-balance calculation completed.")
                st.markdown("## Charge sheet")
                charge_rows = [
                    {"Material": "Base metal / returns", "Charge (kg)": round(result["base_metal_kg"], 2)}
                ]
                charge_rows.extend(
                    {"Material": item["name"], "Charge (kg)": round(item["kg"], 2)}
                    for item in result["master_alloys"]
                )
                st.dataframe(charge_rows, use_container_width=True, hide_index=True)
                result_cols = st.columns(min(4, len(result["master_alloys"]) + 1))
                with result_cols[0]:
                    st.metric("Base metal / returns", f'{result["base_metal_kg"]:,.2f} kg')
                for idx, item in enumerate(result["master_alloys"], start=1):
                    with result_cols[idx % len(result_cols)]:
                        st.metric(item["name"], f'{item["kg"]:,.2f} kg')
                st.metric("Final batch mass", f'{result["batch_kg"]:,.2f} kg')

                st.markdown("### Final composition check")
                check_rows = [
                    {
                        "Element": element,
                        "Target (wt.%)": round(target[element], 4),
                        "Calculated (wt.%)": round(achieved, 4),
                        "Difference (wt.%)": round(achieved - target[element], 5),
                    }
                    for element, achieved in result["achieved_wt_pct"].items()
                ]
                st.dataframe(check_rows, use_container_width=True, hide_index=True)
                if result["unused_master_alloys"]:
                    st.info("No addition required from: " + ", ".join(result["unused_master_alloys"]))
                st.warning(
                    "This is an ideal mass balance only. It does not include recovery, fading, oxidation, "
                    "dross/slag losses, melt loss, contamination, treatment interactions, or unentered trace "
                    "elements. Do not use as a production charge instruction without plant validation."
                )
            except CalculationError as exc:
                st.error(f"Calculation could not be completed: {exc}")
                st.info(
                    "Check that every master alloy has a unique name, all assays are correct, enough "
                    "master alloys are entered, and the selected materials can physically reach the target "
                    "without negative additions or exceeding the batch mass."
                )

with guide_tab:
    st.markdown("## How to use M-Alloy-CAL")
    st.markdown("""
### Step 1 — Select the aluminium casting grade
Choose the alloy designation (for example A356.0). Filter by series if helpful. Check the product route and open the linked ASTM catalogue page. The displayed grade chemistry is a starter reference, not proof of ASTM compliance.

### Step 2 — Enter the final batch mass
Enter the required finished metal mass in **kg**. This is the mass of the final batch, not the furnace capacity or gross charge before melt loss.

### Step 3 — Set the target chemistry
For registered grade elements, the initial target is the midpoint of the recorded range. Replace it with your approved melt target. Targets are entered in **wt.%**.

### Step 4 — Select elements to adjust
The selector contains all 118 chemical element symbols and names. Select every element you want the calculator to balance, including optional modifiers and microalloying additions. Examples include Sr, Na, Sb, Ti, B, Zr, La and Ce. An element being selectable does not mean it is suitable for every alloy or process.

### Step 5 — Enter base-metal / returns assay
Enter the measured concentration of each selected element in the base metal. Use a recent spectrometer or laboratory result. Do not assume an element is zero unless the assay supports that assumption.

### Step 6 — Enter available master alloys
Enter a unique material name or grade for each master alloy. For every selected element, enter its concentration from the supplier's certificate in **wt.%**. Enter zero only if the certificate or reliable analysis supports zero / below-detection content. A multi-element master alloy can be entered with more than one non-zero assay.

### Step 7 — Calculate and review the charge sheet
Press **CALCULATE CHARGE**. Review base-metal mass, each master-alloy addition in **kg**, and the calculated versus target composition. Displayed charge masses are rounded to 0.01 kg; composition values retain more displayed precision for low-level additions.

### Example — adding strontium
If you want to calculate an Sr addition, select **Sr — Strontium** in Step 4, enter the approved final Sr target and the measured Sr already present in the base metal, then enter the Sr concentration from the Al-Sr master-alloy certificate. If you are also adjusting Si and Mg, select those too and provide enough independent master-alloy inputs to solve all selected balances. Do not use a generic Sr target: the correct treatment depends on alloy, process, melt condition, holding time, and plant procedure.
""")
    st.markdown("### Important unit reminder")
    st.write("- Batch and addition masses: **kg**")
    st.write("- Element concentrations and assays: **wt.%**")
    st.write("- 1 wt.% = 10,000 ppm. For ppm-level targets, convert carefully before entering a value in wt.%.")

with warnings_tab:
    st.markdown("## Warnings and troubleshooting")
    st.error("Never use an unverified calculation as a production instruction. Obtain metallurgical approval and validate actual recovery / treatment practice.")
    st.markdown("""
### Common input mistakes
- **Wrong unit:** entering ppm as wt.% causes a factor-of-10,000 error. Convert ppm to wt.% before entry.
- **Wrong assay basis:** enter the master-alloy certificate composition in wt.%, not the percentage of master alloy you intend to add.
- **Unknown base chemistry:** an assumed zero base-metal content can overstate the required addition.
- **Wrong material selected:** check the exact master-alloy grade, lot, certificate, and all relevant element contents.
- **Duplicate names:** every master alloy must have a unique name.
- **Too few master alloys:** the current calculation engine requires at least as many master alloys as selected controlled elements.
- **No feasible solution:** the available master alloys may not be able to reach the targets with non-negative additions, or the required additions may exceed the final batch mass.
- **Compositionally dependent materials:** the selected master alloys may not provide independent composition balances, so the equations cannot be solved.

### Metallurgical limitations
- The solver performs an ideal mass balance. It does not model recovery efficiency, oxidation, fading, dross/slag loss, melt loss, evaporation, contamination, or interactions between treatment elements.
- The solver balances only the elements selected by the operator. It does not certify every element in the alloy or check all registered trace-element limits.
- Strontium, sodium, antimony, phosphorus, boron, titanium, zirconium and rare-earth additions can have process-specific effects. Their appropriate target and addition practice must come from a qualified metallurgist and validated plant procedure. The calculator does not determine treatment effectiveness.
- Some element combinations can be incompatible or can form unwanted phases. A mathematically feasible charge is not necessarily a metallurgically suitable charge.
- Do not use this tool to calculate additions of hazardous, radioactive, or otherwise unsuitable substances. The element selector is a complete periodic-table reference, not a recommendation to use every element.

### If an error appears
1. Read the red error message below the Calculate button.
2. Confirm batch mass is greater than zero.
3. Confirm each target, base assay, and master-alloy assay is between 0 and 100 wt.%.
4. Confirm every master alloy has a name and the names are unique.
5. Confirm you entered at least one master alloy per selected controlled element.
6. Check the assay values against the certificates and confirm the materials can reach the requested targets.
7. If the error persists, ask a metallurgist to review the selected elements and master-alloy combination. Do not force a result by entering fabricated assays.

### Data and standards warning
The starter alloy chemistry records come from The Aluminum Association Pink Sheets (August 2025). They are not independently verified against the full current ASTM specifications. Check the applicable ASTM edition, product form, complete chemistry table, footnotes, trace elements, and other requirements before use.
""")
    st.markdown("### Official reference links")
    st.markdown(
        "- [Aluminum Association Pink Sheets — August 2025](https://www.aluminum.org/sites/default/files/2025-10/Pink%20Sheets%202025.pdf)\n"
        "- [ASTM B26/B26M — Sand castings](https://store.astm.org/b0026_b0026m-25.html)\n"
        "- [ASTM B108/B108M — Permanent-mold castings](https://store.astm.org/b0108_b0108m-25.html)\n"
        "- [ASTM B85/B85M — Die castings](https://store.astm.org/b0085_b0085m-25.html)\n"
        "- [ASTM B179 — Foundry ingot / molten alloy](https://store.astm.org/b0179-26.html)"
    )


with audit_tab:
    st.markdown("## Independent calculation audit")
    st.write("This tab explains how to reproduce the mass balance manually and automatically checks the most recent result. The audit uses full-precision internal masses, not rounded charge-sheet display values.")

    st.markdown("### 1 · Symbols and units")
    st.markdown("""
| Symbol | Meaning | Unit |
|---|---|---|
| \(M\) | Required final batch mass | kg |
| \(m_0\) | Base-metal / returns mass | kg |
| \(m_i\) | Mass of master alloy \(i\) | kg |
| \(b_E\) | Element \(E\) in base metal | wt.% |
| \(a_{i,E}\) | Element \(E\) in master alloy \(i\) | wt.% |
| \(t_E\) | Target concentration of element \(E\) | wt.% |
| \(C_E\) | Calculated final concentration of element \(E\) | wt.% |
""")

    st.markdown("### 2 · Equations used by the current solver")
    st.markdown("**A. Total charge-mass balance**")
    st.latex(r"M = m_0 + \sum_i m_i")
    st.latex(r"m_0 = M - \sum_i m_i")
    st.markdown("**B. Element mass contributed by each material**")
    st.latex(r"m_{E,base}=m_0\frac{b_E}{100}")
    st.latex(r"m_{E,additions}=\sum_i m_i\frac{a_{i,E}}{100}")
    st.latex(r"m_{E,total}=m_0\frac{b_E}{100}+\sum_i m_i\frac{a_{i,E}}{100}")
    st.markdown("**C. Final concentration**")
    st.latex(r"C_E=100\frac{m_{E,total}}{M}")
    st.markdown("**D. Rearranged simultaneous equation solved by the software**")
    st.latex(r"\sum_i m_i(a_{i,E}-b_E)=M(t_E-b_E)")
    st.caption("Concentrations in the solver equation are numerical wt.% values (e.g. 7.0 means 7.0 wt.%), not fractions. Masses are kg. The solver searches square subsets of master alloys and accepts a non-negative solution that leaves non-negative base metal.")

    st.markdown("### 3 · Manual verification procedure")
    st.markdown("""
1. Record the required final batch mass \(M\).
2. For every controlled element, record its base assay \(b_E\) and target \(t_E\).
3. Record every master-alloy assay \(a_{i,E}\) from its certificate and its calculated addition \(m_i\).
4. Add all material masses: base metal plus all master alloys. This must equal \(M\).
5. For each element, calculate the kg contributed by the base metal and by each master alloy.
6. Add the element contributions, divide by \(M\), and multiply by 100 to obtain final wt.%.
7. Compare this result with the target and the software's reported achieved composition.
8. Use unrounded masses for the audit. Rounding each charge to 0.01 kg before checking can create a small apparent error.
""")

    st.markdown("### 4 · Worked example: one master alloy")
    st.write("Assume a 100.00 kg final batch, base-metal Si = 0.50 wt.%, target Si = 7.00 wt.%, and an Al–50Si master alloy containing 50.00 wt.% Si. This is a mathematical example only.")
    st.latex(r"m_{Al-50Si}=\frac{100(7.00-0.50)}{50.00-0.50}=13.1313\;kg")
    st.latex(r"m_0=100-13.1313=86.8687\;kg")
    st.latex(r"m_{Si}=86.8687(0.005)+13.1313(0.50)=7.0000\;kg")
    st.latex(r"C_{Si}=100\frac{7.0000}{100}=7.0000\;wt.\%")
    st.success("Check: 86.8687 kg + 13.1313 kg = 100.0000 kg, and the calculated Si is 7.0000 wt.%.")

    st.markdown("### 5 · Automatic audit of the latest calculation")
    saved = st.session_state.get("last_calculation_audit")
    if not saved:
        st.info("No result is stored in this session yet. Run a calculation in the Charge calculator tab, then return here.")
    else:
        audit_result = saved["result"]
        audit_batch = saved["batch_kg"]
        audit_base_mass = audit_result["base_metal_kg"]
        audit_additions = [item["kg"] for item in audit_result["master_alloys"]]
        audit_total = audit_base_mass + sum(audit_additions)
        mass_error = audit_total - audit_batch
        metrics = st.columns(3)
        metrics[0].metric("Required batch", f"{audit_batch:,.6f} kg")
        metrics[1].metric("Reconstructed charge", f"{audit_total:,.6f} kg")
        metrics[2].metric("Mass difference", f"{mass_error:+.8f} kg")

        audit_rows = []
        for element in saved["elements"]:
            base_element = audit_base_mass * saved["base"].get(element, 0.0) / 100.0
            master_element = sum(
                addition * master["composition"].get(element, 0.0) / 100.0
                for master, addition in zip(saved["master_alloys"], audit_additions)
            )
            total_element = base_element + master_element
            recalculated = 100.0 * total_element / audit_batch
            audit_rows.append({
                "Element": element,
                "Base contribution (kg)": base_element,
                "Master-alloy contribution (kg)": master_element,
                "Total element (kg)": total_element,
                "Target (wt.%)": saved["target"][element],
                "Independent recalculation (wt.%)": recalculated,
                "Software result (wt.%)": audit_result["achieved_wt_pct"][element],
                "Difference vs target (wt.%)": recalculated - saved["target"][element],
            })
        st.dataframe(audit_rows, use_container_width=True, hide_index=True)
        max_error = max(abs(row["Difference vs target (wt.%)"]) for row in audit_rows)
        st.write(f"Maximum absolute element-target deviation: **{max_error:.10f} wt.%**")
        if abs(mass_error) <= 1e-7 and max_error <= 1e-7:
            st.success("The result passes the internal ideal mass-closure and selected-element balance checks.")
        else:
            st.error("The result does not pass the audit tolerance. Do not rely on this charge sheet; report it for code review.")
        st.caption("This reconstructs total mass and selected-element masses from the returned charge quantities. It is a consistency check, not an independent laboratory assay or plant trial.")

    st.markdown("### 6 · Weight loss, metal yield and element recovery")
    st.warning("The current version assumes ideal 100% retention for its theoretical mass balance. It does not calculate furnace losses or element recovery. Metal yield and individual-element recovery are different quantities.")
    st.markdown("**Overall metal yield and weight loss**")
    st.latex(r"Y=\frac{M_{metal\ recovered}}{M_{charge}}")
    st.latex(r"\%\,metal\,loss=100(1-Y)")
    st.latex(r"M_{charge}=\frac{M_{metal\ required}}{Y}")
    st.markdown("**Element-specific recovery**")
    st.latex(r"R_E=\frac{m_{E,\ retained\ in\ metal}}{m_{E,\ charged}}")
    st.latex(r"m_{E,\ retained}=R_E\,m_{E,\ charged}")
    st.write("A future recovery-aware model must use validated, process-specific yield and element-recovery data. It must account for retained element mass and actual final metal mass. Oxidation, dross, fading, evaporation, transfer losses and treatment practice can affect elements differently; do not apply one generic loss factor to every element.")

    st.markdown("### 7 · Unit conversions and practical checks")
    st.latex(r"1\;wt.\%=10{,}000\;ppm")
    st.latex(r"wt.\%=\frac{ppm}{10{,}000}")
    st.latex(r"ppm=wt.\%\times10{,}000")
    st.markdown("""
- 250 ppm = 0.0250 wt.%.
- 0.12 wt.% = 1,200 ppm.
- Do not round intermediate values; round only the final weighing instruction to the plant's approved scale increment.
- Check base-metal and master-alloy assays against the correct heat/lot certificates.
- Check the complete alloy specification, including unselected elements, trace limits and footnotes.
""")

    st.markdown("### 8 · Technical and standards references")
    st.markdown("""
- [The Aluminum Association — Pink Sheets](https://www.aluminum.org/pink-sheets)
- [Pink Sheets, August 2025 — PDF](https://www.aluminum.org/sites/default/files/2025-10/Pink%20Sheets%202025.pdf)
- [The Aluminum Association — Standards and alloy registration](https://www.aluminum.org/standards)
- [ASTM B26/B26M-25 — Sand castings](https://store.astm.org/b0026_b0026m-25.html)
- [ASTM B108/B108M-25 — Permanent-mold castings](https://store.astm.org/b0108_b0108m-25.html)
- [ASTM B85/B85M-25 — Die castings](https://store.astm.org/b0085_b0085m-25.html)
- [ASTM B179-26 — Foundry ingot and molten alloys](https://store.astm.org/b0179-26.html)
- [Academic mass-balance example for foundry charge calculations — Michigan Technological University thesis](https://core.ac.uk/download/pdf/151507827.pdf)
""")
    st.caption("These references support alloy designation/specification lookup and general mass-balance study. They do not certify this prototype's code, input assays, recovery factors or production suitability.")


st.divider()
st.caption("M-Alloy-CAL · Aluminium casting prototype · Complete chemistry and plant process validation are required before production use.")
