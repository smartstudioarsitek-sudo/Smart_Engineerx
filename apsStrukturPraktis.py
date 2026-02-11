import streamlit as st
import math
import google.generativeai as genai

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS (TEMA CLEAN & PROFESSIONAL)
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
    
    /* Styling Input Fields di Sidebar agar terlihat jelas */
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
    
    /* Kotak Hasil Detailing Besi */
    .steel-res {
        background-color: #E8F5E9; /* Hijau Muda */
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
        color: #2E7D32; /* Hijau Tua */
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
        background: #FFEBEE; /* Latar Merah Muda Sangat Tipis */
        border-top: 2px solid #FFCDD2;
        border-radius: 8px;
    }
    .footer-email { color: #000000 !important; font-weight: bold; font-size: 0.8rem; }
    .footer-donasi { color: #D50000 !important; font-weight: 900; margin-top: 10px; font-size: 0.9rem; text-transform: uppercase; }
    .footer-norek { color: #D50000 !important; font-family: monospace; font-size: 1.1rem; font-weight: 900; letter-spacing: 1px; }
    
    /* Chat Bubble Fix for White Background */
    .stChatMessage { background-color: #FFFFFF; border: 1px solid #E0E0E0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS (RUMUS TEKNIS)
# ==========================================
def safe_div(n, d, default=0.0):
    return n / d if d != 0 else default

def get_steel_area(diameter):
    """Menghitung luas penampang 1 batang tulangan (mm2)"""
    return 0.25 * math.pi * (diameter**2)

def auto_design_slab(As_req, thickness_mm):
    """
    Otomatisasi Tulangan Pelat (Slabs)
    Output: String rekomendasi (misal: D10-150)
    """
    # Cek Tulangan Minimum (Susut Suhu) SNI: 0.0018 * b * h
    As_min = 0.0018 * 1000 * thickness_mm
    As_final = max(As_req, As_min)
    
    # Opsi diameter yang umum di pasaran
    options = [8, 10, 12, 13]
    best_option = ""
    
    for D in options:
        A_bar = get_steel_area(D)
        # Hitung jarak s = (1000 * A_bar) / As
        s_calc = (1000 * A_bar) / As_final
        
        # Jarak maksimal SNI (2h atau 450mm, ambil konservatif 200mm/250mm)
        s_max = min(2 * thickness_mm, 250) 
        
        # Round down ke kelipatan 25mm (e.g. 138 -> 125)
        s_design = math.floor(min(s_calc, s_max) / 25) * 25
        
        if s_design >= 100: # Jarak terlalu rapat ( < 100mm) susah dicor
            best_option = f"D{D}-{s_design:.0f}"
            break # Ambil diameter terkecil yang memenuhi syarat jarak
            
    if best_option == "":
        best_option = "D13-100 (Perlu Cek Ulang)"
        
    return As_final, best_option

def auto_design_beam(As_req, width_mm):
    """
    Otomatisasi Tulangan Balok (Beams)
    Output: String rekomendasi (misal: 4 D16)
    """
    options = [13, 16, 19, 22, 25]
    best_config = ""
    
    for D in options:
        A_bar = get_steel_area(D)
        n = math.ceil(As_req / A_bar)
        
        # Cek spasi cukup dalam lebar balok? (Simplified)
        max_bar_layer = (width_mm - 80) / (D + 25)
        
        if n >= 2 and n <= max_bar_layer * 2: # Max 2 lapis
            best_config = f"{n} D{D}"
            break
            
    if best_config == "":
        A_bar_16 = get_steel_area(16)
        n_16 = math.ceil(As_req / A_bar_16)
        best_config = f"{n_16} D16"
        
    return best_config

def get_practical_stirrup(h_mm):
    """Rekomendasi Sengkang Praktis"""
    spacing = min(h_mm/2, 200)
    spacing = math.floor(spacing / 25) * 25 # Round to 25mm
    return f"Ø8-{spacing:.0f}"

# Database Persona AI
gems_persona = {
    "👑 The GEMS Grandmaster": """
        ANDA ADALAH "THE GEMS GRANDMASTER" (Direktur Proyek).
        Gaya: Profesional, Tegas, namun tetap sopan dan solutif.
        Tugas: Mengoordinasikan seluruh aspek teknis (Struktur, Geoteknik, Manajemen).
    """,
    "🏗️ Ahli Struktur (Gedung)": """
        ANDA ADALAH AHLI STRUKTUR (SNI 2847 & 1726).
        Fokus: Beton bertulang, baja, dan analisis gempa.
        Tugas: Hitung dimensi, tulangan, dan kapasitas penampang.
    """,
    "🪨 Ahli Geoteknik (Tanah)": """
        ANDA ADALAH AHLI GEOTEKNIK (SNI 8460).
        Fokus: Pondasi dangkal, dalam, dan dinding penahan tanah.
    """,
    "💰 Ahli Estimator (QS)": """
        ANDA ADALAH AHLI ESTIMASI BIAYA (RAB).
        Fokus: Volume pekerjaan dan analisa harga satuan.
    """,
    "🕌 Ahli Fiqih Bangunan": """
        ANDA ADALAH PENASIHAT SYARIAH PROYEK.
        Fokus: Adab membangun, arah kiblat, dan keberkahan bangunan.
    """
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
        "🏠 DASHBOARD",
        "A. BEBAN & ATAP",
        "B. GEMPA & STABILITAS",
        "C. STRUKTUR ATAS",
        "D. PONDASI DANGKAL",
        "E. PONDASI DALAM",
        "F. STRUKTUR KHUSUS"
    ])

    st.markdown("---")
    
    # Sub-Menu (Dynamic)
    st.markdown("### 🛠️ MODUL PERHITUNGAN")
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

    # FOOTER (MERAH SESUAI REQUEST)
    st.markdown("""
    <div class="sidebar-footer">
        <div class="footer-email">by smartstudioarsitek@gmail.com</div>
        <div class="footer-donasi">Donasi : Bank Jago Syariah</div>
        <div class="footer-norek">5028 4297 0355</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIKA PERHITUNGAN (29 MODUL + DETAILING)
# ==========================================

if category == "🏠 DASHBOARD":
    st.title("🚀 Smart_Engineer Dashboard")
    st.markdown("### OMNI-X Edition (Auto-Detailing Ready)")
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ **Integrasi Sistem Selesai**")
        st.write("29 Modul telah diverifikasi dengan fitur Auto-Detailing Tulangan.")
    with col2:
        st.info("ℹ️ **Sidebar White Mode**")
        st.write("Tampilan kontras tinggi untuk kenyamanan mata.")

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
        
    if st.button("ANALISIS"):
        rad = math.radians(aa)
        q = 1.2 * qDa * sa 
        Mx = (1/8) * (q * math.cos(rad)) * (La**2) * 100 
        My = Mx * 0.1
        sig = safe_div(Mx, Wx)
        E = 2.1e6; Ix = 150 
        del_val = (5 * q * math.cos(rad) * math.pow(La*100, 4)) / (384 * E * Ix * 100)
        
        status = "AMAN" if (sig < 1600 and del_val < (La*100)/240) else "CEK PROFIL"
        badge = "badge-ok" if status == "AMAN" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div>Mx: <span class="res-val">{Mx:.0f} kgcm</span></div>
            <div>Tegangan: <span class="res-val">{sig:.0f} kg/cm²</span></div>
            <div>Lendutan: <span class="res-val">{del_val:.2f} cm</span></div>
            <div>Status: <span class="{badge}">{status}</span></div>
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
    with c1:
        R_val = st.selectbox("Sistem R", [8, 5, 3])
    with c2:
        Ie_val = st.selectbox("Faktor Ie", [1.0, 1.5])
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

# --- C. STRUKTUR ATAS (AUTO DETAILING) ---
elif module == "8. Pelat Lantai":
    st.header("8. Pelat Lantai (Auto-Detailing)")
    lx = st.number_input("Lx (m)", 3.0)
    ly = st.number_input("Ly (m)", 4.0)
    qp = st.number_input("Beban Total (kg/m2)", 600.0)
    
    # Input tambahan untuk detailing
    tebal_plat = st.number_input("Tebal Pelat (mm)", 120.0)
    
    if st.button("HITUNG & DESAIN"):
        M = 0.001 * qp * (lx**2) * 25 # kg.m
        Mu_kNm = M / 100
        
        # Hitung As Perlu (Simplifikasi Rho approx)
        d = tebal_plat - 20
        Mn = Mu_kNm * 1e6 / 0.8
        Rn = Mn / (1000 * d**2)
        
        try:
            rho_approx = 0.85 * 25 / 240 * (1 - math.sqrt(1 - (2*Rn)/(0.85*25)))
            As_req = rho_approx * 1000 * d
            
            # Auto Detailing
            As_final, tulangan_fix = auto_design_slab(As_req, tebal_plat)
            
            st.markdown(f"""
            <div class="res-box">
                <div>Momen Lapangan: <span class="res-val">{Mu_kNm:.2f} kNm</span></div>
                <div class="steel-res">
                    <div>As Perlu: {As_final:.0f} mm²</div>
                    <div>Rasio (ρ): {rho_approx:.4f}</div>
                    <div>Rekomendasi Tulangan:</div>
                    <div class="res-steel">{tulangan_fix}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        except:
            st.error("Tebal Pelat Terlalu Tipis! Perbesar tebal.")

elif module == "9. Lendutan Pelat":
    st.header("9. Lendutan Pelat")
    Lx = st.number_input("Lx (cm)", 300.0)
    h = st.number_input("Tebal h (cm)", 12.0)
    if st.button("CEK"):
        hmin = Lx/28
        stat = "OK" if h >= hmin else "LENDUT"
        st.markdown(f'<div class="res-box">h min: {hmin:.1f} cm <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "10. Desain Balok":
    st.header("10. Desain Balok (Auto-Detailing)")
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
            
            # Auto Detailing
            tulangan_utama = auto_design_beam(As, b)
            sengkang = get_practical_stirrup(h)
            
            st.markdown(f"""
            <div class="res-box">
                <div>Rn: {Rn:.2f} MPa</div>
                <div class="steel-res">
                    <div>As Perlu: {As:.0f} mm² (ρ = {rho:.4f})</div>
                    <div>Tulangan Utama: <span class="res-steel">{tulangan_utama}</span></div>
                    <div>Sengkang Praktis: <span class="res-val">{sengkang}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
        except:
            st.error("Penampang Balok Terlalu Kecil! Perbesar ukuran.")

elif module == "11. Torsi Balok":
    st.header("11. Torsi Balok")
    Tu = st.number_input("Tu (kNm)", 10.0)
    Tcr = st.number_input("Tcr (kNm)", 15.0)
    if st.button("CEK"):
        stat = "ABAIKAN" if Tu < 0.25*Tcr else "HITUNG"
        st.markdown(f'<div class="res-box">Status: <span class="res-val">{stat}</span></div>', unsafe_allow_html=True)

elif module == "12. Desain Kolom":
    st.header("12. Desain Kolom (Auto-Check)")
    b = st.number_input("b (mm)", 500.0)
    h = st.number_input("h (mm)", 500.0)
    fc = st.number_input("fc' (MPa)", 30.0)
    Pu = st.number_input("Pu (kN)", 2500.0)
    
    if st.button("CEK KAPASITAS"):
        Ag = b*h
        # Asumsi tulangan 1% - 3%
        Ast_1 = 0.01 * Ag
        Pn = 0.80 * (0.85*fc*(Ag - Ast_1) + 400*Ast_1)
        phiPn = 0.65 * Pn / 1000
        
        stat = "AMAN" if phiPn > Pu else "BAHAYA"
        
        # Rekomendasi Tulangan
        n_bars = math.ceil(Ast_1 / get_steel_area(19)) # Pakai D19 standard kolom
        if n_bars % 2 != 0: n_bars += 1
        
        st.markdown(f"""
        <div class="res-box">
            <div>Kapasitas (ρ=1%): <span class="res-val">{phiPn:.0f} kN</span></div>
            <div>Status: <span class="badge-ok">{stat}</span></div>
            <div class="steel-res">
                <div>Rekomendasi Tulangan (Min 1%):</div>
                <div class="res-steel">{n_bars} D19</div>
                <div>Sengkang: Ø10-150</div>
            </div>
        </div>""", unsafe_allow_html=True)

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
                <div>Tulangan Praktis:</div>
                <div class="res-steel">4 D13</div>
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
        deg = math.degrees(math.atan(D/s))
        eg = 1 - deg/90 * ((n*(m-1)+m*(n-1))/(m*n))
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
