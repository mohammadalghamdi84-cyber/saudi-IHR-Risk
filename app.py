import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# إعدادات الصفحة
st.set_page_config(
    page_title="منظومة ثغر | الترصد والاستشراف الوبائي بمنافذ الدخول",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص واجهة المستخدم: فرض اتجاه عربي كامل (RTL) للجداول والنصوص وإزالة الخطوط
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1b3e 0%, #060a17 100%) !important;
        color: #e2e8f0;
    }
    
    /* تنظيف القائمة الجانبية وإزالة الحدود */
    section[data-testid="stSidebar"] {
        background-color: #081026 !important;
        border-left: none !important;
        box-shadow: none !important;
        direction: rtl !important;
        text-align: right !important;
    }
    section[data-testid="stSidebar"] hr {
        display: none !important;
    }
    
    /* بطاقات الأرقام والمؤشرات */
    div[data-testid="stMetric"] {
        background: rgba(16, 35, 78, 0.7) !important;
        border: 1px solid rgba(0, 229, 255, 0.25) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-size: 1.7rem !important;
        font-weight: 800 !important;
    }
    
    /* فرض الاتجاه العربي التام على جداول Streamlit الداخلية */
    div[data-testid="stDataFrame"] {
        direction: rtl !important;
        text-align: right !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stDataFrame"] div {
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-testid="stDataFrame"] table, [data-testid="stTable"] table {
        direction: rtl !important;
        text-align: right !important;
        width: 100% !important;
    }
    div[data-testid="stDataFrame"] th, div[data-testid="stDataFrame"] td,
    [data-testid="stTable"] th, [data-testid="stTable"] td {
        text-align: right !important;
        direction: rtl !important;
    }

    h1, h2, h3, h4, h5, p, span, label {
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# قاعدة بيانات SPAR المتخصصة ومحطات القدوم الدولية والتهديد الوبائي الملازم لكل مسار
origins_spar_db = {
    "cairo": {"country": "مصر", "lat": 30.1219, "lon": 31.4056, "c4": 75, "c5": 72, "c10": 70, "duration_h": 2.2, "primary_threat": "متلازمة تنفسية حادة", "incidence": 15.0, "r0": 2.5},
    "dhaka": {"country": "بنغلاديش", "lat": 23.8433, "lon": 90.3978, "c4": 52, "c5": 48, "c10": 45, "duration_h": 6.5, "primary_threat": "الدرن الرئوي المفتوح", "incidence": 32.0, "r0": 3.2},
    "islamabad": {"country": "باكستان", "lat": 33.5492, "lon": 72.8277, "c4": 58, "c5": 56, "c10": 52, "duration_h": 4.8, "primary_threat": "الدرن الرئوي المفتوح", "incidence": 30.0, "r0": 3.2},
    "lahore": {"country": "باكستان", "lat": 31.5216, "lon": 74.4036, "c4": 58, "c5": 56, "c10": 52, "duration_h": 4.5, "primary_threat": "جدري الماء / حماق", "incidence": 24.0, "r0": 1.6},
    "jakarta": {"country": "إندونيسيا", "lat": -6.1275, "lon": 106.6537, "c4": 74, "c5": 70, "c10": 68, "duration_h": 9.5, "primary_threat": "الدرن الرئوي المفتوح", "incidence": 26.0, "r0": 3.2},
    "delhi": {"country": "الهند", "lat": 28.5562, "lon": 77.1000, "c4": 65, "c5": 62, "c10": 58, "duration_h": 5.0, "primary_threat": "الدرن الرئوي المفتوح", "incidence": 35.0, "r0": 3.2},
    "kano": {"country": "نيجيريا", "lat": 12.0476, "lon": 8.5246, "c4": 42, "c5": 38, "c10": 35, "duration_h": 6.0, "primary_threat": "حمى نزفية فيروسية", "incidence": 22.0, "r0": 2.2},
    "istanbul": {"country": "تركيا", "lat": 41.2753, "lon": 28.7519, "c4": 85, "c5": 82, "c10": 80, "duration_h": 3.5, "primary_threat": "متلازمة تنفسية حادة", "incidence": 8.0, "r0": 2.2},
    "amman": {"country": "الأردن", "lat": 31.7226, "lon": 35.9932, "c4": 78, "c5": 75, "c10": 72, "duration_h": 1.8, "primary_threat": "متلازمة تنفسية حادة", "incidence": 6.0, "r0": 2.2},
    "london": {"country": "المملكة المتحدة", "lat": 51.4700, "lon": -0.4543, "c4": 94, "c5": 92, "c10": 90, "duration_h": 6.5, "primary_threat": "إنفلونزا موسمية حادة", "incidence": 5.0, "r0": 1.8}
}

national_airports = {
    "MED": {"name": "مطار الأمير محمد بن عبدالعزيز (المدينة المنورة)", "lat": 24.5534, "lon": 39.7051},
    "JED": {"name": "مطار الملك عبدالعزيز الدولي (جدة)", "lat": 21.6796, "lon": 39.1565},
    "RUH": {"name": "مطار الملك خالد الدولي (الرياض)", "lat": 24.9576, "lon": 46.6988}
}

pathogen_metadata = {
    "الدرن الرئوي المفتوح (محمول جواً)": {
        "r0": 3.2, "incubation_days": 30.0, "type": "airborne",
        "severity": "عالية ومزمنة", "tracing_rule": "full_cabin",
        "ppe_directive": "المستوى الثالث: كمامة N95 محكمة القياس مع نظارات واقية ومريول طبي معقم وقفازات.",
        "ppe_item_name": "كمامات تنفسية N95 مفحوصة القياس"
    },
    "متلازمة تنفسية حادة / إنفلونزا وبائية (رذاذي)": {
        "r0": 2.5, "incubation_days": 3.5, "type": "droplet",
        "severity": "متوسطة إلى عالية", "tracing_rule": "droplet_sector",
        "ppe_directive": "مستوى الرذاذ: كمامة جراحية عالية الترشيح أو N95 مع واقي كامل للوجه ومريول عازل.",
        "ppe_item_name": "أطقم وقاية رذاذية متكاملة مع واقي وجه"
    },
    "جدري الماء / حماق (تلامسي مختلط)": {
        "r0": 1.6, "incubation_days": 14.0, "type": "contact_skin",
        "severity": "خفيفة إلى معتدلة", "tracing_rule": "adjacent_only",
        "ppe_directive": "مستوى التلامس: مريول طبي معقم وقفازات فحص عازلة مع كمامة جراحية أثناء المعاينة.",
        "ppe_item_name": "أطقم فحص تلامسي مخصصة"
    }
}

# شريط التنقل الجانبي
st.sidebar.markdown("### إدارة المنظومة")
view_mode = st.sidebar.radio(
    "الشاشات الميدانية:",
    [
        "الترصد الوبائي ومناظرة الرحلات",
        "بروتوكول البلاغات وتتبع مقصورة الطائرة",
        "تقييم الجاهزية التشغيلية والإمداد"
    ]
)

rumor_factor = st.sidebar.slider(
    "معامل البلاغات غير الرسمية (ω):",
    min_value=1.0, max_value=3.0, value=1.0, step=0.2,
    help="معامل استخباراتي يُرفع عند رصد بلاغات غير رسمية أو إشارات في بلد المنشأ"
)

# -------------------------------------------------------------------------
# قراءة ملف الإكسل المرفوع تلقائياً مع معالجة البيانات
# -------------------------------------------------------------------------
DEFAULT_EXCEL_FILE = "FLIGHTS - Sep 26.xlsx"

@st.cache_data
def load_schedule_data():
    df = None
    if os.path.exists(DEFAULT_EXCEL_FILE):
        try:
            df = pd.read_excel(DEFAULT_EXCEL_FILE)
        except Exception:
            df = None
            
    if df is None or df.empty:
        np.random.seed(42)
        origins_keys = list(origins_spar_db.keys())
        data = []
        flight_idx = 100
        for day in range(1, 31):
            date_str = f"2026-09-{day:02d}"
            for dest in ["MED", "JED", "RUH"]:
                daily_count = np.random.randint(2, 5) if dest in ["MED", "JED"] else np.random.randint(1, 3)
                for _ in range(daily_count):
                    orig_k = origins_keys[np.random.randint(0, len(origins_keys))]
                    orig_data = origins_spar_db[orig_k]
                    hour = np.random.choice(["02:30", "06:15", "10:45", "14:20", "18:50", "22:10"])
                    data.append({
                        "flight": f"SV-{flight_idx}",
                        "date": date_str,
                        "time": hour,
                        "dest": dest,
                        "origin_city": orig_k.capitalize(),
                        "country": orig_data["country"],
                        "pax": int(np.random.randint(260, 410)),
                        "duration_h": orig_data["duration_h"]
                    })
                    flight_idx += 2
        df = pd.DataFrame(data)

    column_mapping = {
        "رقم الرحلة": "flight", "تاريخ الوصول": "date", "وقت الوصول": "time",
        "مطار الوصول": "dest", "مدينة القدوم": "origin_city", "دولة القدوم": "country",
        "عدد الركاب": "pax", "مدة الرحلة (ساعات)": "duration_h", "Flight": "flight",
        "Date": "date", "Time": "time", "Dest": "dest", "Origin": "origin_city",
        "Country": "country", "Pax": "pax", "Duration": "duration_h"
    }
    df = df.rename(columns=column_mapping)

    if "time" not in df.columns:
        times_pool = ["02:30", "06:15", "10:45", "14:20", "18:50", "22:10"]
        df["time"] = [times_pool[i % len(times_pool)] for i in range(len(df))]

    c4_l, c5_l, c10_l, lat_l, lon_l, threat_l, inc_l, r0_l = [], [], [], [], [], [], [], []
    for _, row in df.iterrows():
        orig_lookup = str(row.get("origin_city", "")).lower().strip()
        matched = origins_spar_db.get(orig_lookup)
        
        if not matched:
            ctry_lookup = str(row.get("country", "")).strip()
            for k, v in origins_spar_db.items():
                if v["country"] == ctry_lookup:
                    matched = v
                    break

        if matched:
            c4_l.append(matched["c4"])
            c5_l.append(matched["c5"])
            c10_l.append(matched["c10"])
            lat_l.append(matched["lat"])
            lon_l.append(matched["lon"])
            threat_l.append(matched["primary_threat"])
            inc_l.append(matched["incidence"])
            r0_l.append(matched["r0"])
        else:
            c4_l.append(65)
            c5_l.append(60)
            c10_l.append(60)
            lat_l.append(25.0)
            lon_l.append(45.0)
            threat_l.append("متلازمة تنفسية")
            inc_l.append(10.0)
            r0_l.append(2.0)

    df["c4"] = c4_l
    df["c5"] = c5_l
    df["c10"] = c10_l
    df["lat"] = lat_l
    df["lon"] = lon_l
    df["primary_threat"] = threat_l
    df["incidence"] = inc_l
    df["r0"] = r0_l

    return df

df_all = load_schedule_data()

# محرك الحساب: تقييم كل رحلة بموجب التهديد الوبائي الخاص بوجهتها
def compute_flight_risk(row):
    spar_core = (row["c4"] + row["c5"] + row["c10"]) / 3.0
    surveillance_gap = (100.0 - spar_core) / 35.0
    
    pathogen_weight = float(np.clip((row["incidence"] / 40.0) * (row["r0"] / 2.0) * 35.0, 4.0, 35.0))
    spar_weight = float(np.clip(surveillance_gap * 15.0, 6.0, 35.0))
    flight_weight = float(np.clip((row["duration_h"] / 10.0) * 15.0, 3.0, 15.0))
    rumor_weight = float(np.clip((rumor_factor - 1.0) * 15.0, 0.0, 15.0))
    
    total_score = float(np.clip(pathogen_weight + spar_weight + flight_weight + rumor_weight, 8.0, 96.0).round(1))
    
    hover_text = (
        f"الرحلة: {row['flight']} ({row['time']})<br>"
        f"محطة الإقلاع: {row['origin_city']} ({row['country']})<br>"
        f"التهديد المحتمل: {row['primary_threat']}<br>"
        f"مؤشر SPAR: {spar_core:.1f}/100 | R0={row['r0']}"
    )
    
    return pd.Series([
        f"{pathogen_weight:.1f}%",
        f"{spar_weight:.1f}%",
        f"{flight_weight:.1f}%",
        total_score,
        hover_text
    ])

breakdown_df = df_all.apply(compute_flight_risk, axis=1)
df_all["w_pathogen"] = breakdown_df[0]
df_all["w_spar"] = breakdown_df[1]
df_all["w_flight"] = breakdown_df[2]
df_all["risk_score"] = breakdown_df[3]
df_all["risk_hover"] = breakdown_df[4]

def assign_tier(score):
    if score >= 65:
        return "مشددة", "#e63946", "حرج"
    elif score >= 35:
        return "معززة", "#f4a261", "متوسط"
    else:
        return "روتينية", "#2a9d8f", "منخفض"

tiers = df_all["risk_score"].apply(assign_tier)
df_all["action"] = [t[0] for t in tiers]
df_all["color"] = [t[1] for t in tiers]
df_all["level"] = [t[2] for t in tiers]

# =========================================================================
# الشاشة الأولى: الترصد الوبائي ومناظرة الرحلات (كامل الشهر متاح دائماً)
# =========================================================================
if view_mode == "الترصد الوبائي ومناظرة الرحلات":
    st.title("منظومة الترصد والاستشراف الوبائي بمنافذ الدخول")
    st.caption(f"جدول تشغيلي شامل لرحلات شهر سبتمبر | مضاعف البلاغات غير الرسمية: {rumor_factor}x | مصدر البيانات: {DEFAULT_EXCEL_FILE}")

    selected_airports = st.sidebar.multiselect(
        "المنافذ الوطنية المراقبة:",
        options=list(national_airports.keys()),
        default=["MED", "JED"],
        format_func=lambda x: national_airports[x]["name"]
    )
    if not selected_airports:
        st.warning("يرجى اختيار منفذ واحد على الأقل.")
        st.stop()

    df_filtered = df_all[df_all["dest"].isin(selected_airports)].copy()

    # خيارات التتبع الزمني (كامل الشهر كخيار افتراضي وأساسي)
    date_options = sorted(list(df_filtered["date"].unique()))
    time_scope = st.sidebar.radio("نطاق العرض الزمني:", ["كامل شهر سبتمبر (30 يوماً)", "تحديد يوم مخصص"])

    if time_scope == "تحديد يوم مخصص":
        active_day = st.sidebar.select_slider("اختر اليوم المطلوب:", options=date_options, value=date_options[0])
        df_view = df_filtered[df_filtered["date"] == active_day].copy()
        scope_title = f"ليوم {active_day}"
    else:
        df_view = df_filtered.copy()
        scope_title = "لكامل شهر سبتمبر (140+ رحلة)"

    # المؤشرات الرئيسية
    k1, k2, k3, k4 = st.columns(4)
    tot_f = len(df_view)
    tot_p = int(df_view["pax"].sum())
    crit_f = len(df_view[df_view["level"] == "حرج"])
    med_f = len(df_view[df_view["level"] == "متوسط"])
    low_f = len(df_view[df_view["level"] == "منخفض"])

    k1.metric("إجمالي الرحلات المرصودة", f"{tot_f} رحلة")
    k2.metric("إجمالي المسافرين الوافدين", f"{tot_p:,} مسافر")
    k3.metric("الرحلات عالية الخطورة", f"{crit_f} رحلة", delta="المنافذ آمنة" if crit_f == 0 else "تتطلب مناظرة مشددة", delta_color="normal" if crit_f == 0 else "inverse")
    k4.metric("توزيع مستويات الفرز", f"{med_f} معزز | {low_f} روتيني")

    st.markdown("<br>", unsafe_allow_html=True)

    # المخطط الزمني التفاعلي لكامل شهر سبتمبر
    st.subheader("التوزيع الزمني لمستويات المناظرة طوال شهر سبتمبر")
    
    dates_grouped = []
    for d in date_options:
        sub_d = df_filtered[df_filtered["date"] == d]
        c_sub = len(sub_d[sub_d["level"] == "حرج"])
        m_sub = len(sub_d[sub_d["level"] == "متوسط"])
        l_sub = len(sub_d[sub_d["level"] == "منخفض"])
        
        crit_details = sub_d[sub_d["level"] == "حرج"]
        if len(crit_details) > 0:
            crit_txt = "<br>".join([f"• {r['flight']} من {r['origin_city']} ({r['time']}) - {r['primary_threat']}" for _, r in crit_details.iterrows()])
        else:
            crit_txt = "لا توجد رحلات حرجة"
            
        dates_grouped.append({
            "date": d,
            "حرج": c_sub, "متوسط": m_sub, "منخفض": l_sub,
            "crit_hover": f"التاريخ: {d}<br>الرحلات الحرجة ({c_sub}):<br>{crit_txt}"
        })
    piv_df = pd.DataFrame(dates_grouped)

    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Bar(
        name="مناظرة مشددة",
        x=piv_df["date"], y=piv_df["حرج"],
        marker_color="#e63946",
        hovertext=piv_df["crit_hover"],
        hoverinfo="text"
    ))
    fig_timeline.add_trace(go.Bar(
        name="مناظرة معززة",
        x=piv_df["date"], y=piv_df["متوسط"],
        marker_color="#f4a261",
        hoverinfo="x+y"
    ))
    fig_timeline.add_trace(go.Bar(
        name="مناظرة روتينية",
        x=piv_df["date"], y=piv_df["منخفض"],
        marker_color="#2a9d8f",
        hoverinfo="x+y"
    ))

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

    # خريطة التدفق الجوي والمسارات الوبائية
    st.subheader(f"خريطة التدفق الجوي والمسارات الوبائية ({scope_title})")
    fig_map = go.Figure()

    for _, r in df_view.iterrows():
        dest_coord = national_airports[r["dest"]]
        fig_map.add_trace(go.Scattergeo(
            lon=[r["lon"], dest_coord["lon"]],
            lat=[r["lat"], dest_coord["lat"]],
            mode="lines",
            line=dict(width=2.0, color=r["color"]),
            opacity=0.75,
            hoverinfo="none",
            showlegend=False
        ))

    fig_map.add_trace(go.Scattergeo(
        lon=df_view["lon"],
        lat=df_view["lat"],
        text=df_view["risk_hover"],
        hoverinfo="text",
        mode="markers",
        marker=dict(size=10, color=df_view["color"], line=dict(width=1, color="#ffffff")),
        name="محطات الإقلاع الدولية"
    ))

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
        marker=dict(size=16, color="#00e5ff", symbol="square", line=dict(width=2, color="#ffffff")),
        name="المنافذ الوطنية"
    ))

    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=500,
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

    # جدول فرز الرحلات وتفكيك أوزان الخطر (يوضح التهديد الوبائي المحتمل صراحة لكل رحلة)
    st.subheader(f"جدول فرز الرحلات وتفكيك أوزان الخطر ({scope_title})")
    table_cols = [
        "flight", "date", "time", "dest", "origin_city", "country", "primary_threat", "pax",
        "w_pathogen", "w_spar", "w_flight", "risk_score", "action"
    ]
    disp_df = df_view[table_cols].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    disp_df.columns = [
        "رقم الرحلة", "التاريخ", "وقت الوصول", "المنفذ", "محطة الإقلاع", "الدولة", "التهديد الوبائي الملازم", "الركاب",
        "وزن الممرض", "فجوة SPAR", "وزن الرحلة", "مؤشر الخطورة", "مستوى المناظرة الميدانية"
    ]

    def highlight_score(val):
        if val >= 65:
            color = '#e63946'
        elif val >= 35:
            color = '#f4a261'
        else:
            color = '#2a9d8f'
        return f'background-color: {color}; color: #ffffff; font-weight: bold; border-radius: 4px; text-align: center;'

    styled_df = disp_df.style.map(highlight_score, subset=["مؤشر الخطورة"]).set_properties(**{'text-align': 'right'})
    st.dataframe(styled_df, use_container_width=True)

