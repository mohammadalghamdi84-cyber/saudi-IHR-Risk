import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ضبط الصفحة
st.set_page_config(
    page_title="المركز الوطني للذكاء الوبائي ورصد المنافذ",
    page_icon="🛡️",
    layout="wide"
)

# قاعدة بيانات الإحداثيات ومؤشرات SPAR (WHO) لمحطات الوصول إلى مطار المدينة المنورة
geo_epi_db = {
    "cairo": {"country": "Egypt", "lat": 30.1219, "lon": 31.4056, "spar": 68},
    "dhaka": {"country": "Bangladesh", "lat": 23.8433, "lon": 90.3978, "spar": 52},
    "islamabad": {"country": "Pakistan", "lat": 33.5492, "lon": 72.8277, "spar": 58},
    "lahore": {"country": "Pakistan", "lat": 31.5216, "lon": 74.4036, "spar": 58},
    "karachi": {"country": "Pakistan", "lat": 24.9065, "lon": 67.1608, "spar": 58},
    "jakarta": {"country": "Indonesia", "lat": -6.1275, "lon": 106.6537, "spar": 70},
    "surabaya": {"country": "Indonesia", "lat": -7.3798, "lon": 112.7874, "spar": 70},
    "delhi": {"country": "India", "lat": 28.5562, "lon": 77.1000, "spar": 64},
    "mumbai": {"country": "India", "lat": 19.0896, "lon": 72.8656, "spar": 64},
    "kano": {"country": "Nigeria", "lat": 12.0476, "lon": 8.5246, "spar": 42},
    "lagos": {"country": "Nigeria", "lat": 6.5774, "lon": 3.3212, "spar": 42},
    "amman": {"country": "Jordan", "lat": 31.7226, "lon": 35.9932, "spar": 75},
    "istanbul": {"country": "Turkey", "lat": 41.2753, "lon": 28.7519, "spar": 82},
    "dubai": {"country": "UAE", "lat": 25.2532, "lon": 55.3657, "spar": 88},
    "doha": {"country": "Qatar", "lat": 25.2609, "lon": 51.5651, "spar": 85},
    "kuala lumpur": {"country": "Malaysia", "lat": 2.7456, "lon": 101.7099, "spar": 78}
}

# خصائص العوامل الممرضة المعيارية
pathogen_metadata = {
    "Mpox Clade I (جدري القردة)": {"weight": 1.4, "r0": 1.4},
    "Dengue (حمى الضنك)": {"weight": 0.9, "r0": 1.8},
    "Novel Respiratory Virus (سلالة تنفسية حادة)": {"weight": 1.6, "r0": 2.7},
    "Cholera (الكوليرا)": {"weight": 1.1, "r0": 2.0}
}

# مصفوفة وبائية واقعية ومفصولة لكل مرض ودولة
real_epi_matrix = {
    "Mpox Clade I (جدري القردة)": {
        "Nigeria": 55.0,
        "India": 0.1,
        "Pakistan": 0.1,
        "Egypt": 0.0,
        "Bangladesh": 0.0,
        "Indonesia": 0.2,
        "Turkey": 0.1,
        "Jordan": 0.0,
        "UAE": 0.0,
        "Malaysia": 0.1
    },
    "Dengue (حمى الضنك)": {
        "Bangladesh": 140.0,
        "India": 110.0,
        "Pakistan": 75.0,
        "Indonesia": 85.0,
        "Nigeria": 15.0,
        "Egypt": 4.0,
        "Turkey": 2.0,
        "Jordan": 1.0,
        "UAE": 0.5,
        "Malaysia": 60.0
    },
    "Cholera (الكوليرا)": {
        "Nigeria": 75.0,
        "Pakistan": 40.0,
        "India": 30.0,
        "Bangladesh": 45.0,
        "Egypt": 1.0,
        "Indonesia": 2.0,
        "Turkey": 0.0,
        "Jordan": 0.0,
        "UAE": 0.0,
        "Malaysia": 0.5
    },
    "Novel Respiratory Virus (سلالة تنفسية حادة)": {
        "India": 35.0,
        "Pakistan": 30.0,
        "Egypt": 22.0,
        "Bangladesh": 28.0,
        "Nigeria": 18.0,
        "Indonesia": 25.0,
        "Turkey": 12.0,
        "Jordan": 10.0,
        "UAE": 8.0,
        "Malaysia": 15.0
    }
}

