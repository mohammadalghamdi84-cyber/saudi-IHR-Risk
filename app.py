import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="منظومة ثغر | الاستخبار الوبائي ومراقبة منافذ الدخول الجوية",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الهوية البصرية السيادية (Deep Navy & Cyan Glow)
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
    }
    .iso-card {
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(0, 229, 255, 0.3);
        font-weight: bold;
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
    "MED": {"name": "مطار الأمير محمد بن عبدالعزيز (المدينة)", "lat": 24.5534, "lon": 39.7051, "iso_rooms": 2, "ppe_stock": 25},
    "JED": {"name": "مطار الملك عبدالعزيز الدولي (جدة)", "lat": 21.6796, "lon": 39.1565, "iso_rooms": 4, "ppe_stock": 50},
    "RUH": {"name": "مطار الملك خالد الدولي (الرياض)", "lat": 24.9576, "lon": 46.6988, "iso_rooms": 4, "ppe_stock": 50}
}

# خصائص الأمراض وتوجيهات الوقاية الشخصية الصارمة (PPE Guidelines)
pathogen_metadata = {
    "Ebola / Marburg (حمى نزفية فيروسية - عالية الخطورة)": {
        "r0": 1.9, "incubation_days": 8.0, "type": "contact_fluids",
        "severity": "حرجة جداً (فتك حاد)", "tracing_rule": "direct_contacts_only",
        "ppe_directive": "المستوى الرابع (Level 4): بدلة عزل بيولوجي كاملة (Coverall مدمجة بغطاء رأس) + قفازات مزدوجة + كمامة PAPR/N95 محكمة + واقي وجه وواقي أحذية مقاوم للسوائل. يُمنع أي كشف للبشرة نهائياً.",
        "ppe_kit_name": "طقم عزل حمى نزفية عالي الحماية (Bio-Hazard Suit)"
    },
    "Airborne TB (الدرن الرئوي المفتوح - منقول بالهواء)": {
        "r0": 3.2, "incubation_days": 30.0, "type": "airborne",
        "severity": "عالية ومزمنة", "tracing_rule": "full_cabin",
        "ppe_directive": "المستوى الثالث المحمول جواً (Airborne PPE): كمامة N95 محكمة الفحص (Fit-tested N95 Mask) + نظارات حماية بانورامية (Goggles) + مريول طبي معقم عازل للسوائل + قفازات طبية.",
        "ppe_kit_name": "طقم فحص أمراض تنفسية محمولة جواً (Airborne N95 Kit)"
    },
    "Severe Influenza / Novel Corona (رذاذي حاد)": {
        "r0": 2.5, "incubation_days": 3.5, "type": "droplet",
        "severity": "متوسطة إلى عالية", "tracing_rule": "two_rows",
        "ppe_directive": "مستوى الرذاذ التنفسي (Droplet PPE): كمامة جراحية عالية الكفاءة أو N95 + واقي الوجه الكامل (Face Shield) + مريول حماية طبي + قفازات فحص.",
        "ppe_kit_name": "طقم رذاذ تنفسي قياسي (Droplet PPE Pack)"
    },
    "Chickenpox (جدري الماء - تلامسي مختلط)": {
        "r0": 1.6, "incubation_days": 14.0, "type": "contact_skin",
        "severity": "خفيفة إلى معتدلة", "tracing_rule": "adjacent_only",
        "ppe_directive": "مستوى التلامس والرذاذ (Contact/Droplet): مريول طبي واقٍ + قفازات عزل + كمامة جراحية لمنع انتقال الرذاذ أثناء الفحص المباشر للطفح.",
        "ppe_kit_name": "طقم تلامس ورذاذ اعتيادي (Standard Contact Pack)"
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
    ["1️⃣ شاشة التنبؤ، الإمداد، وحوكمة المنافذ", "2️⃣ الاستجابة الميدانية، البروتوكول، وتتبع المقصورة"]
)
st.sidebar.markdown("---")

selected_pathogen_name = st.sidebar.selectbox("🦠 التهديد الوبائي المحدد:", list(pathogen_metadata.keys()))
p_info = pathogen_metadata[selected_pathogen_name]

# إضافة معامل البلاغات غير الرسمية (EBS Rumor Factor)
st.sidebar.markdown("---")
st.sidebar.subheader("📡 استخبارات الرصد المفتوح (EBS)")
rumor_factor = st.sidebar.slider(
    "معامل البلاغات والتفشيات غير الرسمية (ω):",
    min_value=1.0, max_value=3.0, value=1.0, step=0.2,
    help="يُرفع المعامل تلقائياً عند رصد شائعات أو إشارات وبائية عبر منصات EIOS أو ProMED بدولة المنشأ قبل الإعلان الحكومي الرسمي."
)

# =========================================================================
# الشاشة الأولى: التنبؤ، الإمداد، وغرف العزل
# =========================================================================
if view_mode == "1️⃣ شاشة التنبؤ، الإمداد، وحوكمة المنافذ":
    st.title("🌐 منظومة التنبؤ الاستباقي وحوكمة الإمداد بالمنافذ")
    st.caption(f"المرض المستهدف: **{selected_pathogen_name}** | مؤشر الشائعات والرصد غير الرسمي: **{rumor_factor}x**")

    selected_airport_code = st.sidebar.selectbox(
        "منفذ الدخول الجوي المباشر:",
        options=list(national_airports.keys()),
        format_func=lambda x: national_airports[x]["name"],
        index=0
    )
    port_meta = national_airports[selected_airport_code]

    @st.cache_data
    def generate_schedule():
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
                        "c4": orig_data["c4"], "c5": orig_data["c5"], "c10": orig_data["c10"]
                    })
                    flight_idx += 2
        return pd.DataFrame(data)

    df_all = generate_schedule()
    df_port = df_all[df_all["dest"] == selected_airport_code].copy()

    # حساب مؤشر الخطورة مع معامل البلاغات غير الرسمية
    def eval_flight_risk(row):
        inc = get_pathogen_incidence(selected_pathogen_name, row["country"])
        spar_core = (row["c4"] + row["c5"] + row["c10"]) / 3.0
        gap_factor = (100.0 - spar_core) / 35.0
        incubation_hrs = p_info["incubation_days"] * 24.0
        flight_ratio = 1.0 + (row["duration_h"] / incubation_hrs)
        # دمج معامل البلاغات غير الرسمية
        score = (inc / 100000.0) * row["pax"] * p_info["r0"] * gap_factor * flight_ratio * rumor_factor * 3200
        return np.clip(score, 5.0, 99.0).round(1)

    df_port["risk_score"] = df_port.apply(eval_flight_risk, axis=1)

    def assign_tier(score):
        if score >= 65:
            return "مشددة (أحمر)", "#ff3366", "حرج"
        elif score >= 35:
            return "معززة (برتقالي)", "#ff9900", "متوسط"
        else:
            return "روتينية (سماوي)", "#00e5ff", "منخفض"

    tiers = df_port["risk_score"].apply(assign_tier)
    df_port["level_desc"] = [t[0] for t in tiers]
    df_port["color"] = [t[1] for t in tiers]
    df_port["tier"] = [t[2] for t in tiers]

    # فلترة اليوم
    dates = sorted(list(df_port["date"].unique()))
    chosen_day = st.sidebar.select_slider("📅 تاريخ المناوبة الميدانية:", options=dates, value=dates[0])
    df_day = df_port[df_port["date"] == chosen_day].copy()

    # --- قسم السعة السريرية والإمداد الوقائي المباشر ---
    st.subheader(f"🏥 إدارة السعة السريرية والإمداد الوقائي ({port_meta['name']} - {chosen_day})")

    crit_flights = df_day[df_day["tier"] == "حرج"]
    crit_count = len(crit_flights)
    # كل رحلة حمراء تتطلب استهلاك 4 إلى 6 أطقم وقائية للفحص والفرز
    ppe_needed = crit_count * 5
    remaining_ppe = port_meta["ppe_stock"] - ppe_needed
    # غرف العزل المطلوبة
    iso_needed = min(crit_count, port_meta["iso_rooms"])
    iso_available = port_meta["iso_rooms"] - iso_needed

    c_sup1, c_sup2, c_sup3, c_sup4 = st.columns(4)
    c_sup1.metric("الرحلات الحرجة المتوقعة اليوم", f"{crit_count} رحلات", delta=f"{crit_count} تتطلب طواقم عزل" if crit_count > 0 else "مستقر", delta_color="inverse")
    c_sup2.metric("استهلاك الأطقم الوقائية (PPE)", f"{ppe_needed} طقم", delta=f"المتبقي: {remaining_ppe} من أصل {port_meta['ppe_stock']}")
    c_sup3.metric("غرف العزل الشاغرة بالمطار", f"{iso_available} من أصل {port_meta['iso_rooms']}")
    c_sup4.metric("مؤشر الجاهزية اللوجستية", "جاهزية كاملة" if remaining_ppe >= 10 and iso_available > 0 else "تنبيه: اقتراب استنفاد الطاقة", delta_color="normal" if iso_available > 0 else "inverse")

    # رسم غرف العزل بمطار المنفذ
    st.markdown("**حالة غرف العزل المؤقتة بالمنفذ حالياً:**")
    iso_cols = st.columns(port_meta["iso_rooms"])
    for idx, col in enumerate(iso_cols):
        room_no = idx + 1
        with col:
            if idx < iso_needed:
                st.markdown(f"""
                <div class="iso-card" style="background: rgba(255, 51, 102, 0.2); border-color: #ff3366; color: #ff3366;">
                    🚪 غرفة عزل {room_no}<br>
                    <span style="font-size: 0.85rem;">[ محجوزة لرحلة حرجة ]</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="iso-card" style="background: rgba(0, 229, 255, 0.15); border-color: #00e5ff; color: #00e5ff;">
                    🚪 غرفة عزل {room_no}<br>
                    <span style="font-size: 0.85rem;">[ شاغرة ومجهزة بالكامل ]</span>
                </div>
                """, unsafe_allow_html=True)

    if remaining_ppe < 10:
        st.error(f"🚨 **إنذار نقص سلاسل الإمداد:** المخزون المتبقي من {p_info['ppe_kit_name']} سينخفض إلى ({remaining_ppe}) طقم. يُرجى تفعيل طلب الدعم اللوجستي الفوري من مستودعات التموين الطبي.")

    st.markdown("---")

    # جدول الرحلات مع أداة التفكيك والتشخيص الإكلينيكي
    st.subheader(f"📋 سجل الرحلات اليومية وتفكيك مسببات الخطورة ({chosen_day})")
    
    col_table, col_explain = st.columns([6, 4])
    
    with col_table:
        disp_df = df_day[["flight", "origin_city", "country", "pax", "duration_h", "risk_score", "level_desc"]].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
        disp_df.columns = ["الرحلة", "محطة الإقلاع", "الدولة", "الركاب", "ساعات الطيران", "مؤشر الخطر", "مستوى المناظرة"]
        st.dataframe(disp_df, use_container_width=True)

    with col_explain:
        st.markdown("**🔍 تشخيص وتفكيك أسباب تقييم الرحلة (Explainable Risk):**")
        selected_flight = st.selectbox("اختر رحلة لتحليل سبب تصنيفها:", options=df_day["flight"].tolist())
        target_row = df_day[df_day["flight"] == selected_flight].iloc[0]

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
            reasons.append(f"• **ضعف الشفافية ونظم الرصد:** تقييم قدرات دولة {target_row['country']} في لوائح SPAR متدنٍ ({spar_avg:.1f}/100)، مما يرفع معامل تصحيح الحالات الخفية.")
        if p_info["r0"] > 2.0:
            reasons.append(f"• **سرعة الانتشار الوبائي:** معدل التكاثر الأساسي للمرض مرتفع ($R_0 = {p_info['r0']}$).")
        if target_row["duration_h"] >= 4.5:
            reasons.append(f"• **طول زمن الرحلة:** مدة الطيران ({target_row['duration_h']} ساعة) تزيد احتمالية ظهور أعراض حيوية أثناء التحليق.")
        if rumor_factor > 1.0:
            reasons.append(f"• **إشارات وبائية غير مؤكدة:** تم تفعيل معامل الرصد المفتوح والشائعات بمقدار ({rumor_factor}x) لوجود بلاغات غير رسمية.")

        if not reasons:
            reasons.append("• الرحلة قادمة من دولة ذات مؤشرات رصد متقدمة واستقرار وبائي؛ الإجراء اعتيادي دون قلق.")

        st.markdown(f"""
        <div class="reason-box" style="border-color: {box_border};">
            <h5 style="color: {box_border}; margin-bottom: 8px;">الرحلة: {target_row['flight']} ({target_row['origin_city']}) - {level_name}</h5>
            {"<br>".join(reasons)}
        </div>
        """, unsafe_allow_html=True)

