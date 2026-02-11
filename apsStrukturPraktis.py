import streamlit as st
import math
import google.generativeai as genai
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(
    page_title="Smart_Engineer OMNI-X (Integrated)",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi Session State (Tas Data Global)
if 'global_Wt' not in st.session_state: st.session_state['global_Wt'] = 5000.0
if 'global_V' not in st.session_state: st.session_state['global_V'] = 1500.0
if 'global_fc' not in st.session_state: st.session_state['global_fc'] = 25.0
if 'global_fy' not in st.session_state: st.session_state['global_fy'] = 400.0

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E0E0E0; }
    section[data-testid="stSidebar"] * { color: #000000 !important; }
    section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] select {
        background-color: #F5F5F5 !important; border: 1px solid #CCCCCC; color: #000000 !important;
    }

    /* HEADINGS */
    h1, h2, h3 { color: #0D47A1; font-family: 'Segoe UI', sans-serif; font-weight: 800; }
    
    /* RESULT BOX */
    .res-box {
        background-color: #FFFFFF; padding: 25px; border-radius: 10px;
        border-left: 8px solid #FF6F00; margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: #263238;
    }
    
    /* STEEL RES */
    .steel-res {
        background-color: #E8F5E9; padding: 15px; border-radius: 8px;
        margin-top: 15px; border: 1px solid #C8E6C9;
    }
    
    .res-label { font-weight: 600; color: #455A64; font-size: 0.95rem; display: block; margin-bottom: 2px; }
    .res-val { font-weight: 800; color: #0D47A1; font-size: 1.3rem; font-family: 'Consolas', monospace; }
    .res-steel { font-weight: 900; color: #2E7D32; font-size: 1.4rem; font-family: 'Consolas', monospace; }
    
    /* BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #0D47A1, #1565C0); color: white; font-weight: bold; border: none;
        width: 100%; padding: 12px; border-radius: 6px; transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 5px 15px rgba(13, 71, 161, 0.2);
        background: linear-gradient(135deg, #FF6F00, #F57C00); color: white !important;
    }

    /* BADGES */
    .badge-ok { background-color: #2E7D32; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85rem;}
    .badge-no { background-color: #C62828; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85rem;}
    
    /* FOOTER */
    .sidebar-footer {
        text-align: center; margin-top: 30px; padding: 20px;
        background: #FFEBEE; border-top: 2px solid #FFCDD2; border-radius: 8px;
    }
    .footer-email { color: #000000 !important; font-weight: bold; font-size: 0.8rem; }
    .footer-donasi { color: #D50000 !important; font-weight: 900; margin-top: 10px; font-size: 0.9rem; text-transform: uppercase; }
    .footer-norek { color: #D50000 !important; font-family: monospace; font-size: 1.1rem; font-weight: 900; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI TEKNIS (CORE ENGINE SNI UPDATE)
# ==========================================

def safe_div(n, d, default=0.0):
    return n / d if d != 0 else default

def get_steel_area(diameter):
    return 0.25 * math.pi * (diameter**2)

# --- ENGINE GEMPA SNI 1726:2019 (INTERPOLASI) ---
def get_site_coefficients(site_class, Ss, S1):
    def interp(x, x1, x2, y1, y2):
        return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

    fa_table = {
        "SA": [0.8, 0.8, 0.8, 0.8, 0.8],
        "SB": [1.0, 1.0, 1.0, 1.0, 1.0],
        "SC": [1.2, 1.2, 1.1, 1.0, 1.0],
        "SD": [1.6, 1.4, 1.2, 1.1, 1.0],
        "SE": [2.5, 1.7, 1.2, 0.9, 0.9],
        "SF": [None, None, None, None, None]
    }
    
    fv_table = {
        "SA": [0.8, 0.8, 0.8, 0.8, 0.8],
        "SB": [1.0, 1.0, 1.0, 1.0, 1.0],
        "SC": [1.7, 1.6, 1.5, 1.4, 1.3],
        "SD": [2.4, 2.0, 1.8, 1.6, 1.5],
        "SE": [3.5, 3.2, 2.8, 2.4, 2.4],
        "SF": [None, None, None, None, None]
    }

    vals_fa = fa_table.get(site_class)
    if not vals_fa or vals_fa[0] is None: return None, None
    
    if Ss <= 0.25: Fa = vals_fa[0]
    elif Ss <= 0.50: Fa = interp(Ss, 0.25, 0.50, vals_fa[0], vals_fa[1])
    elif Ss <= 0.75: Fa = interp(Ss, 0.50, 0.75, vals_fa[1], vals_fa[2])
    elif Ss <= 1.00: Fa = interp(Ss, 0.75, 1.00, vals_fa[2], vals_fa[3])
    elif Ss < 1.25:  Fa = interp(Ss, 1.00, 1.25, vals_fa[3], vals_fa[4])
    else: Fa = vals_fa[4]

    vals_fv = fv_table.get(site_class)
    if S1 <= 0.1: Fv = vals_fv[0]
    elif S1 <= 0.2: Fv = interp(S1, 0.1, 0.2, vals_fv[0], vals_fv[1])
    elif S1 <= 0.3: Fv = interp(S1, 0.2, 0.3, vals_fv[1], vals_fv[2])
    elif S1 <= 0.4: Fv = interp(S1, 0.3, 0.4, vals_fv[2], vals_fv[3])
    elif S1 < 0.5:  Fv = interp(S1, 0.4, 0.5, vals_fv[3], vals_fv[4])
    else: Fv = vals_fv[4]

    return Fa, Fv

# --- ENGINE BETON SNI 2847:2019 (PHI DINAMIS) ---
def get_beta1(fc):
    if fc <= 28: return 0.85
    elif fc >= 55: return 0.65
    else: return 0.85 - 0.05 * (fc - 28) / 7

def calculate_phi_moment(d, c, ty_strain=0.002, spiral=False):
    if c <= 0: return 0.90, 0.0, "Terkendali Tarik"
    dt = d 
    epsilon_t = 0.003 * (dt - c) / c
    
    if epsilon_t >= 0.005:
        return 0.90, epsilon_t, "Terkendali Tarik (Aman)"
    elif epsilon_t <= ty_strain:
        phi = 0.75 if spiral else 0.65
        return phi, epsilon_t, "Terkendali Tekan (Getas!)"
    else:
        phi_min = 0.75 if spiral else 0.65
        phi = phi_min + (epsilon_t - ty_strain) * (0.25 / (0.005 - ty_strain))
        return phi, epsilon_t, "Zona Transisi"

# --- VISUALISASI ---
def draw_beam_section(b, h, n_top, n_bottom, diameter_main, diameter_stirrup, title="Detail Balok"):
    fig, ax = plt.subplots(figsize=(4, (h/b)*3.5 if b>0 else 4))
    concrete = patches.Rectangle((0, 0), b, h, linewidth=2, edgecolor='#555', facecolor='#E0E0E0')
    ax.add_patch(concrete)
    cover = 40
    stirrup = patches.Rectangle((cover, cover), b-2*cover, h-2*cover, linewidth=2, edgecolor='#D32F2F', facecolor='none', linestyle='--')
    ax.add_patch(stirrup)
    
    def draw_bar(x, y, d, color='#1565C0'):
        circle = patches.Circle((x, y), d/2, linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(circle)

    y_bot = cover + diameter_stirrup + diameter_main/2
    y_top = h - (cover + diameter_stirrup + diameter_main/2)
    
    if n_bottom > 0:
        if n_bottom == 1: draw_bar(b/2, y_bot, diameter_main)
        else:
            spacing = (b - 2*cover - 2*diameter_stirrup - diameter_main) / (n_bottom - 1)
            for i in range(n_bottom):
                draw_bar(cover + diameter_stirrup + diameter_main/2 + (i * spacing), y_bot, diameter_main)
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
    
    bars = [(cover+10, cover+10), (b-cover-10, cover+10), (b-cover-10, h-cover-10), (cover+10, h-cover-10)]
    sisa = n_total - 4
    if sisa > 0:
        bars.append((b/2, cover+10)); bars.append((b/2, h-cover-10))
        if sisa > 2: bars.append((cover+10, h/2)); bars.append((b-cover-10, h/2))

    for (x, y) in bars:
        ax.add_patch(patches.Circle((x, y), diameter_main/2, edgecolor='black', facecolor='#1565C0'))

    ax.set_xlim(-50, b+50); ax.set_ylim(-50, h+50)
    plt.axis('off'); plt.title("Detail Kolom", fontweight='bold')
    return fig

# --- LOGIKA PRAKTIS ---
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

gems_persona = {
    "👑 The GEMS Grandmaster": "Anda adalah Direktur Proyek. Jawab dengan data teknis, SNI, dan solusi konkret.",
    "🏗️ Ahli Struktur": "Anda Ahli Struktur SNI 2847. Fokus pada beton, baja, dan detailing.",
    "🪨 Ahli Geoteknik": "Anda Ahli Geoteknik SNI 8460. Fokus pada pondasi.",
}

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px; border-bottom: 2px solid #0D47A1; margin-bottom: 20px;">
        <h2 style="color:#0D47A1 !important; margin:0; font-size: 1.8rem; font-weight: 900;">Smart_Engineer</h2>
        <span style="color:#FF6F00 !important; font-weight:bold; letter-spacing:2px; font-size:0.8rem;">INTEGRATED VER</span>
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

    st.markdown("---")
    with st.expander("🤖 KONSULTASI AI", expanded=False):
        api_key = st.text_input("🔑 Google API Key:", type="password")
        selected_model = st.selectbox("Model:", ["models/gemini-pro-latest", "models/gemini-flash-latest"], index=1)
        if prompt := st.chat_input("Tanya AI..."):
            if not api_key: st.error("API Key Kosong!")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model_ai = genai.GenerativeModel(selected_model)
                    response = model_ai.generate_content(f"User bertanya teknik sipil: {prompt}")
                    st.write(response.text)
                except Exception as e: st.error(f"Error: {e}")

    st.markdown("""
    <div class="sidebar-footer">
        <div class="footer-email">by smartstudioarsitek@gmail.com</div>
        <div class="footer-donasi">Donasi : Bank Jago Syariah</div>
        <div class="footer-norek">5028 4297 0355</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIKA PERHITUNGAN (INTEGRATED)
# ==========================================

if category == "🏠 DASHBOARD":
    st.title("🚀 Smart_Engineer Dashboard")
    st.info("💡 **Tips Integrasi:** Hitung Beban di Modul 1, lalu Gempa di Modul 5. Data akan mengalir otomatis!")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Wt (Beban Gempa)", f"{st.session_state['global_Wt']:,.0f} kN")
    col2.metric("V (Base Shear)", f"{st.session_state['global_V']:,.0f} kN")
    col3.metric("Mutu Beton (fc')", f"{st.session_state['global_fc']} MPa")

# --- A. BEBAN & ATAP ---
elif module == "1. Analisis Beban (Wt)":
    st.header("1. Analisis Beban (Wt)")
    st.info("Output Wt akan disimpan otomatis untuk perhitungan Gempa (Modul 5).")
    
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
    
    if st.button("HITUNG & SIMPAN DATA"):
        Wa = A1 * (D1 + 0.3*L1)
        Wt_typ = A2 * (D2 + 0.3*L2) * N_typ
        Wt_tot = (Wa + Wt_typ)/100 
        
        # LINK DATA: SIMPAN KE SESSION STATE
        st.session_state['global_Wt'] = Wt_tot
        
        st.toast(f"✅ Data Wt {Wt_tot:.2f} kN tersimpan ke Memory!", icon="💾")
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
        st.markdown(f'<div class="res-box"><div>Mx: <span class="res-val">{Mx:.0f} kgcm</span></div><div>Tegangan: {sig:.0f} kg/cm²</div><div>Lendutan: {del_val:.2f} cm</div><div>Status: <span class="badge-ok">{status}</span></div></div>', unsafe_allow_html=True)

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
    st.header("5. Gempa SNI 1726:2019 (High Precision)")
    
    # LINK DATA: AMBIL WT DARI SESSION STATE
    val_Wt = st.session_state['global_Wt']
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        site_class = st.selectbox("Kelas Situs (Tanah)", ["SA", "SB", "SC", "SD", "SE"])
        Ss = st.number_input("Ss (Peta Gempa)", value=0.9, format="%.3f")
    with col_t2:
        R_val = st.selectbox("Sistem R", [8, 5, 3], index=0) 
        S1 = st.number_input("S1 (Peta Gempa)", value=0.4, format="%.3f")
    
    Ie_val = st.selectbox("Faktor Keutamaan (Ie)", [1.0, 1.25, 1.5])
    
    # INPUT FIELD OTOMATIS TERISI WT DARI MODUL 1
    Wt = st.number_input("Berat Seismik Wt (kN)", value=val_Wt)
    if val_Wt != 5000.0: st.caption("ℹ️ Nilai Wt diambil otomatis dari Modul 1.")
    
    if st.button("HITUNG & SIMPAN V BASE"):
        Fa, Fv = get_site_coefficients(site_class, Ss, S1)
        
        if Fa is not None:
            Sms = Fa * Ss
            Sm1 = Fv * S1
            Sds = (2/3) * Sms
            Sd1 = (2/3) * Sm1
            Cs_calc = Sds / (R_val / Ie_val)
            V = Cs_calc * Wt
            
            # LINK DATA: SIMPAN V KE SESSION STATE
            st.session_state['global_V'] = V
            st.toast(f"✅ Base Shear V = {V:,.0f} kN tersimpan!", icon="💾")
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown(f'<div class="res-box"><div>Fa: <b>{Fa:.3f}</b> | Fv: <b>{Fv:.3f}</b></div><hr><div>SDS: <span class="res-val">{Sds:.3f} g</span></div><div>SD1: <span class="res-val">{Sd1:.3f} g</span></div></div>', unsafe_allow_html=True)
            with col_res2:
                 st.markdown(f'<div class="res-box" style="border-left: 8px solid #2E7D32;"><div>Gaya Geser Dasar (V):</div><div class="res-val">{V:,.0f} kN</div></div>', unsafe_allow_html=True)
        else:
            st.error("Kelas Situs SF butuh investigasi khusus!")

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

# --- C. STRUKTUR ATAS ---
elif module == "8. Pelat Lantai":
    st.header("8. Pelat Lantai")
    lx = st.number_input("Lx (m)", 3.0)
    ly = st.number_input("Ly (m)", 4.0)
    qp = st.number_input("Beban Total (kg/m2)", 600.0)
    tebal_plat = st.number_input("Tebal Pelat (mm)", 120.0)
    
    if st.button("HITUNG & DESAIN"):
        M = 0.001 * qp * (lx**2) * 25 
        Mu_kNm = M / 100
        d = tebal_plat - 20
        Mn = Mu_kNm * 1e6 / 0.8
        Rn = Mn / (1000 * d**2)
        try:
            rho_approx = 0.85 * 25 / 240 * (1 - math.sqrt(1 - (2*Rn)/(0.85*25)))
            As_req = rho_approx * 1000 * d
            As_final, tulangan_fix = auto_design_slab(As_req, tebal_plat)
            st.markdown(f'<div class="res-box"><div>Mu: {Mu_kNm:.2f} kNm</div><div class="steel-res"><div>As Perlu: {As_final:.0f} mm²</div><div>Tulangan: <span class="res-steel">{tulangan_fix}</span></div></div></div>', unsafe_allow_html=True)
        except: st.error("Tebal Pelat Terlalu Tipis!")

elif module == "9. Lendutan Pelat":
    st.header("9. Lendutan Pelat")
    Lx = st.number_input("Lx (cm)", 300.0)
    h = st.number_input("Tebal h (cm)", 12.0)
    if st.button("CEK"):
        hmin = Lx/28
        stat = "OK" if h >= hmin else "LENDUT"
        st.markdown(f'<div class="res-box">h min: {hmin:.1f} cm <br> Status: {stat}</div>', unsafe_allow_html=True)

elif module == "10. Desain Balok":
    st.header("10. Desain Balok (Strain-Based SNI)")
    
    # LINK DATA: INPUT MATERIAL (BISA DISIMPAN UNTUK KOLOM)
    c1, c2 = st.columns(2)
    fc = c1.number_input("fc' (MPa)", value=st.session_state['global_fc'])
    fy = c2.number_input("fy (MPa)", value=st.session_state['global_fy'])
    
    c3, c4 = st.columns(2)
    b = c3.number_input("b (mm)", 300.0)
    h = c4.number_input("h (mm)", 600.0)
    Mu = st.number_input("Mu (kNm)", 150.0)
    ds = st.number_input("Decking (mm)", 40.0)
    
    if st.button("DESAIN & SIMPAN DATA MATERIAL"):
        # LINK DATA: UPDATE GLOBAL MATERIAL
        st.session_state['global_fc'] = fc
        st.session_state['global_fy'] = fy
        st.toast("Data Material fc & fy diperbarui!", icon="🧱")
        
        d = h - ds
        beta1 = get_beta1(fc)
        phi_trial = 0.9
        Mu_Nmm = Mu * 1e6
        
        try:
            Mn_trial = Mu_Nmm / phi_trial
            Rn = Mn_trial / (b * d**2)
            m = fy / (0.85 * fc)
            rho = (1/m) * (1 - math.sqrt(1 - (2*m*Rn)/fy))
            As_req = rho * b * d
            
            a_actual = (As_req * fy) / (0.85 * fc * b)
            c_actual = a_actual / beta1
            phi_fix, epsilon_t, status_str = calculate_phi_moment(d, c_actual)
            
            Mn_final = As_req * fy * (d - a_actual/2)
            Mu_capacity = phi_fix * Mn_final / 1e6
            tulangan_utama = auto_design_beam(As_req, b)
            
            st.success(f"✅ Analisis: {status_str}")
            col_res, col_img = st.columns([1.5, 1])
            with col_res:
                st.markdown(f'<div class="res-box"><div>Beta1: {beta1:.2f} | εt: <b>{epsilon_t:.4f}</b></div><div>Faktor Reduksi (φ): <b>{phi_fix:.3f}</b></div><hr><div class="steel-res"><div>As Perlu: {As_req:.0f} mm²</div><div>Tulangan: <span class="res-steel">{tulangan_utama}</span></div><div>Kap. (φMn): {Mu_capacity:.1f} kNm</div></div></div>', unsafe_allow_html=True)
            with col_img:
                parts = tulangan_utama.split(' D')
                try: n_bars = int(parts[0]); d_bars = int(parts[1])
                except: n_bars = 4; d_bars = 16
                fig = draw_beam_section(b, h, 2, n_bars, d_bars, 8)
                st.pyplot(fig)
        except ValueError: st.error("❌ Penampang terlalu kecil!")

elif module == "11. Torsi Balok":
    st.header("11. Torsi Balok")
    Tu = st.number_input("Tu (kNm)", 10.0)
    Tcr = st.number_input("Tcr (kNm)", 15.0)
    if st.button("CEK"):
        stat = "ABAIKAN" if Tu < 0.25*Tcr else "HITUNG"
        st.markdown(f'<div class="res-box">Status: <span class="res-val">{stat}</span></div>', unsafe_allow_html=True)

elif module == "12. Desain Kolom":
    st.header("12. Desain Kolom")
    
    # LINK DATA: AMBIL MATERIAL DARI GLOBAL
    fc = st.number_input("fc' (MPa)", value=st.session_state['global_fc'])
    fy = 400.0 # Default tulangan
    
    b = st.number_input("b (mm)", 500.0)
    h = st.number_input("h (mm)", 500.0)
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
            st.markdown(f'<div class="res-box"><div>Kapasitas (ρ=1%): <span class="res-val">{phiPn:.0f} kN</span></div><div>Status: <span class="badge-ok">{stat}</span></div><div class="steel-res"><div>Tulangan: <span class="res-steel">{n_bars} D19</span></div></div></div>', unsafe_allow_html=True)
        with col_img:
            fig = draw_column_section(b, h, n_bars, 19)
            st.pyplot(fig)

elif module == "13. Shear Wall":
    st.header("13. Shear Wall")
    
    # LINK DATA: AMBIL V GEMPA DARI GLOBAL
    val_V = st.session_state['global_V']
    
    fc = st.number_input("fc' (MPa)", value=st.session_state['global_fc'])
    lw = st.number_input("lw (mm)", 4000.0)
    tw = st.number_input("tebal (mm)", 250.0)
    
    # OTOMATIS TERISI DARI MODUL GEMPA
    Vu = st.number_input("Vu (kN)", value=val_V)
    if val_V != 1500.0: st.caption("ℹ️ Vu diambil otomatis dari Base Shear Modul 5.")

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
        st.markdown(f'<div class="res-box"><div>Mu: {Mu:.0f} kgm</div><div class="steel-res"><div>Tulangan: <span class="res-steel">4 D13</span></div><div>Sengkang: Ø8-200</div></div></div>', unsafe_allow_html=True)

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
