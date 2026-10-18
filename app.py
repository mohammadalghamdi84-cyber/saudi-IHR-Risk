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

# تخصيص الهوية البصرية السيادية (Deep Navy & Cyan Glow) مع خط Tajawal
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
        "r0": 1.9, "incubation_days": 8.0, "type": "contact_fluids",
        "severity": "حرجة جداً (فتك حاد)", "tracing_rule": "direct_contacts_only",
        "incidence": {"Nigeria": 48.0, "Pakistan": 0.0, "India": 0.0, "Egypt": 0.0, "Bangladesh": 0.0, "Indonesia": 0.0, "Turkey": 0.0, "Jordan": 0.0, "UK": 0.0}
    },
    "Airborne TB (الدرن الرئوي المفتوح - منقول بالهواء)": {
        "r0": 3.2, "incubation_days": 30.0, "type": "airborne",
        "severity": "عالية ومزمنة", "tracing_rule": "full_cabin",
        "incidence": {"Pakistan": 85.0, "India": 90.0, "Bangladesh": 78.0, "Nigeria": 60.0, "Indonesia": 70.0, "Egypt": 15.0, "Turkey": 8.0, "Jordan": 6.0, "UK": 4.0}
    },
    "Severe Influenza / Novel Corona (رذاذي حاد)": {
        "r0": 2.5, "incubation_days": 3.5, "type": "droplet",
        "severity": "متوسطة إلى عالية", "tracing_rule": "two_rows",
        "incidence": {"Egypt": 30.0, "India": 40.0, "Pakistan": 35.0, "Bangladesh": 30.0, "Indonesia": 28.0, "Nigeria": 15.0, "Turkey": 20.0, "Jordan": 15.0, "UK": 22.0}
    },
    "Chickenpox (جدري الماء - تلامسي مختلط)": {
        "r0": 1.6, "incubation_days": 14.0, "type": "contact_skin",
        "severity": "خفيفة إلى معتدلة", "tracing_rule": "adjacent_only",
        "incidence": {"Pakistan": 25.0, "India": 20.0, "Egypt": 15.0, "Bangladesh": 18.0, "Nigeria": 22.0, "Indonesia": 16.0, "Turkey": 10.0, "Jordan": 8.0, "UK": 5.0}
    }
}

# شريط التبديل بين الشاشتين
st.sidebar.title("🎛️ مركز المراقبة والتحكم")
view_mode = st.sidebar.radio(
    "اختر شاشة العمليات:",
    ["1️⃣ شاشة التنبؤ والمناظرة (شهر سبتمبر كاملاً)", "2️⃣ مقصورة الطائرة التفاعلية وحصر المخالطين"]
)
st.sidebar.markdown("---")

selected_pathogen_name = st.sidebar.selectbox("🦠 التهديد الوبائي المستهدف:", list(pathogen_db.keys()))
p_info = pathogen_db[selected_pathogen_name]