MED_LAT, MED_LON = 24.5534, 39.7051

# الشريط الجانبي
st.sidebar.title("🎛️ وحدة الرصد والمغذيات الوبائية")
st.sidebar.markdown("**حالة التغذية الوبائية:** `مصفوفة وبائية مفصولة (Epi-Matrix)`")

st.sidebar.markdown("---")
st.sidebar.subheader("📂 بيانات الرحلات الجوية")
uploaded_file = st.sidebar.file_uploader("ارفع جدول رحلات الشهر (Excel أو CSV):", type=["xlsx", "xls", "csv"])

st.sidebar.markdown("---")
st.sidebar.subheader("🦠 المحددات الوبائية")
selected_pathogen = st.sidebar.selectbox("التهديد الوبائي المستهدف:", list(pathogen_metadata.keys()))
surge_multiplier = st.sidebar.slider("مضاعف التفشي الاستثنائي (Outbreak Surge):", 0.5, 3.0, 1.0, 0.1)

# تجهيز البيانات
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_flights = pd.read_csv(uploaded_file)
        else:
            df_flights = pd.read_excel(uploaded_file)
        st.sidebar.success(f"تم تحميل {len(df_flights)} رحلة بنجاح.")
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء قراءة الملف: {e}")
        st.stop()
else:
    mock_data = [
        {"flight": "SV-314", "origin": "Islamabad", "country": "Pakistan", "pax": 320, "date": "2026-09-02"},
        {"flight": "SV-804", "origin": "Dhaka", "country": "Bangladesh", "pax": 410, "date": "2026-09-04"},
        {"flight": "MS-661", "origin": "Cairo", "country": "Egypt", "pax": 285, "date": "2026-09-07"},
        {"flight": "SV-741", "origin": "Jakarta", "country": "Indonesia", "pax": 435, "date": "2026-09-10"},
        {"flight": "SV-388", "origin": "Kano", "country": "Nigeria", "pax": 360, "date": "2026-09-13"},
        {"flight": "PK-743", "origin": "Lahore", "country": "Pakistan", "pax": 315, "date": "2026-09-16"},
        {"flight": "SV-890", "origin": "Delhi", "country": "India", "pax": 395, "date": "2026-09-19"},
        {"flight": "TK-108", "origin": "Istanbul", "country": "Turkey", "pax": 260, "date": "2026-09-22"},
        {"flight": "RJ-410", "origin": "Amman", "country": "Jordan", "pax": 195, "date": "2026-09-25"},
        {"flight": "GA-982", "origin": "Surabaya", "country": "Indonesia", "pax": 425, "date": "2026-09-28"}
    ]
    df_flights = pd.DataFrame(mock_data)

def enrich_flight_record(row):
    origin_clean = str(row.get("origin", "")).lower().strip()
    matched_country = str(row.get("country", "")).strip()
    lat, lon, spar = 25.0, 50.0, 60

    for city, info in geo_epi_db.items():
        if city in origin_clean:
            lat, lon, spar = info["lat"], info["lon"], info["spar"]
            matched_country = info["country"]
            break

    pathogen_rates = real_epi_matrix.get(selected_pathogen, {})
    specific_incidence = pathogen_rates.get(matched_country, 5.0)
    return pd.Series([lat, lon, spar, matched_country, specific_incidence])

enriched = df_flights.apply(enrich_flight_record, axis=1)
df_flights["lat"], df_flights["lon"], df_flights["spar"], df_flights["country_matched"], df_flights["disease_incidence"] = enriched[0], enriched[1], enriched[2], enriched[3], enriched[4]

