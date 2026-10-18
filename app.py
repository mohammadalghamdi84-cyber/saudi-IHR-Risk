import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# إعدادات واجهة النظام
st.set_page_config(
    page_title="منظومة الاستخبارات الوبائية ومحاكاة المنافذ الجوية",
    page_icon="🛡️",
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

# قاعدة بيانات مؤشرات SPAR الثلاثية المتخصصة ومحطات الطيران
# C.4 = الترصد | C.5 = المختبرات | C.10 = نقاط الدخول
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

# مصفوفة الأمراض الأربعة المعتمدة علمياً
pathogen_db = {
    "Ebola / Marburg (حمى نزفية فيروسية - عالية الخطورة)": {
        "r0": 1.9, "incubation_days": 8.0, "type": "contact_fluids",
        "severity": "حرجة جداً (فتك حاد)", "tracing_rule": "direct_contacts_only",
        "incidence": {"Nigeria": 45.0, "Pakistan": 0.0, "India": 0.0, "Egypt": 0.0, "Bangladesh": 0.0, "Indonesia": 0.0, "Turkey": 0.0, "Jordan": 0.0, "UK": 0.0}
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

# --- نظام التبديل بين الشاشتين الرئيسيتين ---
st.sidebar.title("🎛️ لوحة القيادة والتحكم")
view_mode = st.sidebar.radio(
    "اختر شاشة العمليات:",
    ["1️⃣ شاشة تقييم الخطورة والفرز بصالة القدوم", "2️⃣ شاشة الاستجابة الميدانية ومحاكاة مقاعد الطائرة"]
)
st.sidebar.markdown("---")

# اختيار المرض والمنافذ
selected_pathogen_name = st.sidebar.selectbox("🦠 التهديد الوبائي المحدد:", list(pathogen_db.keys()))
p_info = pathogen_db[selected_pathogen_name]

# ==========================================
# الشاشة الأولى: تقييم الخطورة وتحديد المناظرة
# ==========================================
if view_mode == "1️⃣ شاشة تقييم الخطورة والفرز بصالة القدوم":
    st.title("🌐 تقييم خطورة الرحلات ومستوى المناظرة الميدانية")
    st.caption(f"المرض المراقب: **{selected_pathogen_name}** | شدة المرض: **{p_info['severity']}**")

    # اختيار المطارات المستهدفة
    selected_airports = st.sidebar.multiselect(
        "المنافذ الوطنية المراقبة:",
        options=list(national_airports.keys()),
        default=["MED", "JED"],
        format_func=lambda x: national_airports[x]["name"]
    )
    if not selected_airports:
        st.warning("يرجى اختيار مطار واحد على الأقل.")
        st.stop()

    uploaded_file = st.sidebar.file_uploader("📂 رفع جدول رحلات (Excel/CSV):", type=["xlsx", "xls", "csv"])

    # توليد بيانات رحلات واقعية
    @st.cache_data
    def get_schedule():
        data = []
        flight_no = 200
        origins_keys = list(origins_spar_db.keys())
        for day in range(1, 31):
            date_s = f"2026-09-{day:02d}"
            for dest in ["MED", "JED", "RUH"]:
                for _ in range(np.random.randint(2, 4)):
                    orig_k = origins_keys[np.random.randint(0, len(origins_keys))]
                    orig_data = origins_spar_db[orig_k]
                    data.append({
                        "flight": f"SV-{flight_no}",
                        "date": date_s,
                        "dest": dest,
                        "origin_city": orig_k.capitalize(),
                        "country": orig_data["country"],
                        "pax": int(np.random.randint(260, 420)),
                        "duration_h": orig_data["duration_h"],
                        "c4": orig_data["c4"], "c5": orig_data["c5"], "c10": orig_data["c10"],
                        "lat": orig_data["lat"], "lon": orig_data["lon"]
                    })
                    flight_no += 2
        return pd.DataFrame(data)

    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    else:
        df = get_schedule()

    df = df[df["dest"].isin(selected_airports)].copy()

    # محرك الحساب العلمي: R0 * SPAR Gap * Flight/Incubation Ratio
    def calculate_risk(row):
        ctry = row["country"]
        inc = p_info["incidence"].get(ctry, 5.0)
        
        # متوسط قدرات الرصد والمختبرات والمنافذ الثلاثية
        spar_core = (row["c4"] + row["c5"] + row["c10"]) / 3.0
        gap_factor = (100.0 - spar_core) / 35.0
        
        # نسبة زمن الطيران لفترة الحضانة
        incubation_hrs = p_info["incubation_days"] * 24.0
        flight_ratio = 1.0 + (row["duration_h"] / incubation_hrs)
        
        # حساب السكور
        score = (inc / 100000.0) * row["pax"] * p_info["r0"] * gap_factor * flight_ratio * 3200
        return np.clip(score, 6.0, 98.5).round(1)

    df["risk_score"] = df.apply(calculate_risk, axis=1)

    # تحديد مستوى المناظرة بصالة المطار (بدون صعود الطائرة)
    def get_tier(score):
        if score >= 65:
            return "مناظرة مشددة (أحمر): تدقيق بصري وحراري فردي عند المخرج وفحص إقرارات", "#ff3366", "مشددة"
        elif score >= 35:
            return "مناظرة معززة (برتقالي): مسح حراري نشط بالكاميرات وفرز عام", "#ff9900", "معززة"
        else:
            return "مناظرة روتينية (سماوي): تدفق طبيعي ومراقبة اعتيادية للمسافرين", "#00e5ff", "روتينية"

    tiers = df["risk_score"].apply(get_tier)
    df["screening_action"] = [t[0] for t in tiers]
    df["color"] = [t[1] for t in tiers]
    df["tier"] = [t[2] for t in tiers]

    # فلترة التاريخ
    st.sidebar.markdown("---")
    dates = sorted(list(df["date"].unique()))
    chosen_date = st.sidebar.select_slider("📅 تاريخ المناوبة والفرز:", options=dates, value=dates[0])
    df_day = df[df["date"] == chosen_date].copy()

    # البطاقات الإحصائية
    k1, k2, k3, k4 = st.columns(4)
    crit_c = len(df_day[df_day["tier"] == "مشددة"])
    k1.metric("رحلات اليوم المرصودة", f"{len(df_day)} رحلة")
    k2.metric("إجمالي المسافرين الوافدين", f"{df_day['pax'].sum():,} مسافر")
    k3.metric("رحلات المناظرة المشددة", f"{crit_c}", delta="تتطلب تركيزاً سريرياً" if crit_c > 0 else "مستقر", delta_color="inverse")
    k4.metric("متوسط مؤشر الخطر العام", f"{df_day['risk_score'].mean():.1f} / 100")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"📋 جدول فرز وتوزيع درجات المناظرة بصالة القدوم ({chosen_date})")
    view_df = df_day[["flight", "dest", "origin_city", "country", "pax", "duration_h", "risk_score", "screening_action"]].sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    view_df.columns = ["الرحلة", "المنفذ", "محطة الإقلاع", "الدولة", "الركاب", "ساعات الطيران", "مؤشر الخطورة", "إجراء المناظرة بصالة المطار"]
    st.dataframe(view_df, use_container_width=True)

# ==========================================
# الشاشة الثانية: الاستجابة ومحاكاة مقاعد الطائرة
# ==========================================
else:
    st.title("🚨 بروتوكول البلاغات وحصر مخالطي الطائرة")
    st.caption("تُفعل هذه الشاشة حصراً عند ورود بلاغ من كابتن الطائرة أو رصد حالة مشتبهة أثناء المناظرة.")

    col_setup, col_meta = st.columns([4, 6])
    
    with col_setup:
        st.subheader("📝 تفاصيل الحالة المشتبهة")
        flight_id = st.text_input("رقم الرحلة:", value="SV-214")
        seat_row = st.number_input("رقم صف المقعد للحالة (1 - 30):", min_value=1, max_value=30, value=12)
        seat_letter = st.selectbox("رمز المقعد:", ["A", "B", "C", "D", "E", "F"], index=1)
        reported_seat = f"{seat_row}{seat_letter}"
        
        st.info(f"**المرض المشتبه:** {selected_pathogen_name}\n\n**قاعدة الحصر:** `{p_info['tracing_rule']}`")

    # حساب المقاعد المحصورة وفق القواعد السريرية
    # الطائرة: 30 صفاً، كل صف 6 مقاعد (A, B, C | D, E, F)
    letters = ["A", "B", "C", "D", "E", "F"]
    total_rows = 30
    
    quarantine_seats = []
    
    if p_info["tracing_rule"] == "full_cabin":
        # الدرن الهوائي: حصر المقصورة كاملة
        for r in range(1, total_rows + 1):
            for l in letters:
                if f"{r}{l}" != reported_seat:
                    quarantine_seats.append(f"{r}{l}")
        rule_desc = "حصر المقصورة بالكامل (Airborne Spread)"
        
    elif p_info["tracing_rule"] == "two_rows":
        # رذاذي (كورونا/إنفلونزا): صفين للأمام وصفين للخلف + نفس الصف
        min_r = max(1, seat_row - 2)
        max_r = min(total_rows, seat_row + 2)
        for r in range(min_r, max_r + 1):
            for l in letters:
                if f"{r}{l}" != reported_seat:
                    quarantine_seats.append(f"{r}{l}")
        rule_desc = "حصر صفين للأمام وصفين للخلف ومقاعد نفس الصف (2 Rows Radius)"
        
    elif p_info["tracing_rule"] == "adjacent_only":
        # جدري الماء: المقاعد المجاورة في نفس الصف
        cur_idx = letters.index(seat_letter)
        adj_letters = []
        if cur_idx > 0: adj_letters.append(letters[cur_idx - 1])
        if cur_idx < 5: adj_letters.append(letters[cur_idx + 1])
        for l in adj_letters:
            quarantine_seats.append(f"{seat_row}{l}")
        rule_desc = "حصر المقاعد الملاصقة يميناً ويساراً في نفس الصف"
        
    else: # direct_contacts_only (إيبولا)
        # إيبولا: الملاصقين فوراً + طاقم الخدمة ومستخدمي الحمام
        cur_idx = letters.index(seat_letter)
        if cur_idx > 0: quarantine_seats.append(f"{seat_row}{letters[cur_idx - 1]}")
        if cur_idx < 5: quarantine_seats.append(f"{seat_row}{letters[cur_idx + 1]}")
        rule_desc = "الملاصقين المباشرين فقط + طاقم الخدمة وحظر تفريغ الصرف الصحي"

    with col_meta:
        st.subheader("🎯 مخرجات حصر المخالطين والتدخل الميداني")
        m1, m2, m3 = st.columns(3)
        m1.metric("المقعد المصاب", reported_seat)
        m2.metric("عدد المخالطين المطلوب حصرهم", f"{len(quarantine_seats)} راكب")
        m3.metric("مستوى الاستجابة", "عزل فوري ونقل طبي" if "Ebola" in selected_pathogen_name else "فرز ومتابعة وبائية")
        
        st.warning(f"**البروتوكول الميداني المعتمد:** {rule_desc}")
        st.markdown("""
        * **إجراء الطاقم الطبي:** الصعود بملابس الوقاية (PPE) المحددة لنمط المرض.
        * **إجراء الصالة:** عزل الحالة المشتبهة إلى غرفة العزل المؤقتة بالمنفذ.
        * **المخالطون:** سحب بيانات الاتصال وتوقيع الإقرار الصحي وحجز السجلات للتتبع الوبائي لمدة 14-21 يوماً.
        """)

    st.markdown("---")
    st.subheader("✈️ المحاكاة التفاعلية لمقصورة الطائرة وتوزيع المقاعد المحصورة")
    st.caption("المقعد الأحمر الوامض يمثل الحالة المشتبهة، والمقاعد البرتقالية تمثل دائرة المخالطين الملزم حصرهم، والمقاعد السماوية آمنة.")

    # بناء شبكة المقاعد بـ Plotly
    rows_list, cols_list, seat_labels, seat_status, colors = [], [], [], [], []
    col_mapping = {"A": 1, "B": 2, "C": 3, "D": 4.5, "E": 5.5, "F": 6.5} # ممر في المنتصف

    for r in range(1, total_rows + 1):
        for l in letters:
            s_name = f"{r}{l}"
            rows_list.append(r)
            cols_list.append(col_mapping[l])
            seat_labels.append(s_name)
            
            if s_name == reported_seat:
                seat_status.append("الحالة المشتبهة (عزل مباشر)")
                colors.append("#ff3366") # أحمر فاقع
            elif s_name in quarantine_seats:
                seat_status.append("مخالط محصور (تتبع وعزل/فحص)")
                colors.append("#ff9900") # برتقالي متوهج
            else:
                seat_status.append("مسافر غير مشتبه")
                colors.append("#0c2340") # كحلي داكن

    fig_seats = go.Figure()

    fig_seats.add_trace(go.Scatter(
        x=cols_list,
        y=rows_list,
        mode="markers+text",
        text=seat_labels,
        textposition="middle center",
        textfont=dict(size=9, color="#ffffff", family="Tajawal"),
        marker=dict(
            size=22,
            color=colors,
            symbol="square",
            line=dict(width=1.5, color="rgba(0, 229, 255, 0.4)")
        ),
        hoverinfo="text",
        hovertext=[f"المقعد: {seat_labels[i]}<br>الحالة: {seat_status[i]}" for i in range(len(seat_labels))]
    ))

    fig_seats.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8, 18, 42, 0.7)",
        height=750,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3, 4.5, 5.5, 6.5],
            ticktext=["A", "B", "C", "D (ممر)", "E", "F"],
            showgrid=False,
            zeroline=False,
            color="#00e5ff"
        ),
        yaxis=dict(
            title="صفوف الطائرة (1 - 30)",
            tickmode="linear",
            tick0=1,
            dtick=1,
            autorange="reversed",
            showgrid=True,
            gridcolor="rgba(0, 229, 255, 0.08)",
            color="#94a3b8"
        )
    )

    st.plotly_chart(fig_seats, use_container_width=True)
