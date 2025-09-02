import streamlit as st
from google.cloud import firestore
import time
from datetime import datetime

# Firestore setup
db = firestore.Client.from_service_account_json("firebase-key.json")

st.set_page_config(page_title="Hospital ER Dashboard", layout="wide")
st.title("🚑 Hospital Emergency Room Dashboard")

REFRESH_INTERVAL = 5  # seconds

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0
if "seen_ids" not in st.session_state:
    st.session_state.seen_ids = set()
    # Preload all current IDs so old accidents don’t flash
    initial_docs = db.collection("accident_data").stream()
    for doc in initial_docs:
        st.session_state.seen_ids.add(doc.id)

def fetch_accidents():
    # Newest accidents at the top
    docs = db.collection("accident_data").order_by(
        "time", direction=firestore.Query.DESCENDING
    ).stream()
    accidents = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        accidents.append(data)
    return accidents

def update_field(doc_id, field, value):
    db.collection("accident_data").document(doc_id).update({field: value})

# Auto-refresh
if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    st.session_state.accidents = fetch_accidents()
    st.session_state.last_refresh = time.time()

# Color scheme with flash
def get_status_color(accident, is_new=False):
    if is_new:
        return "#ff6843"  # bright red flash for new accidents
    if not accident.get("er_dispatched", False):
        return "#ff4d4d"  # light red
    elif accident.get("er_dispatched", False) and not accident.get("patient_rec", False):
        return "#dfc354"  # light yellow
    elif accident.get("patient_rec", False):
        return "#5fdf5f"  # light green
    return "white"

# Format helpers
def format_location(geo):
    try:
        lat, lon = geo.latitude, geo.longitude
        return f'<a href="https://www.google.com/maps?q={lat},{lon}" target="_blank" style="color:#ffffff; text-decoration:none; font-weight:bold;"> {lat:.4f}, {lon:.4f}</a>'
    except Exception:
        return "Unknown"

def format_time(ts):
    try:
        dt = ts if isinstance(ts, datetime) else ts.to_datetime()
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(ts)

# Render accidents as cards
if "accidents" in st.session_state:
    for accident in st.session_state.accidents:
        is_new = accident["id"] not in st.session_state.seen_ids
        bg_color = get_status_color(accident, is_new)

        # Card container
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color:{bg_color};
                    padding:15px;
                    border-radius:12px;
                    margin-bottom:5px;
                    box-shadow:0px 2px 5px rgba(0,0,0,0.15);
                    transition: background-color 2s ease;
                ">
                    <b>ACCIDENT</b><br>
                    • <b>Time:</b> {format_time(accident.get('time'))}<br>
                    • <b>Location:</b> {format_location(accident.get('location'))}<br>
                    • <b>Severity:</b> {accident.get('severity', 'N/A')}<br>
                    • <b>AI Confidence:</b> {accident.get('ai_conf', 'N/A')}<br>
                    • <b>ER Informed:</b> {accident.get('er_informed', False)}<br>
                    • <b>ER Dispatched:</b> {accident.get('er_dispatched', False)}<br>
                    • <b>Patient Recovered:</b> {accident.get('patient_rec', False)}<br>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Buttons below each card
            if not accident.get("er_dispatched", False):
                if st.button("🚑 Dispatched", key=f"dispatch_{accident['id']}"):
                    update_field(accident["id"], "er_dispatched", True)
                    st.success("Marked as Dispatched ✅")
                    st.session_state.accidents = fetch_accidents()
                    st.rerun()

            elif accident.get("er_dispatched", False) and not accident.get("patient_rec", False):
                if st.button("✅ Patient Recovered", key=f"recovered_{accident['id']}"):
                    update_field(accident["id"], "patient_rec", True)
                    st.success("Patient marked as Recovered 🎉")
                    st.session_state.accidents = fetch_accidents()
                    st.rerun()

            st.markdown("---")  # separator between cards

        # Mark accident as seen (so it won’t flash next refresh)
        st.session_state.seen_ids.add(accident["id"])
