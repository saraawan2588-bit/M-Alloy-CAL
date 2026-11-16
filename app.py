import io
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

import streamlit as st

from calculator import calculate_blend, calculate_blend_actual, CalculationError

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

def _report_table(rows, widths=None):
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B4D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7D2D8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6F8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_pdf_report(saved):
    """Build a PDF record containing the user's selected inputs and calculation results."""
    result = saved["result"]
    elements = saved["elements"]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=14*mm, leftMargin=14*mm,
        topMargin=14*mm, bottomMargin=14*mm,
        title="M-Alloy-CAL Charge Calculation Report", author="M-Alloy-CAL",
    )
    styles = getSampleStyleSheet()
    note_style = ParagraphStyle(
        "ReportNote", parent=styles["BodyText"], fontSize=8, leading=10,
        textColor=colors.HexColor("#555555"),
    )
    story = [
        Paragraph("M-Alloy-CAL", styles["Title"]),
        Paragraph("Aluminium Foundry Charge Calculation Report", styles["Heading2"]),
        Paragraph("Prototype / educational report — not a production instruction.", note_style),
        Spacer(1, 4*mm),
        Paragraph("1. Selected setup", styles["Heading2"]),
    ]
    setup = [
        ["Alloy", f'{saved.get("alloy_designation", "")} — {saved.get("alloy_family", "")}'],
        ["Casting / supply route", saved.get("casting_route", "Not specified")],
        ["Composition route", saved.get("composition_route", "")],
        ["Calculation basis", saved.get("calculation_basis", "")],
        ["Required final batch", f'{saved["batch_kg"]:.4f} kg'],
    ]
    if saved.get("metal_yield_pct") is not None:
        setup.append(["Measured overall metal yield", f'{saved["metal_yield_pct"]:.4f} %'])
    story.append(_report_table(setup, [55*mm, 115*mm]))
    story += [Spacer(1, 3*mm), Paragraph("2. Target and base-metal chemistry", styles["Heading2"])]
    chemistry = [["Element", "Target (wt.%)", "Base assay (wt.%)", "Recovery (%)"]]
    for element in elements:
        recovery = saved.get("element_recovery_pct", {}).get(element)
        chemistry.append([
            element, f'{saved["target"][element]:.6f}',
            f'{saved["base"].get(element, 0):.6f}',
            f'{recovery:.4f}' if recovery is not None else "—",
        ])
    story.append(_report_table(chemistry, [30*mm, 48*mm, 48*mm, 44*mm]))
    story += [Spacer(1, 3*mm), Paragraph("3. Master-alloy assays entered (wt.%)", styles["Heading2"])]
    assay = [["Material", "Element", "Assay (wt.%)"]]
    for material in saved["master_alloys"]:
        for element in elements:
            assay.append([material["name"], element, f'{material["composition"].get(element, 0):.6f}'])
    story.append(_report_table(assay))
    story += [Spacer(1, 3*mm), Paragraph("4. Calculated charge sheet", styles["Heading2"])]
    charges = [["Material", "Charge (kg)"], ["Base metal / returns", f'{result["base_metal_kg"]:.6f}']]
    charges.extend([[item["name"], f'{item["kg"]:.6f}'] for item in result["master_alloys"]])
    charges.append(["Total gross charge", f'{result.get("total_charge_kg", result["batch_kg"]):.6f}'])
    if "final_metal_kg" in result:
        charges.append(["Required recovered metal", f'{result["final_metal_kg"]:.6f}'])
    story.append(_report_table(charges, [100*mm, 70*mm]))
    story += [Spacer(1, 3*mm), Paragraph("5. Calculated final chemistry", styles["Heading2"])]
    final_rows = [["Element", "Target (wt.%)", "Calculated (wt.%)", "Difference (wt.%)"]]
    for element in elements:
        value = result["achieved_wt_pct"][element]
        target_value = saved["target"][element]
        final_rows.append([element, f"{target_value:.6f}", f"{value:.6f}", f"{value-target_value:+.6f}"])
    story.append(_report_table(final_rows))
    story += [
        Spacer(1, 4*mm), Paragraph("Important limitations", styles["Heading2"]),
        Paragraph(
            "This report records user-entered data and software outputs. It does not validate laboratory "
            "assays, supplier certificates, standard compliance, process yield, element recovery or "
            "metallurgical suitability. Actual mode uses user-provided measured factors and does not "
            "separately model oxide, dross or slag streams. Obtain qualified metallurgical and plant "
            "approval before production use.", note_style,
        ),
        Spacer(1, 2*mm),
        Paragraph("Bug reports: temporarymail09871234@gmail.com", note_style),
    ]
    doc.build(story)
    return buffer.getvalue()



