import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Infrastructure Risk Dashboard",
    page_icon="🧠",
    layout="wide"
)

# -----------------------------
# SIMPLE LOGIN SYSTEM
# -----------------------------
def login():
    st.title("🔐 AI Infrastructure Control Portal")

    with st.form("login_form"):
        user = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if user == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# -----------------------------
# HARDWARE DATA
# -----------------------------
data = [
    {
        "component": "High-End GPU",
        "supplier_count": 1,
        "lead_time_months": 10,
        "substitutability": 0.2,
        "geo_risk": 0.9,
        "inventory_buffer": 1,
        "demand_volatility": 0.8
    },
    {
        "component": "HBM Memory",
        "supplier_count": 2,
        "lead_time_months": 9,
        "substitutability": 0.3,
        "geo_risk": 0.8,
        "inventory_buffer": 2,
        "demand_volatility": 0.7
    },
    {
        "component": "Network Switch",
        "supplier_count": 4,
        "lead_time_months": 4,
        "substitutability": 0.7,
        "geo_risk": 0.3,
        "inventory_buffer": 6,
        "demand_volatility": 0.4
    }
]

df = pd.DataFrame(data)

# -----------------------------
# RISK CALCULATION
# -----------------------------
def calculate_risk(row):
    return round(
        0.25 * (1 / row["supplier_count"]) +
        0.20 * (row["lead_time_months"] / 12) +
        0.20 * row["geo_risk"] +
        0.15 * (1 - row["substitutability"]) +
        0.10 * row["demand_volatility"] -
        0.10 * (row["inventory_buffer"] / 12),
        3
    )

df["risk_score"] = df.apply(calculate_risk, axis=1)

def classify_risk(score):
    if score >= 0.65:
        return "CRITICAL"
    elif score >= 0.45:
        return "HIGH"
    elif score >= 0.30:
        return "MEDIUM"
    else:
        return "LOW"

df["risk_level"] = df["risk_score"].apply(classify_risk)

# -----------------------------
# MONTE CARLO SIMULATION
# -----------------------------
def simulate_time(base):
    sim = np.random.normal(base, base * 0.25, 10000)
    sim = sim[sim > 0]
    return (
        round(np.percentile(sim, 10), 1),
        round(np.percentile(sim, 50), 1),
        round(np.percentile(sim, 90), 1)
    )

# -----------------------------
# DASHBOARD UI
# -----------------------------
st.title("🧠 AI Infrastructure Risk Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Components", len(df))
col2.metric("Critical Risks", len(df[df["risk_level"] == "CRITICAL"]))
col3.metric("High Risks", len(df[df["risk_level"] == "HIGH"]))

st.divider()

# -----------------------------
# RISK TABLE
# -----------------------------
st.subheader("📊 Dependency Risk Ranking")
st.dataframe(
    df[["component", "risk_score", "risk_level"]]
    .sort_values(by="risk_score", ascending=False),
    use_container_width=True
)

# -----------------------------
# TIMELINE BOXES
# -----------------------------
st.subheader("⏱ Capacity Recovery Timelines")

for _, row in df.iterrows():
    best, mid, worst = simulate_time(row["lead_time_months"])

    with st.expander(f"📦 {row['component']}"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Best Case", f"{best} months")
        c2.metric("Most Likely", f"{mid} months")
        c3.metric("Worst Case", f"{worst} months")

st.divider()
st.success("System operational and continuously reassessing risk.")

# -----------------------------
# LOGOUT
# -----------------------------
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
