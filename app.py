"""FireGuard AI — Streamlit dashboard.

Early wildfire detection, risk prediction, real-time NASA FIRMS monitoring,
and an automated "live danger feed" combining both signals across known
fire-prone Indonesian regions. See README.md for architecture & model
provenance/citations.
"""

import folium
import streamlit as st
from PIL import Image
from streamlit_folium import st_folium

from lib.danger_feed import get_current_danger_points
from lib.detect_model import MODEL_PATH as DETECT_MODEL_PATH
from lib.detect_model import detect
from lib.detect_model import load_model as load_detect_model
from lib.firms import DEFAULT_BBOX, fetch_firms_hotspots
from lib.monitored_locations import MONITORED_LOCATIONS
from lib.risk_model import MODEL_PATH as RISK_MODEL_PATH
from lib.risk_model import RiskInput
from lib.risk_model import load_model as load_risk_model
from lib.risk_model import predict_risk
from lib.style import CSS, HERO_ICON_SVG, badge
from lib.weather import fetch_current_weather

st.set_page_config(page_title="FireGuard AI", page_icon="🔥", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def get_secret(key: str) -> str | None:
    try:
        return st.secrets.get(key)
    except Exception:
        return None


@st.cache_resource(show_spinner="Loading risk model...")
def cached_risk_model():
    return load_risk_model()


@st.cache_resource(show_spinner="Loading detection model...")
def cached_detect_model():
    return load_detect_model()


@st.cache_data(ttl=900, show_spinner="Checking NASA FIRMS...")
def cached_hotspots(map_key: str | None):
    return fetch_firms_hotspots(map_key, DEFAULT_BBOX)


@st.cache_data(ttl=900, show_spinner="Scanning fire-prone regions...")
def cached_danger_points(map_key: str | None):
    return get_current_danger_points(map_key, cached_risk_model())


FIRMS_MAP_KEY = get_secret("NASA_FIRMS_MAP_KEY")

st.markdown(
    f"""
    <div class="fg-hero">
      <div class="fg-brand">{HERO_ICON_SVG} FireGuard AI</div>
      <h1>FireGuard AI</h1>
      <p>Early wildfire detection, risk prediction, and real-time alerts — in one dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_monitor, tab_detect, tab_risk, tab_alerts = st.tabs(
    ["🗺️ Monitoring", "🔥 Detection", "📊 Risk Prediction", "🚨 Live Alerts"]
)

# ---------------------------------------------------------------- Monitoring
with tab_monitor:
    st.markdown('<div class="fg-section-title">Real-time Monitoring</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fg-section-sub">Active hotspots from NASA FIRMS, shown on the map below.</div>',
        unsafe_allow_html=True,
    )

    hotspots, source = cached_hotspots(FIRMS_MAP_KEY)
    risk_colors = {"low": "#7fe3a0", "medium": "#e3d57f", "high": "#e37f7f"}

    fmap = folium.Map(location=[-1.5, 114.5], zoom_start=5, tiles="OpenStreetMap")
    for h in hotspots:
        folium.CircleMarker(
            location=[h.lat, h.lon],
            radius=8,
            color=risk_colors[h.risk],
            fill=True,
            fill_opacity=0.75,
            weight=1,
            popup=f"Risk: {h.risk} · confidence {h.confidence * 100:.0f}%",
        ).add_to(fmap)
    st_folium(fmap, height=420, use_container_width=True, returned_objects=[])

    if source == "sample":
        st.caption(
            "Showing sample data — set `NASA_FIRMS_MAP_KEY` in `.streamlit/secrets.toml` "
            "for real NASA FIRMS hotspot data."
        )

# ------------------------------------------------------------------ Detection
with tab_detect:
    st.markdown('<div class="fg-section-title">Early Detection</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fg-section-sub">Upload a photo and the model will flag fire or smoke with a confidence score.</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded is not None:
        image = Image.open(uploaded).convert("RGB")
        model = cached_detect_model()

        if model is None:
            st.error(
                f"No model found at `{DETECT_MODEL_PATH}`. See "
                "`backend/ml/detect/README.md` for how to get it."
            )
        else:
            with st.spinner("Detecting..."):
                result = detect(model, image)

            st.image(result["annotated_image"], use_container_width=True)

            status = "high" if result["is_danger"] else "low"
            status_text = "DANGER DETECTED" if result["is_danger"] else "CLEAR"
            st.markdown(
                f'{badge(status, status_text)} max confidence {result["max_confidence"] * 100:.1f}%',
                unsafe_allow_html=True,
            )
            for det in result["detections"]:
                st.write(f"- {det['label']} — {det['confidence'] * 100:.1f}%")

# ------------------------------------------------------------- Risk Prediction
with tab_risk:
    st.markdown('<div class="fg-section-title">Risk Prediction</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fg-section-sub">Pick a location, pull live weather, and get a fire-risk score.</div>',
        unsafe_allow_html=True,
    )

    location_names = ["Custom"] + [loc.name for loc in MONITORED_LOCATIONS]
    choice = st.selectbox("Quick-select a monitored region", location_names)

    if choice == "Custom":
        default_lat, default_lon = -2.5, 113.0
    else:
        picked = next(loc for loc in MONITORED_LOCATIONS if loc.name == choice)
        default_lat, default_lon = picked.lat, picked.lon

    col1, col2 = st.columns(2)
    lat = col1.number_input("Latitude", value=default_lat, format="%.4f", key=f"lat_{choice}")
    lon = col2.number_input("Longitude", value=default_lon, format="%.4f", key=f"lon_{choice}")

    if st.button("Auto-fetch Weather"):
        try:
            weather = fetch_current_weather(lat, lon)
            st.session_state["temperature"] = weather.temperature_c
            st.session_state["humidity"] = weather.humidity_pct
            st.session_state["rainfall"] = weather.rainfall_mm
            st.session_state["wind"] = weather.wind_speed_kmh
        except Exception as err:
            st.error(f"Failed to fetch weather: {err}")

    col3, col4, col5, col6 = st.columns(4)
    temperature = col3.number_input("Temperature (°C)", value=st.session_state.get("temperature", 30.0), key="temperature")
    humidity = col4.number_input("Humidity (%)", value=st.session_state.get("humidity", 60.0), key="humidity")
    rainfall = col5.number_input("Rainfall (mm)", value=st.session_state.get("rainfall", 0.0), key="rainfall")
    wind = col6.number_input("Wind speed (km/h)", value=st.session_state.get("wind", 10.0), key="wind")

    if st.button("Predict Risk", type="primary"):
        model = cached_risk_model()
        result = predict_risk(
            model,
            RiskInput(
                temperature_c=temperature,
                humidity_pct=humidity,
                rainfall_mm=rainfall,
                wind_speed_kmh=wind,
            ),
        )
        st.markdown(
            f'{badge(result["risk_label"])} score {result["risk_score"] * 100:.1f}%',
            unsafe_allow_html=True,
        )
        if model is None:
            st.caption(f"No model found at `{RISK_MODEL_PATH}` — using a rule-based fallback.")

# ----------------------------------------------------------------- Live Alerts
with tab_alerts:
    st.markdown('<div class="fg-section-title">Live Danger Feed</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fg-section-sub">Automatically combines NASA FIRMS hotspots with a risk-prediction '
        "sweep across known fire-prone regions — refreshed on load, no manual lookup required.</div>",
        unsafe_allow_html=True,
    )

    danger_points = cached_danger_points(FIRMS_MAP_KEY)

    if not danger_points:
        st.success("No danger points detected right now.")
    else:
        for dp in danger_points:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 2])
                c1.markdown(f"**{dp.name}**")
                c2.markdown(badge(dp.risk), unsafe_allow_html=True)
                c3.caption(f"{dp.source} · {dp.detail}")

st.markdown(
    """
    <div class="fg-footer">
      FireGuard AI — built for Neural Storm 2026 (Green Planet track).
      Detection model: <a href="https://huggingface.co/seawsurf/fire_yolo" target="_blank">seawsurf/fire_yolo</a>
      · Dataset: <a href="https://doi.org/10.1080/10095020.2024.2347922" target="_blank">FASDD_CV</a>
    </div>
    """,
    unsafe_allow_html=True,
)
