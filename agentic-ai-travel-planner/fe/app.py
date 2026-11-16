import os

import requests
import streamlit as st

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="centered")


def get_backend_url() -> str:
    """Read the backend URL from Render environment variables or local Streamlit secrets."""
    value = os.environ.get("BACKEND_URL", "")
    if not value:
        try:
            value = st.secrets.get("BACKEND_URL", "")
        except Exception:
            value = ""
    return value.rstrip("/") or "http://127.0.0.1:8000"


BACKEND_URL = get_backend_url()

st.title("✈️ AI TRAVEL PLANNER")
st.caption("Create a personalized, budget-aware travel itinerary.")

with st.form("travel_form"):
    st.subheader("Enter your trip details")
    starting_loc = st.text_input("Starting location", placeholder="e.g. Hyderabad")
    destination_loc = st.text_input("Destination", placeholder="e.g. Goa")
    col1, col2 = st.columns(2)
    with col1:
        no_of_trip_dys = st.number_input("Number of trip days", min_value=1, max_value=60, value=3, step=1)
    with col2:
        no_of_people = st.number_input("Number of people", min_value=1, max_value=30, value=2, step=1)
    budget = st.number_input("Total budget (₹)", min_value=1000, max_value=10000000, value=30000, step=1000)
    specifications = st.text_area(
        "Your preferences",
        placeholder="Example: beaches, clubs, trekking, family-friendly places..."
    )
    submitted = st.form_submit_button("Build Travel Plan", use_container_width=True)

if submitted:
    if not starting_loc.strip() or not destination_loc.strip():
        st.warning("Please enter both the starting location and destination.")
    else:
        payload = {
            "starting_loc": starting_loc.strip(),
            "destination_loc": destination_loc.strip(),
            "no_of_trip_dys": int(no_of_trip_dys),
            "no_of_people": int(no_of_people),
            "budget": float(budget),
            "specifications": specifications.strip(),
        }

        with st.spinner("Generating your travel plan. The free backend may take a little time to wake up..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/plan_trip",
                    json=payload,
                    timeout=(15, 300),
                )
                response.raise_for_status()
                result = response.json().get("content", "")
                if result:
                    st.success("Your travel plan is ready!")
                    st.markdown(result)
                else:
                    st.error("The backend returned an empty response.")
            except requests.exceptions.Timeout:
                st.error("The request timed out. The free backend may be waking up or the AI request may have taken too long. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Check the BACKEND_URL environment variable and confirm the Render backend is live.")
            except requests.exceptions.HTTPError:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                st.error(f"Backend error ({response.status_code}): {detail}")
            except requests.exceptions.RequestException as exc:
                st.error(f"Request failed: {exc}")

st.divider()
st.caption("AI-generated travel suggestions are estimates. Verify transport, accommodation, prices and local conditions before booking.")