# =========================================================================
# الشاشة الثانية: الاستجابة الميدانية، البروتوكول، وتتبع المقصورة الانسيابي
# =========================================================================
else:
    st.title("🚨 بروتوكول الاستجابة الميدانية ومحاكاة مقصورة الطائرة")
    
    # بطاقة تعليمات وتجهيزات الفريق الطبي الميداني
    st.markdown(f"""
    <div style="background: rgba(16, 35, 78, 0.7); border: 1px solid #00e5ff; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
        <h4 style="color: #00e5ff; margin-top: 0;">🦺 تعليمات وتجهيزات الفريق الطبي الميداني بالمنفذ:</h4>
        <p style="font-size: 1.05rem; margin-bottom: 6px;"><b>توجيهات الوقاية الشخصية (PPE Protocol):</b> {p_info['ppe_directive']}</p>
        <p style="font-size: 0.95rem; color: #94a3b8; margin: 0;"><b>الطقم الميداني المعتمد:</b> {p_info['ppe_kit_name']} | <b>شدة الممرض:</b> {p_info['severity']}</p>
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

    # 1. رسم هيكل الطائرة الانسيابي (Smooth Jet Curve)
    # مقدمة انسيابية بيضاوية + جسم مائل + ذيل رشيق
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

    # 2. أجنحة الطائرة الإيروديناميكية المنحنية (Aerodynamic Swept Wings)
    # الجناح الأيسر
    fig_plane.add_trace(go.Scatter(
        x=[0.5, -4.5, -4.0, 0.5],
        y=[11, 20, 24, 21],
        fill="toself",
        fillcolor="rgba(0, 229, 255, 0.07)",
        line=dict(color="rgba(0, 229, 255, 0.4)", width=2),
        hoverinfo="none",
        showlegend=False
    ))
    # الجناح الأيمن
    fig_plane.add_trace(go.Scatter(
        x=[6.9, 11.9, 11.4, 6.9],
        y=[11, 20, 24, 21],
        fill="toself",
        fillcolor="rgba(0, 229, 255, 0.07)",
        line=dict(color="rgba(0, 229, 255, 0.4)", width=2),
        hoverinfo="none",
        showlegend=False
    ))

    # 3. قمرة القيادة وأبواب الطوارئ الانسيابية
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

    # 4. توزيع المقاعد المريحة
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
