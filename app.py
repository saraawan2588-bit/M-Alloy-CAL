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

calculator_tab, guide_tab, warnings_tab = st.tabs(
    ["⚙️  Charge calculator", "📘  How to use", "⚠️  Warnings & troubleshooting"]
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

st.divider()
st.caption("M-Alloy-CAL · Aluminium casting prototype · Complete chemistry and plant process validation are required before production use.")
