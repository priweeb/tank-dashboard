# dashboard.py — Storage tank integrity monitor, Task 7 (GAT621S)
# Reads results.csv exported from the Excel computation sheet (sheet "results_csv").
# Run locally:  pip install streamlit pandas   then   streamlit run dashboard.py

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tank Shell Integrity", layout="centered")
st.title("Storage Tank — Shell Integrity")
st.caption("Out-of-roundness is monitored as PEAK-TO-PEAK (2A of the second harmonic). "
           "The radius is shown but not alarmed: an oval tank keeps its radius.")

# ---- STEP 1: read the numbers exported from the Excel sheet ----
data = pd.read_csv("results.csv")
latest = data.iloc[-1]                 # most recent epoch
limit = float(latest["limit_mm"])      # limit comes from the data, not typed into the code
p2p = float(latest["peak_to_peak_mm"])

# ---- STEP 2: decide the status ----
def status(value, limit):
    if value > limit:
        return "RED"
    if value > 0.5 * limit:
        return "AMBER"
    return "GREEN"

state = status(p2p, limit)

# ---- STEP 3: the warning banner ----
if state == "RED":
    st.error("ALARM — out-of-roundness exceeds the acceptance limit.")
elif state == "AMBER":
    st.warning("Caution — out-of-roundness above half the limit.")
else:
    st.success("Tank within tolerance.")

# ---- STEP 4: headline numbers ----
left, right = st.columns(2)
left.metric("Peak-to-peak out-of-roundness", f"{p2p:.1f} mm", state)
right.metric("Fitted radius", f"{latest['radius_m']:.4f} m")
st.write(f"Acceptance limit: **{limit:.0f} mm** peak-to-peak. "
         f"Latest epoch: **{int(latest['epoch'])}**.")

# ---- STEP 5: trend and time to the limit ----
st.subheader("Out-of-roundness over time")
chart = data.set_index("epoch")[["peak_to_peak_mm"]].copy()
chart["limit_mm"] = limit
st.line_chart(chart)

growth = (data["peak_to_peak_mm"].iloc[-1] - data["peak_to_peak_mm"].iloc[0]) / (len(data) - 1)
if p2p > limit:
    st.info("The limit has already been exceeded. Average growth was "
            + str(round(growth, 1)) + " mm per epoch.")
elif growth > 0:
    left_to_go = (limit - p2p) / growth
    st.info("At the present rate the limit is crossed in about "
            + str(round(left_to_go, 1)) + " more epochs.")
else:
    st.info("Out-of-roundness is not growing.")

# ---- STEP 6: the numbers behind the colours ----
st.subheader("Data")
st.dataframe(data)
st.caption("RED: above the limit. AMBER: above half the limit. GREEN: otherwise. "
           "Update results.csv with a new epoch and the page updates.")
