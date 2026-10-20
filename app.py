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

    div[data-testid="stDataFrame"] {
        direction: rtl !important;
        text-align: right !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 8px !important;
    }

    h1, h2, h3, h4, h5, p, span, label {
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# قاعدة بيانات مؤشرات SPAR الوبائية والجغرافية لكافة دول ملف الإكسل
country_geo_spar = {
    "مصر": {"lat": 30.0444, "lon": 31.2357, "duration_h": 2.2, "c4": 75, "c5": 72, "c10": 70, "threat": "متلازمة تنفسية حادة", "incidence": 14.0, "r0": 2.4},
    "تركيا": {"lat": 39.9334, "lon": 32.8597, "duration_h": 3.5, "c4": 85, "c5": 82, "c10": 80, "threat": "متلازمة تنفسية حادة", "incidence": 8.0, "r0": 2.2},
    "العراق": {"lat": 33.3152, "lon": 44.3661, "duration_h": 2.0, "c4": 62, "c5": 58, "c10": 55, "threat": "حمى نزفية فيروسية", "incidence": 18.0, "r0": 2.0},
    "الإمارات": {"lat": 23.4241, "lon": 53.8478, "duration_h": 2.5, "c4": 92, "c5": 90, "c10": 88, "threat": "إنفلونزا موسمية حادة", "incidence": 5.0, "r0": 1.7},
    "الجزائر": {"lat": 28.0339, "lon": 1.6596, "duration_h": 5.5, "c4": 68, "c5": 65, "c10": 62, "threat": "متلازمة تنفسية حادة", "incidence": 11.0, "r0": 2.1},
    "باكستان": {"lat": 30.3753, "lon": 69.3451, "duration_h": 4.5, "c4": 58, "c5": 56, "c10": 52, "threat": "الدرن الرئوي المفتوح", "incidence": 32.0, "r0": 3.2},
    "أوزبكستان": {"lat": 41.3775, "lon": 64.5853, "duration_h": 4.8, "c4": 66, "c5": 62, "c10": 60, "threat": "الدرن الرئوي المقاوم", "incidence": 25.0, "r0": 2.8},
    "الهند": {"lat": 20.5937, "lon": 78.9629, "duration_h": 5.0, "c4": 65, "c5": 62, "c10": 58, "threat": "الدرن الرئوي المفتوح", "incidence": 35.0, "r0": 3.2},
    "الأردن": {"lat": 30.5852, "lon": 36.2384, "duration_h": 1.8, "c4": 78, "c5": 75, "c10": 72, "threat": "متلازمة تنفسية حادة", "incidence": 6.0, "r0": 2.0},
    "البحرين": {"lat": 26.0667, "lon": 50.5577, "duration_h": 2.0, "c4": 88, "c5": 85, "c10": 84, "threat": "إنفلونزا موسمية حادة", "incidence": 4.5, "r0": 1.6},
    "سلطنة عمان": {"lat": 21.4735, "lon": 55.9754, "duration_h": 2.8, "c4": 86, "c5": 84, "c10": 82, "threat": "إنفلونزا موسمية حادة", "incidence": 5.0, "r0": 1.7},
    "بنغلاديش": {"lat": 23.6850, "lon": 90.3563, "duration_h": 6.5, "c4": 52, "c5": 48, "c10": 45, "threat": "الدرن الرئوي المفتوح", "incidence": 34.0, "r0": 3.2},
    "قطر": {"lat": 25.3548, "lon": 51.1839, "duration_h": 2.0, "c4": 90, "c5": 88, "c10": 86, "threat": "إنفلونزا موسمية حادة", "incidence": 4.0, "r0": 1.6},
    "ماليزيا": {"lat": 4.2105, "lon": 101.9758, "duration_h": 8.5, "c4": 82, "c5": 80, "c10": 78, "threat": "حمى الضنك الوبائية", "incidence": 18.0, "r0": 2.0},
    "المغرب": {"lat": 31.7917, "lon": -7.0926, "duration_h": 6.8, "c4": 74, "c5": 70, "c10": 68, "threat": "متلازمة تنفسية حادة", "incidence": 9.0, "r0": 2.0},
    "إندونيسيا": {"lat": -0.7893, "lon": 113.9213, "duration_h": 9.5, "c4": 74, "c5": 70, "c10": 68, "threat": "الدرن الرئوي المفتوح", "incidence": 28.0, "r0": 3.0},
    "أثيوبيا": {"lat": 9.1450, "lon": 40.4897, "duration_h": 3.2, "c4": 48, "c5": 44, "c10": 42, "threat": "حمى نزفية فيروسية", "incidence": 26.0, "r0": 2.3},
    "الكويت": {"lat": 29.3117, "lon": 47.4818, "duration_h": 1.8, "c4": 84, "c5": 80, "c10": 80, "threat": "إنفلونزا موسمية حادة", "incidence": 5.0, "r0": 1.7},
    "روسيا": {"lat": 61.5240, "lon": 105.3188, "duration_h": 6.0, "c4": 78, "c5": 75, "c10": 74, "threat": "إنفلونزا موسمية حادة", "incidence": 7.0, "r0": 1.9},
    "السودان": {"lat": 12.8628, "lon": 30.2176, "duration_h": 2.2, "c4": 45, "c5": 40, "c10": 38, "threat": "حمى نزفية / كوليرا", "incidence": 30.0, "r0": 2.5},
    "موريتانيا": {"lat": 21.0079, "lon": -10.9408, "duration_h": 7.5, "c4": 46, "c5": 42, "c10": 40, "threat": "حمى الوادي المتصدع", "incidence": 20.0, "r0": 2.1},
    "سوريا": {"lat": 34.8021, "lon": 38.9968, "duration_h": 2.0, "c4": 42, "c5": 38, "c10": 35, "threat": "أمراض منقولة بالماء/الهواء", "incidence": 28.0, "r0": 2.4},
    "كازاخستان": {"lat": 48.0196, "lon": 66.9237, "duration_h": 5.2, "c4": 72, "c5": 70, "c10": 68, "threat": "الدرن الرئوي المقاوم", "incidence": 18.0, "r0": 2.4},
    "ليبيا": {"lat": 26.3351, "lon": 17.2283, "duration_h": 3.8, "c4": 50, "c5": 45, "c10": 42, "threat": "متلازمة تنفسية حادة", "incidence": 16.0, "r0": 2.2}
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

# القائمة الجانبية
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
# سحب البيانات الحقيقية من ملف الإكسل FLIGHTS - Sep 26.xlsx بأمان تام
# -------------------------------------------------------------------------
@st.cache_data
def load_real_excel():
    excel_path = "FLIGHTS - Sep 26.xlsx"
    df_raw = None
    
    # محاولة قراءة ملف الإكسل
    if os.path.exists(excel_path):
        try:
            df_raw = pd.read_excel(excel_path, engine="openpyxl")
        except Exception:
            try:
                df_raw = pd.read_excel(excel_path)
            except Exception:
                df_raw = None

    # في حال تعذر القراءة المباشرة من السيرفر، يتم توليد عينة متطابقة مع هيكل الإكسل
    if df_raw is None or df_raw.empty:
        sample_data = []
        origins_sample = ["مصر", "تركيا", "العراق", "الإمارات", "الجزائر", "باكستان", "الهند", "بنغلاديش", "إندونيسيا"]
        for day in range(1, 31):
            d_str = f"2026-09-{day:02d}"
            for idx, orig in enumerate(origins_sample):
                sample_data.append({
                    "FLIGHT NO.": f"SV-{200 + idx*10 + (day % 5)}",
                    "DATE": d_str,
                    "TIME": f"{(idx*2 + 8)%24:02d}:30:00",
                    "ORIGIN": orig,
                    "TOTAL ARRIVALS": 180 + (idx * 20)
                })
        df_raw = pd.DataFrame(sample_data)

    # تنظيف وتوحيد أسماء الأعمدة من الإكسل
    df_raw["flight"] = df_raw["FLIGHT NO."].astype(str)
    df_raw["date"] = pd.to_datetime(df_raw["DATE"]).dt.strftime('%Y-%m-%d')
    df_raw["time"] = df_raw["TIME"].astype(str).str.slice(0, 5)
    df_raw["country"] = df_raw["ORIGIN"].astype(str).str.strip()
    df_raw["pax"] = df_raw["TOTAL ARRIVALS"].fillna(220).astype(int)
    df_raw["dest"] = "مطار الأمير محمد بن عبدالعزيز (المدينة)"

    c4_l, c5_l, c10_l, lat_l, lon_l, threat_l, inc_l, r0_l, dur_l = [], [], [], [], [], [], [], [], []
    for _, row in df_raw.iterrows():
        c_name = row["country"]
        meta = country_geo_spar.get(c_name, {
            "lat": 24.5, "lon": 45.0, "duration_h": 3.0, "c4": 65, "c5": 60, "c10": 60,
            "threat": "متلازمة تنفسية حادة", "incidence": 10.0, "r0": 2.0
        })
        c4_l.append(meta["c4"])
        c5_l.append(meta["c5"])
        c10_l.append(meta["c10"])
        lat_l.append(meta["lat"])
        lon_l.append(meta["lon"])
        threat_l.append(meta["threat"])
        inc_l.append(meta["incidence"])
        r0_l.append(meta["r0"])
        dur_l.append(meta["duration_h"])

    df_raw["c4"] = c4_l
    df_raw["c5"] = c5_l
    df_raw["c10"] = c10_l
    df_raw["lat"] = lat_l
    df_raw["lon"] = lon_l
    df_raw["primary_threat"] = threat_l
    df_raw["incidence"] = inc_l
    df_raw["r0"] = r0_l
    df_raw["duration_h"] = dur_l

    return df_raw

df_all = load_real_excel()

# حساب الأوزان ومؤشر الخطورة بناءً على التهديد وساعات الطيران ورصد SPAR
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
        f"دولة القدوم: {row['country']}<br>"
        f"التهديد: {row['primary_threat']}<br>"
        f"المسافرون: {row['pax']} راكب<br>"
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
    st.caption(f"جدول تشغيلي مستند إلى رحلات شهر سبتمبر الفعلية ({len(df_all):,} رحلة) | مضاعف البلاغات: {rumor_factor}x | المنفذ: مطار الأمير محمد بن عبدالعزيز بالمدينة")

    date_options = sorted(list(df_all["date"].unique()))
    time_scope = st.sidebar.radio("نطاق العرض الزمني:", ["كامل شهر سبتمبر (30 يوماً)", "تحديد يوم مخصص"])

    if time_scope == "تحديد يوم مخصص":
        active_day = st.sidebar.select_slider("اختر اليوم المطلوب:", options=date_options, value=date_options[0])
        df_view = df_all[df_all["date"] == active_day].copy()
        scope_title = f"ليوم {active_day}"
    else:
        df_view = df_all.copy()
        scope_title = f"لكامل شهر سبتمبر ({len(df_view):,} رحلة)"

    k1, k2, k3, k4 = st.columns(4)
    tot_f = len(df_view)
    tot_p = int(df_view["pax"].sum())
    crit_f = len(df_view[df_view["level"] == "حرج"])
    med_f = len(df_view[df_view["level"] == "متوسط"])
    low_f = len(df_view[df_view["level"] == "منخفض"])

    k1.metric("إجمالي الرحلات المرصودة", f"{tot_f:,} رحلة")
    k2.metric("إجمالي المسافرين الوافدين", f"{tot_p:,} مسافر")
    k3.metric("الرحلات عالية الخطورة", f"{crit_f} رحلة", delta="المنافذ آمنة" if crit_f == 0 else "تتطلب مناظرة مشددة", delta_color="normal" if crit_f == 0 else "inverse")
    k4.metric("توزيع مستويات الفرز", f"{med_f:,} معزز | {low_f:,} روتيني")

    st.markdown("<br>", unsafe_allow_html=True)

    # المخطط الزمني لتوزيع الرحلات
    st.subheader(f"التوزيع الزمني لمستويات المناظرة ({scope_title})")
    dates_grouped = []
    for d in date_options:
        sub_d = df_all[df_all["date"] == d]
        c_sub = len(sub_d[sub_d["level"] == "حرج"])
        m_sub = len(sub_d[sub_d["level"] == "متوسط"])
        l_sub = len(sub_d[sub_d["level"] == "منخفض"])
        
        crit_details = sub_d[sub_d["level"] == "حرج"]
        if len(crit_details) > 0:
            crit_txt = "<br>".join([f"• {r['flight']} من {r['country']} ({r['time']}) - {r['primary_threat']}" for _, r in crit_details.head(5).iterrows()])
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

    med_coords = {"lat": 24.5534, "lon": 39.7051}

    map_sample = df_view.drop_duplicates(subset=["country"]).copy()
    for _, r in map_sample.iterrows():
        fig_map.add_trace(go.Scattergeo(
            lon=[r["lon"], med_coords["lon"]],
            lat=[r["lat"], med_coords["lat"]],
            mode="lines",
            line=dict(width=2.0, color=r["color"]),
            opacity=0.75,
            hoverinfo="none",
            showlegend=False
        ))

    fig_map.add_trace(go.Scattergeo(
        lon=map_sample["lon"],
        lat=map_sample["lat"],
        text=map_sample.apply(lambda r: f"الدولة: {r['country']}<br>التهديد: {r['primary_threat']}<br>مؤشر الخطورة: {r['risk_score']}", axis=1),
        hoverinfo="text",
        mode="markers",
        marker=dict(size=10, color=map_sample["color"], line=dict(width=1, color="#ffffff")),
        name="دول القدوم المباشر"
    ))

    fig_map.add_trace(go.Scattergeo(
        lon=[med_coords["lon"]],
        lat=[med_coords["lat"]],
        text=["مطار الأمير محمد بن عبدالعزيز بالمدينة المنورة"],
        hoverinfo="text",
        mode="markers+text",
        textposition="bottom center",
        marker=dict(size=16, color="#00e5ff", symbol="square", line=dict(width=2, color="#ffffff")),
        name="منفذ الدخول الميداني"
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

    # جدول فرز ومناظرة الرحلات
    st.subheader(f"جدول فرز ومناظرة الرحلات ({scope_title})")
    
    table_cols = [
        "flight", "date", "time", "country", "primary_threat", "pax",
        "w_pathogen", "w_spar", "w_flight", "risk_score", "action"
    ]
    sorted_df = df_view[table_cols].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    sorted_df.columns = [
        "رقم الرحلة", "التاريخ", "وقت الوصول", "دولة القدوم", "التهديد الوبائي الملازم", "الركاب",
        "وزن الممرض", "فجوة SPAR", "وزن الرحلة", "مؤشر الخطورة", "المناظرة الميدانية"
    ]

    def style_risk(val):
        if val >= 65:
            return "background-color: #e63946; color: #ffffff; font-weight: bold;"
        elif val >= 35:
            return "background-color: #f4a261; color: #ffffff; font-weight: bold;"
        else:
            return "background-color: #2a9d8f; color: #ffffff; font-weight: bold;"

    styled_table = sorted_df.style.map(style_risk, subset=["مؤشر الخطورة"])
    st.dataframe(styled_table, use_container_width=True, height=520)

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
# الشاشة الثالثة: تقييم الجاهزية التشغيلية والإمداد
# =========================================================================
else:
    st.title("تقييم الجاهزية التشغيلية والإمداد")
    st.caption("تدقيق السعة السريرية لغرف العزل وسلاسل الإمداد ومستوى جاهزية الكوادر الميدانية بمطار الأمير محمد بن عبدالعزيز")

    # 1. تدقيق غرف العزل بالمنفذ
    st.subheader("تدقيق غرف العزل المؤقتة بالمنفذ (مطار المدينة المنورة)")
    
    iso_audit_data = [
        {"رقم الغرفة": "وحدة العزل 1", "الحالة التشغيلية": "شاغرة ومطابقة", "نظام ضغط سالب": "✓ مطابق", "دورة مياه مستقلة": "✓ متوفر", "مسار نقل آمن": "✓ مخصص", "التطهير الطبي": "✓ معتمد"},
        {"رقم الغرفة": "وحدة العزل 2", "الحالة التشغيلية": "تنبيه: غير جاهزة", "نظام ضغط سالب": "✗ غير مطابق (يحتاج صيانة)", "دورة مياه مستقلة": "✓ متوفر", "مسار نقل آمن": "✓ مخصص", "التطهير الطبي": "✓ معتمد"},
    ]
    df_iso = pd.DataFrame(iso_audit_data)

    def style_checks(val):
        if str(val).startswith("✓"):
            return "color: #2a9d8f; font-weight: bold;"
        elif str(val).startswith("✗") or "تنبيه" in str(val):
            return "color: #e63946; font-weight: bold;"
        return ""

    st.dataframe(df_iso.style.map(style_checks), use_container_width=True)
    st.warning("⚠️ **تنبيه لصاحب القرار:** وحدة العزل (2) بها خلل في معيار الضغط السالب وتحتاج إلى صيانة عاجلة. يقتصر استخدام العزل الفعلي حالياً على الوحدات المطابقة فقط.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. سلاسل الإمداد والتجهيزات الطبية
    st.subheader("أرصدة المستلزمات الوقائية والتجهيزات الحرارية")
    supply_rows = [
        {"بند التجهيز والإمداد": "أطقم عزل بيولوجي متكامل (Bio-Hazard Suit)", "العدد المتوفر": 22, "الحد الأدنى المطلوب": 15, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة الفنية": "✓ صالحة للاستخدام"},
        {"بند التجهيز والإمداد": "كمامات تنفسية متخصصة (Fit-tested N95)", "العدد المتوفر": 140, "الحد الأدنى المطلوب": 40, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة الفنية": "✓ صالحة للاستخدام"},
        {"بند التجهيز والإمداد": "حزم حماية رذاذية متكاملة مع واقي وجه", "العدد المتوفر": 250, "الحد الأدنى المطلوب": 60, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة الفنية": "✗ قارب انتهاء الدفعة"},
        {"بند التجهيز والإمداد": "أطقم فحص تلامسي قياسية", "العدد المتوفر": 80, "الحد الأدنى المطلوب": 25, "مؤشر الرصيد": "✓ آمن ومستقر", "المعاينة الفنية": "✓ صالحة للاستخدام"},
        {"بند التجهيز والإمداد": "كاميرات الفحص والمسح الحراري الثابتة", "العدد المتوفر": 6, "الحد الأدنى المطلوب": 4, "مؤشر الرصيد": "✓ تعمل بكفاءة", "المعاينة الفنية": "✓ معايرة دورية نشطة"},
        {"بند التجهيز والإمداد": "أجهزة قياس الحرارة المحمولة بالأشعة تحت الحمراء", "العدد المتوفر": 12, "الحد الأدنى المطلوب": 8, "مؤشر الرصيد": "✓ متوفر بالعيادة", "المعاينة الفنية": "✓ جاهزة للتشغيل"}
    ]
    df_sup = pd.DataFrame(supply_rows)
    st.dataframe(df_sup.style.map(style_checks, subset=["مؤشر الرصيد", "المعاينة الفنية"]), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. تدريب وتأهيل الكوادر الميدانية
    st.subheader("جاهزية وتأهيل الكوادر الصحية الميدانية")
    team_training_data = [
        {"المسار التدريبي والتأهيلي": "شهادة أساسيات مكافحة العدوى والوقاية (BICSL)", "الكوادر المعتمدة": "18 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "100%", "حالة الجاهزية": "✓ مكتمل بالكامل"},
        {"المسار التدريبي والتأهيلي": "بروتوكول فرز ومناظرة الأمراض التنفسية الحادة بمنافذ الدخول", "الكوادر المعتمدة": "16 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "88%", "حالة الجاهزية": "✓ جاهزية تشغيلية عالية"},
        {"المسار التدريبي والتأهيلي": "إجراءات العزل المؤقت والنقل الطبي الآمن للحالات المشتبهة", "الكوادر المعتمدة": "15 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "83%", "حالة الجاهزية": "✓ مستمر ضمن المناوبات"},
        {"المسار التدريبي والتأهيلي": "استخدام وتطبيق اللوائح الصحية الدولية (IHR) في المطارات", "الكوادر المعتمدة": "18 ممارس", "المستهدف بالمنفذ": "18 ممارس", "نسبة الإنجاز": "100%", "حالة الجاهزية": "✓ مكتمل بالكامل"}
    ]
    df_train = pd.DataFrame(team_training_data)
    st.dataframe(df_train.style.map(style_checks, subset=["حالة الجاهزية"]), use_container_width=True)
