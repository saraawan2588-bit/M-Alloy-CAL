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

# A restrained visual system: high contrast, clear spacing, and readable controls.
st.markdown("""
<style>
    .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
    .hero {padding: 1.35rem 1.5rem; border-radius: 16px; background: linear-gradient(115deg,#102b3f,#1d5266); color: white; margin-bottom: 1rem;}
    .hero h1 {color: white; margin: 0 0 .25rem 0; font-size: 2rem;}
    .hero p {color: #e5f1f5; margin: 0; font-size: 1rem;}
    .section-head {font-size: 1.18rem; font-weight: 700; margin: .6rem 0 .2rem 0;}
    div[data-testid="stMetric"] {background: #f3f7f9; border: 1px solid #dce7ec; padding: .8rem 1rem; border-radius: 12px;}
    div.stButton > button[kind="primary"] {min-height: 3.25rem; font-size: 1.08rem; font-weight: 700; border-radius: 10px;}
    div[data-testid="stExpander"] {border-radius: 10px;}
    .small-note {font-size: .86rem; color: #64748b;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>⚙️ M-Alloy-CAL</h1>'
    '<p>Master-alloy and charge calculator · Aluminium foundry edition</p></div>',
    unsafe_allow_html=True,
)
st.write("Build an ideal charge from your target chemistry, base-metal assay, and available master alloys.")

st.warning(
    "Prototype / educational use only. The chemistry records are transcribed from The Aluminum "
    "Association Pink Sheets (August 2025), not certified against the applicable ASTM edition. "
    "Confirm the complete chemistry, footnotes, product route, and plant recovery factors before production use."
)

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
st.caption(f'Alloy series: {selected.get("series", "Not classified")}  |  Product form: {selected["product_form"]}')
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
    st.caption("Select the actual product route. The standard listing opens ASTM's official catalogue; the full standard may require purchase/access.")
    route_code = route.split(" — ")[0]
    if route_code in standard_links:
        st.link_button(f"Open official {route_code} standard page", standard_links[route_code])
else:
    st.info("No product route is recorded for this entry yet. Confirm the applicable specification with your metallurgist.")

with st.expander("Registered chemistry limits · wt.%", expanded=False):
    rows = [
        {"Element": element, "Min (wt.%)": limits["min"], "Max (wt.%)": limits["max"]}
        for element, limits in selected["elements"].items()
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.write(f'Aluminium: **{selected["aluminium"]}**')
    each_limit = selected.get("other_elements_each_max")
    each_text = f"each ≤ {each_limit} wt.%" if each_limit is not None else "individual limit not separately stated in this record"
    st.write(f"Other elements: {each_text}; total ≤ {selected['other_elements_total_max']} wt.%." )
    st.caption(f'Source: {selected["chemistry_source"]}, page {selected["chemistry_source_page"]}. {selected["notes"]}')

st.divider()
st.markdown('<div class="section-head">2 · Batch and target chemistry</div>', unsafe_allow_html=True)
left, right = st.columns([1, 2])
with left:
    batch_kg = st.number_input(
        "Required finished batch (kg)", min_value=0.1, value=100.0,
        step=5.0, format="%.2f", help="Enter the required final metal mass in kilograms."
    )
    st.metric("Target batch", f"{batch_kg:,.2f} kg")
with right:
    st.caption("Target values are initially set to the midpoint of the registered range. Adjust them to your approved melt target.")
    target = {}
    cols = st.columns(3)
    for idx, (element, limits) in enumerate(selected["elements"].items()):
        midpoint = (limits["min"] + limits["max"]) / 2
        with cols[idx % 3]:
            target[element] = st.number_input(
                f"{element} target (wt.%)",
                min_value=float(limits["min"]), max_value=float(limits["max"]),
                value=float(midpoint), step=0.01, format="%.2f",
                key=f'target_{selected["designation"]}_{element}',
            )

st.divider()
st.markdown('<div class="section-head">3 · Base metal / returns assay</div>', unsafe_allow_html=True)
st.caption("Enter the latest measured assay. Values are weight percent (wt.%). Do not assume zero unless verified.")
base = {}
base_cols = st.columns(4)
for idx, element in enumerate(selected["elements"]):
    with base_cols[idx % 4]:
        base[element] = st.number_input(
            f"{element} in base metal (wt.%)",
            min_value=0.0, max_value=100.0, value=0.0,
            step=0.01, format="%.2f",
            key=f'base_{selected["designation"]}_{element}',
        )

st.divider()
st.markdown('<div class="section-head">4 · Master alloys available</div>', unsafe_allow_html=True)
st.caption("Choose the elements you will adjust, then enter the certified assay of each available master alloy.")
grade_elements = list(selected["elements"])
default_controls = [e for e in ("Si", "Mg") if e in grade_elements] or grade_elements[:1]
controlled_elements = st.multiselect(
    "Elements to adjust", options=grade_elements, default=default_controls
)
if not controlled_elements:
    st.info("Select at least one element to continue.")
    st.stop()

count = st.number_input(
    "Number of master alloys available", min_value=len(controlled_elements),
    max_value=10, value=len(controlled_elements), step=1,
)
master_alloys = []
ma_cols = st.columns(2)
for i in range(int(count)):
    with ma_cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"**Master alloy {i + 1}**")
            name = st.text_input("Name / grade", value=f"Addition {i + 1}", key=f"name_{i}")
            composition = {}
            assay_cols = st.columns(2)
            for idx, element in enumerate(controlled_elements):
                with assay_cols[idx % 2]:
                    composition[element] = st.number_input(
                        f"{element} assay (wt.%)", min_value=0.0, max_value=100.0,
                        value=0.0, step=0.1, format="%.2f",
                        key=f"ma_{i}_{element}",
                    )
            master_alloys.append({"name": name, "composition": composition})

st.divider()
if st.button("⚙️  CALCULATE CHARGE", type="primary", use_container_width=True):
    try:
        selected_target = {e: target[e] for e in controlled_elements}
        selected_base = {e: base[e] for e in controlled_elements}
        result = calculate_blend(
            batch_kg, controlled_elements, selected_target, selected_base, master_alloys
        )
        st.success("Ideal material-balance calculation completed.")
        st.markdown("## Charge sheet")
        metric_cols = st.columns(min(4, len(result["master_alloys"]) + 2))
        with metric_cols[0]:
            st.metric("Base metal / returns", f'{result["base_metal_kg"]:,.2f} kg')
        for idx, item in enumerate(result["master_alloys"], start=1):
            with metric_cols[idx % len(metric_cols)]:
                st.metric(item["name"], f'{item["kg"]:,.2f} kg')
        st.metric("Final batch mass", f'{result["batch_kg"]:,.2f} kg')

        st.markdown("### Charge breakdown")
        charge_rows = [{"Material": "Base metal / returns", "Charge (kg)": round(result["base_metal_kg"], 2)}]
        charge_rows.extend(
            {"Material": item["name"], "Charge (kg)": round(item["kg"], 2)}
            for item in result["master_alloys"]
        )
        st.dataframe(charge_rows, use_container_width=True, hide_index=True)

        st.markdown("### Final composition check")
        check_rows = [
            {
                "Element": element,
                "Target (wt.%)": round(selected_target[element], 2),
                "Calculated (wt.%)": round(achieved, 2),
                "Difference (wt.%)": round(achieved - selected_target[element], 3),
            }
            for element, achieved in result["achieved_wt_pct"].items()
        ]
        st.dataframe(check_rows, use_container_width=True, hide_index=True)
        if result["unused_master_alloys"]:
            st.info("No addition required from: " + ", ".join(result["unused_master_alloys"]))
        st.caption(
            "Displayed charge weights are rounded to 0.01 kg for readability. The calculation "
            "uses full internal precision; use plant-approved weighing increments. Only selected "
            "elements were solved. No recovery, oxidation, dross/slag loss, melt loss, contamination, "
            "or unentered trace elements are included. This is not a production instruction."
        )
    except CalculationError as exc:
        st.error(str(exc))

st.divider()
st.markdown("**Reference links**")
st.markdown(
    f'- [Aluminum Association Pink Sheets — August 2025]({database["data_sources"][0]["url"]})\n'
    '- [ASTM B26/B26M — Sand castings](https://store.astm.org/b0026_b0026m-25.html)\n'
    '- [ASTM B108/B108M — Permanent-mold castings](https://store.astm.org/b0108_b0108m-25.html)\n'
    '- [ASTM B85/B85M — Die castings](https://store.astm.org/b0085_b0085m-25.html)\n'
    '- [ASTM B179 — Foundry ingot / molten alloy](https://store.astm.org/b0179-26.html)'
)
st.caption("M-Alloy-CAL · Aluminium casting prototype · Verify the complete standard and plant process before production use.")
