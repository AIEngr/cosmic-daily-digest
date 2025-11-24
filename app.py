import streamlit as st
import requests
import os
from datetime import datetime

# --- Configuration ---
# Read the Webhook URL securely from the environment variables
WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

# Set up the Streamlit page aesthetics
st.set_page_config(
    page_title="Cosmic Daily Digest",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply custom dark theme CSS for a futuristic look
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Roboto:wght@400&display=swap');
    
    .stApp {
        background-color: #0d1117; /* Dark space background */
        color: #e0e6ed;
        font-family: 'Roboto', sans-serif;
    }
    h1, .section-title {
        font-family: 'Orbitron', sans-serif;
        color: #a7d0e8; /* Futuristic blue */
        text-shadow: 0 0 10px rgba(167, 208, 232, 0.6);
        text-align: center;
        margin-top: 0;
    }
    .section-title {
        font-size: 2em;
        color: #76e1ff;
        border-bottom: 2px solid #3d495b;
        padding-bottom: 10px;
        margin-top: 50px;
        margin-bottom: 30px;
    }
    .stMetric {
        background-color: #1a202c; /* Card background */
        border: 1px solid #2d3748;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        padding: 20px;
        transition: transform 0.3s;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        background-color: #3b465a;
    }
    [data-testid="stMetricValue"] {
        color: #81e6d9 !important; /* Teal for data */
    }
    [data-testid="stImage"] img, [data-testid="stVideo"] video {
        border-radius: 8px;
        border: 2px solid #5a667a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_time(iso_time):
    """Converts ISO 8601 time string to a friendly time format."""
    if not iso_time:
        return 'N/A'
    try:
        dt_object = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt_object.strftime("%I:%M %p")
    except ValueError:
        return 'Time N/A'

def format_date(iso_time):
    """Converts ISO 8601 time string to a friendly date format."""
    if not iso_time:
        return 'N/A'
    try:
        dt_object = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt_object.strftime("%B %d, %Y")
    except ValueError:
        return 'Date N/A'

def fetch_data(url):
    """Fetches the APOD and weather data from the n8n webhook."""
    try:
        st.info("🛰️ Fetching data from the Cosmos...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        st.empty() # Clear the info message
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"🔴 Connection Error: Could not connect to webhook. Details: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        st.stop()


def main():
    """Main Streamlit application logic."""

    st.title("🌌 Cosmic Daily Digest 🗓️")

    # --- Configuration Check ---
    if not WEBHOOK_URL:
        st.error("🚨 CONFIGURATION ERROR: The 'N8N_WEBHOOK_URL' environment variable is not set.")
        st.markdown("Please set the environment variable to your full n8n webhook URL to run the application.")
        return

    # --- Fetch Data ---
    data = fetch_data(WEBHOOK_URL)

    # --- DEBUGGING AID START ---
    # Add a checkbox to show the raw JSON data received from n8n for debugging
    if st.checkbox("Show Raw Webhook Data (for debugging temperature/windspeed issues)", value=False):
        st.subheader("Raw JSON Data Received")
        st.json(data)
        st.warning("If Temperature/Wind Speed are missing, check the key names in the 'weather' section of the JSON above. They must be exactly 'temperature' and 'windspeed'.")
    # --- DEBUGGING AID END ---


    # --- Validate Data Structure ---
    if not data or 'apod' not in data or 'weather' not in data:
        st.error("Data structure invalid. Ensure your n8n workflow returns 'apod' and 'weather' objects.")
        return

    apod = data['apod']
    weather = data['weather']

    # --- NASA APOD SECTION ---
    st.markdown('<h2 class="section-title">✨ NASA Astronomy Picture of the Day (APOD)</h2>', unsafe_allow_html=True)
    
    # Use columns to align media and explanation side-by-side
    col_media, col_info = st.columns([1, 2])

    with col_media:
        st.subheader(apod.get('title', 'Title Missing'))
        
        # Display the media (Image or Video)
        media_type = apod.get('media_type')
        media_url = apod.get('url')
        
        if media_url:
            if media_type == 'video':
                # Streamlit requires a direct video file URL, but for YouTube/APOD, iframe is better
                # We'll stick to a simple image placeholder for now, or display the link for videos
                st.video(media_url) 
            elif media_type == 'image':
                st.image(media_url, caption=apod.get('title'))
            else:
                st.warning("Unknown media type.")
        else:
            st.warning("APOD media URL not available.")

    with col_info:
        st.caption(f"**Date:** {format_date(apod.get('date'))}")
        st.markdown(apod.get('explanation', 'No explanation available.'))


    # --- WEATHER SECTION ---
    st.markdown('<h2 class="section-title">☁️ Local Weather Summary</h2>', unsafe_allow_html=True)

    # Use columns for weather metrics
    col1, col2, col3 = st.columns(3)

    # Note: The keys 'temperature' and 'windspeed' MUST match the final output 
    # structure of your n8n workflow (the last node before the Webhook Response).

    with col1:
        # Safely extract temperature and format the string
        temp_value = weather.get('temperature')
        temp_display = f"{temp_value}°C" if temp_value is not None else '--'
        st.metric(label="Temperature", value=temp_display, delta_color="off")

    with col2:
        # Safely extract windspeed and format the string
        wind_value = weather.get('windspeed')
        wind_display = f"{wind_value} km/h" if wind_value is not None else '--'
        st.metric(label="Wind Speed", value=wind_display, delta_color="off")

    with col3:
        local_time = format_time(weather.get('time'))
        st.metric(label="Local Time", value=local_time, delta_color="off")


if __name__ == "__main__":
    main()