# =========================================================================
# الشاشة الثانية: بروتوكول البلاغات وتتبع مقصورة الطائرة
# =========================================================================
elif view_mode == "بروتوكول البلاغات وتتبع مقصورة الطائرة":
    st.title("بروتوكول البلاغات وتتبع مقصورة الطائرة")
    
    selected_pathogen_name = st.sidebar.selectbox("التهديد الوبائي المبلّغ عنه:", list(pathogen_metadata.keys()))
    p_info = pathogen_metadata[selected_pathogen_name]

    st.markdown(f"""
    <div style="background: rgba(16, 35, 78, 0.7); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 8px; padding: 14px; margin-bottom: 20px; direction: rtl; text-align: right;">
        <h4 style="color: #00e5ff; margin: 0 0 6px 0;">توجيهات الوقاية الشخصية للفريق الميداني ({selected_pathogen_name})</h4>
        <p style="margin: 0; font-size: 1rem;">{p_info['ppe_directive']}</p>
        <span style="font-size: 0.85rem; color: #94a3b8;">البند المعتمد: {p_info['ppe_item_name']} | تصنيف الخطورة: {p_info['severity']}</span>
    </div>
    """, unsafe_allow_html=True)

    c_in1, c_in2 = st.columns([4, 6])
    with c_in1:
        st.subheader("بيانات الحالة والمقصورة")
        plane_type = st.selectbox(
            "طراز الطائرة والتشكيل:",
            ["طائرة ضيقة الممر (3-3 / Airbus A320)", "طائرة عريضة البدن بممرين (3-3-3 / Boeing 777)"]
        )
        
        f_num = st.text_input("رقم الرحلة الجوية:", value="SV-112")
        chosen_row = st.number_input("صف المقعد للحالة المشتبهة (1 إلى 30):", min_value=1, max_value=30, value=12)
        
        if "3-3-3" in plane_type:
            cols_order = ["A", "B", "C", "D", "E", "F", "G", "H", "J"]
            col_x_map = {"A": 1.2, "B": 2.0, "C": 2.8, "D": 4.2, "E": 5.0, "F": 5.8, "G": 7.2, "H": 8.0, "J": 8.8}
            fuselage_width = 10.0
        else:
            cols_order = ["A", "B", "C", "D", "E", "F"]
            col_x_map = {"A": 1.4, "B": 2.2, "C": 3.0, "D": 4.6, "E": 5.4, "F": 6.2}
            fuselage_width = 7.6

        chosen_col = st.selectbox("رمز المقعد للحالة المشتبهة:", cols_order, index=1)
        infected_seat = f"{chosen_row}{chosen_col}"

    total_rows = 30
    traced_seats = []

    if p_info["tracing_rule"] == "full_cabin":
        for r in range(1, total_rows + 1):
            for c in cols_order:
                if f"{r}{c}" != infected_seat:
                    traced_seats.append(f"{r}{c}")
        rule_desc = "حصر كامل مقصورة الركاب"

    elif p_info["tracing_rule"] == "droplet_sector":
        start_r = max(1, chosen_row - 2)
        end_r = min(total_rows, chosen_row + 2)
        
        if "3-3-3" in plane_type:
            if chosen_col in ["A", "B", "C"]:
                target_cols = ["A", "B", "C", "D", "E", "F"]
            elif chosen_col in ["G", "H", "J"]:
                target_cols = ["D", "E", "F", "G", "H", "J"]
            else:
                target_cols = cols_order
        else:
            target_cols = cols_order

        for r in range(start_r, end_r + 1):
            for c in target_cols:
                if f"{r}{c}" != infected_seat:
                    traced_seats.append(f"{r}{c}")
        rule_desc = "حصر صفين للأمام وصفين للخلف مع المقاطع المتصلة عبر الممر"

    else:
        c_idx = cols_order.index(chosen_col)
        if c_idx > 0: traced_seats.append(f"{chosen_row}{cols_order[c_idx - 1]}")
        if c_idx < len(cols_order) - 1: traced_seats.append(f"{chosen_row}{cols_order[c_idx + 1]}")
        rule_desc = "حصر المقاعد الملاصقة مباشرة في نفس الصف"

    with c_in2:
        st.subheader("مخرجات حصر المخالطين")
        m1, m2 = st.columns(2)
        m1.metric("رقم المقعد للحالة المشتبهة", infected_seat)
        m2.metric("عدد ركاب حصر المخالطين", f"{len(traced_seats)} راكب")
        st.info(f"إجراء الحصر المعتمد: {rule_desc}")

        export_df = pd.DataFrame({
            "رقم الرحلة": [f_num] * (len(traced_seats) + 1),
            "المقعد": [infected_seat] + traced_seats,
            "التصنيف": ["الحالة المشتبهة"] + ["حصر مخالطين"] * len(traced_seats),
            "المرض": [selected_pathogen_name] * (len(traced_seats) + 1)
        })
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="تصدير كشف حصر المخالطين (CSV)",
            data=csv_data,
            file_name=f"Contact_Tracing_{f_num}.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.subheader("موقع الحالة والمخالطين")

    fig_plane = go.Figure()

    center_x = fuselage_width / 2.0
    t = np.linspace(0, np.pi, 30)
    nose_x = center_x + (center_x - 0.4) * np.cos(t)
    nose_y = 2 - 4.5 * np.sin(t)

    fuselage_x = list(nose_x) + [fuselage_width - 0.4, fuselage_width - 0.4, center_x + 1.2, center_x, center_x - 1.2, 0.4, 0.4]
    fuselage_y = list(nose_y) + [2, 32, 34.5, 35.5, 34.5, 32, 2]

    fig_plane.add_trace(go.Scatter(
        x=fuselage_x, y=fuselage_y,
        fill="toself",
        fillcolor="rgba(12, 28, 62, 0.6)",
        line=dict(color="#00e5ff", width=2.0),
        hoverinfo="none",
        showlegend=False
    ))

    fig_plane.add_trace(go.Scatter(
        x=[center_x], y=[-1.5],
        mode="text", text=["قمرة القيادة"],
        textfont=dict(color="#00e5ff", size=11, family="Tajawal"),
        hoverinfo="none", showlegend=False
    ))
    fig_plane.add_trace(go.Scatter(
        x=[0.4, fuselage_width - 0.4, 0.4, fuselage_width - 0.4],
        y=[2, 2, 16, 16],
        mode="text", text=["مخرج", "مخرج", "طوارئ", "طوارئ"],
        textfont=dict(color="#f4a261", size=10, family="Tajawal"),
        hoverinfo="none", showlegend=False
    ))

    seat_xs, seat_ys, seat_texts, seat_colors, seat_hovers = [], [], [], [], []

    for r in range(1, total_rows + 1):
        for c in cols_order:
            s_code = f"{r}{c}"
            seat_xs.append(col_x_map[c])
            seat_ys.append(r)
            seat_texts.append(s_code)

            if s_code == infected_seat:
                seat_colors.append("#e63946")
                seat_hovers.append(f"المقعد: {s_code} (الحالة المشتبهة)")
            elif s_code in traced_seats:
                seat_colors.append("#f4a261")
                seat_hovers.append(f"المقعد: {s_code} (حصر مخالطين)")
            else:
                seat_colors.append("#0c203b")
                seat_hovers.append(f"المقعد: {s_code} (مسافر سليم)")

    fig_plane.add_trace(go.Scatter(
        x=seat_xs, y=seat_ys,
        mode="markers+text",
        text=seat_texts,
        textposition="middle center",
        textfont=dict(size=7.5, color="#ffffff", family="Tajawal"),
        marker=dict(size=19, color=seat_colors, symbol="square", line=dict(width=1.0, color="rgba(0, 229, 255, 0.4)")),
        hoverinfo="text", hovertext=seat_hovers, showlegend=False
    ))

    fig_plane.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(6, 12, 28, 0.7)",
        height=850,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(autorange="reversed", showgrid=False, zeroline=False, range=[-3.5, 36], dtick=1, color="#94a3b8")
    )
    st.plotly_chart(fig_plane, use_container_width=True)

