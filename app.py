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

with st.expander("View registered composition limits (wt.%)", expanded=True):
    rows = []
    for element, limits in selected["elements"].items():
        rows.append({
            "Element": element,
            "Minimum": limits["min"],
            "Maximum": limits["max"],
        })
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
st.caption("Initial targets are set to the midpoint of each registered range. You can change them.")
elements = list(selected["elements"].keys())
target = {}
cols = st.columns(2)
for idx, element in enumerate(elements):
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

st.markdown("### 4. Enter the base metal / returns assay")
st.caption("Enter the latest measured composition of the base metal or returns. Use zero only if the element is confirmed absent/negligible.")
base = {}
cols = st.columns(2)
for idx, element in enumerate(elements):
    with cols[idx % 2]:
        base[element] = st.number_input(
            f"Base metal {element} (wt.%)",
            min_value=0.0, max_value=100.0, value=0.0,
            step=0.01, format="%.3f", key=f"base_{element}"
        )

st.markdown("### 5. Select and assay available master alloys")
count = st.number_input(
    "How many master alloys are available?",
    min_value=len(elements), max_value=10, value=len(elements), step=1
)
master_alloys = []
for i in range(int(count)):
    with st.expander(f"Master alloy {i + 1}", expanded=(i == 0)):
        name = st.text_input("Name / grade", value=f"Addition {i + 1}", key=f"name_{i}")
        composition = {}
        cols = st.columns(2)
        for idx, element in enumerate(elements):
            with cols[idx % 2]:
                composition[element] = st.number_input(
                    f"{element} in {name} (wt.%)",
                    min_value=0.0, max_value=100.0, value=0.0,
                    step=0.1, format="%.3f", key=f"ma_{i}_{element}"
                )
        master_alloys.append({"name": name, "composition": composition})

if st.button("Calculate charge", type="primary", use_container_width=True):
    try:
        result = calculate_blend(batch_kg, elements, target, base, master_alloys)
        st.success("Ideal material-balance calculation completed.")
        st.markdown("### Charge sheet")
        st.metric("Base metal / returns", f"{result['base_metal_kg']:.3f} kg")
        for item in result["master_alloys"]:
            st.metric(item["name"], f"{item['kg']:.3f} kg")
        st.markdown("### Final composition check")
        for element, achieved in result["achieved_wt_pct"].items():
            st.write(
                f"**{element}:** {achieved:.4f} wt.% "
                f"(target {target[element]:.4f} wt.%)"
            )
        st.caption(
            "This is an ideal mass balance only. It does not account for "
            "element recovery, oxidation, dross/slag losses, melt loss, "
            "charge contamination, or unentered trace elements. Do not use "
            "as a production instruction until plant-specific recoveries and "
            "all specification limits are validated."
        )
    except CalculationError as exc:
        st.error(str(exc))

st.divider()
st.caption("M-Alloy-CAL prototype • Aluminium casting database • Not yet certified for production use")
