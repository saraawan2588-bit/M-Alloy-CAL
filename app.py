import streamlit as st

from calculator import calculate_blend, CalculationError

st.set_page_config(page_title="M-Alloy-CAL", page_icon="⚙️", layout="centered")

st.title("M-Alloy-CAL")
st.subheader("Master Alloy & Charge Calculator")
st.write("Enter the required batch, target composition, base-metal composition, and the master alloys available.")

st.info("This first version uses compositions entered by the operator. ASTM grade data will be added after the alloy family and applicable standards are confirmed.")

batch_kg = st.number_input("Required final batch weight (kg)", min_value=0.001, value=100.0, step=1.0)

element_text = st.text_input(
    "Which elements do you need to control? (comma-separated)",
    value="C, Mn, Si",
    help="Example: C, Mn, Si, Cr. Do not include the base element (such as Fe or Al) unless you intend to balance it explicitly."
)
elements = [item.strip() for item in element_text.split(",") if item.strip()]
if not elements:
    st.warning("Enter at least one element.")
    st.stop()
if len(set(elements)) != len(elements):
    st.error("Each element must appear only once.")
    st.stop()

st.markdown("### 1. Target composition")
st.caption("Enter weight percentages (wt.%).")
target = {}
cols = st.columns(2)
for idx, element in enumerate(elements):
    with cols[idx % 2]:
        target[element] = st.number_input(
            f"Target {element} (wt.%)", min_value=0.0, max_value=100.0,
            value=0.0, step=0.01, key=f"target_{element}"
        )

st.markdown("### 2. Base metal composition")
base_name = st.text_input("Base metal name", value="Base metal")
base = {}
cols = st.columns(2)
for idx, element in enumerate(elements):
    with cols[idx % 2]:
        base[element] = st.number_input(
            f"{base_name}: {element} (wt.%)", min_value=0.0, max_value=100.0,
            value=0.0, step=0.01, key=f"base_{element}"
        )

st.markdown("### 3. Master alloys available")
count = st.number_input("Number of master alloys to use", min_value=1, max_value=8, value=len(elements), step=1)
master_alloys = []
for i in range(int(count)):
    with st.expander(f"Master alloy {i + 1}", expanded=(i == 0)):
        name = st.text_input("Master alloy name", value=f"Master alloy {i + 1}", key=f"name_{i}")
        composition = {}
        cols = st.columns(2)
        for idx, element in enumerate(elements):
            with cols[idx % 2]:
                composition[element] = st.number_input(
                    f"{name}: {element} (wt.%)", min_value=0.0, max_value=100.0,
                    value=0.0, step=0.1, key=f"ma_{i}_{element}"
                )
        master_alloys.append({"name": name, "composition": composition})

if st.button("Calculate required charge", type="primary", use_container_width=True):
    try:
        result = calculate_blend(batch_kg, elements, target, base, master_alloys)
        st.success("Calculation completed.")
        st.markdown("### Required charge")
        st.metric("Base metal", f"{result['base_metal_kg']:.3f} kg")
        for item in result["master_alloys"]:
            st.metric(item["name"], f"{item['kg']:.3f} kg")
        st.markdown("### Composition check")
        for element, value in result["achieved_wt_pct"].items():
            st.write(f"**{element}:** {value:.4f} wt.% (target: {target[element]:.4f} wt.%)")
        st.caption("Ideal material balance only. This version does not account for oxidation, recovery, slag losses, moisture, or process yield.")
    except CalculationError as exc:
        st.error(str(exc))