# =========================================================================
# الشاشة الأولى: التنبؤ الوبائي لشهر سبتمبر بالكامل + فرز الأيام
# =========================================================================
if view_mode == "1️⃣ شاشة التنبؤ والمناظرة (شهر سبتمبر كاملاً)":
    st.title("🌐 منظومة التنبؤ الوبائي ومناظرة رحلات شهر سبتمبر")
    st.caption(f"المرض المراقب: **{selected_pathogen_name}** | مؤشر الشدة: **{p_info['severity']}**")

    selected_airports = st.sidebar.multiselect(
        "المنافذ الوطنية المراقبة:",
        options=list(national_airports.keys()),
        default=["MED", "JED"],
        format_func=lambda x: national_airports[x]["name"]
    )
    if not selected_airports:
        st.warning("يرجى اختيار مطار واحد على الأقل.")
        st.stop()

    uploaded_file = st.sidebar.file_uploader("📂 تحميل جدول رحلات سبتمبر (Excel / CSV):", type=["xlsx", "xls", "csv"])

    @st.cache_data
    def generate_full_september_schedule():
        np.random.seed(42)
        origins_keys = list(origins_spar_db.keys())
        data = []
        flight_idx = 100
        for day in range(1, 31):
            date_str = f"2026-09-{day:02d}"
            for dest in ["MED", "JED", "RUH"]:
                daily_flights = np.random.randint(2, 5) if dest in ["MED", "JED"] else np.random.randint(1, 3)
                for _ in range(daily_flights):
                    orig_k = origins_keys[np.random.randint(0, len(origins_keys))]
                    orig_data = origins_spar_db[orig_k]
                    data.append({
                        "flight": f"SV-{flight_idx}",
                        "date": date_str,
                        "dest": dest,
                        "origin_city": orig_k.capitalize(),
                        "country": orig_data["country"],
                        "pax": int(np.random.randint(270, 430)),
                        "duration_h": orig_data["duration_h"],
                        "c4": orig_data["c4"], "c5": orig_data["c5"], "c10": orig_data["c10"],
                        "lat": orig_data["lat"], "lon": orig_data["lon"]
                    })
                    flight_idx += 2
        return pd.DataFrame(data)

    if uploaded_file:
        df_all = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    else:
        df_all = generate_full_september_schedule()

    df_filtered = df_all[df_all["dest"].isin(selected_airports)].copy()

    def calculate_risk(row):
        ctry = row["country"]
        inc = p_info["incidence"].get(ctry, 5.0)
        spar_core = (row["c4"] + row["c5"] + row["c10"]) / 3.0
        gap_factor = (100.0 - spar_core) / 35.0
        incubation_hrs = p_info["incubation_days"] * 24.0
        flight_ratio = 1.0 + (row["duration_h"] / incubation_hrs)
        score = (inc / 100000.0) * row["pax"] * p_info["r0"] * gap_factor * flight_ratio * 3200
        return np.clip(score, 6.0, 98.5).round(1)

    df_filtered["risk_score"] = df_filtered.apply(calculate_risk, axis=1)

    def assign_tier(score):
        if score >= 65:
            return "مناظرة مشددة (أحمر): تدقيق بصري وحراري فردي", "#ff3366", "مشددة"
        elif score >= 35:
            return "مناظرة معززة (برتقالي): مسح حراري نشط بالكاميرات", "#ff9900", "معززة"
        else:
            return "مناظرة روتينية (سماوي): مراقبة اعتيادية للمسافرين", "#00e5ff", "روتينية"

    tiers = df_filtered["risk_score"].apply(assign_tier)
    df_filtered["action"] = [t[0] for t in tiers]
    df_filtered["color"] = [t[1] for t in tiers]
    df_filtered["level"] = [t[2] for t in tiers]

    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 نافذة التتبع الزمني")
    date_options = sorted(list(df_filtered["date"].unique()))
    time_scope = st.sidebar.radio("نطاق العرض:", ["كامل شهر سبتمبر (30 يوماً)", "تحديد يوم مخصص"])

    if time_scope == "تحديد يوم مخصص":
        active_day = st.sidebar.select_slider("اختر اليوم المطلوب:", options=date_options, value=date_options[0])
        df_view = df_filtered[df_filtered["date"] == active_day].copy()
        scope_title = f"ليوم {active_day}"
    else:
        df_view = df_filtered.copy()
        scope_title = "لكامل شهر سبتمبر (140+ رحلة)"

    k1, k2, k3, k4 = st.columns(4)
    total_f = len(df_view)
    total_p = int(df_view["pax"].sum())
    crit_f = len(df_view[df_view["level"] == "مشددة"])
    avg_r = df_view["risk_score"].mean() if total_f > 0 else 0

    k1.metric("إجمالي الرحلات المرصودة", f"{total_f:,}")
    k2.metric("إجمالي المسافرين الوافدين", f"{total_p:,}")
    k3.metric("رحلات المناظرة المشددة", f"{crit_f}", delta=f"{crit_f} رحلة حرجة" if crit_f > 0 else "الوضع مستقر", delta_color="inverse")
    k4.metric("متوسط الخطر الوبائي العام", f"{avg_r:.1f} / 100")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 التوزيع الزمني لمستويات الفرز طوال شهر سبتمبر")
    st.caption("يكشف هذا المخطط أيام الذروة الوبائية في المطار وأعداد الرحلات التي تتطلب مناظرة مشددة يوماً بيوم.")

    daily_summary = df_filtered.groupby(["date", "level"]).size().reset_index(name="count")
    daily_pivot = daily_summary.pivot(index="date", columns="level", values="count").fillna(0)
    for col in ["مشددة", "معززة", "روتينية"]:
        if col not in daily_pivot.columns:
            daily_pivot[col] = 0

    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Bar(name="مناظرة مشددة (أحمر)", x=daily_pivot.index, y=daily_pivot["مشددة"], marker_color="#ff3366"))
    fig_timeline.add_trace(go.Bar(name="مناظرة معززة (برتقالي)", x=daily_pivot.index, y=daily_pivot["معززة"], marker_color="#ff9900"))
    fig_timeline.add_trace(go.Bar(name="مناظرة روتينية (سماوي)", x=daily_pivot.index, y=daily_pivot["روتينية"], marker_color="#00e5ff"))

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
    st.subheader(f"📋 سجل الرحلات ومستويات المناظرة بصالة المطار ({scope_title})")
    cols_disp = ["flight", "date", "dest", "origin_city", "country", "pax", "duration_h", "risk_score", "action"]
    v_df = df_view[cols_disp].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    v_df.columns = ["رقم الرحلة", "التاريخ", "المنفذ", "محطة الإقلاع", "الدولة", "الركاب", "ساعات الطيران", "مؤشر الخطر", "إجراء المناظرة بصالة القدوم"]
    st.dataframe(v_df, use_container_width=True)

# =========================================================================
# الشاشة الثانية: مقصورة الطائرة التفاعلية الكاملة (Fuselage & Seats)
# =========================================================================
else:
    st.title("✈️ محاكاة مقصورة الطائرة وحصر المخالطين الميداني")
    st.caption("محاكاة دقيقة لهيكل الطائرة ومقاعد الركاب لتحديد دائرة المخالطين عند ورود بلاغ أو رصد حالة مشتبهة.")

    c_in1, c_in2 = st.columns([4, 6])
    with c_in1:
        st.subheader("📝 تفاصيل الحالة والمقعد")
        f_num = st.text_input("رقم الرحلة الجوية:", value="SV-314")
        chosen_row = st.number_input("رقم صف المقعد (1 إلى 30):", min_value=1, max_value=30, value=14)
        chosen_col = st.selectbox("رمز المقعد:", ["A", "B", "C", "D", "E", "F"], index=1)
        infected_seat = f"{chosen_row}{chosen_col}"
        st.info(f"**المرض المشتبه:** {selected_pathogen_name}\n\n**قاعدة الحصر:** `{p_info['tracing_rule']}`")

    total_rows = 30
    cols_order = ["A", "B", "C", "D", "E", "F"]
    traced
