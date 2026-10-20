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

# تخصيص واجهة المستخدم: اتجاه عربي كامل
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

    /* تنسيق HTML للجداول لضمان الاتجاه العربي الصارم والتلوين */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
        text-align: right;
        margin-top: 10px;
        background-color: rgba(10, 20, 48, 0.5);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 8px;
        overflow: hidden;
    }
    .custom-table th {
        background-color: rgba(16, 35, 78, 0.9);
        color: #00e5ff;
        padding: 10px 14px;
        font-size: 0.9rem;
        border-bottom: 2px solid rgba(0, 229, 255, 0.3);
        text-align: right;
    }
    .custom-table td {
        padding: 9px 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.88rem;
        color: #e2e8f0;
        text-align: right;
    }
    .custom-table tr:hover {
        background-color: rgba(0, 229, 255, 0.05);
    }
    .badge-check {
        color: #2a9d8f;
        font-weight: bold;
    }
    .badge-alert {
        color: #e63946;
        font-weight: bold;
        background-color: rgba(230, 57, 70, 0.15);
        padding: 2px 6px;
        border-radius: 4px;
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

# شريط التنقل
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
# محرك قراءة وتوليد رحلات شهر سبتمبر الكاملة (150+ رحلة مضمونة)
# -------------------------------------------------------------------------
possible_filenames = ["FLIGHTS - Sep 26.xlsx", "FLIGHTS - Sep 26.xls", "flights.xlsx", "flights_data.xlsx"]

@st.cache_data
def load_schedule_data():
    df = None
    loaded_source = "قاعدة بيانات سبتمبر الافتراضية المدمجة"

    # محاولة قراءة الملف المرفوع إذا وجد
    for fname in possible_filenames:
        if os.path.exists(fname):
            try:
                df = pd.read_excel(fname)
                loaded_source = f"الملف المرفوع: {fname}"
                break
            except Exception:
                pass

    # إذا لم يوجد الملف أو فشلت قراءته، ننشئ جدول سبتمبر الكامل لـ 30 يوماً (150 رحلة كاملة)
    if df is None or len(df) < 50:
        origins_list = list(origins_spar_db.keys())
        data = []
        flight_idx = 102
        time_slots = ["01:15", "03:40", "06:20", "09:05", "11:30", "14:50", "17:15", "19:40", "21:10", "23:25"]
        
        for day in range(1, 31):
            date_str = f"2026-09-{day:02d}"
            # توليد 5 رحلات يومياً موزعة على منافذ المملكة
            daily_schedule = [
                ("MED", origins_list[(day * 2) % len(origins_list)]),
                ("MED", origins_list[(day * 2 + 1) % len(origins_list)]),
                ("JED", origins_list[(day * 3) % len(origins_list)]),
                ("JED", origins_list[(day * 3 + 2) % len(origins_list)]),
                ("RUH", origins_list[(day * 5) % len(origins_list)])
            ]
            for slot_idx, (dest_code, orig_k) in enumerate(daily_schedule):
                orig_data = origins_spar_db[orig_k]
                pax_val = 310 + ((day * 7 + slot_idx * 13) % 95)
                data.append({
                    "flight": f"SV-{flight_idx}",
                    "date": date_str,
                    "time": time_slots[(day + slot_idx) % len(time_slots)],
                    "dest": dest_code,
                    "origin_city": orig_k.capitalize(),
                    "country": orig_data["country"],
                    "pax": int(pax_val),
                    "duration_h": orig_data["duration_h"]
                })
                flight_idx += 2
        df = pd.DataFrame(data)

    # توحيد أسماء الأعمدة
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

    return df, loaded_source

df_all, data_source_name = load_schedule_data()

# محرك الحساب
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
        f"التهديد: {row['primary_threat']}<br>"
        f"مؤشر SPAR: {spar_core:.1f}/100"
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
# الشاشة الأولى: الترصد الوبائي ومناظرة الرحلات
# =========================================================================
if view_mode == "الترصد الوبائي ومناظرة الرحلات":
    st.title("منظومة الترصد والاستشراف الوبائي بمنافذ الدخول")
    st.caption(f"حالة البيانات: {data_source_name} | إجمالي المسجل: {len(df_all)} رحلة | مضاعف البلاغات: {rumor_factor}x")

    # تحديد المنافذ المشمولة
    selected_airports = st.sidebar.multiselect(
        "المنافذ الوطنية المراقبة:",
        options=list(national_airports.keys()),
        default=["MED", "JED", "RUH"],
        format_func=lambda x: national_airports[x]["name"]
    )
    if not selected_airports:
        st.warning("يرجى اختيار منفذ واحد على الأقل.")
        st.stop()

    df_filtered = df_all[df_all["dest"].isin(selected_airports)].copy()

    date_options = sorted(list(df_filtered["date"].unique()))
    time_scope = st.sidebar.radio("نطاق العرض الزمني:", ["كامل شهر سبتمبر (30 يوماً)", "تحديد يوم مخصص"])

    if time_scope == "تحديد يوم مخصص":
        active_day = st.sidebar.select_slider("اختر اليوم المطلوب:", options=date_options, value=date_options[0])
        df_view = df_filtered[df_filtered["date"] == active_day].copy()
        scope_title = f"ليوم {active_day}"
    else:
        df_view = df_filtered.copy()
        scope_title = f"لكامل شهر سبتمبر ({len(df_view)} رحلة)"

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

    # المخطط الزمني لتوزيع الرحلات
    st.subheader(f"التوزيع الزمني لمستويات المناظرة ({scope_title})")
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

    # خريطة التدفق الجوي
    st.subheader(f"خريطة التدفق الجوي والمسارات الوبائية ({scope_title})")
    fig_map = go.Figure()

    for _, r in df_view.iterrows():
        dest_coord = national_airports[r["dest"]]
        fig_map.add_trace(go.Scattergeo(
            lon=[r["lon"], dest_coord["lon"]],
            lat=[r["lat"], dest_coord["lat"]],
            mode="lines",
            line=dict(width=1.8, color=r["color"]),
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
        marker=dict(size=9, color=df_view["color"], line=dict(width=1, color="#ffffff")),
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
        marker=dict(size=15, color="#00e5ff", symbol="square", line=dict(width=2, color="#ffffff")),
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

    # جدول فرز الرحلات بتصميم HTML عربي خالص ومحاذاة تامة لليمين
    st.subheader(f"جدول فرز ومناظرة الرحلات ({scope_title})")
    
    table_cols = [
        "flight", "date", "time", "dest", "origin_city", "country", "primary_threat", "pax",
        "w_pathogen", "w_spar", "w_flight", "risk_score", "action"
    ]
    sorted_df = df_view[table_cols].sort_values(by="risk_score", ascending=False).reset_index(drop=True)

    # بناء كود HTML للجدول لضمان الـ RTL والتلوين
    html_rows = []
    for _, row in sorted_df.head(40).iterrows(): # عرض أول 40 رحلة لتسريع التحميل مع إمكانية التمرير
        score_val = row["risk_score"]
        if score_val >= 65:
            badge_style = "background-color: #e63946; color: #ffffff;"
        elif score_val >= 35:
            badge_style = "background-color: #f4a261; color: #ffffff;"
        else:
            badge_style = "background-color: #2a9d8f; color: #ffffff;"

        html_rows.append(f"""
        <tr>
            <td style="font-weight: bold; color: #00e5ff;">{row['flight']}</td>
            <td>{row['date']}</td>
            <td>{row['time']}</td>
            <td>{row['dest']}</td>
            <td>{row['origin_city']}</td>
            <td>{row['country']}</td>
            <td style="color: #ffb703;">{row['primary_threat']}</td>
            <td>{row['pax']}</td>
            <td>{row['w_pathogen']}</td>
            <td>{row['w_spar']}</td>
            <td>{row['w_flight']}</td>
            <td><span style="{badge_style} padding: 3px 8px; border-radius: 4px; font-weight: bold;">{score_val}</span></td>
            <td>{row['action']}</td>
        </tr>
        """)

    table_html = f"""
    <div style="max-height: 520px; overflow-y: auto; border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 8px;">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>رقم الرحلة</th>
                    <th>التاريخ</th>
                    <th>وقت الوصول</th>
                    <th>المنفذ</th>
                    <th>محطة الإقلاع</th>
                    <th>الدولة</th>
                    <th>التهديد الوبائي الملازم</th>
                    <th>الركاب</th>
                    <th>وزن الممرض</th>
                    <th>فجوة SPAR</th>
                    <th>وزن الرحلة</th>
                    <th>مؤشر الخطورة</th>
                    <th>المناظرة الميدانية</th>
                </tr>
            </thead>
            <tbody>
                {"".join(html_rows)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

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
# الشاشة الثالثة: تقييم الجاهزية التشغيلية والإمداد (RTL صريح بـ HTML)
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

    # 1. تدقيق غرف العزل بالمنفذ (HTML)
    st.subheader(f"تدقيق غرف العزل المؤقتة بالمنفذ ({port_name})")
    
    iso_html = f"""
    <table class="custom-table">
        <thead>
            <tr>
                <th>رقم الغرفة</th>
                <th>الحالة التشغيلية</th>
                <th>نظام ضغط سالب</th>
                <th>دورة مياه مستقلة</th>
                <th>مسار نقل آمن</th>
                <th>التطهير الطبي</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="font-weight: bold; color: #00e5ff;">وحدة العزل 1</td>
                <td class="badge-check">شاغرة ومطابقة</td>
                <td class="badge-check">✓ مطابق</td>
                <td class="badge-check">✓ متوفر</td>
                <td class="badge-check">✓ مخصص</td>
                <td class="badge-check">✓ معتمد</td>
            </tr>
            <tr>
                <td style="font-weight: bold; color: #00e5ff;">وحدة العزل 2</td>
                <td class="badge-alert">تنبيه: غير جاهزة</td>
                <td class="badge-alert">✗ غير مطابق (يحتاج صيانة)</td>
                <td class="badge-check">✓ متوفر</td>
                <td class="badge-check">✓ مخصص</td>
                <td class="badge-check">✓ معتمد</td>
            </tr>
            {"<tr><td style='font-weight: bold; color: #00e5ff;'>وحدة العزل 3</td><td class='badge-check'>شاغرة ومطابقة</td><td class='badge-check'>✓ مطابق</td><td class='badge-check'>✓ متوفر</td><td class='badge-check'>✓ مخصص</td><td class='badge-check'>✓ معتمد</td></tr>" if target_port in ["JED", "RUH"] else ""}
        </tbody>
    </table>
    """
    st.markdown(iso_html, unsafe_allow_html=True)

    st.warning("⚠️ **تنبيه لصاحب القرار:** وحدة العزل (2) بها خلل في معيار الضغط السالب وتحتاج إلى صيانة عاجلة. يقتصر استخدام العزل الفعلي حالياً على الوحدات المطابقة فقط.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. سلاسل الإمداد والتجهيزات الطبية (HTML)
    st.subheader("أرصدة المستلزمات الوقائية والتجهيزات الحرارية")
    
    supply_html = """
    <table class="custom-table">
        <thead>
            <tr>
                <th>بند التجهيز والإمداد</th>
                <th>العدد المتوفر</th>
                <th>الحد الأدنى المطلوب</th>
                <th>مؤشر الرصيد</th>
                <th>المعاينة الفنية</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>أطقم عزل بيولوجي متكامل (Bio-Hazard Suit)</td>
                <td>22</td>
                <td>15</td>
                <td class="badge-check">✓ آمن ومستقر</td>
                <td class="badge-check">✓ صالحة للاستخدام</td>
            </tr>
            <tr>
                <td>كمامات تنفسية متخصصة (Fit-tested N95)</td>
                <td>140</td>
                <td>40</td>
                <td class="badge-check">✓ آمن ومستقر</td>
                <td class="badge-check">✓ صالحة للاستخدام</td>
            </tr>
            <tr>
                <td>حزم حماية رذاذية متكاملة مع واقي وجه</td>
                <td>250</td>
                <td>60</td>
                <td class="badge-check">✓ آمن ومستقر</td>
                <td class="badge-alert">✗ قارب انتهاء الدفعة</td>
            </tr>
            <tr>
                <td>أطقم فحص تلامسي قياسية</td>
                <td>80</td>
                <td>25</td>
                <td class="badge-check">✓ آمن ومستقر</td>
                <td class="badge-check">✓ صالحة للاستخدام</td>
            </tr>
            <tr>
                <td>كاميرات الفحص والمسح الحراري الثابتة</td>
                <td>6</td>
                <td>4</td>
                <td class="badge-check">✓ تعمل بكفاءة</td>
                <td class="badge-check">✓ معايرة دورية نشطة</td>
            </tr>
            <tr>
                <td>أجهزة قياس الحرارة المحمولة بالأشعة تحت الحمراء</td>
                <td>12</td>
                <td>8</td>
                <td class="badge-check">✓ متوفر بالعيادة</td>
                <td class="badge-check">✓ جاهزة للتشغيل</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(supply_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. تدريب وتأهيل الكوادر الميدانية (HTML)
    st.subheader("جاهزية وتأهيل الكوادر الصحية الميدانية")
    
    team_html = """
    <table class="custom-table">
        <thead>
            <tr>
                <th>المسار التدريبي والتأهيلي</th>
                <th>الكوادر المعتمدة</th>
                <th>المستهدف بالمنفذ</th>
                <th>نسبة الإنجاز</th>
                <th>حالة الجاهزية</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>شهادة أساسيات مكافحة العدوى والوقاية (BICSL)</td>
                <td>18 ممارس</td>
                <td>18 ممارس</td>
                <td>100%</td>
                <td class="badge-check">✓ مكتمل بالكامل</td>
            </tr>
            <tr>
                <td>بروتوكول فرز ومناظرة الأمراض التنفسية الحادة بمنافذ الدخول</td>
                <td>16 ممارس</td>
                <td>18 ممارس</td>
                <td>88%</td>
                <td class="badge-check">✓ جاهزية تشغيلية عالية</td>
            </tr>
            <tr>
                <td>إجراءات العزل المؤقت والنقل الطبي الآمن للحالات المشتبهة</td>
                <td>15 ممارس</td>
                <td>18 ممارس</td>
                <td>83%</td>
                <td class="badge-check">✓ مستمر ضمن المناوبات</td>
            </tr>
            <tr>
                <td>استخدام وتطبيق اللوائح الصحية الدولية (IHR) في المطارات</td>
                <td>18 ممارس</td>
                <td>18 ممارس</td>
                <td>100%</td>
                <td class="badge-check">✓ مكتمل بالكامل</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(team_html, unsafe_allow_html=True)
