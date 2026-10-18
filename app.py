import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="المنظومة الوطنية للاستخبارات الوبائية بمنافذ الدخول",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم بصري متقدم: كحلي، أزرق داكن، وإضاءات سماوية نيونية مع خط Tajawal التقني
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    * {
        font-family: 'Tajawal', sans-serif !important;
    }
    
    /* خلفية المنصة العامة: كحلي ملكي عميق بتدرج لوني */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1b3e 0%, #060a17 100%) !important;
        color: #e2e8f0;
    }
    
    /* الشريط الجانبي */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 20, 48, 0.95) !important;
        border-left: 1px solid rgba(0, 229, 255, 0.15) !important;
    }
    
    /* بطاقات المقاييس الرقمية المضيئة (Glassmorphism Metric Cards) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(16, 35, 78, 0.6) 0%, rgba(8, 18, 42, 0.8) 100%) !important;
        border: 1px solid rgba(0, 229, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 114, 255, 0.12) !important;
    }
    
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-size: 2.1rem !important;
        font-weight: 900 !important;
        text-shadow: 0 0 15px rgba(0, 229, 255, 0.35);
    }
    
    /* الجداول */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    
    /* العناوين المضيئة */
    h1, h2, h3 {
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: linear-gradient(90deg, #ffffff 0%, #00e5ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
    }
</style>
""", unsafe_allow_html=True)

# قواعد البيانات الجيومكانية للمطارات الوطنية الرئيسية
national_airports = {
    "MED": {"name": "مطار الأمير محمد بن عبدالعزيز (المدينة)", "lat": 24.5534, "lon": 39.7051, "code": "MED"},
    "JED": {"name": "مطار الملك عبدالعزيز الدولي (جدة)", "lat": 21.6796, "lon": 39.1565, "code": "JED"},
    "RUH": {"name": "مطار الملك خالد الدولي (الرياض)", "lat": 24.9576, "lon": 46.6988, "code": "RUH"},
    "DMM": {"name": "مطار الملك فهد الدولي (الدمام)", "lat": 26.4712, "lon": 49.7978, "code": "DMM"}
}

# محطات الانطلاق العالمية وربطها بمؤشر WHO SPAR
origin_nodes = {
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
    "kuala lumpur": {"country": "Malaysia", "lat": 2.7456, "lon": 101.7099, "spar": 78},
    "london": {"country": "UK", "lat": 51.4700, "lon": -0.4543, "spar": 92}
}

pathogen_metadata = {
    "Mpox Clade I (جدري القردة)": {"weight": 1.4, "r0": 1.4},
    "Dengue (حمى الضنك)": {"weight": 0.9, "r0": 1.8},
    "Novel Respiratory Virus (سلالة تنفسية حادة)": {"weight": 1.6, "r0": 2.7},
    "Cholera (الكوليرا)": {"weight": 1.1, "r0": 2.0}
}

real_epi_matrix = {
    "Mpox Clade I (جدري القردة)": {
        "Nigeria": 58.0, "India": 0.1, "Pakistan": 0.1, "Egypt": 0.0,
        "Bangladesh": 0.0, "Indonesia": 0.2, "Turkey": 0.1, "Jordan": 0.0,
        "UAE": 0.0, "Malaysia": 0.1, "UK": 0.3
    },
    "Dengue (حمى الضنك)": {
        "Bangladesh": 140.0, "India": 110.0, "Pakistan": 75.0, "Indonesia": 85.0,
        "Nigeria": 15.0, "Egypt": 4.0, "Turkey": 2.0, "Jordan": 1.0,
        "UAE": 0.5, "Malaysia": 60.0, "UK": 0.0
    },
    "Cholera (الكوليرا)": {
        "Nigeria": 75.0, "Pakistan": 40.0, "India": 30.0, "Bangladesh": 45.0,
        "Egypt": 1.0, "Indonesia": 2.0, "Turkey": 0.0, "Jordan": 0.0,
        "UAE": 0.0, "Malaysia": 0.5, "UK": 0.0
    },
    "Novel Respiratory Virus (سلالة تنفسية حادة)": {
        "India": 35.0, "Pakistan": 30.0, "Egypt": 22.0, "Bangladesh": 28.0,
        "Nigeria": 18.0, "Indonesia": 25.0, "Turkey": 12.0, "Jordan": 10.0,
        "UAE": 8.0, "Malaysia": 15.0, "UK": 14.0
    }
}

# دالة توليد بيانات رحلات سبتمبر موزعة على المطارات الوطنية
@st.cache_data
def generate_september_data():
    np.random.seed(42)
    origins_pool = [
        ("Cairo", "Egypt", 285), ("Dhaka", "Bangladesh", 410),
        ("Islamabad", "Pakistan", 330), ("Lahore", "Pakistan", 310),
        ("Jakarta", "Indonesia", 440), ("Surabaya", "Indonesia", 415),
        ("Delhi", "India", 380), ("Kano", "Nigeria", 360),
        ("Istanbul", "Turkey", 250), ("Amman", "Jordan", 190),
        ("Kuala Lumpur", "Malaysia", 320), ("Dubai", "UAE", 220),
        ("London", "UK", 290)
    ]
    dest_keys = list(national_airports.keys())
    rows = []
    flight_num = 110
    
    for day in range(1, 31):
        date_str = f"2026-09-{day:02d}"
        for dest in dest_keys:
            # عدد الرحلات اليومية لكل مطار
            daily_flights = np.random.randint(2, 5) if dest in ["MED", "JED"] else np.random.randint(1, 4)
            for _ in range(daily_flights):
                orig, ctry, base_pax = origins_pool[np.random.randint(0, len(origins_pool))]
                pax = base_pax + np.random.randint(-25, 35)
                rows.append({
                    "flight": f"SV-{flight_num}",
                    "date": date_str,
                    "dest": dest,
                    "origin": orig,
                    "country": ctry,
                    "pax": int(pax)
                })
                flight_num += 2
    return pd.DataFrame(rows)

# --- الشريط الجانبي الفاخر للتحكم ---
st.sidebar.markdown("### 🎛️ لوحة القيادة والتحكم")
st.sidebar.markdown("---")

# اختيار المطارات المتعددة (Multi-Select)
selected_airports = st.sidebar.multiselect(
    "المنافذ الجوية المستهدفة بالمراقبة:",
    options=list(national_airports.keys()),
    default=["MED", "JED"],
    format_func=lambda x: national_airports[x]["name"]
)

if not selected_airports:
    st.sidebar.warning("يرجى اختيار مطار واحد على الأقل.")
    st.stop()

# رفع الملف
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📂 تحميل ملف الرحلات (Excel / CSV):", type=["xlsx", "xls", "csv"])

# اختيار المرض والمضاعف
st.sidebar.markdown("---")
selected_pathogen = st.sidebar.selectbox("🦠 التهديد الوبائي المستهدف:", list(pathogen_metadata.keys()))
surge_multiplier = st.sidebar.slider("مضاعف التفشي الوبائي (Surge Factor):", 0.5, 3.0, 1.0, 0.1)

# تجهيز البيانات
if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        if "dest" not in df_raw.columns:
            df_raw["dest"] = selected_airports[0]
        st.sidebar.success(f"تم تحميل {len(df_raw)} رحلة من ملفك.")
    except Exception as e:
        st.sidebar.error(f"خطأ في قراءة الملف: {e}")
        st.stop()
else:
    df_raw = generate_september_data()

# فلترة البيانات حسب المطارات المختارة
df_active = df_raw[df_raw["dest"].isin(selected_airports)].copy()

# ربط الإحداثيات والبيانات الوبائية
def enrich(row):
    orig = str(row.get("origin", "")).lower().strip()
    dest = row.get("dest", "MED")
    matched_country = str(row.get("country", "")).strip()
    
    o_lat, o_lon, spar = 25.0, 50.0, 60
    for city, info in origin_nodes.items():
        if city in orig:
            o_lat, o_lon, spar = info["lat"], info["lon"], info["spar"]
            matched_country = info["country"]
            break
            
    d_info = national_airports.get(dest, national_airports["MED"])
    d_lat, d_lon = d_info["lat"], d_info["lon"]
    
    pathogen_rates = real_epi_matrix.get(selected_pathogen, {})
    specific_incidence = pathogen_rates.get(matched_country, 5.0)
    
    return pd.Series([o_lat, o_lon, d_lat, d_lon, spar, matched_country, specific_incidence])

enrich_res = df_active.apply(enrich, axis=1)
df_active["orig_lat"], df_active["orig_lon"] = enrich_res[0], enrich_res[1]
df_active["dest_lat"], df_active["dest_lon"] = enrich_res[2], enrich_res[3]
df_active["spar"] = enrich_res[4]
df_active["country_matched"] = enrich_res[5]
df_active["disease_incidence"] = enrich_res[6]

# معادلة تقييم الخطر والفرز
p_data = pathogen_metadata[selected_pathogen]
df_active["adjusted_incidence"] = df_active["disease_incidence"] * surge_multiplier
df_active["surveillance_gap"] = (100 - df_active["spar"]) / 40.0

df_active["risk_score"] = np.clip(
    ((df_active["adjusted_incidence"] / 100000.0) * df_active["pax"] * p_data["weight"] * df_active["surveillance_gap"] * 1500) * (p_data["r0"] / 1.5),
    5.0, 99.2
).round(1)

def assign_tier(score):
    if score >= 65:
        return "حرج (أحمر): عزل وقائي وفرز مباشر", "#ff3366", "حرج"
    elif score >= 35:
        return "متوسط (برتقالي): مسح حراري واستقصاء بصري", "#ff9900", "متوسط"
    else:
        return "منخفض (سماوي): مراقبة روتينية اعتيادية", "#00e5ff", "منخفض"

tiers = df_active["risk_score"].apply(assign_tier)
df_active["protocol"] = [t[0] for t in tiers]
df_active["color"] = [t[1] for t in tiers]
df_active["level"] = [t[2] for t in tiers]

# تصفية التاريخ
st.sidebar.markdown("---")
st.sidebar.subheader("📅 نافذة التتبع الزمني")
all_dates = sorted(list(df_active["date"].dropna().unique()))
mode = st.sidebar.radio("نطاق العرض:", ["كامل شهر سبتمبر", "يوم محدد"])

if mode == "يوم محدد" and len(all_dates) > 0:
    cur_date = st.sidebar.select_slider("اختر اليوم:", options=all_dates, value=all_dates[0])
    df_view = df_active[df_active["date"] == cur_date].copy()
    scope_desc = f"ليوم {cur_date}"
else:
    df_view = df_active.copy()
    scope_desc = "لكامل شهر سبتمبر (30 يوماً)"

# --- الشاشة الرئيسية ---
st.title("🌐 المنظومة الوطنية للاستخبارات الوبائية ومراقبة المنافذ")
monitored_names = " ، ".join([national_airports[k]["name"] for k in selected_airports])
st.caption(f"المنافذ النشطة: **{monitored_names}** | النطاق: **{scope_desc}** | التهديد الوبائي: **{selected_pathogen}**")

# المؤشرات السيادية الرقمية
m1, m2, m3, m4 = st.columns(4)
total_f = len(df_view)
total_p = int(df_view["pax"].sum())
crit_f = len(df_view[df_view["level"] == "حرج"])
avg_r = df_view["risk_score"].mean() if len(df_view) > 0 else 0

m1.metric("إجمالي الرحلات المرصودة", f"{total_f:,}")
m2.metric("إجمالي المسافرين الوافدين", f"{total_p:,}")
m3.metric("الرحلات عالية الخطورة (عزل/فرز)", f"{crit_f}", delta=f"{crit_f} رحلة حرجة" if crit_f > 0 else "الوضع مستقر", delta_color="inverse")
m4.metric("مؤشر الخطر الوبائي العام", f"{avg_r:.1f} / 100")

st.markdown("<br>", unsafe_allow_html=True)

# المخطط الزمني للرصد
st.subheader("📈 مؤشر التوزيع الزمني للرحلات وذروة المخاطر الوبائية طوال الشهر")
daily_grp = df_active.groupby(["date", "level"]).size().reset_index(name="count")
daily_piv = daily_grp.pivot(index="date", columns="level", values="count").fillna(0)

for col in ["حرج", "متوسط", "منخفض"]:
    if col not in daily_piv.columns:
        daily_piv[col] = 0

fig_timeline = go.Figure()
fig_timeline.add_trace(go.Bar(name="حرج (أحمر)", x=daily_piv.index, y=daily_piv["حرج"], marker_color="#ff3366"))
fig_timeline.add_trace(go.Bar(name="متوسط (برتقالي)", x=daily_piv.index, y=daily_piv["متوسط"], marker_color="#ff9900"))
fig_timeline.add_trace(go.Bar(name="منخفض (سماوي)", x=daily_piv.index, y=daily_piv["منخفض"], marker_color="#00e5ff"))

fig_timeline.update_layout(
    barmode="stack",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10, 20, 48, 0.6)",
    margin=dict(l=0, r=0, t=10, b=0),
    height=260,
    font=dict(family="Tajawal", color="#94a3b8"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(gridcolor="rgba(0, 229, 255, 0.1)"),
    yaxis=dict(gridcolor="rgba(0, 229, 255, 0.1)")
)
st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# الخريطة الكحلية البحرية السيادية
st.subheader(f"🌐 خريطة التدفق الجوي والمسارات الوبائية ثلاثية الأبعاد ({scope_desc})")

fig_map = go.Figure()

# رسم المسارات
for _, r in df_view.iterrows():
    fig_map.add_trace(go.Scattergeo(
        lon=[r["orig_lon"], r["dest_lon"]],
        lat=[r["orig_lat"], r["dest_lat"]],
        mode="lines",
        line=dict(width=2.2, color=r["color"]),
        opacity=0.75,
        hoverinfo="none",
        showlegend=False
    ))

# نقاط الإقلاع
fig_map.add_trace(go.Scattergeo(
    lon=df_view["orig_lon"],
    lat=df_view["orig_lat"],
    text=df_view.apply(lambda r: f"الرحلة: {r['flight']}<br>التاريخ: {r['date']}<br>المنشأ: {r['origin']} ({r['country_matched']})<br>الوجهة: {r['dest']}<br>المسافرين: {r['pax']}<br>الخطر الوبائي: {r['risk_score']}<br>الإجراء: {r['protocol']}", axis=1),
    hoverinfo="text",
    mode="markers",
    marker=dict(size=11, color=df_view["color"], line=dict(width=1, color="#ffffff")),
    name="محطات الإقلاع الدولية"
))

# نقاط المنافذ الوطنية المستهدفة
dest_lats = [national_airports[k]["lat"] for k in selected_airports]
dest_lons = [national_airports[k]["lon"] for k in selected_airports]
dest_names = [national_airports[k]["name"] for k in selected_airports]

fig_map.add_trace(go.Scattergeo(
    lon=dest_lons,
    lat=dest_lats,
    text=dest_names,
    hoverinfo="text",
    mode="markers+text",
    textposition="bottom center",
    marker=dict(size=18, color="#00e5ff", symbol="star", line=dict(width=2, color="#ffffff")),
    name="المنافذ الوطنية المراقبة"
))

fig_map.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=10, b=0),
    height=550,
    geo=dict(
        scope="world",
        projection_type="natural earth",
        showland=True,
        landcolor="#0c1633",
        countrycolor="#1e3a6e",
        coastlinecolor="#1e3a6e",
        showocean=True,
        oceancolor="#040814",
        center=dict(lat=24.5, lon=45.0),
        projection_scale=2.3
    )
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# الجداول الإحصائية
c_tbl, c_bar = st.columns([6, 4])

with c_tbl:
    st.subheader("📋 سجل فرز الرحلات العملياتي")
    cols_to_show = ["flight", "date", "dest", "origin", "country_matched", "pax", "disease_incidence", "risk_score", "level", "protocol"]
    disp_df = df_view[cols_to_show].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    disp_df.columns = ["الرحلة", "التاريخ", "المنفذ", "محطة الإقلاع", "الدولة", "الركاب", "معدل التفشي", "مؤشر الخطر", "المستوى", "البروتوكول الطبي"]
    st.dataframe(disp_df, use_container_width=True)

with c_bar:
    st.subheader("📊 توزيع مؤشر الخطر حسب محطات الإقلاع")
    agg_origins = df_view.groupby("origin")["risk_score"].mean().reset_index()
    fig_b = px.bar(
        agg_origins.sort_values(by="risk_score"),
        x="risk_score",
        y="origin",
        orientation="h",
        color="risk_score",
        color_continuous_scale=["#00e5ff", "#ff9900", "#ff3366"],
    )
    fig_b.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10, 20, 48, 0.6)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=350,
        font=dict(family="Tajawal", color="#94a3b8"),
        xaxis=dict(gridcolor="rgba(0, 229, 255, 0.1)"),
        yaxis=dict(gridcolor="rgba(0, 229, 255, 0.1)")
    )
    st.plotly_chart(fig_b, use_container_width=True)
