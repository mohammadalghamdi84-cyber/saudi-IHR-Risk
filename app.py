import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# إعدادات واجهة النظام
st.set_page_config(
    page_title="المنظومة الوطنية للاستخبارات الوبائية بمنافذ الدخول",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الهوية البصرية السيادية مع خط Tajawal
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif !important; }
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1b3e 0%, #060a17 100%) !important;
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 20, 48, 0.95) !important;
        border-left: 1px solid rgba(0, 229, 255, 0.15) !important;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(16, 35, 78, 0.6) 0%, rgba(8, 18, 42, 0.8) 100%) !important;
        border: 1px solid rgba(0, 229, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 20px rgba(0, 114, 255, 0.12) !important;
    }
    div[data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-size: 1.9rem !important;
        font-weight: 900 !important;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.35);
    }
    h1 {
        background: linear-gradient(90deg, #ffffff 0%, #00e5ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
    }
</style>
""", unsafe_allow_html=True)

# قاعدة بيانات SPAR المتخصصة ومحطات القدوم الدولية
origins_spar_db = {
    "cairo": {"country": "Egypt", "lat": 30.1219, "lon": 31.4056, "c4": 72, "c5": 70, "c10": 65, "duration_h": 2.2},
    "dhaka": {"country": "Bangladesh", "lat": 23.8433, "lon": 90.3978, "c4": 55, "c5": 50, "c10": 48, "duration_h": 6.5},
    "islamabad": {"country": "Pakistan", "lat": 33.5492, "lon": 72.8277, "c4": 60, "c5": 58, "c10": 55, "duration_h": 4.8},
    "lahore": {"country": "Pakistan", "lat": 31.5216, "lon": 74.4036, "c4": 60, "c5": 58, "c10": 55, "duration_h": 4.5},
    "jakarta": {"country": "Indonesia", "lat": -6.1275, "lon": 106.6537, "c4": 74, "c5": 70, "c10": 68, "duration_h": 9.5},
    "delhi": {"country": "India", "lat": 28.5562, "lon": 77.1000, "c4": 68, "c5": 65, "c10": 60, "duration_h": 5.0},
    "kano": {"country": "Nigeria", "lat": 12.0476, "lon": 8.5246, "c4": 45, "c5": 40, "c10": 38, "duration_h": 6.0},
    "istanbul": {"country": "Turkey", "lat": 41.2753, "lon": 28.7519, "c4": 85, "c5": 82, "c10": 80, "duration_h": 3.5},
    "amman": {"country": "Jordan", "lat": 31.7226, "lon": 35.9932, "c4": 78, "c5": 75, "c10": 72, "duration_h": 1.8},
    "london": {"country": "UK", "lat": 51.4700, "lon": -0.4543, "c4": 94, "c5": 92, "c10": 90, "duration_h": 6.5}
}

national_airports = {
    "MED": {"name": "مطار الأمير محمد بن عبدالعزيز (المدينة)", "lat": 24.5534, "lon": 39.7051},
    "JED": {"name": "مطار الملك عبدالعزيز الدولي (جدة)", "lat": 21.6796, "lon": 39.1565},
    "RUH": {"name": "مطار الملك خالد الدولي (الرياض)", "lat": 24.9576, "lon": 46.6988}
}

# مصفوفة الأوبئة الأربعة المعتمدة
pathogen_db = {
    "Ebola / Marburg (حمى نزفية فيروسية - عالية الخطورة)": {
        "r0": 1.9,
        "incubation_days": 8.0,
        "type": "contact_fluids",
        "severity": "حرجة جداً (فتك حاد)",
        "tracing_rule": "direct_contacts_only",
        "incidence": {
            "Nigeria": 48.0, "Pakistan": 0.0, "India": 0.0, "Egypt": 0.0,
            "Bangladesh": 0.0, "Indonesia": 0.0, "Turkey": 0.0, "Jordan": 0.0, "UK": 0.0
        }
    },
    "Airborne TB (الدرن الرئوي المفتوح - منقول بالهواء)": {
        "r0": 3.2,
        "incubation_days": 30.0,
        "type": "airborne",
        "severity": "عالية ومزمنة",
        "tracing_rule": "full_cabin",
        "incidence": {
            "Pakistan": 85.0, "India": 90.0, "Bangladesh": 78.0, "Nigeria": 60.0,
            "Indonesia": 70.0, "Egypt": 15.0, "Turkey": 8