p_data = pathogen_metadata[selected_pathogen]
df_flights["adjusted_incidence"] = df_flights["disease_incidence"] * surge_multiplier
df_flights["surveillance_gap"] = (100 - df_flights["spar"]) / 40.0

df_flights["risk_score"] = np.clip(
    ((df_flights["adjusted_incidence"] / 100000.0) * df_flights["pax"] * p_data["weight"] * df_flights["surveillance_gap"] * 1500) * (p_data["r0"] / 1.5),
    5.0, 99.2
).round(1)

def assign_action_protocol(score):
    if score >= 65:
        return "المستوى الأحمر: فرز إكلينيكي مباشر، عزل وقائي، وحصر مخالطين", "#ff4b4b", "حرج"
    elif score >= 35:
        return "المستوى البرتقالي: تدقيق حراري بالكاميرات ومسح بصري نشط", "#ffa726", "متوسط"
    else:
        return "المستوى الأخضر: مراقبة بصرية وافدة روتينية معتادة", "#26a69a", "منخفض"

proto_res = df_flights["risk_score"].apply(assign_action_protocol)
df_flights["protocol"] = [p[0] for p in proto_res]
df_flights["color"] = [p[1] for p in proto_res]
df_flights["level"] = [p[2] for p in proto_res]

# واجهة لوحة القيادة
st.title("🛡️ المنظومة الوطنية للرصد والتنبؤ الوبائي بمنافذ الدخول")
st.caption(f"المنفذ المستهدف: **مطار الأمير محمد بن عبدالعزيز الدولي بالمدينة المنورة** | التهديد النشط: **{selected_pathogen}**")

k1, k2, k3, k4 = st.columns(4)
k1.metric("إجمالي الرحلات المرصودة", f"{len(df_flights):,} رحلة")
k2.metric("إجمالي المسافرين", f"{int(df_flights['pax'].sum()):,} مسافر")
k3.metric("متوسط الخطر الوبائي", f"{df_flights['risk_score'].mean():.1f} / 100")
top_risk = df_flights.loc[df_flights["risk_score"].idxmax()]
k4.metric("أعلى رحلة خطورة وفود", f"{top_risk['flight']} ({top_risk['origin']})", f"Risk: {top_risk['risk_score']}")

st.markdown("---")
st.subheader("🌐 شبكة التدفق الجوي والمسارات الوبائية المباشرة")

fig = go.Figure()

for _, r in df_flights.iterrows():
    fig.add_trace(go.Scattergeo(
        lon=[r["lon"], MED_LON],
        lat=[r["lat"], MED_LAT],
        mode="lines",
        line=dict(width=2.5, color=r["color"]),
        opacity=0.75,
        hoverinfo="none",
        showlegend=False
    ))

fig.add_trace(go.Scattergeo(
    lon=df_flights["lon"],
    lat=df_flights["lat"],
    text=df_flights.apply(lambda r: f"الرحلة: {r['flight']}<br>التاريخ: {r.get('date', 'N/A')}<br>المنشأ: {r['origin']} ({r['country_matched']})<br>الركاب: {r['pax']}<br>معدل الإصابة بالمنشأ: {r['disease_incidence']}<br>الخطر الوبائي: {r['risk_score']}<br>الإجراء: {r['protocol']}", axis=1),
    hoverinfo="text",
    mode="markers",
    marker=dict(size=13, color=df_flights["color"], line=dict(width=1, color="#ffffff")),
    name="مطارات الإقلاع"
))

fig.add_trace(go.Scattergeo(
    lon=[MED_LON],
    lat=[MED_LAT],
    text=["مطار الأمير محمد بن عبدالعزيز الدولي بالمدينة المنورة"],
    hoverinfo="text",
    mode="markers",
    marker=dict(size=20, color="#00e5ff", symbol="star", line=dict(width=2, color="#ffffff")),
    name="مطار المدينة المنورة"
))

fig.update_layout(
    template="plotly_dark",
    margin=dict(l=0, r=0, t=10, b=0),
