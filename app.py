import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# ضبط الصفحة
st.set_page_config(
    page_title="المركز الوطني للذكاء الوبائي ورصد المنافذ",
    page_icon="🚨",
    layout="wide"
)

# قاعدة بيانات المطارات الوطنية
airports_db = {
    "MED": {"name": "مطار الأمير محمد بن عبدالعزيز الدولي (المدينة)", "lat": 24.5534, "lon": 39.7051},
    "JED": {"name": "مطار الملك عبدالعزيز الدولي (جدة)", "lat": 21.6796, "lon": 39.1565},
    "RUH": {"name": "مطار الملك خالد الدولي (الرياض)", "lat": 24.9576, "lon": 46.6988},
    "DMM": {"name": "مطار الملك فهد الدولي (الدمام)", "lat": 26.4712, "lon": 49.7978}
}

# خصائص التهديدات الوبائية
pathogen_db = {
    "Novel Respiratory Virus (سلالة تنفسية حادة)": {"r0": 2.8, "severity_weight": 1.5},
    "Mpox Clade I (جدري القردة - سلالة وبائية)": {"r0": 1.4, "severity_weight": 1.2},
    "Dengue / Vector-borne (حمى الضنك)": {"r0": 1.8, "severity_weight": 0.8},
    "Viral Hemorrhagic Fever (حمى نزفية فيروسية)": {"r0": 1.9, "severity_weight": 2.0}
}

# شبكة الرحلات الوافدة
flights_db = [
    {"flight": "SV-314", "dest": "MED", "origin": "Islamabad", "country": "Pakistan", "lat": 33.5492, "lon": 72.8277, "pax": 320, "cases_active": 4500, "pop_m": 240, "spar_score": 58, "duration_h": 4.8},
    {"flight": "SV-804", "dest": "MED", "origin": "Dhaka", "country": "Bangladesh", "lat": 23.8433, "lon": 90.3978, "pax": 410, "cases_active": 12000, "pop_m": 170, "spar_score": 52, "duration_h": 6.2},
    {"flight": "SV-741", "dest": "MED", "origin": "Jakarta", "country": "Indonesia", "lat": -6.1275, "lon": 106.6537, "pax": 450, "cases_active": 8500, "pop_m": 275, "spar_score": 68, "duration_h": 9.5},
    {"flight": "SV-112", "dest": "MED", "origin": "Cairo", "country": "Egypt", "lat": 30.1219, "lon": 31.4056, "pax": 290, "cases_active": 1800, "pop_m": 110, "spar_score": 65, "duration_h": 2.1},
    {"flight": "SV-388", "dest": "MED", "origin": "Kano", "country": "Nigeria", "lat": 12.0476, "lon": 8.5246, "pax": 360, "cases_active": 6200, "pop_m": 220, "spar_score": 42, "duration_h": 5.8},
    {"flight": "SV-202", "dest": "JED", "origin": "Lagos", "country": "Nigeria", "lat": 6.5774, "lon": 3.3212, "pax": 380, "cases_active": 7100, "pop_m": 220, "spar_score": 42, "duration_h": 6.5},
    {"flight": "SV-450", "dest": "JED", "origin": "Nairobi", "country": "Kenya", "lat": -1.3192, "lon": 36.9278, "pax": 260, "cases_active": 3900, "pop_m": 54, "spar_score": 60, "duration_h": 4.1},
    {"flight": "SV-890", "dest": "JED", "origin": "Delhi", "country": "India", "lat": 28.5562, "lon": 77.1000, "pax": 420, "cases_active": 24000, "pop_m": 1400, "spar_score": 64, "duration_h": 5.0},
    {"flight": "SV-156", "dest": "RUH", "origin": "London Heathrow", "country": "UK", "lat": 51.4700, "lon": -0.4543, "pax": 290, "cases_active": 1200, "pop_m": 67, "spar_score": 92, "duration_h": 6.5},
    {"flight": "SV-810", "dest": "RUH", "origin": "Mumbai", "country": "India", "lat": 19.0896, "lon": 72.8656, "pax": 360, "cases_active": 19500, "pop_m": 1400, "spar_score": 64, "duration_h": 4.5}
]

df_raw = pd.DataFrame(flights_db)