st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] {font-family:'DM Sans',sans-serif;}
h1,h2,h3,h4 {font-family:'Manrope',sans-serif;letter-spacing:-.025em;}
.block-container {max-width:1240px;padding-top:1.4rem;padding-bottom:3rem;}
.hero {padding:2.2rem 1.6rem;border-radius:18px;color:white;text-align:center;margin-bottom:1rem;background:linear-gradient(90deg,rgba(8,24,37,.90),rgba(13,65,78,.72)),url('https://images.unsplash.com/photo-1567789884554-0b844b597180?auto=format&fit=crop&w=1800&q=85') center/cover;}
.hero h1 {color:white;margin:0 0 .4rem 0;font-size:2.45rem;font-weight:800;}
.hero p {color:rgba(255,255,255,.72);margin:0;font-size:1rem;}
div[data-testid="stAlert"] p,.intro-copy {opacity:.5;}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {justify-content:flex-end;gap:.35rem;border-bottom:1px solid var(--secondary-background-color);}
div[data-testid="stTabs"] button[data-baseweb="tab"] {font-weight:600;padding:.65rem .95rem;}
div[data-testid="stMetric"] {background:var(--secondary-background-color);color:var(--text-color);border:1px solid var(--border-color,#8885);padding:.8rem 1rem;border-radius:12px;}
div.stButton > button[kind="primary"] {min-height:3.15rem;font-size:1rem;font-weight:700;border-radius:10px;}
div[data-testid="stExpander"] {border-radius:10px;}
div[data-testid="stNumberInput"] label,div[data-testid="stTextInput"] label {color:var(--text-color)!important;}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input {background:var(--secondary-background-color)!important;color:var(--text-color)!important;border-color:var(--border-color,#8885)!important;}
div[data-testid="stNumberInput"] button {color:var(--text-color)!important;border-color:var(--border-color,#8885)!important;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-color:var(--border-color,#8885)!important;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>⚙️ M-Alloy-CAL</h1>'
    '<p>Master-alloy and charge calculator · Aluminium foundry edition</p></div>',
    unsafe_allow_html=True,
)
st.markdown('<p class="intro-copy" style="text-align:center">A practical charge-planning workspace for aluminium foundry operations.</p>', unsafe_allow_html=True)

st.warning(
    "Prototype / educational use only. The alloy-grade chemistry records are transcribed from "
    "The Aluminum Association Pink Sheets (August 2025), not certified against the applicable ASTM edition. "
    "This calculator does not replace melt-treatment procedures or metallurgical approval."
)

calculator_tab, guide_tab, warnings_tab, audit_tab = st.tabs(["Charge calculator", "Frequently asked questions", "Warnings", "Calculation audit"])

with calculator_tab:
    st.markdown("## 1 · Choose your production calculation")
    mode_cols = st.columns(2)
    with mode_cols[0]:
        composition_route = st.radio(
            "Composition route",
            ["Registered grade target", "Modified / custom composition"],
            help="Registered grade mode starts from the recorded alloy chemistry range. Custom mode allows you to enter an approved target that may differ from that range."
        )
    with mode_cols[1]:
        calculation_basis = st.radio(
            "Calculation basis",
            ["Ideal theoretical", "Actual process-adjusted"],
            help="Ideal assumes 100% retention. Actual process-adjusted requires measured overall metal yield and element-specific recovery data."
        )
    if composition_route == "Registered grade target":
        st.info("Registered-grade route: choose a casting alloy and set targets within the recorded chemistry limits. This prototype's starter limits are transcribed from the Aluminum Association Pink Sheets, not independently ASTM-certified.")
    else:
        st.warning("Custom route: you may enter modified chemistry targets. The app will not certify that the modified composition complies with the selected alloy standard. Obtain metallurgical and customer approval.")
    if calculation_basis == "Ideal theoretical":
        st.info("Ideal basis: charge mass equals the requested final batch mass. No oxidation, dross, slag, fading, transfer loss or element recovery is applied.")
    else:
        st.warning("Actual process-adjusted basis: enter measured metal yield and recovery for every controlled element. The software uses these measured factors; it does not predict oxidation, dross or slag formation. Do not invent generic loss percentages.")
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
    route = "Not specified"
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
                if composition_route == "Registered grade target":
                    grade_target[element] = st.number_input(
                        f"{element} target (wt.%)",
                        min_value=float(limits["min"]), max_value=float(limits["max"]),
                        value=float(midpoint), step=0.01, format="%.2f",
                        key=f'grade_target_{selected["designation"]}_{element}',
                    )
                else:
                    grade_target[element] = st.number_input(
                        f"{element} custom target (wt.%)",
                        min_value=0.0, max_value=100.0,
                        value=float(midpoint), step=0.01, format="%.4f",
                        key=f'custom_grade_target_{selected["designation"]}_{element}',
                        help=f"Recorded reference range: {limits['min']}–{limits['max']} wt.%. Custom values outside this range are not standard-compliant by this record."
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
        element_recovery = {}
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
                if calculation_basis == "Actual process-adjusted":
                    element_recovery[element] = st.number_input(
                        f"{element} recovery (%)",
                        min_value=0.01, max_value=100.0, value=100.0,
                        step=0.1, format="%.2f",
                        key=f'element_recovery_{selected["designation"]}_{element}',
                        help="Use a validated process-specific recovery value for this element, not a guessed value."
                    )

        metal_yield_pct = 100.0
        if calculation_basis == "Actual process-adjusted":
            st.markdown("### Measured process yield")
            metal_yield_pct = st.number_input(
                "Overall metal yield (%)",
                min_value=0.01, max_value=100.0, value=95.0,
                step=0.1, format="%.2f",
                help="Recovered metal mass divided by total charged mass. Use historical or measured data for the same furnace, alloy family, treatment and operating practice."
            )
            st.caption("This single measured yield represents the combined net effect of metal losses such as oxidation, dross, slag carry-over/removal and transfer losses. Do not add separate loss percentages again if they are already included in the measured yield.")
            process_data_confirmed = st.checkbox(
                "I confirm that the yield and element-recovery values are based on measured, validated data for a comparable process.",
                value=False,
                help="The example defaults are not recommended process values. Confirm only after replacing them with your own validated data."
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
                if calculation_basis == "Actual process-adjusted" and not process_data_confirmed:
                    raise CalculationError("Confirm that the actual-mode yield and element recoveries are measured and validated before calculating.")
                if calculation_basis == "Ideal theoretical":
                    result = calculate_blend(
                        batch_kg, controlled_elements, target, base, master_alloys
                    )
                else:
                    result = calculate_blend_actual(
                        batch_kg, controlled_elements, target, base, master_alloys,
                        metal_yield_pct, element_recovery
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
                    "calculation_basis": calculation_basis,
                    "composition_route": composition_route,
                    "alloy_designation": selected["designation"],
                    "alloy_family": selected.get("family", ""),
                    "casting_route": route,
                    "metal_yield_pct": metal_yield_pct if calculation_basis == "Actual process-adjusted" else None,
                    "element_recovery_pct": dict(element_recovery) if calculation_basis == "Actual process-adjusted" else {},
                }
                st.success(f"{calculation_basis} calculation completed.")
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
                if calculation_basis == "Ideal theoretical":
                    st.metric("Final batch mass", f'{result["batch_kg"]:,.2f} kg')
                else:
                    actual_cols = st.columns(3)
                    actual_cols[0].metric("Required recovered metal", f'{result["final_metal_kg"]:,.2f} kg')
                    actual_cols[1].metric("Total gross charge", f'{result["total_charge_kg"]:,.2f} kg')
                    actual_cols[2].metric("Measured metal yield", f'{result["metal_yield_pct"]:.2f} %')
                    st.caption("The base metal and master-alloy charge masses above sum to gross charge mass. The requested final batch is the recovered metal mass after the measured overall yield is applied.")

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
                pdf_bytes = build_pdf_report(st.session_state["last_calculation_audit"])
                st.download_button(
                    "Save calculation report as PDF",
                    data=pdf_bytes,
                    file_name=f"M-Alloy-CAL_{selected['designation'].replace('.', '-')}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_charge_report_pdf",
                )
                if result["unused_master_alloys"]:
                    st.info("No addition required from: " + ", ".join(result["unused_master_alloys"]))
                if calculation_basis == "Ideal theoretical":
                    st.warning(
                        "This is an ideal mass balance only. It does not include recovery, fading, oxidation, "
                        "dross/slag losses, melt loss, contamination, treatment interactions, or unentered trace "
                        "elements. Do not use as a production charge instruction without plant validation."
                    )
                else:
                    st.warning(
                        "This is a process-adjusted estimate using user-supplied overall metal yield and "
                        "element-specific recoveries. It does not independently calculate oxide, dross or slag "
                        "mass/composition, and it is only as reliable as the measured process data entered."
                    )
            except CalculationError as exc:
                st.error(f"Calculation could not be completed: {exc}")
                st.info(
                    "Check that every master alloy has a unique name, all assays are correct, enough "
                    "master alloys are entered, and the selected materials can physically reach the target "
                    "without negative additions or exceeding the batch mass."
                )

with guide_tab:
    st.markdown("## Frequently asked questions")
    faq_items = [
        ("Registered grade or custom composition?", "Registered grade mode constrains listed elements to stored chemistry ranges. Custom mode permits modified targets but does not certify ASTM, customer or plant-specification compliance."),
        ("Ideal or actual process-adjusted calculation?", "Ideal mode assumes 100% retention. Actual mode uses measured overall metal yield and element-specific recovery values. It does not predict furnace losses."),
        ("What does metal yield include?", "Use recovered metal mass divided by gross charged mass from a comparable process. The yield should already include the combined net effect of oxidation, dross, slag removal/carry-over and transfer losses. Do not subtract these losses twice."),
        ("Where should I obtain assay values?", "Use recent base-metal laboratory/spectrometer results and supplier certificates for the exact master-alloy lot. Starter alloy records come from the Aluminum Association Pink Sheets (August 2025), not independent ASTM certification."),
        ("Why is a base-metal assay necessary?", "Returns and base metal already contain elements. Ignoring these contributions can overstate or understate required additions."),
        ("Why can a blend be rejected?", "The chosen master alloys may be compositionally dependent, require negative additions, or exceed the charge mass. The current solver needs at least as many master alloys as controlled elements."),
        ("Are all 118 selectable elements suitable?", "No. The periodic-table selector is a reference, not a recommendation. Use only metallurgically approved additions and validated procedures."),
        ("Can I use the PDF as a production instruction?", "No. It records entered inputs and calculated outputs. Qualified metallurgical review and plant validation remain essential."),
        ("How do I report a bug?", "Email the steps to reproduce the issue, selected calculation mode, and error text to temporarymail09871234@gmail.com. Do not send confidential plant or supplier data unless authorized.")
    ]
    for question, answer in faq_items:
        with st.expander(question):
            st.write(answer)
    st.markdown("### Contact and bug reports")
    st.markdown("[temporarymail09871234@gmail.com](mailto:temporarymail09871234@gmail.com)")

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
- Ideal mode performs a theoretical mass balance and assumes 100% retention. Actual process-adjusted mode uses operator-supplied measured overall metal yield and selected-element recovery values; it does not independently predict oxidation, fading, dross/slag mass or composition, evaporation, contamination, or treatment interactions.
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
        expected_charge = audit_result.get("total_charge_kg", audit_batch)
        mass_error = audit_total - expected_charge
        metrics = st.columns(4)
        metrics[0].metric("Required final metal", f"{audit_batch:,.6f} kg")
        metrics[1].metric("Expected gross charge", f"{expected_charge:,.6f} kg")
        metrics[2].metric("Reconstructed charge", f"{audit_total:,.6f} kg")
        metrics[3].metric("Mass difference", f"{mass_error:+.8f} kg")

        audit_rows = []
        for element in saved["elements"]:
            base_element = audit_base_mass * saved["base"].get(element, 0.0) / 100.0
            master_element = sum(
                addition * master["composition"].get(element, 0.0) / 100.0
                for master, addition in zip(saved["master_alloys"], audit_additions)
            )
            total_element = base_element + master_element
            recovery_fraction = audit_result.get("element_recovery_pct", {}).get(element, 100.0) / 100.0
            retained_element = total_element * recovery_fraction
            recalculated = 100.0 * retained_element / audit_batch
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
        software_error = max(abs(row["Independent recalculation (wt.%)"] - row["Software result (wt.%)"]) for row in audit_rows)
        st.write(f"Maximum absolute element-target deviation: **{max_error:.10f} wt.%**")
        st.write(f"Maximum difference between independent audit and software result: **{software_error:.10f} wt.%**")
        if abs(mass_error) <= 1e-7 and max_error <= 1e-7 and software_error <= 1e-7:
            st.success("The result passes the internal ideal mass-closure and selected-element balance checks.")
        else:
            st.error("The result does not pass the audit tolerance. Do not rely on this charge sheet; report it for code review.")
        st.caption("This reconstructs total mass and selected-element masses from the returned charge quantities. It is a consistency check, not an independent laboratory assay or plant trial.")

    st.markdown("### 6 · Process-adjusted calculation equations")
    st.write("When Actual process-adjusted is selected, the requested batch mass is the required recovered final metal mass, not the gross furnace charge.")
    st.latex(r"Y=\frac{M_{final\ metal}}{M_{gross\ charge}}")
    st.latex(r"M_{gross\ charge}=\frac{M_{final\ metal}}{Y}")
    st.latex(r"m_{base,charge}=M_{gross\ charge}-\sum_i m_i")
    st.latex(r"R_E=\frac{m_{E,retained}}{m_{E,charged}}")
    st.latex(r"C_E=100\frac{R_E\left(m_{base,charge}b_E/100+\sum_i m_i a_{i,E}/100\right)}{M_{final\ metal}}")
    st.latex(r"\sum_i m_i(a_{i,E}-b_E)=\frac{M_{final\ metal}t_E}{R_E}-M_{gross\ charge}b_E")
    st.caption("For this equation, concentrations are numerical wt.% values and recovery fractions are decimals (e.g. 95% = 0.95). Overall yield is the measured combined metal yield. Element recovery is a separate measured fraction. The model does not independently predict the individual masses or chemistry of oxide, dross or slag streams.")

    st.markdown("### 7 · Weight loss and recovery definitions")
    st.warning("The current version assumes ideal 100% retention for its theoretical mass balance. It does not calculate furnace losses or element recovery. Metal yield and individual-element recovery are different quantities.")
    st.markdown("**Overall metal yield and weight loss**")
    st.latex(r"Y=\frac{M_{metal\ recovered}}{M_{charge}}")
    st.latex(r"\%\,metal\,loss=100(1-Y)")
    st.latex(r"M_{charge}=\frac{M_{metal\ required}}{Y}")
    st.markdown("**Element-specific recovery**")
    st.latex(r"R_E=\frac{m_{E,\ retained\ in\ metal}}{m_{E,\ charged}}")
    st.latex(r"m_{E,\ retained}=R_E\,m_{E,\ charged}")
    st.write("The actual mode uses the entered overall metal yield to scale gross charge and the entered element recovery to calculate retained selected-element mass. The yield must already represent the combined net effect of process metal losses; do not subtract oxidation/dross/slag losses again. This mode does not calculate the separate mass or composition of each loss stream. Use measured data from comparable operating conditions.")

    st.markdown("### 8 · Unit conversions and practical checks")
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

    st.markdown("### 9 · Technical and standards references")
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
st.caption("Bug reports and feedback: temporarymail09871234@gmail.com")
