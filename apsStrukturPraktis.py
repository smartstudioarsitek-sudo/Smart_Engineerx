import streamlit as st
import math
import google.generativeai as genai

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS (TEMA CERAH & KONTRAS)
# ==========================================
st.set_page_config(
    page_title="Smart_Engineer OMNI-X",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Bright Blue Sidebar & Clean Content
st.markdown("""
    <style>
    /* Main Background - Abu-abu sangat muda agar mata nyaman */
    .stApp { background-color: #F5F7F9; }
    
    /* SIDEBAR STYLING - REVISI WARNA LEBIH CERAH */
    section[data-testid="stSidebar"] {
        background-color: #1565C0; /* Biru Engineering Cerah */
        color: #FFFFFF; /* Teks Putih Mutlak */
    }
    
    /* Memastikan semua teks di sidebar putih & kontras */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }
    
    /* Input fields di sidebar agar tetap terlihat jelas */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select {
        color: #333333 !important;
        background-color: #FFFFFF !important;
    }

    /* Headers di Main Content */
    h1, h2, h3 {
        color: #0D47A1;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
    }
    
    /* Result Box (Card Style) */
    .res-box {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        border-left: 8px solid #FF6F00; /* Amber Accent */
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #263238;
    }
    
    .res-label {
        font-weight: 600;
        color: #546E7A;
        font-size: 0.95rem;
        display: block;
        margin-bottom: 2px;
    }
    
    .res-val {
        font-weight: 800;
        color: #1565C0;
        font-size: 1.3rem;
        font-family: 'Consolas', monospace;
    }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #1565C0, #0277BD);
        color: white;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(21, 101, 192, 0.3);
        background: linear-gradient(135deg, #FF6F00, #F57C00); /* Amber Hover */
    }

    /* Status Badges */
    .badge-ok { background-color: #2E7D32; color: white; padding: 5px 12px; border-radius: 15px; font-size: 0.85rem; font-weight: bold; letter-spacing: 1px;}
    .badge-no { background-color: #C62828; color: white; padding: 5px 12px; border-radius: 15px; font-size: 0.85rem; font-weight: bold; letter-spacing: 1px;}
    .badge-warn { background-color: #F9A825; color: #263238; padding: 5px 12px; border-radius: 15px; font-size: 0.85rem; font-weight: bold; letter-spacing: 1px;}
    
    /* Divider */
    hr { margin: 10px 0; border-top: 1px dashed #B0BEC5; }
    
    /* Chat Message Style */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS & PERSONA AI
# ==========================================
def safe_div(n, d, default=0.0):
    """Mencegah error pembagian nol"""
    return n / d if d != 0 else default

# Database Persona AI (GEMS BRAIN - REVISI HUMANIS & ISLAMI)
gems_persona = {
    "👑 The GEMS Grandmaster": """
        ANDA ADALAH "THE GEMS GRANDMASTER" (Direktur Utama yang Bijaksana).
        
        KARAKTER:
        - Memulai dengan salam (Assalamu'alaikum) dan Bismillah.
        - Menggabungkan kecerdasan teknis (Science) dengan kebijaksanaan spiritual (Hikmah).
        - Memandang setiap proyek bangunan sebagai "Amanah" yang harus kuat, aman, dan bermanfaat.
        - Gaya bicara: Berwibawa namun mengayomi (seperti Kiai atau Profesor sepuh). Tidak galak, tapi tegas dalam prinsip keamanan struktur.
        
        KAPABILITAS:
        - Menguasai integrasi Struktur, Geoteknik, Manajemen, dan Hukum.
        - Jika user bingung, bimbing pelan-pelan.
    """,
    "🏗️ Ahli Struktur (Gedung)": """
        ANDA ADALAH PRINCIPAL STRUCTURAL ENGINEER.
        Fokus: Keamanan & Kekuatan (SNI 2847 & SNI 1726).
        Gaya: Profesional, detail, dan teliti. Selalu mengingatkan bahwa "Struktur yang kuat menyelamatkan nyawa".
        Tugas: Analisis beban, dimensi, dan penulangan dengan presisi.
    """,
    "🪨 Ahli Geoteknik (Tanah)": """
        ANDA ADALAH SENIOR GEOTECHNICAL ENGINEER.
        Fokus: Pondasi & Tanah (SNI 8460).
        Gaya: Hati-hati dan waspada. Sering mengingatkan "Bangunan kuat dimulai dari tanah yang baik".
        Tugas: Analisis Sondir/SPT dan daya dukung.
    """,
    "💰 Ahli Estimator (QS)": """
        ANDA ADALAH CHIEF QUANTITY SURVEYOR.
        Fokus: Efisiensi & Amanah Anggaran.
        Gaya: Transparan dan jujur. Mengingatkan agar "Jangan mengurangi takaran/spek demi keuntungan".
        Tugas: Hitung RAB dan volume material.
    """,
    "🕌 Ahli Fiqih Bangunan": """
        ANDA ADALAH USTADZ & AHLI FIQIH BANGUNAN.
        Fokus: Keberkahan, Arah Kiblat, Privasi (Hijab antar ruang), dan Adab Tetangga.
        Gaya: Lembut, menyejukkan, sering mengutip dalil atau kaidah fiqih muamalah yang relevan dengan konstruksi.
        Tugas: Memberi nasihat agar bangunan membawa berkah bagi penghuninya.
    """
}

# ==========================================
# 3. SIDEBAR NAVIGATION & AI CHAT
# ==========================================
with st.sidebar:
    # Logo Area dengan Background Transparan Putih tipis
    st.markdown("""
    <div style="text-align: center; padding: 20px 10px; background: rgba(255,255,255,0.15); border-radius: 12px; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.2);">
        <h2 style="margin:0; font-size: 1.6rem; letter-spacing: 1px; color: #FFFFFF; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">Smart_Engineer</h2>
        <div style="color:#FFD54F; font-weight:800; letter-spacing:3px; font-size:0.75rem; margin-top:5px; text-transform:uppercase;">OMNI-X ULTIMATE</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- MENU UTAMA ---
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
    
    # --- SUB MENU (DYNAMIC) ---
    st.markdown("### 🛠️ PILIH MODUL")
    module = None
    if category == "A. BEBAN & ATAP":
        module = st.radio("Modul Tersedia:", ["1. Analisis Beban (Wt)", "2. Konstruksi Atap", "3. Tributary Area", "4. Pusat Massa (COG)"])
    elif category == "B. GEMPA & STABILITAS":
        module = st.radio("Modul Tersedia:", ["5. Respon Spektrum", "6. Drift & Simpangan", "7. Eksentrisitas"])
    elif category == "C. STRUKTUR ATAS":
        module = st.radio("Modul Tersedia:", ["8. Pelat Lantai", "9. Lendutan Pelat", "10. Desain Balok", "11. Torsi Balok", "12. Desain Kolom", "13. Shear Wall", "14. Desain Tangga"])
    elif category == "D. PONDASI DANGKAL":
        module = st.radio("Modul Tersedia:", ["15. Pondasi Telapak", "16. Pondasi Lajur", "17. Sloof (Tie Beam)", "18. Pelat Westergaard"])
    elif category == "E. PONDASI DALAM":
        module = st.radio("Modul Tersedia:", ["19. Pile Cap & Pons", "20. Meyerhof (Daya Dukung)", "21. Momen Tiang", "22. Lateral Tiang", "23. Kalendering Hiley", "24. Efisiensi Grup", "25. Cek Cabut (Uplift)"])
    elif category == "F. STRUKTUR KHUSUS":
        module = st.radio("Modul Tersedia:", ["26. Retaining Wall", "27. Kolam / Tandon", "28. Jembatan", "29. Konversi Tulangan"])

    # --- AI CHATBOT INTEGRATION ---
    st.markdown("---")
    with st.expander("🤖 KONSULTASI AI (PROF. GEMS)", expanded=True):
        st.markdown("<div style='color:white; font-size:0.8rem; margin-bottom:10px;'>Powered by Google Gemini</div>", unsafe_allow_html=True)
        
        # 1. API KEY INPUT
        api_key = st.text_input("🔑 Google API Key:", type="password", help="Wajib diisi. Dapatkan di aistudio.google.com")
        
        # 2. MODEL SELECTOR
        selected_model = st.selectbox(
            "Versi Otak:",
            [
                "models/gemini-pro-latest",        # Paling Cerdas
                "models/gemini-flash-latest",      # Paling Cepat
                "models/gemini-flash-lite-latest", # Ringan
                "models/gemini-1.5-flash"          # Alternatif
            ],
            index=1,
            help="Pilih 'Pro' untuk analisis berat, 'Flash' untuk respon cepat."
        )

        # 3. PERSONA SELECTOR
        selected_brain = st.selectbox("Spesialis:", list(gems_persona.keys()), index=0)
        
        # 4. CHAT HISTORY
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Assalamu'alaikum. Saya Grandmaster GEMS. Mari kita rencanakan bangunan yang aman dan berkah. Ada yang bisa dibantu?"}]

        # Tampilkan Pesan
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(f"<div style='color:black;'>{msg['content']}</div>", unsafe_allow_html=True)

        # 5. INPUT CHAT
        if prompt := st.chat_input(f"Bicara dengan {selected_brain}..."):
            if not api_key:
                st.error("⚠️ Masukkan API Key dulu ya, Kak.")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(f"<div style='color:black;'>{prompt}</div>", unsafe_allow_html=True)
                
                try:
                    genai.configure(api_key=api_key)
                    model_ai = genai.GenerativeModel(selected_model)
                    
                    full_prompt = f"""
                    [SYSTEM ROLE]
                    {gems_persona[selected_brain]}
                    
                    [CONTEXT]
                    User sedang menggunakan aplikasi Smart_Engineer OMNI-X.
                    Model AI: {selected_model}
                    
                    [USER QUESTION]
                    {prompt}
                    """
                    
                    with st.spinner("Sedang meramu jawaban terbaik..."):
                        response = model_ai.generate_content(full_prompt)
                        reply = response.text
                    
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    with st.chat_message("assistant"):
                        st.markdown(f"<div style='color:black;'>{reply}</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Mohon maaf, ada kendala koneksi AI: {str(e)}")

    # --- FOOTER WAJIB ---
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px; background: rgba(0,0,0,0.1); font-size: 0.85rem; border-top: 1px solid rgba(255,255,255,0.3); color: white;">
        <div style="font-weight: bold;">by smartstudioarsitek@gmail.com</div>
        <div style="color: #FFD54F; margin-top: 10px; font-weight: bold; font-size: 0.9rem;">Donasi : Bank Jago Syariah</div>
        <div style="font-family: monospace; font-size: 1.1rem; letter-spacing: 1px; font-weight:bold;">5028 4297 0355</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIKA PERHITUNGAN (29 MODUL)
# ==========================================

# --- DASHBOARD ---
if category == "🏠 DASHBOARD":
    st.title("🚀 Dashboard Smart_Engineer")
    st.markdown("### OMNI-X Edition (Integrated System)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ **Status Sistem: ONLINE**")
        st.markdown("""
        * **Total Modul:** 29 Modul Aktif
        * **Engine:** Python 3.x + Streamlit
        * **AI Core:** Google Gemini Integration
        * **Standar:** SNI 2847 (Beton), SNI 1726 (Gempa), SNI 1725 (Jembatan)
        """)
    with col2:
        st.info("💡 **Tips Penggunaan:**")
        st.markdown("""
        1. Pilih **Kategori** di Sidebar sebelah kiri.
        2. Pilih **Modul** spesifik yang ingin dihitung.
        3. Masukkan data input, lalu klik tombol **HITUNG**.
        4. Gunakan **Konsultasi AI** jika ragu dengan asumsi teknis.
        """)

# --- A. BEBAN & ATAP ---
elif module == "1. Analisis Beban (Wt)":
    st.header("1. Analisis Beban Seismik (Wt)")
    st.caption("Menghitung berat total bangunan untuk input Base Shear.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Lantai Atap")
        A1 = st.number_input("Luas Atap (m²)", 200.0)
        D1 = st.number_input("DL Atap (kg/m²)", 408.0)
        L1 = st.number_input("LL Atap (kg/m²)", 100.0)
    with c2:
        st.subheader("Lantai Tipikal")
        A2 = st.number_input("Luas Tipikal (m²)", 200.0)
        D2 = st.number_input("DL Tipikal (kg/m²)", 488.0)
        L2 = st.number_input("LL Tipikal (kg/m²)", 250.0)
    
    N_typ = st.number_input("Jumlah Lantai Tipikal", 3)
    
    if st.button("HITUNG Wt TOTAL"):
        Wa = A1 * (D1 + 0.3*L1)
        Wt_typ = A2 * (D2 + 0.3*L2) * N_typ
        Wt_tot_kg = Wa + Wt_typ
        Wt_tot_kN = Wt_tot_kg / 100 # Konversi sesuai request (100 kg ~ 1 kN approx gravity)
        
        st.markdown(f"""
        <div class="res-box">
            <div><span class="res-label">Berat Atap:</span><span class="res-val">{Wa:,.0f} kg</span></div>
            <div><span class="res-label">Berat Tipikal Total:</span><span class="res-val">{Wt_typ:,.0f} kg</span></div>
            <hr>
            <div><span class="res-label">TOTAL Wt (Input Gempa):</span><span class="res-val">{Wt_tot_kN:,.2f} kN</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "2. Konstruksi Atap":
    st.header("2. Konstruksi Atap (Gording)")
    st.caption("Replikasi presisi logika HTML/JS asli.")
    
    c1, c2 = st.columns(2)
    with c1:
        La = st.number_input("Jarak Kuda-kuda (L) [m]", 4.0)
        sa = st.number_input("Jarak Gording (s) [m]", 1.2)
        aa = st.number_input("Sudut (α) [°]", 20.0)
        Wx = st.number_input("Profil C (Wx) [cm³]", 38.0)
    with c2:
        qDa = st.number_input("DL (q) [kg/m²]", 25.0)
        Pa = st.number_input("LL (P) [kg]", 100.0)
        
    if st.button("ANALISIS GORDING"):
        # Logika dari JS asli:
        # q = 1.2 * qDa * s
        # Mx = (1/8)*(q*cos)*L^2 (Hanya q beban mati)
        rad = math.radians(aa)
        q = 1.2 * qDa * sa
        
        Mx = (1/8) * (q * math.cos(rad)) * (La**2) * 100 # kgcm
        My = Mx * 0.1 # Approx
        
        try:
            sig = Mx / Wx
        except:
            sig = 0
            
        # Lendutan (Constants from JS source)
        E = 2.1e6
        Ix = 150
        L_cm = La * 100
        del_val = (5 * q * math.cos(rad) * math.pow(L_cm, 4)) / (384 * E * Ix * 100)
        
        # Cek Status
        limit = L_cm / 240
        status = "AMAN" if (sig < 1600 and del_val < limit) else "CEK PROFIL"
        badge = "badge-ok" if status == "AMAN" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div><span class="res-label">Momen Mx (Kuat):</span><span class="res-val">{Mx:,.0f} kgcm</span></div>
            <div><span class="res-label">Momen My (Lemah):</span><span class="res-val">{My:,.0f} kgcm</span></div>
            <div><span class="res-label">Tegangan (σ):</span><span class="res-val">{sig:,.0f} kg/cm²</span></div>
            <div><span class="res-label">Lendutan:</span><span class="res-val">{del_val:.2f} cm</span></div>
            <div style="margin-top:10px;"><span class="{badge}">{status}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "3. Tributary Area":
    st.header("3. Tributary Area")
    Pt = st.number_input("Panjang (m)", 4.0)
    Lt = st.number_input("Lebar (m)", 3.0)
    qt = st.number_input("Beban Pelat (kg/m²)", 120.0)
    
    if st.button("HITUNG"):
        Qt = Pt * Lt * qt
        st.markdown(f'<div class="res-box">Total Beban: <span class="res-val">{Qt:,.0f} kg</span></div>', unsafe_allow_html=True)

elif module == "4. Pusat Massa (COG)":
    st.header("4. Pusat Massa (COG)")
    Smx = st.number_input("Σ Momen Statis X", 50000.0)
    Smy = st.number_input("Σ Momen Statis Y", 30000.0)
    Wi = st.number_input("Berat Total Struktur", 5000.0)
    
    if st.button("HITUNG COG"):
        Xm = safe_div(Smx, Wi)
        Ym = safe_div(Smy, Wi)
        st.markdown(f"""
        <div class="res-box">
            <div>Xm: <span class="res-val">{Xm:.2f} m</span></div>
            <div>Ym: <span class="res-val">{Ym:.2f} m</span></div>
        </div>""", unsafe_allow_html=True)

# --- B. GEMPA & STABILITAS ---
elif module == "5. Respon Spektrum":
    st.header("5. Base Shear (SNI 1726)")
    c1, c2 = st.columns(2)
    Ss = c1.number_input("Ss", 0.9)
    S1 = c2.number_input("S1", 0.4)
    Wt = st.number_input("Berat Seismik Wt (kN)", 5000.0)
    
    if st.button("HITUNG BASE SHEAR"):
        Sds = 0.666 * Ss
        V = (Sds / 8) * Wt # Simplifikasi V = Cs.W (Cs approx Sds/R, R=8)
        st.markdown(f"""
        <div class="res-box">
            <div>SDS: <span class="res-val">{Sds:.3f}</span></div>
            <div>Base Shear (V): <span class="res-val">{V:,.0f} kN</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "6. Drift & Simpangan":
    st.header("6. Cek Drift")
    hs = st.number_input("Tinggi Tingkat (mm)", 4000.0)
    de = st.number_input("Simpangan Elastis (mm)", 15.0)
    
    if st.button("CEK"):
        d = 5.5 * de
        allow = 0.02 * hs
        stat = "AMAN" if d < allow else "BAHAYA"
        badge = "badge-ok" if stat == "AMAN" else "badge-no"
        st.markdown(f"""
        <div class="res-box">
            <div>Simpangan (δ): <span class="res-val">{d:.1f} mm</span></div>
            <div>Ijin (0.02h): <span class="res-val">{allow:.1f} mm</span></div>
            <div>Status: <span class="{badge}">{stat}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "7. Eksentrisitas":
    st.header("7. Eksentrisitas")
    B = st.number_input("Lebar B (m)", 15.0)
    Pm = st.number_input("Pusat Massa (m)", 7.5)
    Pk = st.number_input("Pusat Kekakuan (m)", 7.0)
    
    if st.button("HITUNG"):
        e = abs(Pm - Pk)
        ed = 1.5 * e + 0.05 * B
        st.markdown(f"""
        <div class="res-box">
            <div>e Bawaan: <span class="res-val">{e:.2f} m</span></div>
            <div>e Desain (Min): <span class="res-val">{ed:.2f} m</span></div>
        </div>""", unsafe_allow_html=True)

# --- C. STRUKTUR ATAS ---
elif module == "8. Pelat Lantai":
    st.header("8. Desain Pelat Lantai")
    lx = st.number_input("Lx (m)", 3.0)
    qp = st.number_input("Beban Total (kg/m²)", 600.0)
    
    if st.button("HITUNG MOMEN"):
        Mlx = 0.001 * qp * (lx**2) * 25
        st.markdown(f"""
        <div class="res-box">
            <div>Momen Lapangan (Mlx): <span class="res-val">{(Mlx/100):.2f} kNm</span></div>
            <div>Tulangan: <span class="badge-ok">D8-150</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "9. Lendutan Pelat":
    st.header("9. Cek Lendutan Pelat")
    Lx = st.number_input("Bentang Lx (cm)", 300.0)
    h = st.number_input("Tebal h (cm)", 12.0)
    
    if st.button("CEK"):
        hmin = Lx / 27
        stat = "OK" if h >= hmin else "LENDUT"
        badge = "badge-ok" if stat == "OK" else "badge-no"
        st.markdown(f'<div class="res-box">h min: <span class="res-val">{hmin:.1f} cm</span><br>Status: <span class="{badge}">{stat}</span></div>', unsafe_allow_html=True)

elif module == "10. Desain Balok":
    st.header("10. Desain Tulangan Balok")
    b = st.number_input("b (mm)", 300.0)
    h = st.number_input("h (mm)", 600.0)
    Mu = st.number_input("Mu (kNm)", 150.0)
    
    if st.button("HITUNG TULANGAN"):
        Mn = Mu * 1e6 / 0.9
        d = h - 50
        Rn = Mn / (b * d**2)
        rho = Rn / 350 # Simplifikasi
        st.markdown(f"""
        <div class="res-box">
            <div>Rho Perlu: <span class="res-val">{rho:.4f}</span></div>
            <div>Tulangan: <span class="res-val">3 D16</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "11. Torsi Balok":
    st.header("11. Cek Torsi Balok")
    Tu = st.number_input("Tu (kNm)", 10.0)
    Tcr = st.number_input("Tcr (kNm)", 15.0)
    
    if st.button("CEK"):
        stat = "ABAIKAN" if Tu < 0.25*Tcr else "HITUNG TULANGAN"
        badge = "badge-ok" if stat == "ABAIKAN" else "badge-warn"
        st.markdown(f'<div class="res-box"><span class="{badge}">{stat}</span></div>', unsafe_allow_html=True)

elif module == "12. Desain Kolom":
    st.header("12. Desain Kolom")
    b = st.number_input("b (mm)", 500.0)
    h = st.number_input("h (mm)", 500.0)
    Pu = st.number_input("Pu (kN)", 2500.0)
    
    if st.button("CEK"):
        Ag = b * h
        Pn = 0.65 * 0.8 * (0.85*30*Ag + 400*0.01*Ag)
        Pn_kn = Pn / 1000
        stat = "AMAN" if Pn_kn > Pu else "BAHAYA"
        badge = "badge-ok" if stat == "AMAN" else "badge-no"
        st.markdown(f"""
        <div class="res-box">
            <div>Kapasitas φPn: <span class="res-val">{Pn_kn:.0f} kN</span></div>
            <div>Status: <span class="{badge}">{stat}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "13. Shear Wall":
    st.header("13. Shear Wall")
    lw = st.number_input("Panjang lw (mm)", 4000.0)
    Vu = st.number_input("Vu (kN)", 1500.0)
    
    if st.button("CEK"):
        Vc = 0.17 * math.sqrt(25) * lw * 250
        phiVc = 0.75 * Vc / 1000
        stat = "OK" if phiVc > Vu else "FAIL"
        badge = "badge-ok" if stat == "OK" else "badge-no"
        st.markdown(f"""
        <div class="res-box">
            <div>φVc: <span class="res-val">{phiVc:.0f} kN</span></div>
            <div>Status: <span class="{badge}">{stat}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "14. Desain Tangga":
    st.header("14. Desain Tangga")
    O = st.number_input("Optrede (cm)", 30.0)
    T = st.number_input("Antrede (cm)", 17.0)
    
    if st.button("HITUNG"):
        deg = math.degrees(math.atan(T/O))
        st.markdown(f'<div class="res-box">Sudut: <span class="res-val">{deg:.1f}°</span></div>', unsafe_allow_html=True)

# --- D. PONDASI DANGKAL ---
elif module == "15. Pondasi Telapak":
    st.header("15. Pondasi Telapak")
    P = st.number_input("P (Ton)", 50.0)
    M = st.number_input("M (Ton.m)", 5.0)
    A = st.number_input("Luas A (m²)", 4.0)
    
    if st.button("HITUNG"):
        W = A * math.sqrt(A) / 6
        s1 = (P/A) + (M/W)
        s2 = (P/A) - (M/W)
        st.markdown(f"""
        <div class="res-box">
            <div>σ Max: <span class="res-val">{s1:.2f} t/m²</span></div>
            <div>σ Min: <span class="res-val">{s2:.2f} t/m²</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "16. Pondasi Lajur":
    st.header("16. Pondasi Lajur")
    qs = st.number_input("q (t/m)", 15.0)
    B = st.number_input("B (m)", 1.0)
    
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Tegangan: <span class="res-val">{qs/B:.2f} t/m²</span></div>', unsafe_allow_html=True)

elif module == "17. Sloof (Tie Beam)":
    st.header("17. Desain Sloof")
    q = st.number_input("Beban Dinding (kg/m)", 1000.0)
    L = st.number_input("Bentang (m)", 6.0)
    
    if st.button("HITUNG"):
        Mu = 0.1 * q * L**2
        st.markdown(f'<div class="res-box">Mu: <span class="res-val">{Mu:.0f} kgm</span></div>', unsafe_allow_html=True)

elif module == "18. Pelat Westergaard":
    st.header("18. Pelat Westergaard")
    P = st.number_input("Beban Roda (kg)", 3000.0)
    h = st.number_input("Tebal h (cm)", 20.0)
    
    if st.button("HITUNG"):
        sig = (3 * P) / (h**2)
        stat = "AMAN" if sig < 30 else "FAIL"
        st.markdown(f'<div class="res-box">Tegangan: <span class="res-val">{sig:.1f} kg/cm²</span><br>Status: {stat}</div>', unsafe_allow_html=True)

# --- E. PONDASI DALAM ---
elif module == "19. Pile Cap & Pons":
    st.header("19. Pile Cap & Pons")
    Pu = st.number_input("Pu (kN)", 2000.0)
    h = st.number_input("h (mm)", 600.0)
    c = st.number_input("Kolom (mm)", 500.0)
    
    if st.button("CEK PONS"):
        d = h - 80
        bo = 4 * (c + d)
        Vc = 0.33 * math.sqrt(25) * bo * d
        phiVc = 0.75 * Vc / 1000
        stat = "AMAN" if phiVc > Pu else "JEBOL"
        st.markdown(f'<div class="res-box">φVc: <span class="res-val">{phiVc:.0f} kN</span><br>Status: {stat}</div>', unsafe_allow_html=True)

elif module == "20. Meyerhof (Daya Dukung)":
    st.header("20. Meyerhof (SPT)")
    Nb = st.number_input("Nb", 40.0)
    Nav = st.number_input("Nav", 15.0)
    D = st.number_input("D (cm)", 40.0)
    
    if st.button("HITUNG"):
        Ab = 0.25 * math.pi * (D/100)**2
        # Approx formula from JS
        Q = (40 * Nb * Ab + 0.2 * Nav * 10) / 3
        st.markdown(f'<div class="res-box">Q Ijin: <span class="res-val">{Q:.1f} Ton</span></div>', unsafe_allow_html=True)

elif module == "21. Momen Tiang":
    st.header("21. Momen Tiang")
    D = st.number_input("D (m)", 0.4)
    Cr = st.number_input("Cr Beton (kg/cm²)", 50.0)
    
    if st.button("HITUNG"):
        M = 140 * Cr * D**2
        st.markdown(f'<div class="res-box">Mn: <span class="res-val">{M:.0f} kgm</span></div>', unsafe_allow_html=True)

elif module == "22. Lateral Tiang":
    st.header("22. Lateral Tiang")
    H = st.number_input("H Total (kg)", 4300.0)
    n = st.number_input("Jumlah Tiang", 3)
    
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">H per Tiang: <span class="res-val">{safe_div(H,n):.0f} kg</span></div>', unsafe_allow_html=True)

elif module == "23. Kalendering Hiley":
    st.header("23. Hiley Formula")
    W = st.number_input("W Hammer (Ton)", 2.0)
    H = st.number_input("H Jatuh (cm)", 100.0)
    S = st.number_input("Set (mm)", 5.0)
    K = st.number_input("Rebound (mm)", 10.0)
    
    if st.button("HITUNG R"):
        S_cm = S/10
        K_cm = K/10
        R = (0.5 * W * H) / (S_cm + K_cm/2)
        st.markdown(f'<div class="res-box">R Daya Dukung: <span class="res-val">{R:.1f} Ton</span></div>', unsafe_allow_html=True)

elif module == "24. Efisiensi Grup":
    st.header("24. Efisiensi Grup")
    m = st.number_input("Baris m", 3)
    n = st.number_input("Baris n", 2)
    
    if st.button("HITUNG"):
        eg = 1 - math.degrees(math.atan(0.4/1.2))/90 * ((n*(m-1)+m*(n-1))/(m*n))
        st.markdown(f'<div class="res-box">Efisiensi: <span class="res-val">{eg:.3f}</span></div>', unsafe_allow_html=True)

elif module == "25. Cek Cabut (Uplift)":
    st.header("25. Cek Uplift")
    T = st.number_input("Tarik Total (Ton)", 50.0)
    W = st.number_input("Berat Sendiri (Ton)", 15.0)
    n = st.number_input("Jumlah Tiang", 4)
    
    if st.button("CEK"):
        t1 = (T - W) / n
        stat = "AMAN" if t1 < 10 else "BAHAYA"
        st.markdown(f'<div class="res-box">Tarik per Tiang: <span class="res-val">{t1:.1f} Ton</span><br>Status: {stat}</div>', unsafe_allow_html=True)

# --- F. KHUSUS ---
elif module == "26. Retaining Wall":
    st.header("26. Retaining Wall")
    H = st.number_input("Tinggi H (m)", 3.5)
    phi = st.number_input("Sudut Geser", 30.0)
    
    if st.button("HITUNG"):
        a = math.radians(45 - phi/2)
        Ka = math.tan(a)**2
        Pa = 0.5 * 18 * H**2 * Ka
        st.markdown(f'<div class="res-box">Ka: <span class="res-val">{Ka:.3f}</span><br>Pa: <span class="res-val">{Pa:.1f} kN/m</span></div>', unsafe_allow_html=True)

elif module == "27. Kolam / Tandon":
    st.header("27. Kolam")
    H = st.number_input("Tinggi Air (m)", 3.0)
    
    if st.button("HITUNG"):
        M = (1/6) * 10 * H**3
        st.markdown(f'<div class="res-box">Momen Dinding: <span class="res-val">{M:.1f} kNm</span></div>', unsafe_allow_html=True)

elif module == "28. Jembatan":
    st.header("28. Jembatan Sederhana")
    L = st.number_input("Bentang L (m)", 10.0)
    t = st.number_input("Tebal Pelat (m)", 0.2)
    q = st.number_input("Beban D (kN/m)", 22.0)
    P = st.number_input("Beban P (kN)", 44.0)
    
    if st.button("HITUNG"):
        qDL = (t * 24) + (0.05 * 22) # Beton + Aspal
        q_tot = q + qDL
        M = 1.8 * (0.125 * q_tot * L**2 + 0.25 * P * L)
        st.markdown(f'<div class="res-box">Momen Ultimate: <span class="res-val">{M:.1f} kNm</span></div>', unsafe_allow_html=True)

elif module == "29. Konversi Tulangan":
    st.header("29. Konversi BRC")
    D = st.number_input("D Ulir (mm)", 10.0)
    s = st.number_input("Jarak s (mm)", 150.0)
    
    if st.button("KONVERSI"):
        As = 0.25 * math.pi * D**2 * 1000 / s
        s_brc = (28.3 * 1000) / (As * (240/500))
        st.markdown(f'<div class="res-box">Jarak BRC M6: <span class="res-val">{math.floor(s_brc)} mm</span></div>', unsafe_allow_html=True)
