import streamlit as st
import math
import google.generativeai as genai
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(
    page_title="Smart_Engineer OMNI-X",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Sidebar Putih, Teks Hitam, Footer Merah
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #F8F9FA; }
    
    /* --- SIDEBAR STYLING --- */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Memaksa Semua Teks di Sidebar Menjadi HITAM */
    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    
    /* Styling Input Fields di Sidebar */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #F5F5F5 !important;
        border: 1px solid #CCCCCC;
        color: #000000 !important;
    }

    /* --- MAIN CONTENT STYLING --- */
    h1, h2, h3 {
        color: #0D47A1;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
    }
    
    /* Result Box (Card Style) */
    .res-box {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 10px;
        border-left: 8px solid #FF6F00; /* Amber Accent */
        margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        color: #263238;
    }
    
    /* Hasil Detailing Besi */
    .steel-res {
        background-color: #E8F5E9;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        border: 1px solid #C8E6C9;
    }
    
    .res-label {
        font-weight: 600;
        color: #455A64;
        font-size: 0.95rem;
        display: block;
        margin-bottom: 2px;
    }
    
    .res-val {
        font-weight: 800;
        color: #0D47A1;
        font-size: 1.3rem;
        font-family: 'Consolas', monospace;
    }

    .res-steel {
        font-weight: 900;
        color: #2E7D32;
        font-size: 1.4rem;
        font-family: 'Consolas', monospace;
    }
    
    /* Custom Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #0D47A1, #1565C0);
        color: white;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 12px;
        border-radius: 6px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(13, 71, 161, 0.2);
        background: linear-gradient(135deg, #FF6F00, #F57C00);
        color: white !important;
    }

    /* Status Badges */
    .badge-ok { background-color: #2E7D32; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85rem;}
    .badge-no { background-color: #C62828; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85rem;}
    .badge-warn { background-color: #F9A825; color: #263238; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85rem;}
    
    /* Footer Styling Specific - MERAH */
    .sidebar-footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        background: #FFEBEE;
        border-top: 2px solid #FFCDD2;
        border-radius: 8px;
    }
    .footer-email { color: #000000 !important; font-weight: bold; font-size: 0.8rem; }
    .footer-donasi { color: #D50000 !important; font-weight: 900; margin-top: 10px; font-size: 0.9rem; text-transform: uppercase; }
    .footer-norek { color: #D50000 !important; font-family: monospace; font-size: 1.1rem; font-weight: 900; letter-spacing: 1px; }
    
    /* Chat Bubble Fix */
    .stChatMessage { background-color: #FFFFFF; border: 1px solid #E0E0E0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI BANTUAN TEKNIS & VISUALISASI
# ==========================================
def safe_div(n, d, default=0.0):
    return n / d if d != 0 else default

def get_steel_area(diameter):
    """Luas penampang 1 batang tulangan (mm2)"""
    return 0.25 * math.pi * (diameter**2)

# --- FUNGSI GAMBAR (VISUALISASI) ---
def draw_beam_section(b, h, n_top, n_bottom, diameter_main, diameter_stirrup, title="Detail Balok"):
    fig, ax = plt.subplots(figsize=(4, (h/b)*3.5 if b>0 else 4))
    # Beton
    concrete = patches.Rectangle((0, 0), b, h, linewidth=2, edgecolor='#555', facecolor='#E0E0E0')
    ax.add_patch(concrete)
    # Sengkang (Selimut 40mm)
    cover = 40
    stirrup = patches.Rectangle((cover, cover), b-2*cover, h-2*cover, linewidth=2, edgecolor='#D32F2F', facecolor='none', linestyle='--')
    ax.add_patch(stirrup)
    
    def draw_bar(x, y, d, color='#1565C0'):
        circle = patches.Circle((x, y), d/2, linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(circle)

    y_bot = cover + diameter_stirrup + diameter_main/2
    y_top = h - (cover + diameter_stirrup + diameter_main/2)
    
    # Tulangan Bawah
    if n_bottom > 0:
        if n_bottom == 1: draw_bar(b/2, y_bot, diameter_main)
        else:
            spacing = (b - 2*cover - 2*diameter_stirrup - diameter_main) / (n_bottom - 1)
            for i in range(n_bottom):
                draw_bar(cover + diameter_stirrup + diameter_main/2 + (i * spacing), y_bot, diameter_main)
    # Tulangan Atas (Min 2)
    n_top = max(n_top, 2) 
    spacing_top = (b - 2*cover - 2*diameter_stirrup - diameter_main) / (n_top - 1)
    for i in range(n_top):
        draw_bar(cover + diameter_stirrup + diameter_main/2 + (i * spacing_top), y_top, diameter_main)

    ax.set_xlim(-50, b+50); ax.set_ylim(-50, h+50)
    plt.axis('off'); plt.title(title, fontweight='bold')
    return fig

def draw_column_section(b, h, n_total, diameter_main):
    fig, ax = plt.subplots(figsize=(4, (h/b)*3.5 if b>0 else 4))
    concrete = patches.Rectangle((0, 0), b, h, linewidth=2, edgecolor='#333', facecolor='#CFD8DC')
    ax.add_patch(concrete)
    cover = 40
    ax.add_patch(patches.Rectangle((cover, cover), b-2*cover, h-2*cover, linewidth=2, edgecolor='#D32F2F', facecolor='none', linestyle='--'))
    
    # Distribusi Tulangan Sederhana (4 Sudut + Sisa)
    bars = [(cover+10, cover+10), (b-cover-10, cover+10), (b-cover-10, h-cover-10), (cover+10, h-cover-10)]
    sisa = n_total - 4
    if sisa > 0: # Tambah di tengah
        bars.append((b/2, cover+10)); bars.append((b/2, h-cover-10))
        if sisa > 2: bars.append((cover+10, h/2)); bars.append((b-cover-10, h/2))

    for (x, y) in bars:
        ax.add_patch(patches.Circle((x, y), diameter_main/2, edgecolor='black', facecolor='#1565C0'))

    ax.set_xlim(-50, b+50); ax.set_ylim(-50, h+50)
    plt.axis('off'); plt.title("Detail Kolom", fontweight='bold')
    return fig

# --- LOGIKA AUTO-DESIGN ---
def auto_design_slab(As_req, thickness_mm):
    As_min = 0.0018 * 1000 * thickness_mm
    As_final = max(As_req, As_min)
    options = [8, 10, 12, 13]
    best_option = ""
    for D in options:
        A_bar = get_steel_area(D)
        s_calc = (1000 * A_bar) / As_final
        s_max = min(2 * thickness_mm, 250) 
        s_design = math.floor(min(s_calc, s_max) / 25) * 25
        if s_design >= 100: 
            best_option = f"D{D}-{s_design:.0f}"; break
    if best_option == "": best_option = "D13-100 (Perlu Cek)"
    return As_final, best_option

def auto_design_beam(As_req, width_mm):
    options = [13, 16, 19, 22, 25]
    best_config = ""
    for D in options:
        A_bar = get_steel_area(D)
        n = math.ceil(As_req / A_bar)
        max_bar_layer = (width_mm - 80) / (D + 25)
        if n >= 2 and n <= max_bar_layer * 2: 
            best_config = f"{n} D{D}"; break
    if best_config == "": 
        n_16 = math.ceil(As_req / get_steel_area(16))
        best_config = f"{n_16} D16"
    return best_config

def get_practical_stirrup(h_mm):
    spacing = min(h_mm/2, 200)
    spacing = math.floor(spacing / 25) * 25 
    return f"Ø8-{spacing:.0f}"

# Database Persona AI
gems_persona = {
    "👑 The GEMS Grandmaster": "Anda adalah Direktur Proyek yang Bijaksana. Jawab dengan data teknis, SNI, dan solusi konkret.",
    "🏗️ Ahli Struktur (Gedung)": "Anda Ahli Struktur SNI 2847. Fokus pada beton, baja, dan detailing tulangan.",
    "🪨 Ahli Geoteknik (Tanah)": "Anda Ahli Geoteknik SNI 8460. Fokus pada pondasi dan daya dukung tanah.",
    "💰 Ahli Estimator (QS)": "Anda Ahli Estimasi Biaya. Fokus pada volume dan efisiensi material.",
    "🕌 Ahli Fiqih Bangunan": "Anda Penasihat Syariah. Fokus pada keberkahan dan adab membangun."
}

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px; border-bottom: 2px solid #0D47A1; margin-bottom: 20px;">
        <h2 style="color:#0D47A1 !important; margin:0; font-size: 1.8rem; font-weight: 900;">Smart_Engineer</h2>
        <span style="color:#FF6F00 !important; font-weight:bold; letter-spacing:2px; font-size:0.8rem;">OMNI-X EDITION</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📂 MENU UTAMA")
    category = st.selectbox("Pilih Kategori:", [
        "🏠 DASHBOARD", "A. BEBAN & ATAP", "B. GEMPA & STABILITAS", 
        "C. STRUKTUR ATAS", "D. PONDASI DANGKAL", "E. PONDASI DALAM", "F. STRUKTUR KHUSUS"
    ])

    st.markdown("---")
    
    module = None
    if category == "A. BEBAN & ATAP":
        module = st.radio("Pilih Modul:", ["1. Analisis Beban (Wt)", "2. Konstruksi Atap", "3. Tributary Area", "4. Pusat Massa (COG)"])
    elif category == "B. GEMPA & STABILITAS":
        module = st.radio("Pilih Modul:", ["5. Respon Spektrum", "6. Drift & Simpangan", "7. Eksentrisitas"])
    elif category == "C. STRUKTUR ATAS":
        module = st.radio("Pilih Modul:", ["8. Pelat Lantai", "9. Lendutan Pelat", "10. Desain Balok", "11. Torsi Balok", "12. Desain Kolom", "13. Shear Wall", "14. Desain Tangga"])
    elif category == "D. PONDASI DANGKAL":
        module = st.radio("Pilih Modul:", ["15. Pondasi Telapak", "16. Pondasi Lajur", "17. Sloof (Tie Beam)", "18. Pelat Westergaard"])
    elif category == "E. PONDASI DALAM":
        module = st.radio("Pilih Modul:", ["19. Pile Cap & Pons", "20. Meyerhof (Daya Dukung)", "21. Momen Tiang", "22. Lateral Tiang", "23. Kalendering Hiley", "24. Efisiensi Grup", "25. Cek Cabut (Uplift)"])
    elif category == "F. STRUKTUR KHUSUS":
        module = st.radio("Pilih Modul:", ["26. Retaining Wall", "27. Kolam / Tandon", "28. Jembatan", "29. Konversi Tulangan"])

    # AI Section
    st.markdown("---")
    with st.expander("🤖 KONSULTASI AI (GEN-AI)", expanded=False):
        api_key = st.text_input("🔑 Google API Key:", type="password")
        selected_model = st.selectbox("Model:", ["models/gemini-pro-latest", "models/gemini-flash-latest"], index=1)
        selected_brain = st.selectbox("Spesialis:", list(gems_persona.keys()))
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa saya bantu?"}]
            
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
            
        if prompt := st.chat_input("Tanya AI..."):
            if not api_key:
                st.error("API Key Kosong!")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                try:
                    genai.configure(api_key=api_key)
                    model_ai = genai.GenerativeModel(selected_model)
                    full_prompt = f"{gems_persona[selected_brain]}\nUser: {prompt}"
                    response = model_ai.generate_content(full_prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.chat_message("assistant").write(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

    # FOOTER MERAH
    st.markdown("""
    <div class="sidebar-footer">
        <div class="footer-email">by smartstudioarsitek@gmail.com</div>
        <div class="footer-donasi">Donasi : Bank Jago Syariah</div>
        <div class="footer-norek">5028 4297 0355</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIKA PERHITUNGAN (FULL 29 MODUL)
# ==========================================

if category == "🏠 DASHBOARD":
    st.title("🚀 Smart_Engineer Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ **Status: SIAP (29 Modul)**")
        st.write("Fitur: Analisis SNI, Auto-Detailing, & Visualisasi.")
    with col2:
        st.info("ℹ️ **Tips:**")
        st.write("Pilih modul di sidebar kiri untuk memulai perhitungan.")

# --- A. BEBAN & ATAP ---
elif module == "1. Analisis Beban (Wt)":
    st.header("1. Analisis Beban (Wt)")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Atap")
        A1 = st.number_input("Luas Atap (m²)", 200.0)
        D1 = st.number_input("DL Atap (kg/m²)", 408.0)
        L1 = st.number_input("LL Atap (kg/m²)", 100.0)
    with c2:
        st.subheader("Lantai Tipikal")
        A2 = st.number_input("Luas Tipikal (m²)", 200.0)
        D2 = st.number_input("DL Tipikal (kg/m²)", 488.0)
        L2 = st.number_input("LL Tipikal (kg/m²)", 250.0)
    
    N_typ = st.number_input("Jumlah Lantai Tipikal", 3)
    
    if st.button("HITUNG"):
        Wa = A1 * (D1 + 0.3*L1)
        Wt_typ = A2 * (D2 + 0.3*L2) * N_typ
        Wt_tot = (Wa + Wt_typ)/100 
        st.markdown(f'<div class="res-box"><div>Wa: {Wa:,.0f} kg</div><div>Wt Typ: {Wt_typ:,.0f} kg</div><hr><div>Total Wt: <span class="res-val">{Wt_tot:.2f} kN</span></div></div>', unsafe_allow_html=True)

elif module == "2. Konstruksi Atap":
    st.header("2. Konstruksi Atap")
    c1, c2 = st.columns(2)
    with c1:
        La = st.number_input("Jarak Kuda-kuda (m)", 4.0)
        sa = st.number_input("Jarak Gording (m)", 1.2)
        aa = st.number_input("Sudut (deg)", 20.0)
        Wx = st.number_input("Profil C (Wx) [cm3]", 38.0)
    with c2:
        qDa = st.number_input("DL (kg/m2)", 25.0)
        Pa = st.number_input("LL (kg)", 100.0)
        E_val = st.number_input("E (kg/cm2)", 2100000.0)
        Ix_val = st.number_input("Ix (cm4)", 150.0)
        
    if st.button("ANALISIS"):
        rad = math.radians(aa)
        q = 1.2 * qDa * sa 
        Mx = (1/8) * (q * math.cos(rad)) * (La**2) * 100 
        My = Mx * 0.1
        sig = safe_div(Mx, Wx)
        
        L_cm = La * 100
        q_perp_cm = (q * math.cos(rad)) / 100 
        P_perp = Pa * math.cos(rad)
        
        del_q = (5 * q_perp_cm * math.pow(L_cm, 4)) / (384 * E_val * Ix_val)
        del_P = (1 * P_perp * math.pow(L_cm, 3)) / (48 * E_val * Ix_val)
        del_val = del_q + del_P
        
        status = "AMAN" if (sig < 1600 and del_val < (L_cm/240)) else "CEK PROFIL"
        st.markdown(f"""
        <div class="res-box">
            <div>Mx: <span class="res-val">{Mx:.0f} kgcm</span></div>
            <div>Tegangan: <span class="res-val">{sig:.0f} kg/cm²</span></div>
            <div>Lendutan: <span class="res-val">{del_val:.2f} cm</span></div>
            <div>Status: <span class="badge-ok">{status}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "3. Tributary Area":
    st.header("3. Tributary Area")
    Pt = st.number_input("P (m)", 4.0)
    Lt = st.number_input("L (m)", 3.0)
    qt = st.number_input("q Pelat (kg/m²)", 120.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Total: <span class="res-val">{Pt*Lt*qt:.0f} kg</span></div>', unsafe_allow_html=True)

elif module == "4. Pusat Massa (COG)":
    st.header("4. Pusat Massa")
    Smx = st.number_input("Sum Momen X", 50000.0)
    Smy = st.number_input("Sum Momen Y", 30000.0)
    Wi = st.number_input("Berat Wi", 5000.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Xm: {safe_div(Smx,Wi):.2f} m <br> Ym: {safe_div(Smy,Wi):.2f} m</div>', unsafe_allow_html=True)

# --- B. GEMPA ---
elif module == "5. Respon Spektrum":
    st.header("5. Gempa SNI 1726")
    c1, c2 = st.columns(2)
    Ss = c1.number_input("Ss", 0.9)
    S1 = c2.number_input("S1", 0.4)
    with c1: R_val = st.selectbox("Sistem R", [8, 5, 3])
    with c2: Ie_val = st.selectbox("Faktor Ie", [1.0, 1.5])
    Wt = st.number_input("Wt (kN)", 5000.0)
    
    if st.button("HITUNG"):
        Sds = 0.666 * Ss
        V = (Sds * Ie_val / R_val) * Wt 
        st.markdown(f'<div class="res-box">SDS: {Sds:.2f} <br> Base Shear V: <span class="res-val">{V:.0f} kN</span></div>', unsafe_allow_html=True)

elif module == "6. Drift & Simpangan":
    st.header("6. Drift")
    hs = st.number_input("Tinggi (mm)", 4000.0)
    de = st.number_input("Simpangan Elastis (mm)", 15.0)
    if st.button("CEK"):
        d = 5.5 * de
        allow = 0.02 * hs
        stat = "AMAN" if d < allow else "BAHAYA"
        st.markdown(f'<div class="res-box">Drift: {d:.1f} mm <br> Status: <span class="badge-ok">{stat}</span></div>', unsafe_allow_html=True)

elif module == "7. Eksentrisitas":
    st.header("7. Eksentrisitas")
    B = st.number_input("Lebar B", 15.0)
    Pm = st.number_input("Pusat Massa", 7.5)
    Pk = st.number_input("Pusat Kaku", 7.0)
    if st.button("HITUNG"):
        e = abs(Pm - Pk)
        ed = 0.05*B
        st.markdown(f'<div class="res-box">e Bawaan: {e:.2f} <br> e Aksidental: <span class="res-val">{ed:.2f}</span></div>', unsafe_allow_html=True)

# --- C. STRUKTUR ATAS (AUTO DETAILING + VISUALISASI) ---
elif module == "8. Pelat Lantai":
    st.header("8. Pelat Lantai (Auto-Detailing)")
    lx = st.number_input("Lx (m)", 3.0)
    ly = st.number_input("Ly (m)", 4.0)
    qp = st.number_input("Beban Total (kg/m2)", 600.0)
    tebal_plat = st.number_input("Tebal Pelat (mm)", 120.0)
    
    if st.button("HITUNG & DESAIN"):
        M = 0.001 * qp * (lx**2) * 25 # kg.m
        Mu_kNm = M / 100
        d = tebal_plat - 20
        Mn = Mu_kNm * 1e6 / 0.8
        Rn = Mn / (1000 * d**2)
        
        try:
            rho_approx = 0.85 * 25 / 240 * (1 - math.sqrt(1 - (2*Rn)/(0.85*25)))
            As_req = rho_approx * 1000 * d
            As_final, tulangan_fix = auto_design_slab(As_req, tebal_plat)
            
            st.markdown(f"""
            <div class="res-box">
                <div>Momen Lapangan: <span class="res-val">{Mu_kNm:.2f} kNm</span></div>
                <div class="steel-res">
                    <div>As Perlu: {As_final:.0f} mm²</div>
                    <div>Rekomendasi Tulangan: <span class="res-steel">{tulangan_fix}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
        except:
            st.error("Tebal Pelat Terlalu Tipis!")

elif module == "9. Lendutan Pelat":
    st.header("9. Lendutan Pelat")
    Lx = st.number_input("Lx (cm)", 300.0)
    h = st.number_input("Tebal h (cm)", 12.0)
    if st.button("CEK"):
        hmin = Lx/28
        stat = "OK" if h >= hmin else "LENDUT"
        st.markdown(f'<div class="res-box">h min: {hmin:.1f} cm <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "10. Desain Balok":
    st.header("10. Desain Balok (Auto-Detailing & Visualisasi)")
    c1, c2 = st.columns(2)
    fc = c1.number_input("fc' (MPa)", 25.0)
    fy = c2.number_input("fy (MPa)", 400.0)
    c3, c4 = st.columns(2)
    b = c3.number_input("b (mm)", 300.0)
    h = c4.number_input("h (mm)", 600.0)
    Mu = st.number_input("Mu (kNm)", 150.0)
    
    if st.button("HITUNG & DESAIN"):
        Mn = Mu * 1e6 / 0.9
        d = h - 50
        Rn = Mn / (b * d**2)
        m = fy / (0.85 * fc)
        
        try:
            rho = (1/m) * (1 - math.sqrt(1 - (2*m*Rn)/fy))
            rho_min = 1.4/fy
            if rho < rho_min: rho = rho_min
            
            As = rho * b * d
            tulangan_utama = auto_design_beam(As, b)
            sengkang = get_practical_stirrup(h)
            
            # Parsing untuk Visualisasi
            try:
                parts = tulangan_utama.split(' D')
                n_bars = int(parts[0])
                d_bars = int(parts[1])
            except:
                n_bars = 4; d_bars = 16

            col_res, col_img = st.columns([1.5, 1])
            with col_res:
                st.markdown(f"""
                <div class="res-box">
                    <div>Rn: {Rn:.2f} MPa</div>
                    <div class="steel-res">
                        <div>As Perlu: {As:.0f} mm² (ρ = {rho:.4f})</div>
                        <div>Tulangan Utama: <span class="res-steel">{tulangan_utama}</span></div>
                        <div>Sengkang: <span class="res-val">{sengkang}</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_img:
                fig = draw_beam_section(b, h, 2, n_bars, d_bars, 8)
                st.pyplot(fig)
        except:
            st.error("Penampang Balok Terlalu Kecil!")

elif module == "11. Torsi Balok":
    st.header("11. Torsi Balok")
    Tu = st.number_input("Tu (kNm)", 10.0)
    Tcr = st.number_input("Tcr (kNm)", 15.0)
    if st.button("CEK"):
        stat = "ABAIKAN" if Tu < 0.25*Tcr else "HITUNG"
        st.markdown(f'<div class="res-box">Status: <span class="res-val">{stat}</span></div>', unsafe_allow_html=True)

elif module == "12. Desain Kolom":
    st.header("12. Desain Kolom (Auto-Check & Visualisasi)")
    b = st.number_input("b (mm)", 500.0)
    h = st.number_input("h (mm)", 500.0)
    fc = st.number_input("fc' (MPa)", 30.0)
    Pu = st.number_input("Pu (kN)", 2500.0)
    
    if st.button("CEK KAPASITAS"):
        Ag = b*h
        Ast_1 = 0.01 * Ag
        Pn = 0.80 * (0.85*fc*(Ag - Ast_1) + 400*Ast_1)
        phiPn = 0.65 * Pn / 1000
        stat = "AMAN" if phiPn > Pu else "BAHAYA"
        
        n_bars = math.ceil(Ast_1 / get_steel_area(19)) 
        if n_bars % 2 != 0: n_bars += 1
        if n_bars < 4: n_bars = 4
        
        col_res, col_img = st.columns([1.5, 1])
        with col_res:
            st.markdown(f"""
            <div class="res-box">
                <div>Kapasitas (ρ=1%): <span class="res-val">{phiPn:.0f} kN</span></div>
                <div>Status: <span class="badge-ok">{stat}</span></div>
                <div class="steel-res">
                    <div>Rekomendasi Tulangan: <span class="res-steel">{n_bars} D19</span></div>
                    <div>Sengkang: Ø10-150</div>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_img:
            fig = draw_column_section(b, h, n_bars, 19)
            st.pyplot(fig)

elif module == "13. Shear Wall":
    st.header("13. Shear Wall")
    fc = st.number_input("fc' (MPa)", 30.0)
    lw = st.number_input("lw (mm)", 4000.0)
    tw = st.number_input("tebal (mm)", 250.0)
    Vu = st.number_input("Vu (kN)", 1500.0)
    if st.button("CEK"):
        Vc = 0.17 * math.sqrt(fc) * tw * (0.8*lw)
        phiVc = 0.75 * Vc / 1000
        stat = "OK" if phiVc > Vu else "FAIL"
        st.markdown(f'<div class="res-box">phiVc: {phiVc:.0f} kN <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "14. Desain Tangga":
    st.header("14. Tangga")
    O = st.number_input("Optr (cm)", 30.0)
    T = st.number_input("Antr (cm)", 17.0)
    if st.button("HITUNG"):
        deg = math.degrees(math.atan(T/O))
        st.markdown(f'<div class="res-box">Sudut: <span class="res-val">{deg:.1f}°</span></div>', unsafe_allow_html=True)

# --- D. PONDASI DANGKAL ---
elif module == "15. Pondasi Telapak":
    st.header("15. Pondasi Telapak")
    P = st.number_input("P (Ton)", 50.0)
    M = st.number_input("M (tm)", 5.0)
    A = st.number_input("A (m2)", 4.0)
    if st.button("HITUNG"):
        W = A * math.sqrt(A) / 6
        s1 = P/A + M/W
        s2 = P/A - M/W
        st.markdown(f'<div class="res-box">Max: {s1:.2f} <br> Min: {s2:.2f}</div>', unsafe_allow_html=True)

elif module == "16. Pondasi Lajur":
    st.header("16. Pondasi Lajur")
    q = st.number_input("q (t/m)", 15.0)
    B = st.number_input("B (m)", 1.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Tegangan: {q/B:.2f} t/m2</div>', unsafe_allow_html=True)

elif module == "17. Sloof (Tie Beam)":
    st.header("17. Sloof")
    q = st.number_input("Beban (kg/m)", 1000.0)
    L = st.number_input("Bentang (m)", 6.0)
    if st.button("HITUNG"):
        Mu = 0.1 * q * L**2
        st.markdown(f"""
        <div class="res-box">
            <div>Mu: {Mu:.0f} kgm</div>
            <div class="steel-res">
                <div>Tulangan Praktis: <span class="res-steel">4 D13</span></div>
                <div>Sengkang: Ø8-200</div>
            </div>
        </div>""", unsafe_allow_html=True)

elif module == "18. Pelat Westergaard":
    st.header("18. Westergaard")
    P = st.number_input("P (kg)", 3000.0)
    h = st.number_input("h (cm)", 20.0)
    if st.button("HITUNG"):
        sig = 3*P / h**2
        stat = "AMAN" if sig < 30 else "FAIL"
        st.markdown(f'<div class="res-box">Tegangan: {sig:.1f} <br> Status: {stat}</div>', unsafe_allow_html=True)

# --- E. PONDASI DALAM ---
elif module == "19. Pile Cap & Pons":
    st.header("19. Pile Cap")
    fc = st.number_input("fc' (MPa)", 25.0)
    Pu = st.number_input("Pu (kN)", 2000.0)
    h = st.number_input("h (mm)", 600.0)
    c = st.number_input("c (mm)", 500.0)
    if st.button("CEK"):
        d = h - 80
        bo = 4*(c+d)
        Vc = 0.33 * math.sqrt(fc) * bo * d
        phiVc = 0.75 * Vc / 1000
        stat = "AMAN" if phiVc > Pu else "JEBOL"
        st.markdown(f'<div class="res-box">phiVc: {phiVc:.0f} kN <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "20. Meyerhof (Daya Dukung)":
    st.header("20. Meyerhof")
    Nb = st.number_input("Nb", 40.0)
    Nav = st.number_input("Nav", 15.0)
    D = st.number_input("D (cm)", 40.0)
    L = st.number_input("L (m)", 12.0)
    if st.button("HITUNG"):
        Ab = 0.25 * math.pi * (D/100)**2
        As = math.pi * (D/100) * L
        Qult = 40 * Nb * Ab + 0.2 * Nav * As 
        st.markdown(f'<div class="res-box">Q Ijin: <span class="res-val">{Qult/3:.1f} Ton</span></div>', unsafe_allow_html=True)

elif module == "21. Momen Tiang":
    st.header("21. Momen Tiang")
    D = st.number_input("D (m)", 0.4)
    Cr = st.number_input("Cr (kg/cm2)", 250.0)
    if st.button("HITUNG"):
        M = 140 * Cr * D**2
        st.markdown(f'<div class="res-box">Mn: {M:.0f} kgm</div>', unsafe_allow_html=True)

elif module == "22. Lateral Tiang":
    st.header("22. Lateral")
    H = st.number_input("H Total (kg)", 4300.0)
    n = st.number_input("n", 3)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">H per Tiang: {safe_div(H,n):.0f} kg</div>', unsafe_allow_html=True)

elif module == "23. Kalendering Hiley":
    st.header("23. Hiley")
    W = st.number_input("W Hammer (t)", 2.0)
    H = st.number_input("H Jatuh (cm)", 100.0)
    S = st.number_input("S (mm)", 5.0)
    K = st.number_input("K (mm)", 10.0)
    ef = st.selectbox("Efisiensi", [0.75, 0.9, 1.0])
    if st.button("HITUNG"):
        R = (ef * W * H) / (S/10 + K/10/2)
        st.markdown(f'<div class="res-box">R Ijin: <span class="res-val">{R/3:.1f} Ton</span></div>', unsafe_allow_html=True)

elif module == "24. Efisiensi Grup":
    st.header("24. Efisiensi Grup")
    m = st.number_input("m", 3)
    n = st.number_input("n", 2)
    D = st.number_input("D (cm)", 40.0)
    s = st.number_input("s (cm)", 120.0)
    if st.button("HITUNG"):
        eg = 1 - math.degrees(math.atan(D/s))/90 * ((n*(m-1)+m*(n-1))/(m*n))
        st.markdown(f'<div class="res-box">Eg: {eg:.3f}</div>', unsafe_allow_html=True)

elif module == "25. Cek Cabut (Uplift)":
    st.header("25. Uplift")
    T = st.number_input("Tarik (t)", 50.0)
    W = st.number_input("Berat (t)", 15.0)
    n = st.number_input("n", 4)
    if st.button("CEK"):
        t1 = (T-W)/n
        stat = "AMAN" if t1 < 10 else "BAHAYA"
        st.markdown(f'<div class="res-box">Tarik/Tiang: {t1:.1f} t <br> Status: {stat}</div>', unsafe_allow_html=True)

# --- F. STRUKTUR KHUSUS ---
elif module == "26. Retaining Wall":
    st.header("26. Retaining Wall")
    H = st.number_input("H (m)", 3.5)
    phi = st.number_input("Sudut Geser", 30.0)
    gamma = st.number_input("Gamma Tanah", 18.0)
    if st.button("HITUNG"):
        Ka = math.tan(math.radians(45 - phi/2))**2
        Pa = 0.5 * gamma * H**2 * Ka
        st.markdown(f'<div class="res-box">Ka: {Ka:.3f} <br> Pa: <span class="res-val">{Pa:.1f} kN/m</span></div>', unsafe_allow_html=True)

elif module == "27. Kolam / Tandon":
    st.header("27. Kolam")
    H = st.number_input("Tinggi Air (m)", 3.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Momen: {(1/6)*10*H**3:.1f} kNm</div>', unsafe_allow_html=True)

elif module == "28. Jembatan":
    st.header("28. Jembatan")
    L = st.number_input("L (m)", 10.0)
    t = st.number_input("t (m)", 0.2)
    q = st.number_input("D (kN/m)", 22.0)
    P = st.number_input("P (kN)", 44.0)
    if st.button("HITUNG"):
        qDL = t*24 + 0.05*22
        M = 1.8 * (0.125*(q+qDL)*L**2 + 0.25*P*L)
        st.markdown(f'<div class="res-box">Momen Ultimate: <span class="res-val">{M:.1f} kNm</span></div>', unsafe_allow_html=True)

elif module == "29. Konversi Tulangan":
    st.header("29. Konversi Tulangan")
    D = st.number_input("D (mm)", 10.0)
    s = st.number_input("s (mm)", 150.0)
    if st.button("KONVERSI"):
        As = 0.25 * math.pi * D**2 * 1000/s
        sbrc = (28.3*1000) / (As * (240/500))
        st.markdown(f'<div class="res-box">Jarak BRC M6: <span class="res-val">{math.floor(sbrc)} mm</span></div>', unsafe_allow_html=True)
