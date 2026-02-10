import streamlit as st
import math
import google.generativeai as genai

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS (TEMA WHITE-CLEAN & HIGH CONTRAST)
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
    /* Main Background - Abu-abu sangat muda/Netral agar mata nyaman */
    .stApp { background-color: #F8F9FA; }
    
    /* --- SIDEBAR STYLING (WHITE MODE) --- */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important; /* Sidebar Putih Mutlak */
        border-right: 1px solid #E0E0E0; /* Garis pemisah tipis */
    }
    
    /* MEMAKSA SEMUA TEKS DI SIDEBAR MENJADI HITAM PEKAT */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #000000 !important;
        font-weight: 500;
    }
    
    /* Styling Input Fields di Sidebar agar kontras */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        color: #000000 !important;
        background-color: #F5F5F5 !important;
        border: 1px solid #CCCCCC;
    }

    /* --- MAIN CONTENT STYLING --- */
    h1, h2, h3 {
        color: #0D47A1; /* Navy Blue untuk Judul Konten */
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
# 2. HELPER FUNCTIONS & PERSONA AI
# ==========================================
def safe_div(n, d, default=0.0):
    return n / d if d != 0 else default

gems_persona = {
    "👑 The GEMS Grandmaster": """
        ANDA ADALAH "THE GEMS GRANDMASTER" (Direktur Proyek).
        Gaya: Profesional, Tegas, namun tetap sopan dan solutif.
        Tugas: Mengoordinasikan seluruh aspek teknis (Struktur, Geoteknik, Manajemen).
        Instruksi: Jawab pertanyaan user dengan data teknis yang akurat sesuai SNI.
    """,
    "🏗️ Ahli Struktur (Gedung)": """
        ANDA ADALAH AHLI STRUKTUR (SNI 2847 & 1726).
        Fokus: Beton bertulang, baja, dan analisis gempa.
        Tugas: Hitung dimensi, tulangan, dan kapasitas penampang.
    """,
    "🪨 Ahli Geoteknik (Tanah)": """
        ANDA ADALAH AHLI GEOTEKNIK (SNI 8460).
        Fokus: Pondasi dangkal, dalam, dan dinding penahan tanah.
        Tugas: Analisis daya dukung tanah berdasarkan N-SPT atau Sondir.
    """,
    "🌊 Ahli Sumber Daya Air": """
        ANDA ADALAH AHLI HIDROLOGI & HIDROLIKA.
        Fokus: Drainase, kolam, dan bangunan air.
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
    # Logo / Branding (Text Biru Tua di atas Putih)
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
# 4. LOGIKA PERHITUNGAN (29 MODUL VERIFIKASI)
# ==========================================

if category == "🏠 DASHBOARD":
    st.title("🚀 Smart_Engineer Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ **Integrasi HTML Original Berhasil**")
        st.write("Semua 29 Modul dari file SMARTSTURTUR 10.txt telah diporting ke Python.")
    with col2:
        st.info("ℹ️ **Mode Sidebar: Putih (High Contrast)**")
        st.write("Background Putih, Teks Hitam, Footer Merah.")

# --- A. BEBAN & ATAP ---
elif module == "1. Analisis Beban (Wt)":
    st.header("1. Analisis Beban (Wt)")
    st.caption("Referensi: SNI 1726 (Beban Gempa)")
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
    
    if st.button("HITUNG BERAT TOTAL (Wt)"):
        # Logika: W = A * (DL + 0.3*LL)
        Wa = A1 * (D1 + 0.3*L1)
        Wt_typ = A2 * (D2 + 0.3*L2) * N_typ
        Wt_tot = (Wa + Wt_typ)/100 # Original logic /100 -> to kN (approx)
        
        st.markdown(f"""
        <div class="res-box">
            <div>Berat Atap (Wa): <span class="res-val">{Wa:,.0f} kg</span></div>
            <div>Berat Tipikal (Wt_typ): <span class="res-val">{Wt_typ:,.0f} kg</span></div>
            <hr>
            <div>TOTAL SEISMIK (Wt): <span class="res-val">{Wt_tot:.2f} kN</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "2. Konstruksi Atap":
    st.header("2. Konstruksi Atap")
    st.caption("Metode ASD (Allowable Stress Design)")
    c1, c2 = st.columns(2)
    with c1:
        La = st.number_input("Jarak Kuda-kuda (L) [m]", 4.0)
        sa = st.number_input("Jarak Gording (s) [m]", 1.2)
        aa = st.number_input("Sudut (α) [°]", 20.0)
        Wx = st.number_input("Profil C (Wx) [cm3]", 38.0)
    with c2:
        qDa = st.number_input("Beban Mati (qDL) [kg/m2]", 25.0)
        Pa = st.number_input("Beban Hidup (P) [kg]", 100.0)
        E_val = st.number_input("Modulus Elastisitas E [kg/cm2]", 2100000.0)
        Ix_val = st.number_input("Inersia Ix [cm4]", 150.0)
        
    if st.button("ANALISIS GORDING"):
        rad = math.radians(aa)
        q = 1.2 * qDa * sa # Logic JS Original
        # Momen ASD (Service)
        # q_perp dan P_perp
        q_perp = q * math.cos(rad) # kg/m
        P_perp = Pa * math.cos(rad) # kg
        
        # Mx = 1/8 q L^2 + 1/4 P L
        M_q = (1/8) * q_perp * (La**2) * 100 # kgcm
        M_P = (1/4) * P_perp * La * 100 # kgcm
        Mx = M_q + M_P
        My = Mx * 0.1 # Approx weak axis
        
        sig = safe_div(Mx, Wx)
        
        # Deflection 
        L_cm = La * 100
        q_perp_cm = q_perp / 100 # kg/cm
        del_q = (5 * q_perp_cm * math.pow(L_cm, 4)) / (384 * E_val * Ix_val)
        del_P = (1 * P_perp * math.pow(L_cm, 3)) / (48 * E_val * Ix_val)
        del_val = del_q + del_P
        
        status = "AMAN" if (sig < 1600 and del_val < (L_cm/240)) else "CEK PROFIL"
        badge = "badge-ok" if status == "AMAN" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div>Momen Mx (Kuat): <span class="res-val">{Mx:.0f} kgcm</span></div>
            <div>Momen My (Lemah): <span class="res-val">{My:.0f} kgcm</span></div>
            <div>Tegangan (σ): <span class="res-val">{sig:.0f} kg/cm²</span></div>
            <div>Lendutan: <span class="res-val">{del_val:.2f} cm</span></div>
            <div>Status: <span class="{badge}">{status}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "3. Tributary Area":
    st.header("3. Tributary Area")
    Pt = st.number_input("P (m)", 4.0)
    Lt = st.number_input("L (m)", 3.0)
    qt = st.number_input("q Pelat (kg/m²)", 120.0)
    if st.button("HITUNG BEBAN"):
        Qt = Pt * Lt * qt
        st.markdown(f'<div class="res-box">Total Beban: <span class="res-val">{Qt:,.0f} kg</span></div>', unsafe_allow_html=True)

elif module == "4. Pusat Massa (COG)":
    st.header("4. Pusat Massa (COG)")
    c1, c2 = st.columns(2)
    with c1:
        Smx = st.number_input("Σ Momen Statis X", 50000.0)
        Smy = st.number_input("Σ Momen Statis Y", 30000.0)
    with c2:
        Wi = st.number_input("Berat Total Struktur (Wi)", 5000.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Xm: <span class="res-val">{safe_div(Smx,Wi):.2f} m</span> <br> Ym: <span class="res-val">{safe_div(Smy,Wi):.2f} m</span></div>', unsafe_allow_html=True)

# --- B. GEMPA (VERIFIKASI INPUT R & Ie) ---
elif module == "5. Respon Spektrum":
    st.header("5. Gempa SNI 1726 (Updated)")
    c1, c2 = st.columns(2)
    with c1:
        Ss = st.number_input("Ss (Peta Gempa)", 0.9)
        S1 = st.number_input("S1 (Peta Gempa)", 0.4)
    with c2:
        # PENTING: Input R dan Ie sesuai file asli
        R_val = st.selectbox("Sistem Struktur (R)", 
                             options=[8, 5, 3], 
                             format_func=lambda x: f"R={x} (SRPMK/SRPMM/Biasa)")
        Ie_val = st.selectbox("Faktor Keutamaan (Ie)", 
                              options=[1.0, 1.5], 
                              format_func=lambda x: f"Ie={x} (Rumah/RS)")
    
    Wt = st.number_input("Berat Seismik Wt [kN]", 5000.0)
    
    if st.button("HITUNG BASE SHEAR (V)"):
        # Logika: Sds = 2/3 Ss (Simplified)
        # V = (Sds * Ie / R) * Wt
        Sds = 0.666 * Ss
        V = (Sds * Ie_val / R_val) * Wt 
        
        st.markdown(f"""
        <div class="res-box">
            <div>SDS: <span class="res-val">{Sds:.2f}</span></div>
            <div>Koefisien Gempa (Cs): <span class="res-val">{(Sds*Ie_val/R_val):.4f}</span></div>
            <hr>
            <div>Base Shear V: <span class="res-val">{V:.0f} kN</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "6. Drift & Simpangan":
    st.header("6. Drift & Simpangan")
    hs = st.number_input("Tinggi Tingkat (mm)", 4000.0)
    de = st.number_input("Simpangan Elastis (mm)", 15.0)
    if st.button("CEK DRIFT"):
        # Asumsi Cd approx 5.5
        d = 5.5 * de
        allow = 0.02 * hs
        stat = "AMAN" if d < allow else "BAHAYA"
        st.markdown(f'<div class="res-box">Simpangan (δ): {d:.1f} mm <br> Ijin (0.02H): {allow:.1f} mm <br> Status: <span class="badge-ok">{stat}</span></div>', unsafe_allow_html=True)

elif module == "7. Eksentrisitas":
    st.header("7. Eksentrisitas")
    B = st.number_input("Lebar B (m)", 15.0)
    Pm = st.number_input("Pusat Massa", 7.5)
    Pk = st.number_input("Pusat Kaku", 7.0)
    if st.button("HITUNG"):
        e = abs(Pm - Pk)
        ed = 0.05 * B # Accidental Torsion SNI
        st.markdown(f'<div class="res-box">e Bawaan: {e:.2f} m <br> e Aksidental (0.05B): <span class="res-val">{ed:.2f} m</span></div>', unsafe_allow_html=True)

# --- C. STRUKTUR ATAS ---
elif module == "8. Pelat Lantai":
    st.header("8. Pelat Lantai")
    c1, c2 = st.columns(2)
    lx = c1.number_input("Lx [m]", 3.0)
    ly = c2.number_input("Ly [m]", 4.0)
    qp = st.number_input("Beban Total [kg/m²]", 600.0)
    if st.button("HITUNG MOMEN"):
        Mlx = 0.001 * qp * (lx**2) * 25 # Coeff PBI
        st.markdown(f'<div class="res-box">Momen Lap (Mlx): <span class="res-val">{(Mlx/100):.2f} kNm</span> <br> Tulangan: D8-150</div>', unsafe_allow_html=True)

elif module == "9. Lendutan Pelat":
    st.header("9. Lendutan Pelat")
    Lx = st.number_input("Bentang Lx (cm)", 300.0)
    h = st.number_input("Tebal h (cm)", 12.0)
    if st.button("CEK SYARAT"):
        hmin = Lx / 28 # SNI approx
        stat = "OK" if h >= hmin else "LENDUT"
        st.markdown(f'<div class="res-box">h min: {hmin:.1f} cm <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "10. Desain Balok":
    st.header("10. Desain Balok (SNI Presisi)")
    c1, c2 = st.columns(2)
    fc = c1.number_input("fc' (MPa)", 25.0)
    fy = c2.number_input("fy (MPa)", 400.0)
    c3, c4 = st.columns(2)
    b = c3.number_input("b (mm)", 300.0)
    h = c4.number_input("h (mm)", 600.0)
    Mu = st.number_input("Mu (kNm)", 150.0)
    
    if st.button("HITUNG TULANGAN"):
        Mn = Mu * 1e6 / 0.9
        d = h - 50
        Rn = Mn / (b * d**2)
        m = fy / (0.85 * fc)
        rho = (1/m) * (1 - math.sqrt(1 - (2*m*Rn)/fy))
        As = rho * b * d
        st.markdown(f"""
        <div class="res-box">
            <div>Rn: {Rn:.2f} MPa</div>
            <div>Rho Perlu: <span class="res-val">{rho:.5f}</span></div>
            <div>As Perlu: <span class="res-val">{As:.0f} mm²</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "11. Torsi Balok":
    st.header("11. Torsi Balok")
    Tu = st.number_input("Tu (kNm)", 10.0)
    Tcr = st.number_input("Tcr (kNm)", 15.0)
    if st.button("CEK TORSI"):
        stat = "ABAIKAN" if Tu < 0.25*Tcr else "HITUNG TULANGAN"
        st.markdown(f'<div class="res-box">Status: <span class="res-val">{stat}</span></div>', unsafe_allow_html=True)

elif module == "12. Desain Kolom":
    st.header("12. Desain Kolom")
    c1, c2 = st.columns(2)
    fc = c1.number_input("fc' (MPa)", 30.0)
    fy = c2.number_input("fy (MPa)", 400.0)
    c3, c4 = st.columns(2)
    b = c3.number_input("b (mm)", 500.0)
    h = c4.number_input("h (mm)", 500.0)
    Pu = st.number_input("Pu (kN)", 2500.0)
    
    if st.button("CEK KAPASITAS"):
        Ag = b*h
        Ast = 0.01 * Ag
        Pn = 0.85 * fc * (Ag - Ast) + fy * Ast
        phiPn = 0.65 * 0.8 * Pn / 1000
        stat = "AMAN" if phiPn > Pu else "BAHAYA"
        st.markdown(f'<div class="res-box">Kapasitas φPn: <span class="res-val">{phiPn:.0f} kN</span> <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "13. Shear Wall":
    st.header("13. Shear Wall")
    fc = st.number_input("fc' (MPa)", 30.0)
    lw = st.number_input("lw (mm)", 4000.0)
    tw = st.number_input("tebal (mm)", 250.0)
    Vu = st.number_input("Vu (kN)", 1500.0)
    if st.button("CEK GESER"):
        Vc = 0.17 * math.sqrt(fc) * tw * (0.8*lw)
        phiVc = 0.75 * Vc / 1000
        stat = "OK" if phiVc > Vu else "FAIL"
        st.markdown(f'<div class="res-box">φVc: {phiVc:.0f} kN <br> Status: {stat}</div>', unsafe_allow_html=True)

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
    P = st.number_input("P [Ton]", 50.0)
    M = st.number_input("M [tm]", 5.0)
    A = st.number_input("A [m²]", 4.0)
    if st.button("HITUNG TEGANGAN"):
        W = A * math.sqrt(A) / 6
        s1 = P/A + M/W
        s2 = P/A - M/W
        st.markdown(f'<div class="res-box">σ Max: {s1:.2f} <br> σ Min: {s2:.2f}</div>', unsafe_allow_html=True)

elif module == "16. Pondasi Lajur":
    st.header("16. Pondasi Lajur")
    q = st.number_input("q [t/m]", 15.0)
    B = st.number_input("B [m]", 1.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Tegangan: {q/B:.2f} t/m²</div>', unsafe_allow_html=True)

elif module == "17. Sloof (Tie Beam)":
    st.header("17. Sloof")
    q = st.number_input("Beban [kg/m]", 1000.0)
    L = st.number_input("Bentang [m]", 6.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Mu: {0.1*q*L**2:.0f} kgm</div>', unsafe_allow_html=True)

elif module == "18. Pelat Westergaard":
    st.header("18. Westergaard")
    P = st.number_input("Beban Roda [kg]", 3000.0)
    h = st.number_input("Tebal h [cm]", 20.0)
    if st.button("HITUNG"):
        sig = 3*P / h**2
        st.markdown(f'<div class="res-box">Tegangan: <span class="res-val">{sig:.1f} kg/cm²</span></div>', unsafe_allow_html=True)

# --- E. PONDASI DALAM ---
elif module == "19. Pile Cap & Pons":
    st.header("19. Pile Cap & Pons")
    fc = st.number_input("fc' (MPa)", 25.0)
    Pu = st.number_input("Pu (kN)", 2000.0)
    h = st.number_input("h Pilecap (mm)", 600.0)
    c = st.number_input("Lebar Kolom (mm)", 500.0)
    if st.button("CEK PONS"):
        d = h - 80
        bo = 4*(c+d)
        Vc = 0.33 * math.sqrt(fc) * bo * d
        phiVc = 0.75 * Vc / 1000
        stat = "AMAN" if phiVc > Pu else "JEBOL"
        st.markdown(f'<div class="res-box">φVc: {phiVc:.0f} kN <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "20. Meyerhof (Daya Dukung)":
    st.header("20. Meyerhof (N-SPT)")
    Nb = st.number_input("Nb", 40.0)
    Nav = st.number_input("Nav", 15.0)
    D = st.number_input("D (cm)", 40.0)
    L = st.number_input("L (m)", 12.0)
    if st.button("HITUNG Qall"):
        Ab = 0.25 * math.pi * (D/100)**2
        As = math.pi * (D/100) * L
        Qult = 40*Nb*Ab + 0.2*Nav*As # Empiris
        st.markdown(f'<div class="res-box">Q Ultimate: {Qult:.1f} Ton <br> Q Ijin (FK=3): <span class="res-val">{Qult/3:.1f} Ton</span></div>', unsafe_allow_html=True)

elif module == "21. Momen Tiang":
    st.header("21. Momen Tiang")
    D = st.number_input("Diameter D [m]", 0.4)
    Cr = st.number_input("Cr Beton [kg/cm²]", 250.0)
    if st.button("HITUNG KAPASITAS"):
        M = 140 * Cr * D**2
        st.markdown(f'<div class="res-box">Mn Approx: <span class="res-val">{M:.0f} kgm</span></div>', unsafe_allow_html=True)

elif module == "22. Lateral Tiang":
    st.header("22. Lateral Tiang")
    H = st.number_input("H Total [kg]", 4300.0)
    n = st.number_input("Jumlah Tiang", 3)
    if st.button("CEK"):
        st.markdown(f'<div class="res-box">H per Tiang: {H/n:.0f} kg</div>', unsafe_allow_html=True)

elif module == "23. Kalendering Hiley":
    st.header("23. Hiley Formula")
    W = st.number_input("W Hammer (Ton)", 2.0)
    H = st.number_input("H Jatuh (cm)", 100.0)
    S = st.number_input("Set (mm)", 5.0)
    K = st.number_input("Rebound (mm)", 10.0)
    ef = st.selectbox("Efisiensi", [0.75, 0.9, 1.0])
    if st.button("HITUNG R"):
        R = (ef * W * H) / (S/10 + K/10/2)
        st.markdown(f'<div class="res-box">R Ultimate: {R:.1f} Ton <br> R Ijin: <span class="res-val">{R/3:.1f} Ton</span></div>', unsafe_allow_html=True)

elif module == "24. Efisiensi Grup":
    st.header("24. Efisiensi Grup")
    m = st.number_input("Baris m", 3)
    n = st.number_input("Baris n", 2)
    D = st.number_input("D (cm)", 40.0)
    s = st.number_input("s (cm)", 120.0)
    if st.button("HITUNG"):
        deg = math.degrees(math.atan(D/s))
        eg = 1 - deg/90 * ((n*(m-1)+m*(n-1))/(m*n))
        st.markdown(f'<div class="res-box">Efisiensi: <span class="res-val">{eg:.3f}</span></div>', unsafe_allow_html=True)

elif module == "25. Cek Cabut (Uplift)":
    st.header("25. Uplift")
    T = st.number_input("Tarik Total (Ton)", 50.0)
    W = st.number_input("Berat Sendiri (Ton)", 15.0)
    n = st.number_input("Jumlah Tiang", 4)
    if st.button("CEK"):
        t1 = (T-W)/n
        stat = "AMAN" if t1 < 10 else "BAHAYA"
        st.markdown(f'<div class="res-box">Tarik per Tiang: {t1:.1f} Ton <br> Status: {stat}</div>', unsafe_allow_html=True)

# --- F. STRUKTUR KHUSUS ---
elif module == "26. Retaining Wall":
    st.header("26. Retaining Wall")
    H = st.number_input("Tinggi H (m)", 3.5)
    phi = st.number_input("Sudut Geser", 30.0)
    gamma = st.number_input("Berat Jenis Tanah (kN/m3)", 18.0)
    if st.button("HITUNG"):
        Ka = math.tan(math.radians(45-phi/2))**2
        Pa = 0.5 * gamma * H**2 * Ka
        st.markdown(f'<div class="res-box">Ka: {Ka:.3f} <br> Pa: <span class="res-val">{Pa:.1f} kN/m</span></div>', unsafe_allow_html=True)

elif module == "27. Kolam / Tandon":
    st.header("27. Kolam")
    H = st.number_input("Tinggi Air (m)", 3.0)
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Momen: <span class="res-val">{(1/6)*10*H**3:.1f} kNm</span></div>', unsafe_allow_html=True)

elif module == "28. Jembatan":
    st.header("28. Jembatan Sederhana")
    st.caption("Ref: SNI 1725:2016")
    L = st.number_input("Bentang L (m)", 10.0)
    t = st.number_input("Tebal Pelat (m)", 0.2)
    ta = st.number_input("Aspal (m)", 0.05)
    qD = st.number_input("Beban Jalur D (kN/m)", 9.0)
    PT = st.number_input("Beban Truk T (kN)", 112.5)
    
    if st.button("HITUNG TOTAL"):
        qDL = t*24 + ta*22
        Mu_DL = 1.3 * (1/8) * qDL * L**2
        Mu_Lane = 1.8 * (1/8) * qD * L**2
        Mu_Truck = 1.8 * (1/4) * PT * L
        M_tot = Mu_DL + Mu_Lane + Mu_Truck
        st.markdown(f'<div class="res-box">Berat Sendiri: {qDL:.1f} kN/m <br> Momen Ultimate: <span class="res-val">{M_tot:.1f} kNm</span></div>', unsafe_allow_html=True)

elif module == "29. Konversi Tulangan":
    st.header("29. Konversi BRC")
    D = st.number_input("D Ulir (mm)", 10.0)
    s = st.number_input("Jarak s (mm)", 150.0)
    if st.button("KONVERSI"):
        As = 0.25 * math.pi * D**2 * 1000/s
        sbrc = (28.3*1000) / (As * (240/500))
        st.markdown(f'<div class="res-box">Jarak BRC M6: <span class="res-val">{math.floor(sbrc)} mm</span></div>', unsafe_allow_html=True)