# =========================================================================
# الشاشة الثالثة: تقييم الجاهزية التشغيلية والإمداد (RTL كامل وتلوين مباشر)
# =========================================================================
else:
    st.title("تقييم الجاهزية التشغيلية والإمداد")
    st.caption("تدقيق السعة السريرية لغرف العزل وسلاسل الإمداد ومستوى جاهزية الكوادر الميدانية")

    target_port = st.sidebar.selectbox(
        "منفذ المراقبة الصحية المستهدف:",
        options=list(national_airports.keys()),
        format_func=lambda x: national_airports[x]["name"],
        index=0
    )
    port_name = national_airports[target_port]["name"]

    # 1. تدقيق غرف العزل بالمنفذ مع غرفة غير مطابقة
    st.subheader(f"تدقيق غرف العزل المؤقتة بالمنفذ ({port_name})")
    
    iso_audit_data = [
        {"رقم الغرفة": "وحدة العزل 1", "الحالة التشغيلية": "شاغرة ومطابقة", "نظام ضغط سالب": "✓ مطابق", "دورة مياه مستقلة": "✓ متوفر", "مسار نقل آمن": "✓ مخصص", "التطهير الطبي": "✓ معتمد"},
        {"رقم الغرفة": "وحدة العزل 2", "الحالة التشغيلية": "تنبيه: غير جاهزة", "نظام ضغط سالب": "✗ غير مطابق (يحتاج صيانة)", "دورة مياه مستقلة": "✓ متوفر", "مسار نقل آمن": "✓ مخصص", "التطهير الطبي": "✓ معتمد"},
    ]
    if target_port in ["JED", "RUH"]:
        iso_audit_data.extend([
            {"رقم الغرفة": "وحدة العزل 3", "الحالة التشغيلية": "شاغرة ومطابقة", "نظام ضغط سالب": "✓ مطابق", "دورة مياه مستقلة": "✓ متوفر", "مسار نقل آمن": "✓ مخصص", "التطهير الطبي": "✓ معتمد"},
            {"رقم الغرفة": "وحدة العزل 4", "الحالة التشغيلية": "شاغرة ومطابقة", "نظام ضغط سالب": "✓ مطابق", "دورة مياه مستقلة": "✓ متوفر", "مسار نقل آمن": "✓ مخصص", "التطهير الطبي": "✓ معتمد"},
        ])
    
    df_iso_audit = pd.DataFrame(iso_audit_data)

    def style_iso_checks(val):
        if str(val).startswith("✓"):
            return "color: #2a9d8f; font-weight: bold; text-align: right;"
        elif str(val).startswith("✗"):
            return "color: #e63946; font-weight: bold; background-color: rgba(230, 57, 70, 0.15); border-radius: 4px; text-align: right;"
        elif "تنبيه" in str(val):
            return "color: #e63946; font-weight: bold; text-align: right;"
        return "text-align: right;"

    styled_iso = df_iso_audit.style.map(style_iso_checks).set_properties(**{'text-align': 'right'})
    st.dataframe(styled_iso, use_container_width=True)

    st.warning("⚠️ **تنبيه لصاحب القرار:** وحدة العزل (2) بها خلل في معيار الضغط السالب وتحتاج إلى صيانة عاجلة. يقتصر استخدام العزل الفعلي حالياً على الوحدات المطابقة فقط.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. سلاسل الإمداد والتجهيزات الطبية
    st.subheader("أرصدة المستلزمات الوقائية والتجهيزات الحرارية")
    
    supply_rows = [
        {"بند التجهيز والإمداد": "أطقم عزل بيولوجي متكامل (Bio-Hazard Suit)", "العدد المتوفر": 22, "الحد الأدنى المطلوب": 15, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة": "✓ صالحة للاستخدام"},
        {"بند التجهيز والإمداد": "كمامات تنفسية متخصصة (Fit-tested N95)", "العدد المتوفر": 140, "الحد الأدنى المطلوب": 40, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة": "✓ صالحة للاستخدام"},
        {"بند التجهيز والإمداد": "حزم حماية رذاذية متكاملة مع واقي وجه", "العدد المتوفر": 250, "الحد الأدنى المطلوب": 60, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة": "✗ قارب انتهاء الدفعة"},
        {"بند التجهيز والإمداد": "أطقم فحص تلامسي قياسية", "العدد المتوفر": 80, "الحد الأدنى المطلوب": 25, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة": "✓ صالحة للاستخدام"},
        {"بند التجهيز والإمداد": "كاميرات الفحص والمسح الحراري الثابتة", "العدد المتوفر": 6, "الحد الأدنى المطلوب": 4, "مؤشر الرصيد": "✓ تعمل بكفاءة", "المعاينة": "✓ معايرة دورية نشطة"},
        {"بند التجهيز والإمداد": "أجهزة قياس الحرارة المحمولة بالأشعة تحت الحمراء", "العدد المتوفر": 12, "الحد الأدنى المطلوب": 8, "مؤشر الرصيد": "✓ متوفر بالعيادة", "المعاينة": "✓ جاهزة للتشغيل"}
    ]
    df_supply = pd.DataFrame(supply_rows)
    styled_supply = df_supply.style.map(style_iso_checks, subset=["مؤشر الرصيد", "المعاينة"]).set_properties(**{'text-align': 'right'})
    st.dataframe(styled_supply, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. تدريب وتأهيل الكوادر الميدانية
    st.subheader("جاهزية وتأهيل الكوادر الصحية الميدانية")
    
    team_training_data = [
        {"المسار التدريبي والتأهيلي": "شهادة أساسيات مكافحة العدوى والوقاية (BICSL)", "عدد الكوادر المعتمدة": "18 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "100%", "حالة الجاهزية": "✓ مكتمل بالكامل"},
        {"المسار التدريبي والتأهيلي": "بروتوكول فرز ومناظرة الأمراض التنفسية الحادة بمنافذ الدخول", "عدد الكوادر المعتمدة": "16 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "88%", "حالة الجاهزية": "✓ جاهزية تشغيلية عالية"},
        {"المسار التدريبي والتأهيلي": "إجراءات العزل المؤقت والنقل الطبي الآمن للحالات المشتبهة", "عدد الكوادر المعتمدة": "15 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "83%", "حالة الجاهزية": "✓ مستمر ضمن المناوبات"},
        {"المسار التدريبي والتأهيلي": "استخدام وتطبيق اللوائح الصحية الدولية (IHR) في المطارات", "عدد الكوادر المعتمدة": "18 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "100%", "حالة الجاهزية": "✓ مكتمل بالكامل"}
    ]
    df_training = pd.DataFrame(team_training_data)
    styled_training = df_training.style.map(style_iso_checks, subset=["حالة الجاهزية"]).set_properties(**{'text-align': 'right'})
    st.dataframe(styled_training, use_container_width=True)
