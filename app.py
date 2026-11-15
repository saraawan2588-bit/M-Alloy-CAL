import json
from pathlib import Path

import streamlit as st

from calculator import calculate_blend, CalculationError

st.set_page_config(page_title="M-Alloy-CAL", page_icon="⚙️", layout="centered")

DATA_PATH = Path(__file__).parent / "data" / "aluminium_cast_alloys.json"
with DATA_PATH.open(encoding="utf-8") as data_file:
    alloy_database = json.load(data_file)

st.title("M-Alloy-CAL")
st.caption("Master Alloy & Charge Calculator")
st.write("A guided charge calculation for foundry operators.")

st.warning(
    "Database status: starter reference data. Chemical limits shown below are "
    "transcribed from The Aluminum Association Pink Sheets (August 2025), not "
    "independently certified ASTM limits. Verify the current ASTM product "
    "specification and all footnotes before using a result for production."
)

st.markdown("### 1. Select the alloy")
alloys = alloy_database["alloys"]
selected = st.selectbox(
    "Choose the required aluminium casting alloy",
    alloys,
    format_func=lambda alloy: f"{alloy['designation']} — {alloy['family']}",
)
st.caption(f"Product form: {selected['product_form']} | AA source: {selected['chemistry_source']}")

route = st.selectbox(
    "Casting / supply route",
    [
        "Sand casting — check ASTM B26/B26M",
        "Permanent-mold casting — check ASTM B108/B108M",
        "Foundry ingot / molten alloy — check ASTM B179",
        "Not sure — ask a metallurgist",
    ],
)
st.caption("ASTM route is a selection aid, not a declaration of compliance. Check the applicable current edition.")

grade_elements = list(selected["elements"].keys())
with st.expander("View registered composition limits (wt.%)", expanded=True):
    rows = [
        {"Element": element, "Minimum": selected["elements"][element]["min"],
         "Maximum": selected["elements"][element]["max"]}
        for element in grade_elements
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.write(f"Aluminium: **{selected['aluminium']}**")
    st.write(
        f"Other elements: each ≤ {selected['other_elements_each_max']} wt.%; "
        f"total ≤ {selected['other_elements_total_max']} wt.%."
    )
    st.caption(selected["notes"])

st.markdown("### 2. Enter batch weight")
batch_kg = st.number_input(
    "How many kilograms of finished alloy do you need?",
    min_value=0.1, value=100.0, step=5.0
)

st.markdown("### 3. Set target chemistry")
st.caption("Initial targets are the midpoint of the registered ranges. Change them to your approved melt target.")
target = {}
cols = st.columns(2)
for idx, element in enumerate(grade_elements):
    limits = selected["elements"][element]
    midpoint = (limits["min"] + limits["max"]) / 2
    with cols[idx % 2]:
        target[element] = st.number_input(
            f"{element} target (wt.%)",
            min_value=float(limits["min"]),
            max_value=float(limits["max"]),
            value=float(midpoint),
            step=0.01,
            format="%.3f",
            key=f"target_{selected['designation']}_{element}",
        )

st.markdown("### 4. Enter base-metal / returns assay")
st.caption("Use a recent chemical-analysis result. Do not assume an element is zero unless verified.")
base = {}
cols = st.columns(2)
for idx, element in enumerate(grade_elements):
    with cols[idx % 2]:
        base[element] = st.number_input(
            f"Base metal {element} (wt.%)",
            min_value=0.0, max_value=100.0, value=0.0,
            step=0.01, format="%.3f", key=f"base_{selected['designation']}_{element}"
        )

st.markdown("### 5. Which elements do you need to adjust?")
default_controls = [e for e in ("Si", "Mg") if e in grade_elements]
if len(default_controls) < 1:
    default_controls = grade_elements[:1]
controlled_elements = st.multiselect(
    "Select the elements you intend to add using master alloys",
    options=grade_elements,
    default=default_controls,
)
if not controlled_elements:
    st.info("Select at least one element to calculate its master-alloy addition.")
    st.stop()

st.markdown("### 6. Enter available master alloys")
st.caption("Enter the actual supplier assay or certificate value for each selected element.")
count = st.number_input(
    "How many master alloys are available?",
    min_value=len(controlled_elements), max_value=10,
    value=len(controlled_elements), step=1
)
master_alloys = []
for i in range(int(count)):
    with st.expander(f"Master alloy {i + 1}", expanded=(i == 0)):
        name = st.text_input("Name / grade", value=f"Addition {i + 1}", key=f"name_{i}")
        composition = {}
        cols = st.columns(2)
        for idx, element in enumerate(controlled_elements):
            with cols[idx % 2]:
                composition[element] = st.number_input(
                    f"{element} in {name} (wt.%)",
                    min_value=0.0, max_value=100.0, value=0.0,
                    step=0.1, format="%.3f", key=f"ma_{i}_{element}"
                )
        master_alloys.append({"name": name, "composition": composition})

if st.button("Calculate charge", type="primary", use_container_width=True):
    try:
        selected_target = {e: target[e] for e in controlled_elements}
        selected_base = {e: base[e] for e in controlled_elements}
        result = calculate_blend(
            batch_kg, controlled_elements, selected_target, selected_base, master_alloys
        )
        st.success("Ideal material-balance calculation completed.")
        st.markdown("### Charge sheet")
        st.metric("Base metal / returns", f"{result['base_metal_kg']:.3f} kg")
        for item in result["master_alloys"]:
            st.metric(item["name"], f"{item['kg']:.3f} kg")
        st.markdown("### Final composition check")
        for element, achieved in result["achieved_wt_pct"].items():
            st.write(
                f"**{element}:** {achieved:.4f} wt.% "
                f"(target {selected_target[element]:.4f} wt.%)"
            )
        if result["unused_master_alloys"]:
            st.caption("No addition required from: " + ", ".join(result["unused_master_alloys"]))
        st.caption(
            "Only the selected adjustment elements were solved. This result does not "
            "certify the unselected elements or full alloy compliance. The ideal balance "
            "does not account for recovery, oxidation, dross/slag losses, melt loss, "
            "charge contamination, or unentered trace elements. Do not use as a production "
            "instruction until plant-specific recoveries and all specification limits are validated."
        )
    except CalculationError as exc:
        st.error(str(exc))

st.divider()
st.caption("M-Alloy-CAL prototype • Aluminium casting database • Not yet certified for production use")
