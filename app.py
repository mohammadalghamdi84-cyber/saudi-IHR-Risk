import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="نظام الرصد والذكاء الوبائي - مطار الأمير محمد بن عبدالعزيز",
    page_icon="🛡️",
    layout="wide"
)

# تخصيص المظهر وتنسيق بطاقات المراقبة
st.markdown("""
<style>
    .main { background-color: #0b0e14; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; }
    .stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# قاعدة بيانات الإحداثيات ومؤشرات SPAR الدولية
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

# خصائص التهديدات الوبائية المعيارية
pathogen_metadata = {
    "Mpox Clade I (جدري القردة)": {"weight": 1.4, "r0": 1.4},
    "Dengue (حمى الضنك)": {"weight": 0.9, "r0": 1.8},
    "Novel Respiratory Virus (سلالة تنفسية حادة)": {"weight": 1.6, "r0": 2.7},
    "Cholera (الكوليرا)": {"weight": 1.1, "r0": 2.0}
}

# مصفوفة وبائية مفصولة لكل مرض ودولة
real_epi_matrix = {
    "Mpox Clade I (جدري القردة)": {
        "Nigeria": 55.0, "India": 0.1, "Pakistan": 0.1, "Egypt": 0.0,
        "Bangladesh": 0.0, "Indonesia": 0.2, "Turkey": 0.1, "Jordan": 0.0,
        "UAE": 0.0, "Malaysia": 0.1
    },
    "Dengue (حمى الضنك)": {
        "Bangladesh": 140.0, "India": 110.0, "Pakistan": 75.0, "Indonesia": 85.0,
        "Nigeria": 15.0, "Egypt": 4.0, "Turkey": 2.0, "Jordan": 1.0,
        "UAE": 0.5, "Malaysia": 60.0
    },
    "Cholera (الكوليرا)": {
        "Nigeria": 75.0, "Pakistan": 40.0, "India": 30.0, "Bangladesh": 45.0,
        "Egypt": 1.0, "Indonesia": 2.0, "Turkey": 0.0, "Jordan": 0.0,
        "UAE": 0.0, "Malaysia": 0.5
    },
    "Novel Respiratory Virus (سلالة تنفسية حادة)": {
        "India": 35.0, "Pakistan": 30.0, "Egypt": 22.0, "Bangladesh": 28.0,
        "Nigeria": 18.0, "Indonesia": 25.0, "Turkey": 12.0, "Jordan": 10.0,
        "UAE": 8.0, "Malaysia": 15.0
    }
}

MED_LAT, MED_LON = 24.5534, 39.7051

# دالة توليد جدول كامل لرحلات شهر سبتمبر (30 يوماً واقعياً)
@st.cache_data
def generate_september_schedule():
    np.random.seed(42)
    origins_pool = [
        ("Cairo", "Egypt", 280), ("Dhaka", "Bangladesh", 410),
        ("Islamabad", "Pakistan", 330), ("Lahore", "Pakistan", 310),
        ("Jakarta", "Indonesia", 440), ("Surabaya", "Indonesia", 415),
        ("Delhi", "India", 380), ("Kano", "Nigeria", 360),
        ("Istanbul", "Turkey", 250), ("Amman", "Jordan", 190),
        ("Kuala Lumpur", "Malaysia", 320), ("Dubai", "UAE", 220)
    ]
    rows = []
    flight_idx = 100
    for day in range(1, 31):
        date_str = f"2026-09-{day:02d}"
        daily_count = np.random.randint(3, 7)
        for _ in range(daily_count):
            orig, ctry, base_pax = origins_pool[np.random.randint(0, len(origins_pool))]
            pax = base_pax + np.random.randint(-30, 30)
            rows.append({
                "flight": f"SV-{flight_idx}",
                "date": date_str,
                "origin": orig,
                "country": ctry,
                "pax": int(pax)
            })
            flight_idx += 2
    return pd.DataFrame(rows)

# الشريط الجانبي
st.sidebar.title("🎛️ مركز التحكم والإعدادات")
st.sidebar.markdown("**المنفذ المستهدف:** مطار الأمير محمد بن عبدالعزيز (MED)")

# 1. قسم الملفات
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📂 ارفع جدول الرحلات (Excel أو CSV):", type=["xlsx", "xls", "csv"])

# 2. تحديد المرض والتحكم
st.sidebar.markdown("---")
selected_pathogen = st.sidebar.selectbox("🦠 التهديد الوبائي المستهدف:", list(pathogen_metadata.keys()))
surge_multiplier = st.sidebar.slider("مضاعف التفشي الوبائي (Surge Multiplier):", 0.5, 3.0, 1.0, 0.1)

# تجهيز البيانات
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_all = pd.read_csv(uploaded_file)
        else:
            df_all = pd.read_excel(uploaded_file)
        st.sidebar.success(f"تم تحميل {len(df_all)} رحلة بنجاح.")
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء قراءة الملف: {e}")
        st.stop()
else:
    df_all = generate_september_schedule()

# مطابقة الإحداثيات والبيانات الوبائية
def enrich_flight(row):
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

enriched = df_all.apply(enrich_flight, axis=1)
df_all["lat"] = enriched[0]
df_all["lon"] = enriched[1]
df_all["spar"] = enriched[2]
df_all["country_matched"] = enriched[3]
df_all["disease_incidence"] = enriched[4]

p_data = pathogen_metadata[selected_pathogen]
df_all["adjusted_incidence"] = df_all["disease_incidence"] * surge_multiplier
df_all["surveillance_gap"] = (100 - df_all["spar"]) / 40.0

df_all["risk_score"] = np.clip(
    ((df_all["adjusted_incidence"] / 100000.0) * df_all["pax"] * p_data["weight"] * df_all["surveillance_gap"] * 1500) * (p_data["r0"] / 1.5),
    5.0, 99.2
).round(1)

def assign_tier(score):
    if score >= 65:
        return "حرج (أحمر): عزل وقائي وفرز سريري مباشر", "#ff4b4b", "حرج"
    elif score >= 35:
        return "متوسط (برتقالي): تدقيق حراري ومسح بصري نشط", "#ffa726", "متوسط"
    else:
        return "منخفض (أخضر): مراقبة وبائية روتينية وافدة", "#26a69a", "منخفض"

tiers = df_all["risk_score"].apply(assign_tier)
df_all["protocol"] = [t[0] for t in tiers]
df_all["color"] = [t[1] for t in tiers]
df_all["level"] = [t[2] for t in tiers]

# فلتر التاريخ والتحكم بالجدول الزمني
st.sidebar.markdown("---")
st.sidebar.subheader("📅 نافذة التتبع الزمني (سبتمبر)")
all_dates = sorted(list(df_all["date"].unique()))
filter_choice = st.sidebar.radio("نطاق العرض:", ["كامل الشهر (إجمالي)", "تحديد يوم محدد"])

if filter_choice == "تحديد يوم محدد":
    selected_date = st.sidebar.select_slider("اختر اليوم:", options=all_dates, value=all_dates[0])
    df_view = df_all[df_all["date"] == selected_date].copy()
    display_title_suffix = f"ليوم {selected_date}"
else:
    df_view = df_all.copy()
    display_title_suffix = "لكامل شهر سبتمبر (30 يوماً)"

# واجهة لوحة القيادة
st.title("🛡️ المنظومة الوطنية للاستخبارات الوبائية بمنافذ الدخول")
st.caption(f"مطار الأمير محمد بن عبدالعزيز الدولي بالمدينة المنورة | النطاق: **{display_title_suffix}** | التهديد: **{selected_pathogen}**")

# المؤشرات الرئيسية
k1, k2, k3, k4 = st.columns(4)
total_flights = len(df_view)
total_pax = int(df_view["pax"].sum())
critical_flights = len(df_view[df_view["level"] == "حرج"])
avg_risk = df_view["risk_score"].mean()

k1.metric("إجمالي الرحلات المرصودة", f"{total_flights:,} رحلة")
k2.metric("إجمالي المسافرين الوافدين", f"{total_pax:,} مسافر")
k3.metric("الرحلات الحرجة (المستوى الأحمر)", f"{critical_flights} رحلات", delta=f"{critical_flights} تتطلب عزل" if critical_flights > 0 else "مستقر", delta_color="inverse")
k4.metric("متوسط الخطر الوبائي العام", f"{avg_risk:.1f} / 100")

st.markdown("---")

# التقويم الزمني الشهري لتحليل ذروة المخاطر الوبائية
st.subheader("📈 التوزيع الزمني للرحلات ومستويات الخطر طوال شهر سبتمبر")
st.caption("يوضح المخطط أيام الذروة الوبائية في المطار وأعداد الرحلات الحرجة والمتوسطة يومياً لتوجيه الفرق الطبية الميدانية.")

daily_summary = df_all.groupby(["date", "level"]).size().reset_index(name="count")
daily_pivot = daily_summary.pivot(index="date", columns="level", values="count").fillna(0)

# التأكد من وجود كل الأعمدة
for col in ["حرج", "متوسط", "منخفض"]:
    if col not in daily_pivot.columns:
        daily_pivot[col] = 0

fig_timeline = go.Figure()
fig_timeline.add_trace(go.Bar(name="حرج (أحمر)", x=daily_pivot.index, y=daily_pivot["حرج"], marker_color="#ff4b4b"))
fig_timeline.add_trace(go.Bar(name="متوسط (برتقالي)", x=daily_pivot.index, y=daily_pivot["متوسط"], marker_color="#ffa726"))
fig_timeline.add_trace(go.Bar(name="منخفض (أخضر)", x=daily_pivot.index, y=daily_pivot["منخفض"], marker_color="#26a69a"))

fig_timeline.update_layout(
    barmode="stack",
    template="plotly_dark",
    margin=dict(l=0, r=0, t=20, b=0),
    height=280,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="تاريخ الرحلة (سبتمبر 2026)",
    yaxis_title="عدد الرحلات الوافدة"
)
st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("---")

# الخريطة التفاعلية لمسارات الطيران
st.subheader(f"🌐 خريطة مسارات التدفق الجوي والفرز الوبائي ({display_title_suffix})")

fig_map = go.Figure()

for _, r in df_view.iterrows():
    fig_map.add_trace(go.Scattergeo(
        lon=[r["lon"], MED_LON],
        lat=[r["lat"], MED_LAT],
        mode="lines",
        line=dict(width=2.5, color=r["color"]),
        opacity=0.75,
        hoverinfo="none",
        showlegend=False
    ))

fig_map.add_trace(go.Scattergeo(
    lon=df_view["lon"],
    lat=df_view["lat"],
    text=df_view.apply(lambda r: f"الرحلة: {r['flight']}<br>التاريخ: {r['date']}<br>المنشأ: {r['origin']} ({r['country_matched']})<br>الركاب: {r['pax']}<br>معدل تفشي المنشأ: {r['disease_incidence']}<br>مؤشر الخطر: {r['risk_score']}<br>الإجراء: {r['protocol']}", axis=1),
    hoverinfo="text",
    mode="markers",
    marker=dict(size=12, color=df_view["color"], line=dict(width=1, color="#ffffff")),
    name="محطات الإقلاع"
))

fig_map.add_trace(go.Scattergeo(
    lon=[MED_LON],
    lat=[MED_LAT],
    text=["منفذ الدخول: مطار الأمير محمد بن عبدالعزيز الدولي بالمدينة المنورة"],
    hoverinfo="text",
    mode="markers",
    marker=dict(size=20, color="#00e5ff", symbol="star", line=dict(width=2, color="#ffffff")),
    name="مطار المدينة المنورة"
))

map_layout = dict(
    template="plotly_dark",
    margin=dict(l=0, r=0, t=10, b=0),
    height=520,
    geo=dict(
        scope="world",
        projection_type="natural earth",
        showland=True,
        landcolor="#1a1d24",
        countrycolor="#2e3440",
        coastlinecolor="#2e3440",
        showocean=True,
        oceancolor="#0b0e14",
        center=dict(lat=24.5, lon=45.0),
        projection_scale=2.3
    )
)
fig_map.update_layout(map_layout)
st.plotly_chart(fig_map, use_container_width=True)

# جداول التوزيع العملياتي اليومي والشهري
st.markdown("---")
c_tbl, c_bar = st.columns([6, 4])

with c_tbl:
    st.subheader("📋 جدول فرز الرحلات العملياتي المباشر")
    disp = df_view[["flight", "date", "origin", "country_matched", "pax", "disease_incidence", "risk_score", "level", "protocol"]].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    disp.columns = ["الرحلة", "التاريخ", "محطة الإقلاع", "الدولة", "الركاب", "معدل تفشي المنشأ", "مؤشر الخطر", "المستوى", "البروتوكول الطبي بالمطار"]
    st.dataframe(disp, use_container_width=True)

with c_bar:
    st.subheader("📊 توزيع مؤشر الخطورة حسب العواصم")
    agg_origins = df_view.groupby("origin")["risk_score"].mean().reset_index()
    fig_bar = px.bar(
        agg_origins.sort_values(by="risk_score"),
        x="risk_score",
        y="origin",
        orientation="h",
        color="risk_score",
        color_continuous_scale=["#26a69a", "#ffa726", "#ff4b4b"],
        template="plotly_dark"
    )
    fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=340)
    st.plotly_chart(fig_bar, use_container_width=True)
