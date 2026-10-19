import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# إعدادات الصفحة
st.set_page_config(
    page_title="منظومة ثغر | الاستخبار الوبائي ومراقبة منافذ الدخول الجوية",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# فرض اللغة العربية ومحاذاة اليمين لليسار (RTL) والهوية السيادية
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
        background-color: rgba(10, 20, 48, 0.95) !important;
        border-left: 1px solid rgba(0, 229, 255, 0.15) !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(16, 35, 78, 0.6) 0%, rgba(8, 18, 42, 0.8) 100%) !important;
        border: 1px solid rgba(0, 229, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 20px rgba(0, 114, 255, 0.12) !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-size: 1.85rem !important;
        font-weight: 900 !important;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.35);
    }
    
    .reason-box {
        background: rgba(16, 35, 78, 0.5);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 10px;
        padding: 16px;
        margin-top: 10px;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .iso-unit {
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        border: 1px solid rgba(0, 229, 255, 0.3);
        font-weight: bold;
        line-height: 1.6;
    }
    
    h1, h2, h3, h4, h5, p, span, label {
        text-align: right !important;
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
    "MED": {"name": "مطار الأمير محمد بن عبدالعزيز (المدينة)", "lat": 24.5534, "lon": 39.7051, "iso_total": 2},
    "JED": {"name": "مطار الملك عبدالعزيز الدولي (جدة)", "lat": 21.6796, "lon": 39.1565, "iso_total": 4},
    "RUH": {"name": "مطار الملك خالد الدولي (الرياض)", "lat": 24.9576, "lon": 46.6988, "iso_total": 4}
}

pathogen_metadata = {
    "Ebola / Marburg (حمى نزفية فيروسية - عالية الخطورة)": {
        "r0": 1.9, "incubation_days": 8.0, "type": "contact_fluids",
        "severity": "حرجة جداً (فتك حاد)", "tracing_rule": "direct_contacts_only",
        "ppe_directive": "المستوى الرابع (Level 4): بدلة عزل بيولوجي كاملة (Coverall) + قفازات مزدوجة + كمامة PAPR/N95 محكمة + واقي وجه وأحذية مقاوم للسوائل.",
        "ppe_item_name": "أطقم عزل بيولوجي متكامل (Level-4 Bio-Coverall)",
        "stock_current": 18, "stock_critical_threshold": 15, "stock_expiry": "2027-04-30"
    },
    "Airborne TB (الدرن الرئوي المفتوح - منقول بالهواء)": {
        "r0": 3.2, "incubation_days": 30.0, "type": "airborne",
        "severity": "عالية ومزمنة", "tracing_rule": "full_cabin",
        "ppe_directive": "المستوى الثالث المحمول جواً: كمامة N95 مفحوصة (Fit-tested) + نظارات حماية بانورامية + مريول طبي معقم عازل للسوائل + قفازات فحص.",
        "ppe_item_name": "كمامات تنفسية متخصصة (Fit-tested N95 Mask)",
        "stock_current": 120, "stock_critical_threshold": 40, "stock_expiry": "2028-01-15"
    },
    "Severe Influenza / Novel Corona (رذاذي حاد)": {
        "r0": 2.5, "incubation_days": 3.5, "type": "droplet",
        "severity": "متوسطة إلى عالية", "tracing_rule": "two_rows",
        "ppe_directive": "مستوى الرذاذ التنفسي: كمامة جراحية عالية الكفاءة أو N95 + واقي الوجه الكامل (Face Shield) + مريول حماية طبي + قفازات فحص.",
        "ppe_item_name": "حزم حماية تنفسية رذاذية (Droplet PPE Pack)",
        "stock_current": 250, "stock_critical_threshold": 50, "stock_expiry": "2026-11-30" # قارب على الانتهاء
    },
    "Chickenpox (جدري الماء - تلامسي مختلط)": {
        "r0": 1.6, "incubation_days": 14.0, "type": "contact_skin",
        "severity": "خفيفة إلى معتدلة", "tracing_rule": "adjacent_only",
        "ppe_directive": "مستوى التلامس والرذاذ: مريول طبي واقٍ + قفازات عزل + كمامة جراحية لمنع انتقال الرذاذ أثناء الفحص المباشر للطفح.",
        "ppe_item_name": "أطقم فحص تلامسي قياسية (Contact Isolation Pack)",
        "stock_current": 80, "stock_critical_threshold": 20, "stock_expiry": "2027-09-15"
    }
}

def get_pathogen_incidence(disease_name, country_name):
    if "Ebola" in disease_name:
        return {"Nigeria": 48.0}.get(country_name, 0.0)
    elif "TB" in disease_name:
        rates = {"Pakistan": 85.0, "India": 90.0, "Bangladesh": 78.0, "Nigeria": 60.0, "Indonesia": 70.0, "Egypt": 15.0, "Turkey": 8.0, "Jordan": 6.0, "UK": 4.0}
        return rates.get(country_name, 5.0)
    elif "Corona" in disease_name or "Influenza" in disease_name:
        rates = {"Egypt": 30.0, "India": 40.0, "Pakistan": 35.0, "Bangladesh": 30.0, "Indonesia": 28.0, "Nigeria": 15.0, "Turkey": 20.0, "Jordan": 15.0, "UK": 22.0}
        return rates.get(country_name, 10.0)
    else:
        rates = {"Pakistan": 25.0, "India": 20.0, "Egypt": 15.0, "Bangladesh": 18.0, "Nigeria": 22.0, "Indonesia": 16.0, "Turkey": 10.0, "Jordan": 8.0, "UK": 5.0}
        return rates.get(country_name, 8.0)

# شريط التحكم الرئيسي
st.sidebar.title("🛡️ منظومة «ثغر» للمنافذ")
view_mode = st.sidebar.radio(
    "الشاشة التشغيلية:",
    ["1️⃣ شاشة التنبؤ، الخريطة، وجاهزية المنفذ", "2️⃣ بروتوكول البلاغات وتتبع مقصورة الطائرة"]
)
st.sidebar.markdown("---")

selected_pathogen_name = st.sidebar.selectbox("🦠 التهديد الوبائي المحدد:", list(pathogen_metadata.keys()))
p_info = pathogen_metadata[selected_pathogen_name]

# إضافة معامل البلاغات غير الرسمية
st.sidebar.markdown("---")
st.sidebar.subheader("📡 استخبارات الرصد المفتوح (EBS)")
rumor_factor = st.sidebar.slider(
    "معامل البلاغات والتفشيات غير الرسمية (ω):",
    min_value=1.0, max_value=3.0, value=1.0, step=0.2,
    help="يُرفع المعامل تلقائياً عند رصد شائعات أو إشارات وبائية عبر منصات EIOS أو ProMED بدولة المنشأ قبل الإعلان الحكومي الرسمي."
)

# =========================================================================
# الشاشة الأولى: التنبؤ الوبائي، الخريطة، تقويم سبتمبر، وغرف العزل والإمداد
# =========================================================================
if view_mode == "1️⃣ شاشة التنبؤ، الخريطة، وجاهزية المنفذ":
    st.title("🌐 منظومة التنبؤ الاستباقي ومراقبة تدفقات المنافذ")
    st.caption(f"التهديد الوبائي: **{selected_pathogen_name}** | مؤشر الرصد المفتوح والشائعات: **{rumor_factor}x**")

    # اختيار المنافذ المستهدفة
    selected_airports = st.sidebar.multiselect(
        "المنافذ الوطنية المراقبة:",
        options=list(national_airports.keys()),
        default=["MED", "JED"],
        format_func=lambda x: national_airports[x]["name"]
    )
    if not selected_airports:
        st.warning("يرجى اختيار منفذ واحد على الأقل.")
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
                daily_count = np.random.randint(2, 5) if dest in ["MED", "JED"] else np.random.randint(1, 3)
                for _ in range(daily_count):
                    orig_k = origins_keys[np.random.randint(0, len(origins_keys))]
                    orig_data = origins_spar_db[orig_k]
                    data.append({
                        "flight": f"SV-{flight_idx}",
                        "date": date_str,
                        "dest": dest,
                        "origin_city": orig_k.capitalize(),
                        "country": orig_data["country"],
                        "pax": int(np.random.randint(270, 420)),
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

    # محرك الحساب العلمي متضمناً معامل البلاغات غير الرسمية
    def calculate_risk(row):
        inc = get_pathogen_incidence(selected_pathogen_name, row["country"])
        spar_core = (row["c4"] + row["c5"] + row["c10"]) / 3.0
        gap_factor = (100.0 - spar_core) / 35.0
        incubation_hrs = p_info["incubation_days"] * 24.0
        flight_ratio = 1.0 + (row["duration_h"] / incubation_hrs)
        score = (inc / 100000.0) * row["pax"] * p_info["r0"] * gap_factor * flight_ratio * rumor_factor * 3200
        return np.clip(score, 6.0, 98.5).round(1)

    df_filtered["risk_score"] = df_filtered.apply(calculate_risk, axis=1)

    def assign_tier(score):
        if score >= 65:
            return "مشددة (أحمر)", "#ff3366", "حرج"
        elif score >= 35:
            return "معززة (برتقالي)", "#ff9900", "متوسط"
        else:
            return "روتينية (سماوي)", "#00e5ff", "منخفض"

    tiers = df_filtered["risk_score"].apply(assign_tier)
    df_filtered["action"] = [t[0] for t in tiers]
    df_filtered["color"] = [t[1] for t in tiers]
    df_filtered["level"] = [t[2] for t in tiers]

    # فلترة التاريخ (كامل الشهر مقابل يوم محدد)
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
        active_day = date_options[0]
        scope_title = "لكامل شهر سبتمبر (140+ رحلة)"

    # --- 1. قسم جاهزية غرف العزل وسلاسل الإمداد اللوجستية المتقدمة ---
    st.subheader(f"🏥 جاهزية غرف العزل وسلاسل الإمداد الطبي الميداني")
    
    # حساب احتياج اليوم لرحلات المنفذ المختار
    main_port = selected_airports[0]
    port_data = national_airports[main_port]
    today_port_flights = df_filtered[(df_filtered["date"] == active_day) & (df_filtered["dest"] == main_port)]
    crit_count = len(today_port_flights[today_port_flights["level"] == "حرج"])
    
    # غرف العزل
    total_iso = port_data["iso_total"]
    reserved_iso = min(crit_count, total_iso)
    available_iso = total_iso - reserved_iso
    
    # الإمداد الطبي
    current_stock = p_info["stock_current"]
    est_consumption = crit_count * 5 # استهلاك تقديري 5 أطقم لكل رحلة حرجة
    projected_remaining = current_stock - est_consumption
    expiry_date = p_info["stock_expiry"]
    
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    s_col1.metric("غرف العزل بمطار المنفذ", f"{available_iso} متاحة", delta=f"{reserved_iso} محجوزة لرحلات حرجة" if reserved_iso > 0 else "الكل شاغر")
    s_col2.metric(f"المتوفر من {p_info['ppe_item_name']}", f"{current_stock} طقم", delta=f"المتوقع استهلاكه اليوم: {est_consumption} طقم", delta_color="inverse" if est_consumption > 0 else "normal")
    s_col3.metric("الرصيد المتبقي المتوقع", f"{projected_remaining} طقم", delta="قارب على النفاذ (طلب دعم)" if projected_remaining <= p_info["stock_critical_threshold"] else "ضمن الحدود الآمنة", delta_color="inverse" if projected_remaining <= p_info["stock_critical_threshold"] else "normal")
    s_col4.metric("تاريخ انتهاء صلاحية المخزون", expiry_date, delta="قارب على الانتهاء!" if "2026-11" in expiry_date else "صلاحية سارية", delta_color="inverse" if "2026-11" in expiry_date else "normal")

    # بطاقات غرف العزل الرسومية
    iso_cols = st.columns(total_iso)
    for idx, col in enumerate(iso_cols):
        r_num = idx + 1
        with col:
            if idx < reserved_iso:
                st.markdown(f"""
                <div class="iso-unit" style="background: rgba(255, 51, 102, 0.2); border-color: #ff3366; color: #ff3366;">
                    🚪 وحدة عزل {r_num} ({port_data['name']})<br>
                    <span>● محجوزة مسبقاً لرحلة حرجة قادمة</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="iso-unit" style="background: rgba(0, 229, 255, 0.12); border-color: #00e5ff; color: #00e5ff;">
                    🚪 وحدة عزل {r_num} ({port_data['name']})<br>
                    <span>● شاغرة وجاهزة بنظام ضغط سالب</span>
                </div>
                """, unsafe_allow_html=True)

    if projected_remaining <= p_info["stock_critical_threshold"]:
        st.error(f"🚨 **تنبيه إمداد حرج:** المخزون المتوقع للبند ({p_info['ppe_item_name']}) سيصل إلى ({projected_remaining}) وهو أقل من حد الأمان ({p_info['stock_critical_threshold']}). تم تفعيل طلب إمداد تعزيزي من الإسناد الطبي.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. المؤشرات الاستخبارية للرحلات ---
    k1, k2, k3, k4 = st.columns(4)
    tot_f = len(df_view)
    tot_p = int(df_view["pax"].sum())
    crit_f = len(df_view[df_view["level"] == "حرج"])
    avg_r = df_view["risk_score"].mean() if tot_f > 0 else 0

    k1.metric("إجمالي الرحلات المرصودة", f"{tot_f:,} رحلة")
    k2.metric("إجمالي المسافرين الوافدين", f"{tot_p:,} مسافر")
    k3.metric("الرحلات الحرجة (مناظرة مشددة)", f"{crit_f}", delta=f"{crit_f} رحلة تستدعي الفرز الفردي" if crit_f > 0 else "المستوى مستقر", delta_color="inverse")
    k4.metric("متوسط الخطر الوبائي العام", f"{avg_r:.1f} / 100")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. المخطط الزمني لتوزيع المخاطر طوال شهر سبتمبر ---
    st.subheader("📈 التوزيع الزمني للرحلات ومستويات الفرز طوال شهر سبتمبر")
    st.caption("يكشف هذا المخطط أيام الذروة الوبائية في المطار وأعداد الرحلات التي تتطلب مناظرة مشددة يوماً بيوم.")

    daily_summary = df_filtered.groupby(["date", "level"]).size().reset_index(name="count")
    daily_pivot = daily_summary.pivot(index="date", columns="level", values="count").fillna(0)
    for col in ["حرج", "متوسط", "منخفض"]:
        if col not in daily_pivot.columns:
            daily_pivot[col] = 0

    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Bar(name="مناظرة مشددة (أحمر)", x=daily_pivot.index, y=daily_pivot["حرج"], marker_color="#ff3366"))
    fig_timeline.add_trace(go.Bar(name="مناظرة معززة (برتقالي)", x=daily_pivot.index, y=daily_pivot["متوسط"], marker_color="#ff9900"))
    fig_timeline.add_trace(go.Bar(name="مناظرة روتينية (سماوي)", x=daily_pivot.index, y=daily_pivot["منخفض"], marker_color="#00e5ff"))

    fig_timeline.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10, 20, 48, 0.6)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=250,
        font=dict(family="Tajawal", color="#94a3b8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="rgba(0, 229, 255, 0.1)"),
        yaxis=dict(gridcolor="rgba(0, 229, 255, 0.1)")
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 4. خريطة المسارات الجوية والتدفق الوبائي السيادية ---
    st.subheader(f"🌐 خريطة التدفق الجوي والمسارات الوبائية ثلاثية الأبعاد ({scope_title})")

    fig_map = go.Figure()

    # خطوط الرحلات
    for _, r in df_view.iterrows():
        dest_coord = national_airports[r["dest"]]
        fig_map.add_trace(go.Scattergeo(
            lon=[r["lon"], dest_coord["lon"]],
            lat=[r["lat"], dest_coord["lat"]],
            mode="lines",
            line=dict(width=2.2, color=r["color"]),
            opacity=0.75,
            hoverinfo="none",
            showlegend=False
        ))

    # نقاط الانطلاق
    fig_map.add_trace(go.Scattergeo(
        lon=df_view["lon"],
        lat=df_view["lat"],
        text=df_view.apply(lambda r: f"الرحلة: {r['flight']}<br>التاريخ: {r['date']}<br>المنشأ: {r['origin_city']} ({r['country']})<br>الوجهة: {r['dest']}<br>الركاب: {r['pax']}<br>مؤشر الخطر: {r['risk_score']}<br>الإجراء: {r['action']}", axis=1),
        hoverinfo="text",
        mode="markers",
        marker=dict(size=11, color=df_view["color"], line=dict(width=1, color="#ffffff")),
        name="محطات الإقلاع الدولية"
    ))

    # نقاط المنافذ المستهدفة
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
        height=520,
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

    # --- 5. جدول الرحلات وتفكيك مسببات الخطورة ---
    col_table, col_explain = st.columns([6, 4])

    with col_table:
        st.subheader("📋 سجل الفرز اليومي للرحلات")
        cols_disp = ["flight", "date", "dest", "origin_city", "country", "pax", "duration_h", "risk_score", "action"]
        v_df = df_view[cols_disp].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
        v_df.columns = ["الرحلة", "التاريخ", "المنفذ", "محطة الإقلاع", "الدولة", "الركاب", "ساعات الطيران", "مؤشر الخطر", "مستوى المناظرة"]
        st.dataframe(v_df, use_container_width=True)

    with col_explain:
        st.subheader("🔍 تفكيك أسباب التصنيف (Explainable AI)")
        selected_flight = st.selectbox("اختر رحلة لتشخيص أسباب تصنيفها:", options=df_view["flight"].tolist())
        target_row = df_view[df_view["flight"] == selected_flight].iloc[0]

        spar_avg = (target_row["c4"] + target_row["c5"] + target_row["c10"]) / 3.0
        
        reasons = []
        if target_row["risk_score"] >= 65:
            box_border = "#ff3366"
            level_name = "مستوى أحمر (حرج / مناظرة مشددة)"
        elif target_row["risk_score"] >= 35:
            box_border = "#ff9900"
            level_name = "مستوى برتقالي (معزز)"
        else:
            box_border = "#00e5ff"
            level_name = "مستوى سماوي (اعتيادي)"

        if spar_avg < 60:
            reasons.append(f"• **ضعف نظم الرصد والمختبرات:** تقييم دولة {target_row['country']} في مؤشر SPAR متدنٍ ({spar_avg:.1f}/100)، مما يرفع احتمالية وجود حالات خفية غير مبلغة.")
        if p_info["r0"] > 2.0:
            reasons.append(f"• **سرعة الانتشار الوبائي للمرض:** الممرض ذو معدل انتشار مرتفع ($R_0 = {p_info['r0']}$).")
        if target_row["duration_h"] >= 4.5:
            reasons.append(f"• **طول زمن الرحلة:** مدة الطيران ({target_row['duration_h']} ساعة) تزيد احتمالية ظهور أعراض حرارية أثناء التحليق.")
        if rumor_factor > 1.0:
            reasons.append(f"• **إشارات وبائية غير رسمية نشطة:** تم تطبيق مضاعف الرصد المفتوح ({rumor_factor}x) استجابة لبلاغات استخبارات مبكرة بدولة المنشأ.")

        if not reasons:
            reasons.append("• الرحلة قادمة من وجهة ذات مؤشرات رصد متقدمة واستقرار وبائي؛ الإجراء روتيني بالصالة.")

        st.markdown(f"""
        <div class="reason-box" style="border-color: {box_border};">
            <h5 style="color: {box_border}; margin-bottom: 8px;">الرحلة: {target_row['flight']} ({target_row['origin_city']}) - {level_name}</h5>
            {"<br>".join(reasons)}
        </div>
        """, unsafe_allow_html=True)

# =========================================================================
# الشاشة الثانية: بروتوكول البلاغات وتتبع مقصورة الطائرة
# =========================================================================
else:
    st.title("🚨 بروتوكول الاستجابة الميدانية ومحاكاة مقصورة الطائرة")
    
    # بطاقة تعليمات وتجهيزات الفريق الطبي الميداني
    st.markdown(f"""
    <div style="background: rgba(16, 35, 78, 0.7); border: 1px solid #00e5ff; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
        <h4 style="color: #00e5ff; margin-top: 0;">🦺 تعليمات وتجهيزات الفريق الطبي الميداني بالمنفذ:</h4>
        <p style="font-size: 1.05rem; margin-bottom: 6px;"><b>توجيهات الوقاية الشخصية (PPE Protocol):</b> {p_info['ppe_directive']}</p>
        <p style="font-size: 0.95rem; color: #94a3b8; margin: 0;"><b>الطقم الميداني المعتمد:</b> {p_info['ppe_item_name']} | <b>شدة الممرض:</b> {p_info['severity']}</p>
    </div>
    """, unsafe_allow_html=True)

    c_in1, c_in2 = st.columns([4, 6])
    with c_in1:
        st.subheader("📝 بلاغ الحالة المشتبهة")
        f_num = st.text_input("رقم الرحلة الجوية:", value="SV-314")
        chosen_row = st.number_input("صف المقعد (1 إلى 30):", min_value=1, max_value=30, value=12)
        chosen_col = st.selectbox("رمز المقعد:", ["A", "B", "C", "D", "E", "F"], index=1)
        infected_seat = f"{chosen_row}{chosen_col}"

    total_rows = 30
    cols_order = ["A", "B", "C", "D", "E", "F"]
    traced_seats = []

    if p_info["tracing_rule"] == "full_cabin":
        for r in range(1, total_rows + 1):
            for c in cols_order:
                if f"{r}{c}" != infected_seat:
                    traced_seats.append(f"{r}{c}")
        rule_desc = "حصر كامل كابينة الركاب (Airborne TB Protocol)"
    elif p_info["tracing_rule"] == "two_rows":
        start_r = max(1, chosen_row - 2)
        end_r = min(total_rows, chosen_row + 2)
        for r in range(start_r, end_r + 1):
            for c in cols_order:
                if f"{r}{c}" != infected_seat:
                    traced_seats.append(f"{r}{c}")
        rule_desc = "حصر دائرة مقاعد (صفين للأمام + صفين للخلف ونفس الصف بالكامل)"
    else:
        c_idx = cols_order.index(chosen_col)
        if c_idx > 0: traced_seats.append(f"{chosen_row}{cols_order[c_idx - 1]}")
        if c_idx < 5: traced_seats.append(f"{chosen_row}{cols_order[c_idx + 1]}")
        rule_desc = "حصر الملاصقين مباشرة يميناً ويساراً في نفس الصف"

    with c_in2:
        st.subheader("🎯 دائرة المخالطين والإخلاء")
        m1, m2 = st.columns(2)
        m1.metric("المقعد المصاب", infected_seat)
        m2.metric("عدد المخالطين الواجب حصرهم", f"{len(traced_seats)} راكب")
        st.info(f"**القاعدة المعيارية للحصر:** {rule_desc}")

        export_df = pd.DataFrame({
            "رقم الرحلة": [f_num] * (len(traced_seats) + 1),
            "المقعد": [infected_seat] + traced_seats,
            "التصنيف الإكلينيكي": ["حالة مشتبهة (عزل فوري بالمنفذ)"] + ["مخالط محصور (متابعة وبائية)"] * len(traced_seats),
            "المرض": [selected_pathogen_name] * (len(traced_seats) + 1)
        })
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تصدير كشف المخالطين لفرق الطب الوقائي (CSV)",
            data=csv_data,
            file_name=f"Contact_Tracing_{f_num}.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.subheader(f"✈️ المحاكاة الانسيابية لمقصورة الطائرة (Boeing/Airbus Streamlined Fuselage)")

    fig_plane = go.Figure()

    # 1. رسم هيكل الطائرة الانسيابي
    t = np.linspace(0, np.pi, 30)
    nose_x = 3.7 + 3.2 * np.cos(t)
    nose_y = 2 - 4.5 * np.sin(t)

    fuselage_x = list(nose_x) + [6.9, 6.9, 5.5, 3.7, 1.9, 0.5, 0.5]
    fuselage_y = list(nose_y) + [2, 32, 34.5, 35.5, 34.5, 32, 2]

    fig_plane.add_trace(go.Scatter(
        x=fuselage_x, y=fuselage_y,
        fill="toself",
        fillcolor="rgba(12, 28, 62, 0.6)",
        line=dict(color="#00e5ff", width=2.5),
        hoverinfo="none",
        showlegend=False
    ))

    # 2. أجنحة الطائرة الإيروديناميكية المنحنية
    fig_plane.add_trace(go.Scatter(
        x=[0.5, -4.5, -4.0, 0.5],
        y=[11, 20, 24, 21],
        fill="toself",
        fillcolor="rgba(0, 229, 255, 0.07)",
        line=dict(color="rgba(0, 229, 255, 0.4)", width=2),
        hoverinfo="none",
        showlegend=False
    ))
    fig_plane.add_trace(go.Scatter(
        x=[6.9, 11.9, 11.4, 6.9],
        y=[11, 20, 24, 21],
        fill="toself",
        fillcolor="rgba(0, 229, 255, 0.07)",
        line=dict(color="rgba(0, 229, 255, 0.4)", width=2),
        hoverinfo="none",
        showlegend=False
    ))

    # 3. قمرة القيادة وأبواب الطوارئ
    fig_plane.add_trace(go.Scatter(
        x=[3.7], y=[-1.5],
        mode="text",
        text=["✈️ قمرة القيادة"],
        textfont=dict(color="#00e5ff", size=12, family="Tajawal"),
        hoverinfo="none",
        showlegend=False
    ))
    fig_plane.add_trace(go.Scatter(
        x=[0.5, 6.9, 0.5, 6.9],
        y=[2, 2, 16, 16],
        mode="text",
        text=["🚪 مخرج", "مخرج 🚪", "🚪 طوارئ", "طوارئ 🚪"],
        textfont=dict(color="#ff9900", size=10, family="Tajawal"),
        hoverinfo="none",
        showlegend=False
    ))

    # 4. توزيع المقاعد
    x_coords = {"A": 1.4, "B": 2.2, "C": 3.0, "D": 4.4, "E": 5.2, "F": 6.0}
    seat_xs, seat_ys, seat_texts, seat_colors, seat_hovers = [], [], [], [], []

    for r in range(1, total_rows + 1):
        for c in cols_order:
            s_code = f"{r}{c}"
            seat_xs.append(x_coords[c])
            seat_ys.append(r)
            seat_texts.append(s_code)

            if s_code == infected_seat:
                seat_colors.append("#ff3366")
                seat_hovers.append(f"المقعد: {s_code} | الحالة المشتبهة (عزل فوري بالمنفذ)")
            elif s_code in traced_seats:
                seat_colors.append("#ff9900")
                seat_hovers.append(f"المقعد: {s_code} | مخالط محصور (حجر ومتابعة وبائية)")
            else:
                seat_colors.append("#0c203b")
                seat_hovers.append(f"المقعد: {s_code} | مسافر سليم")

    fig_plane.add_trace(go.Scatter(
        x=seat_xs,
        y=seat_ys,
        mode="markers+text",
        text=seat_texts,
        textposition="middle center",
        textfont=dict(size=8, color="#ffffff", family="Tajawal"),
        marker=dict(
            size=21,
            color=seat_colors,
            symbol="square",
            line=dict(width=1.5, color="rgba(0, 229, 255, 0.4)")
        ),
        hoverinfo="text",
        hovertext=seat_hovers,
        showlegend=False
    ))

    fig_plane.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(6, 12, 28, 0.7)",
        height=850,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            tickmode="array",
            tickvals=[1.4, 2.2, 3.0, 3.7, 4.4, 5.2, 6.0],
            ticktext=["A", "B", "C", "الممر", "D", "E", "F"],
            showgrid=False,
            zeroline=False,
            color="#00e5ff"
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            range=[-3.5, 36],
            tickmode="linear",
            tick0=1,
            dtick=1,
            color="#94a3b8"
        )
    )

    st.plotly_chart(fig_plane, use_container_width=True)
