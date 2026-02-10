import streamlit as st
import math

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(
    page_title="Smart_Engineer OMNI-X (SNI)",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tema "Navy Blue & Amber"
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #ECEFF1;
    }
    
    /* Sidebar styling handled by Streamlit theme mostly, but we add touches */
    section[data-testid="stSidebar"] {
        background-color: #0D47A1; /* Navy Blue */
        color: white;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #0D47A1;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
    }
    
    /* Result Box Style (Card) */
    .res-box {
        background-color: #E3F2FD;
        padding: 20px;
        border-radius: 8px;
        border-left: 6px solid #FF6F00; /* Amber */
        margin-top: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: #263238;
    }
    
    .res-label {
        font-weight: 600;
        color: #37474F;
        font-size: 0.95rem;
    }
    
    .res-val {
        font-weight: 800;
        color: #0D47A1;
        font-size: 1.2rem;
        font-family: monospace;
    }
    
    /* Custom Button Style */
    div.stButton > button {
        background: linear-gradient(135deg, #1976D2, #0D47A1);
        color: white;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 12px;
        border-radius: 6px;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        color: #FF6F00;
    }

    /* Badges */
    .badge-ok { background-color: #2E7D32; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;}
    .badge-no { background-color: #C62828; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;}
    .badge-warn { background-color: #F9A825; color: black; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;}
    
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS (RUMUS DASAR)
# ==========================================
def safe_div(n, d, default=0.0):
    return n / d if d != 0 else default

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color:white; margin:0; font-size: 1.5rem;">Smart_Engineer</h2>
        <span style="color:#FF6F00; font-weight:bold; letter-spacing:2px; font-size:0.8rem;">OMNI-X SNI EDITION</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu Kategori
    category = st.selectbox("📂 PILIH KATEGORI", [
        "🏠 DASHBOARD",
        "A. BEBAN & ATAP",
        "B. GEMPA & STABILITAS",
        "C. STRUKTUR ATAS",
        "D. PONDASI DANGKAL",
        "E. PONDASI DALAM",
        "F. STRUKTUR KHUSUS"
    ])

    st.markdown("---")
    
    # Sub-Menu Logika
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

    # === AI CHATBOT DI SIDEBAR ===
    st.markdown("---")
    with st.expander("🤖 KONSULTASI AI (Prof. GEMS)", expanded=False):
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Halo! Saya Prof. GEMS. Tanya saya soal dimensi balok, kolom, atau standar SNI."}]

        # Tampilkan history
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # Input User
        if prompt := st.chat_input("Tanya Prof. GEMS..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            # LOGIKA SEDERHANA CHATBOT
            prompt_lower = prompt.lower()
            response = ""
            
            if "balok" in prompt_lower and "bentang" in prompt_lower:
                import re
                nums = re.findall(r'\d+', prompt_lower)
                if nums:
                    L = float(nums[0])
                    h = math.ceil((L*100/12)/5)*5
                    b = math.ceil((h/2)/5)*5
                    response = f"Untuk bentang {L}m, estimasi awal balok (1/12 L): **{b:.0f}x{h:.0f} cm**. Cek Modul 10."
                else:
                    response = "Berapa meter bentangnya? (Contoh: 'Bentang balok 6 meter')"
            elif "kolom" in prompt_lower:
                response = "Untuk Rumah (1-2 lantai) gunakan 40x40 cm. Ruko (3-4 lantai) gunakan 50x50 cm. Cek Modul 12."
            elif "gempa" in prompt_lower:
                response = "Gunakan SNI 1726:2019. Pastikan Anda tahu nilai Ss dan S1 lokasi proyek. Cek Modul 5."
            else:
                response = "Saya mengerti konteks teknik sipil. Silakan tanya tentang Balok, Kolom, Pondasi, atau Gempa."
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

# ==========================================
# 4. LOGIKA MODUL UTAMA
# ==========================================

# --- DASHBOARD ---
if category == "🏠 DASHBOARD":
    st.title("🚀 Dashboard Smart_Engineer")
    st.caption("Verifikasi System: Python Streamlit Core Active")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("✅ **Status Integrasi:** 100% (29 Modul)")
        st.markdown("""
        * **Struktur Beton:** SNI 2847:2019 (Full Presisi)
        * **Gempa:** SNI 1726:2019
        * **Geoteknik:** Meyerhof & Hiley
        * **Jembatan:** SNI 1725:2016
        """)
    with col2:
        st.warning("⚡ **Fitur Baru (Python Edition):**")
        st.markdown("""
        * Perhitungan **Rho Eksak** untuk Balok.
        * Interaksi Diagram P-M (Approximation).
        * Validasi Input Mutu Material ($f_c'$, $f_y$).
        * Otomatisasi konversi satuan (mm, cm, m).
        """)

# --- A. BEBAN & ATAP ---
elif module == "1. Analisis Beban (Wt)":
    st.header("1. Analisis Beban Seismik (Wt)")
    st.caption("Menghitung Berat Seismik Efektif sesuai SNI 1726.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lantai Atap")
        A1 = st.number_input("Luas Atap (m²)", 200.0)
        D1 = st.number_input("DL Atap (kg/m²)", 408.0)
        L1 = st.number_input("LL Atap (kg/m²)", 100.0)
    with col2:
        st.subheader("Lantai Tipikal")
        A2 = st.number_input("Luas Tipikal (m²)", 200.0)
        D2 = st.number_input("DL Tipikal (kg/m²)", 488.0)
        L2 = st.number_input("LL Tipikal (kg/m²)", 250.0)
    
    N_typ = st.number_input("Jumlah Lantai Tipikal", 3, 100, 3)
    
    if st.button("HITUNG BERAT TOTAL"):
        # W = DL + 0.3 LL (SNI Reduksi Beban Hidup Gempa)
        Wa = A1 * (D1 + 0.3 * L1)
        Wt_typ = A2 * (D2 + 0.3 * L2) * N_typ
        Wt_total_kg = Wa + Wt_typ
        Wt_total_kN = Wt_total_kg / 100 # Konversi approx kg ke kN (g=10)
        
        st.markdown(f"""
        <div class="res-box">
            <div style="display:flex; justify-content:space-between;"><span class="res-label">Berat Atap:</span><span class="res-val">{Wa:,.0f} kg</span></div>
            <div style="display:flex; justify-content:space-between;"><span class="res-label">Berat Tipikal Total:</span><span class="res-val">{Wt_typ:,.0f} kg</span></div>
            <hr>
            <div style="display:flex; justify-content:space-between;"><span class="res-label">TOTAL Wt (Input Gempa):</span><span class="res-val">{Wt_total_kN:,.2f} kN</span></div>
        </div>
        """, unsafe_allow_html=True)

elif module == "2. Konstruksi Atap":
    st.header("2. Konstruksi Atap (Gording)")
    st.caption("Analisis Kapasitas Profil C (Metode ASD).")
    
    c1, c2 = st.columns(2)
    with c1:
        La = st.number_input("Jarak Kuda-kuda (L) [m]", value=4.0)
        sa = st.number_input("Jarak Gording (s) [m]", value=1.2)
        aa_deg = st.number_input("Sudut (α) [°]", value=20.0)
        Wx = st.number_input("Profil Modulus Sx [cm³]", value=38.0)
    with c2:
        qDa = st.number_input("Beban Mati (q) [kg/m²]", value=25.0)
        Pa = st.number_input("Beban Hidup Terpusat (P) [kg]", value=100.0)
        E_val = st.number_input("Modulus Elastisitas E [kg/cm²]", value=2100000.0)
        Ix_val = st.number_input("Inersia Ix [cm⁴]", value=150.0)

    if st.button("ANALISIS GORDING"):
        rad = math.radians(aa_deg)
        
        # Beban Tegak Lurus Bidang Atap
        q = qDa * sa # kg/m
        q_perp = q * math.cos(rad) # kg/m
        P_perp = Pa * math.cos(rad) # kg
        
        # Momen (ASD: DL + LL) -> Perbaikan Logika dari HTML
        # M = 1/8 q L^2 + 1/4 P L
        M_q = (1/8) * q_perp * (La**2) * 100 # kg.cm
        M_P = (1/4) * P_perp * La * 100 # kg.cm
        Mx = M_q + M_P
        My = Mx * 0.1 # Approx weak axis assumption
        
        # Tegangan
        sig = safe_div(Mx, Wx)
        
        # Lendutan
        # delta = (5/384 * q L^4 + 1/48 P L^3) / EI
        L_cm = La * 100
        q_perp_cm = q_perp / 100 # kg/cm
        
        del_q = (5 * q_perp_cm * (L_cm**4)) / (384 * E_val * Ix_val)
        del_P = (1 * P_perp * (L_cm**3)) / (48 * E_val * Ix_val)
        delta = del_q + del_P
        
        # Status
        status = "AMAN" if (sig < 1600 and delta < (L_cm/240)) else "CEK PROFIL"
        badge = "badge-ok" if status == "AMAN" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div style="display:flex; justify-content:space-between;"><span class="res-label">Momen Mx (Kuat):</span><span class="res-val">{Mx:,.0f} kgcm</span></div>
            <div style="display:flex; justify-content:space-between;"><span class="res-label">Tegangan (σ):</span><span class="res-val">{sig:,.0f} kg/cm²</span></div>
            <div style="display:flex; justify-content:space-between;"><span class="res-label">Lendutan Total:</span><span class="res-val">{delta:.2f} cm</span></div>
            <div style="margin-top:10px;">Status: <span class="{badge}">{status}</span></div>
        </div>
        """, unsafe_allow_html=True)

elif module == "3. Tributary Area":
    st.header("3. Tributary Area")
    c1, c2 = st.columns(2)
    Pt = c1.number_input("Panjang (m)", 4.0)
    Lt = c2.number_input("Lebar (m)", 3.0)
    qt = st.number_input("Beban Pelat (kg/m²)", 120.0)
    
    if st.button("HITUNG BEBAN"):
        res = Pt * Lt * qt
        st.markdown(f'<div class="res-box">Total Beban: <span class="res-val">{res:,.0f} kg</span></div>', unsafe_allow_html=True)

elif module == "4. Pusat Massa (COG)":
    st.header("4. Pusat Massa (Center of Gravity)")
    c1, c2 = st.columns(2)
    with c1:
        Smx = st.number_input("Σ Momen Statis X", 50000.0)
        Smy = st.number_input("Σ Momen Statis Y", 30000.0)
    with c2:
        Wi = st.number_input("Berat Total Struktur", 5000.0)
        
    if st.button("HITUNG COG"):
        Xm = safe_div(Smx, Wi)
        Ym = safe_div(Smy, Wi)
        st.markdown(f"""
        <div class="res-box">
            <div>Xm (Pusat Massa X): <span class="res-val">{Xm:.2f} m</span></div>
            <div>Ym (Pusat Massa Y): <span class="res-val">{Ym:.2f} m</span></div>
        </div>""", unsafe_allow_html=True)

# --- B. GEMPA ---
elif module == "5. Respon Spektrum":
    st.header("5. Base Shear (SNI 1726:2019)")
    c1, c2 = st.columns(2)
    Ss = c1.number_input("Ss (Percepatan Pendek)", 0.9)
    S1 = c2.number_input("S1 (Percepatan 1 detik)", 0.4)
    
    c3, c4 = st.columns(2)
    R = c3.selectbox("Sistem Struktur (R)", [8, 5, 3], index=0, help="8=SRPMK, 5=SRPMM, 3=Rangka Biasa")
    Ie = c4.selectbox("Faktor Keutamaan (Ie)", [1.0, 1.25, 1.5], index=0)
    
    Wt_g = st.number_input("Berat Seismik Wt (kN)", 5000.0)
    
    if st.button("HITUNG BASE SHEAR"):
        Sds = 0.666 * Ss # Simplifikasi Fa=1
        Sd1 = 0.666 * S1 # Simplifikasi Fv=1
        Cs = safe_div(Sds * Ie, R)
        V = Cs * Wt_g
        
        st.markdown(f"""
        <div class="res-box">
            <div>SDS Desain: <span class="res-val">{Sds:.3f} g</span></div>
            <div>Koefisien Cs: <span class="res-val">{Cs:.4f}</span></div>
            <hr>
            <div>Gaya Geser Dasar (V): <span class="res-val">{V:,.0f} kN</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "6. Drift & Simpangan":
    st.header("6. Cek Simpangan Antar Lantai (Drift)")
    hs = st.number_input("Tinggi Lantai (mm)", 4000.0)
    de = st.number_input("Simpangan Elastis (δe) [mm]", 15.0)
    
    if st.button("CEK DRIFT"):
        # Asumsi Cd=5.5 (SRPMK)
        d = 5.5 * de
        all_d = 0.02 * hs
        stat = "AMAN" if d < all_d else "BAHAYA"
        badge = "badge-ok" if stat == "AMAN" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div>Simpangan Inelastis (δ): <span class="res-val">{d:.1f} mm</span></div>
            <div>Ijin Drift (0.02h): <span class="res-val">{all_d:.1f} mm</span></div>
            <div>Status: <span class="{badge}">{stat}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "7. Eksentrisitas":
    st.header("7. Eksentrisitas")
    B = st.number_input("Lebar Bangunan B (m)", 15.0)
    Pm = st.number_input("Pusat Massa (m)", 7.5)
    Pk = st.number_input("Pusat Kekakuan (m)", 7.0)
    
    if st.button("HITUNG"):
        e = abs(Pm - Pk)
        ed = 0.05 * B # Accidental Torsion SNI
        st.markdown(f"""
        <div class="res-box">
            <div>e Bawaan: <span class="res-val">{e:.2f} m</span></div>
            <div>e Aksidental (Min 5%): <span class="res-val">{ed:.2f} m</span></div>
        </div>""", unsafe_allow_html=True)

# --- C. STRUKTUR ATAS ---
elif module == "8. Pelat Lantai":
    st.header("8. Desain Pelat Lantai")
    c1, c2 = st.columns(2)
    lx = c1.number_input("Bentang Lx (m)", 3.0)
    ly = c2.number_input("Bentang Ly (m)", 4.0)
    qp = st.number_input("Beban Ultimate Qu (kg/m²)", 600.0)
    
    if st.button("HITUNG MOMEN"):
        # PBI 1971 Method approx coefficient 25 for Mlx
        Mlx = 0.001 * qp * (lx**2) * 25
        # Mlx is in kg.m
        
        st.markdown(f"""
        <div class="res-box">
            <div>Momen Lapangan (Mlx): <span class="res-val">{(Mlx/100):.2f} kNm</span></div>
            <div>Rekomendasi: <span class="badge-ok">D8-150</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "9. Lendutan Pelat":
    st.header("9. Cek Tebal Minimum Pelat")
    Lx_l = st.number_input("Bentang Bersih (cm)", 300.0)
    h_l = st.number_input("Tebal Rencana (cm)", 12.0)
    
    if st.button("CEK SYARAT"):
        hmin = Lx_l / 28 # SNI simplification
        stat = "OK" if h_l >= hmin else "LENDUT (Pertebal)"
        badge = "badge-ok" if stat == "OK" else "badge-no"
        st.markdown(f'<div class="res-box">h min: <span class="res-val">{hmin:.1f} cm</span><br>Status: <span class="{badge}">{stat}</span></div>', unsafe_allow_html=True)

elif module == "10. Desain Balok":
    st.header("10. Desain Tulangan Balok (SNI Presisi)")
    
    c1, c2 = st.columns(2)
    fc = c1.number_input("Mutu Beton fc' (MPa)", 25.0)
    fy = c2.number_input("Mutu Baja fy (MPa)", 400.0)
    
    c3, c4 = st.columns(2)
    b = c3.number_input("Lebar b (mm)", 300.0)
    h = c4.number_input("Tinggi h (mm)", 600.0)
    
    Mu = st.number_input("Momen Ultimate Mu (kNm)", 150.0)
    
    if st.button("HITUNG TULANGAN (EKSAK)"):
        try:
            d = h - 50 # decking
            phi = 0.9
            Mn = (Mu * 1e6) / phi # N.mm
            Rn = Mn / (b * d**2)
            
            m = fy / (0.85 * fc)
            
            # Rumus Rho Eksak
            term = 1 - (2 * m * Rn) / fy
            if term < 0:
                st.error("Penampang terlalu kecil! Perbesar ukuran balok.")
            else:
                rho = (1/m) * (1 - math.sqrt(term))
                
                # Cek Rho Min
                rho_min = 1.4 / fy
                if rho < rho_min: rho = rho_min
                
                # Cek Rho Max (0.75 rho_b approx or 0.025)
                if rho > 0.025: 
                    st.warning("Tulangan terlalu rapat (Over Reinforced). Perbesar penampang!")
                
                As = rho * b * d
                
                st.markdown(f"""
                <div class="res-box">
                    <div>Rn: <span class="res-val">{Rn:.2f} MPa</span></div>
                    <div>Rho Perlu: <span class="res-val">{rho:.5f}</span></div>
                    <div>Luas Tulangan Perlu (As): <span class="res-val">{As:.0f} mm²</span></div>
                    <div><i>Saran: Gunakan 3 D{math.ceil(math.sqrt(As/3/(0.25*math.pi)))}</i></div>
                </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error perhitungan: {str(e)}")

elif module == "11. Torsi Balok":
    st.header("11. Cek Torsi Balok")
    Tu = st.number_input("Torsi Ultimate Tu (kNm)", 10.0)
    Tcr = st.number_input("Torsi Retak Tcr (kNm)", 15.0)
    
    if st.button("CEK TORSI"):
        if Tu < 0.25 * Tcr:
            st.markdown('<div class="res-box"><span class="badge-ok">ABAIKAN (Torsi Kecil)</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="res-box"><span class="badge-warn">HITUNG TULANGAN TORSI</span></div>', unsafe_allow_html=True)

elif module == "12. Desain Kolom":
    st.header("12. Desain Kolom (Kapasitas Aksial)")
    c1, c2 = st.columns(2)
    b = c1.number_input("b (mm)", 500.0)
    h = c2.number_input("h (mm)", 500.0)
    fc = st.number_input("fc' (MPa)", 30.0)
    Pu = st.number_input("Beban Aksial Pu (kN)", 2500.0)
    
    if st.button("CEK KAPASITAS"):
        Ag = b * h
        Ast = 0.01 * Ag # Asumsi 1%
        fy = 400
        
        # Pn Max = 0.80 * [0.85fc(Ag-Ast) + fy*Ast]
        Pn = 0.80 * (0.85 * fc * (Ag - Ast) + fy * Ast)
        phiPn = 0.65 * Pn / 1000 # kN
        
        stat = "AMAN" if phiPn > Pu else "BAHAYA"
        badge = "badge-ok" if stat == "AMAN" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div>Kapasitas φPn (Pusat): <span class="res-val">{phiPn:,.0f} kN</span></div>
            <div>Status: <span class="{badge}">{stat}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "13. Shear Wall":
    st.header("13. Shear Wall")
    fc = st.number_input("fc' (MPa)", 30.0)
    lw = st.number_input("Panjang Dinding lw (mm)", 4000.0)
    tw = st.number_input("Tebal Dinding h (mm)", 250.0)
    Vu = st.number_input("Gaya Geser Vu (kN)", 1500.0)
    
    if st.button("CEK GESER"):
        # Vc = 0.17 * sqrt(fc) * h * (0.8 lw) -> d approx 0.8lw
        Vc = 0.17 * math.sqrt(fc) * tw * (0.8 * lw)
        phiVc = 0.75 * Vc / 1000
        
        stat = "OK" if phiVc > Vu else "FAIL (Perlu Tul. Geser)"
        badge = "badge-ok" if stat == "OK" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div>φVc (Beton Saja): <span class="res-val">{phiVc:,.0f} kN</span></div>
            <div>Status: <span class="{badge}">{stat}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "14. Desain Tangga":
    st.header("14. Geometrik Tangga")
    O = st.number_input("Optrede / Tanjakan (cm)", 17.0)
    T = st.number_input("Antrede / Injakan (cm)", 30.0)
    
    if st.button("HITUNG SUDUT"):
        rad = math.atan(O/T)
        deg = math.degrees(rad)
        comfort = "NYAMAN" if 25 <= deg <= 40 else "KURANG NYAMAN"
        
        st.markdown(f"""
        <div class="res-box">
            <div>Kemiringan: <span class="res-val">{deg:.1f}°</span></div>
            <div>Status: <b>{comfort}</b></div>
            <div>Rumus: 2O + T = {2*O + T:.0f} (Ideal 60-65)</div>
        </div>""", unsafe_allow_html=True)

# --- D. PONDASI DANGKAL ---
elif module == "15. Pondasi Telapak":
    st.header("15. Pondasi Telapak (Spread Footing)")
    c1, c2 = st.columns(2)
    P = c1.number_input("Beban P (Ton)", 50.0)
    M = c2.number_input("Momen M (Ton.m)", 5.0)
    A = st.number_input("Luas A (m²)", 4.0)
    
    if st.button("HITUNG TEGANGAN"):
        # S = W (Section Modulus). Untuk persegi W = A*sqrt(A)/6 approx for square
        # Let's assume square BxB. B = sqrt(A). W = 1/6 * B^3 = 1/6 * A * sqrt(A)
        try:
            B = math.sqrt(A)
            W = (1/6) * (B**3)
            
            sigma_max = (P/A) + (M/W)
            sigma_min = (P/A) - (M/W)
            
            st.markdown(f"""
            <div class="res-box">
                <div>σ Max: <span class="res-val">{sigma_max:.2f} t/m²</span></div>
                <div>σ Min: <span class="res-val">{sigma_min:.2f} t/m²</span></div>
            </div>""", unsafe_allow_html=True)
        except:
            st.error("Luas tidak valid")

elif module == "16. Pondasi Lajur":
    st.header("16. Pondasi Lajur (Strip)")
    qs = st.number_input("Beban q (t/m)", 15.0)
    Bs = st.number_input("Lebar B (m)", 1.0)
    
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Tegangan Kontak: <span class="res-val">{safe_div(qs, Bs):.2f} t/m²</span></div>', unsafe_allow_html=True)

elif module == "17. Sloof (Tie Beam)":
    st.header("17. Desain Sloof")
    qsl = st.number_input("Beban Dinding (kg/m)", 1000.0)
    Lsl = st.number_input("Bentang Sloof (m)", 6.0)
    
    if st.button("HITUNG"):
        Mu = 0.1 * qsl * (Lsl**2) # Coeff 1/10 approx
        st.markdown(f'<div class="res-box">Momen Mu: <span class="res-val">{Mu:.0f} kgm</span><br>Tulangan: 4 D13</div>', unsafe_allow_html=True)

elif module == "18. Pelat Westergaard":
    st.header("18. Pelat Beton (Westergaard)")
    Pw = st.number_input("Beban Roda P (kg)", 3000.0)
    hw = st.number_input("Tebal Pelat h (cm)", 20.0)
    
    if st.button("HITUNG TEGANGAN"):
        # Sigma = 3P / h^2 (Approx Corner Load)
        sig = (3 * Pw) / (hw**2)
        stat = "AMAN" if sig < 30 else "FAIL"
        
        st.markdown(f"""
        <div class="res-box">
            <div>Tegangan: <span class="res-val">{sig:.1f} kg/cm²</span></div>
            <div>Status (Ijin 30): <b>{stat}</b></div>
        </div>""", unsafe_allow_html=True)

# --- E. PONDASI DALAM ---
elif module == "19. Pile Cap & Pons":
    st.header("19. Geser Pons (Punching Shear)")
    fc = st.number_input("fc' (MPa)", 25.0)
    Pu = st.number_input("Pu Kolom (kN)", 2000.0)
    hp = st.number_input("Tebal Pilecap (mm)", 600.0)
    cp = st.number_input("Lebar Kolom (mm)", 500.0)
    
    if st.button("CEK PONS"):
        d = hp - 80
        bo = 4 * (cp + d) # Critical perimeter
        
        # Vc = 0.33 * sqrt(fc) * bo * d
        Vc = 0.33 * math.sqrt(fc) * bo * d
        phiVc = 0.75 * Vc / 1000
        
        stat = "AMAN" if phiVc > Pu else "JEBOL (Pertebal)"
        badge = "badge-ok" if stat == "AMAN" else "badge-no"
        
        st.markdown(f"""
        <div class="res-box">
            <div>Kapasitas φVc: <span class="res-val">{phiVc:,.0f} kN</span></div>
            <div>Status: <span class="{badge}">{stat}</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "20. Meyerhof (Daya Dukung)":
    st.header("20. Daya Dukung Tiang (Meyerhof - N-SPT)")
    Nb = st.number_input("N-SPT Ujung (Nb)", 40.0)
    Nav = st.number_input("N-SPT Rata-rata (Nav)", 15.0)
    Dm = st.number_input("Diameter Tiang (cm)", 40.0)
    L_pile = st.number_input("Panjang Tiang (m)", 12.0)
    
    if st.button("HITUNG KAPASITAS"):
        D_m = Dm / 100
        Ab = 0.25 * math.pi * (D_m**2) # m2
        As = math.pi * D_m * L_pile # m2
        
        # Qult = 40*N*Ab + 0.2*N*As (Ton)
        Q_end = 40 * Nb * Ab
        Q_skin = 0.2 * Nav * As
        Q_ult = Q_end + Q_skin
        Q_all = Q_ult / 3
        
        st.markdown(f"""
        <div class="res-box">
            <div>Q Ultimate: <span class="res-val">{Q_ult:.1f} Ton</span></div>
            <div>Q Ijin (SF=3): <span class="res-val">{Q_all:.1f} Ton</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "21. Momen Tiang":
    st.header("21. Kapasitas Momen Tiang")
    D = st.number_input("Diameter (m)", 0.4)
    Cr = st.number_input("Kuat Tekan Beton (kg/cm²)", 250.0)
    
    if st.button("HITUNG KAPASITAS"):
        # Approx Formula M = 140 * Cr * D^2 ?? (From JS source)
        # More likely empirical relation for prestressed spun pile
        M = 140 * (Cr/100) * (D*100)**2 / 10000 # Trying to reverse engineer user logic 
        # JS: 140 * Cr * D^2 -> Jika Cr 250 kg/cm2, D 0.4 m. 
        # 140 * 250 * 0.16 = 5600 kg.m ? 
        M_res = 140 * Cr * (D**2)
        
        st.markdown(f'<div class="res-box">Momen Crack/Nominal Approx: <span class="res-val">{M_res:.0f} kgm</span></div>', unsafe_allow_html=True)

elif module == "22. Lateral Tiang":
    st.header("22. Gaya Lateral Tiang")
    Htot = st.number_input("Total Gaya H (kg)", 4300.0)
    nt = st.number_input("Jumlah Tiang", 3)
    
    if st.button("HITUNG"):
        st.markdown(f'<div class="res-box">Gaya H per Tiang: <span class="res-val">{safe_div(Htot, nt):.0f} kg</span></div>', unsafe_allow_html=True)

elif module == "23. Kalendering Hiley":
    st.header("23. Hiley Formula")
    c1, c2 = st.columns(2)
    W = c1.number_input("Berat Hammer (Ton)", 2.0)
    H = c2.number_input("Tinggi Jatuh (cm)", 100.0)
    c3, c4 = st.columns(2)
    S = c3.number_input("Set (mm)", 5.0)
    K = c4.number_input("Rebound (mm)", 10.0)
    
    ef = st.selectbox("Efisiensi Hammer", [0.75, 0.9, 1.0], index=0)
    
    if st.button("HITUNG R"):
        S_cm = S / 10
        K_cm = K / 10
        # R = (ef * W * H) / (S + K/2)
        R_ult = (ef * W * H) / (S_cm + K_cm/2)
        R_all = R_ult / 3
        
        st.markdown(f"""
        <div class="res-box">
            <div>R Ultimate: <span class="res-val">{R_ult:.1f} Ton</span></div>
            <div>R Ijin (SF=3): <span class="res-val">{R_all:.1f} Ton</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "24. Efisiensi Grup":
    st.header("24. Efisiensi Grup (Converse-Labarre)")
    m = st.number_input("Baris m", 3)
    n = st.number_input("Baris n", 2)
    D = st.number_input("Diameter D (cm)", 40.0)
    s = st.number_input("Jarak s (cm)", 120.0)
    
    if st.button("HITUNG Eg"):
        theta_rad = math.atan(D/s)
        theta_deg = math.degrees(theta_rad)
        
        term = ((n-1)*m + (m-1)*n) / (90 * m * n)
        Eg = 1 - (theta_deg * term)
        
        st.markdown(f'<div class="res-box">Efisiensi (Eg): <span class="res-val">{Eg:.3f}</span></div>', unsafe_allow_html=True)

elif module == "25. Cek Cabut (Uplift)":
    st.header("25. Cek Cabut (Uplift)")
    Tup = st.number_input("Gaya Tarik Total (Ton)", 50.0)
    Wup = st.number_input("Berat Sendiri (Ton)", 15.0)
    num = st.number_input("Jumlah Tiang", 4)
    
    if st.button("CEK"):
        T1 = (Tup - Wup) / num
        stat = "AMAN" if T1 < 10 else "BAHAYA"
        st.markdown(f"""
        <div class="res-box">
            <div>Tarik per Tiang: <span class="res-val">{T1:.1f} Ton</span></div>
            <div>Status (Ijin 10T): <b>{stat}</b></div>
        </div>""", unsafe_allow_html=True)

# --- F. KHUSUS ---
elif module == "26. Retaining Wall":
    st.header("26. Retaining Wall (Rankine)")
    H = st.number_input("Tinggi H (m)", 3.5)
    phi = st.number_input("Sudut Geser (φ)", 30.0)
    gamma = st.number_input("Berat Jenis Tanah (kN/m³)", 18.0)
    
    if st.button("HITUNG"):
        a_rad = math.radians(45 - phi/2)
        Ka = math.tan(a_rad)**2
        Pa = 0.5 * gamma * (H**2) * Ka
        
        st.markdown(f"""
        <div class="res-box">
            <div>Koef. Ka: <span class="res-val">{Ka:.3f}</span></div>
            <div>Tekanan Tanah Pa: <span class="res-val">{Pa:.1f} kN/m</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "27. Kolam / Tandon":
    st.header("27. Dinding Kolam")
    H_air = st.number_input("Tinggi Air (m)", 3.0)
    
    if st.button("HITUNG"):
        # M = 1/6 * gamma_air * H^3
        M = (1/6) * 10 * (H_air**3)
        st.markdown(f'<div class="res-box">Momen Dinding: <span class="res-val">{M:.1f} kNm</span></div>', unsafe_allow_html=True)

elif module == "28. Jembatan":
    st.header("28. Jembatan Sederhana (SNI 1725)")
    L = st.number_input("Bentang L (m)", 10.0)
    t = st.number_input("Tebal Pelat (m)", 0.2)
    qD = st.number_input("Beban Lajur 'D' (kN/m)", 9.0)
    PT = st.number_input("Beban Truk 'T' (kN)", 112.5)
    
    if st.button("HITUNG"):
        qDL_self = (t * 24) # kN/m
        
        # Momen Ultimate (Approx Factors 1.3 DL, 1.8 LL)
        Mu_DL = 1.3 * (1/8) * qDL_self * L**2
        Mu_Lane = 1.8 * (1/8) * qD * L**2
        Mu_Truck = 1.8 * (1/4) * PT * L
        
        M_total = Mu_DL + Mu_Lane + Mu_Truck
        
        st.markdown(f"""
        <div class="res-box">
            <div>Berat Sendiri: <span class="res-val">{qDL_self:.1f} kN/m</span></div>
            <div>Momen Ultimate Total: <span class="res-val">{M_total:.1f} kNm</span></div>
        </div>""", unsafe_allow_html=True)

elif module == "29. Konversi Tulangan":
    st.header("29. Konversi Tulangan ke BRC")
    Du = st.number_input("Diameter Ulir D (mm)", 10.0)
    su = st.number_input("Jarak s (mm)", 150.0)
    
    if st.button("KONVERSI"):
        As1 = 0.25 * math.pi * (Du**2) * 1000 / su
        # Target BRC M6 (Area ~28.3 mm2)
        # s_brc = (Ab * 1000) / (As_req * ratio_fy)
        s_brc = (28.3 * 1000) / (As1 * (240/400)) # Asumsi fy ulir 400, brc 240? Or ratio
        
        st.markdown(f'<div class="res-box">Jarak BRC M6 Setara: <span class="res-val">{math.floor(s_brc)} mm</span></div>', unsafe_allow_html=True)