# التحكم والتصفية
st.sidebar.title("🎛️ غرفة التحكم والفرز الوبائي")
selected_airport = st.sidebar.selectbox("المنفذ الجوي المستهدف:", list(airports_db.keys()), format_func=lambda x: airports_db[x]["name"])
selected_pathogen = st.sidebar.selectbox("التهديد الوبائي:", list(pathogen_db.keys()))
surge = st.sidebar.slider("مضاعف التفشي الوبائي:", 0.5, 3.0, 1.0, 0.1)

target_info = airports_db[selected_airport]
p_info = pathogen_db[selected_pathogen]

df = df_raw[df_raw["dest"] == selected_airport].copy()
df["target_lat"] = target_info["lat"]
df["target_lon"] = target_info["lon"]

# محرك الحسابات
df["incidence"] = ((df["cases_active"] * surge) / (df["pop_m"] * 10))
df["gap_factor"] = (100 - df["spar_score"]) / 40.0
df["risk_score"] = np.clip(((df["incidence"] / 100000.0) * df["pax"] * p_info["severity_weight"] * df["gap_factor"] * 1200) * (p_info["r0"] / 1.5), 10.0, 99.0).round(1)

def get_protocol(score):
    if score >= 65:
        return "أحمر: فحص سريري نشط وعزل وحصر مخالطين", [235, 50, 50, 220]
    elif score >= 40:
        return "برتقالي: مسح حراري واستقصاء بصري", [255, 170, 0, 200]
    else:
        return "أخضر: مراقبة وبائية روتينية وافدة", [46, 204, 113, 180]

res = df["risk_score"].apply(get_protocol)
df["protocol"] = [r[0] for r in res]
df["color"] = [r[1] for r in res]

# واجهة المركز
st.title("🚨 المركز الوطني للذكاء الوبائي ومراقبة المنافذ")
st.caption(f"المنفذ المراقب: **{target_info['name']}** | التهديد: **{selected_pathogen}**")

k1, k2, k3 = st.columns(3)
k1.metric("إجمالي المسافرين المرصودين", f"{df['pax'].sum():,} مسافر")
k2.metric("متوسط مؤشر وفود العدوى", f"{df['risk_score'].mean():.1f} / 100")
k3.metric("الرحلة الأكثر خطورة", f"{df.loc[df['risk_score'].idxmax()]['flight']} ({df.loc[df['risk_score'].idxmax()]['origin']})")

st.markdown("---")
st.subheader("🌐 شبكة التدفق الجوي والمسارات الوبائية")

# رسم الخريطة
arc_layer = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position=["lon", "lat"],
    get_target_position=["target_lon", "target_lat"],
    get_source_color="color",
    get_target_color=[0, 160, 255, 200],
    get_width="risk_score / 12",
    auto_highlight=True,
    pickable=True,
)

origin_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius="risk_score * 3500",
    pickable=True,
)

target_layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame([{"lon": target_info["lon"], "lat": target_info["lat"]}]),
    get_position=["lon", "lat"],
    get_color=[0, 220, 255, 255],
    get_radius=60000,
    pickable=True,
)

deck = pdk.Deck(
    layers=[arc_layer, origin_layer, target_layer],
    initial_view_state=pdk.ViewState(latitude=23.5, longitude=55.0, zoom=3.0, pitch=45),
    map_provider="carto",
    map_style="dark",
    tooltip={"text": "الرحلة: {flight}\nالمنشأ: {origin} ({country})\nالمسافرين: {pax}\nمؤشر الخطر: {risk_score}\nالإجراء: {protocol}"}
)

st.pydeck_chart(deck)

# الجدول والمخطط البياني
st.markdown("---")
c_tbl, c_chart = st.columns([6, 4])

with c_tbl:
    st.subheader("📋 جدول فرز الرحلات بالمطار")
    display_df = df[["flight", "origin", "country", "pax", "risk_score", "protocol"]].copy()
    display_df.columns = ["الرحلة", "مدينة الإقلاع", "الدولة", "المسافرين", "مؤشر الخطر", "البروتوكول بالمطار"]
    st.dataframe(display_df.sort_values(by="مؤشر الخطر", ascending=False).reset_index(drop=True), use_container_width=True)

with c_chart:
    st.subheader("📊 مقارنة مستويات الخطر حسب المنشأ")
    fig = px.bar(
        df.sort_values(by="risk_score"),
        x="risk_score",
        y="origin",
        orientation="h",
        color="risk_score",
        color_continuous_scale=["#26a69a", "#ffa726", "#ff4b4b"],
        template="plotly_dark"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)
