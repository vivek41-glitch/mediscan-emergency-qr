import streamlit as st
import cv2
import socket
import time
from database import init_db, insert_user, get_user
from qr_generator import generate_qr
from scanner import decode_qr_from_frame, draw_qr_box

st.set_page_config(
    page_title="MediScan — Emergency QR",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ── Helpers ──────────────────────────────────────────────
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

# ── Handle QR redirect ──────────────────────────────────
scanned_id = st.query_params.get("scan", None)
if scanned_id:
    user = get_user(scanned_id)
    if user:
        st.session_state["found_user"] = user
        st.session_state["from_qr"] = True

# ── Handle mobile nav via query params ──────────────────
nav = st.query_params.get("nav", None)
if nav == "register":
    st.session_state["_page"] = "📋  Register"
elif nav == "scanner":
    st.session_state["_page"] = "📷  Scanner"
elif nav == "home":
    st.session_state["_page"] = "🏠  Home"


# ═══════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Tokens ── */
:root {
    --primary:       #4F6EF7;
    --primary-hover: #3B5BDB;
    --primary-light: #EDF0FF;
    --primary-glow:  rgba(79,110,247,0.25);
    --accent:        #7C3AED;
    --accent-light:  #F3EEFF;
    --danger:        #EF4444;
    --danger-light:  #FEF2F2;
    --danger-glow:   rgba(239,68,68,0.15);
    --success:       #10B981;
    --success-light: #ECFDF5;
    --success-glow:  rgba(16,185,129,0.2);
    --warn:          #F59E0B;
    --warn-light:    #FFFBEB;
    --bg:            #F8FAFC;
    --surface:       #FFFFFF;
    --surface-2:     #F1F5F9;
    --border:        #E2E8F0;
    --border-focus:  #CBD5E1;
    --text-1:        #0F172A;
    --text-2:        #475569;
    --text-3:        #94A3B8;
    --radius:        14px;
    --radius-sm:     10px;
    --radius-lg:     20px;
    --shadow-sm:     0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
    --shadow:        0 4px 14px rgba(15,23,42,0.08);
    --shadow-lg:     0 10px 40px rgba(15,23,42,0.12);
    --shadow-xl:     0 20px 60px rgba(15,23,42,0.16);
    --transition:    all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text-1) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 1.5rem 2rem 4rem !important;
    max-width: 920px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.88em !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    border-radius: var(--radius-sm) !important;
    transition: var(--transition) !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
    caret-color: var(--primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9em !important;
    padding: 12px 16px !important;
    transition: var(--transition) !important;
    box-shadow: var(--shadow-sm) !important;
    -webkit-text-fill-color: var(--text-1) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px var(--primary-glow) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: var(--text-3) !important; opacity: 1 !important;
}
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
}
div[data-baseweb="select"] * { color: var(--text-1) !important; }
label { color: var(--text-2) !important; font-size: 0.82em !important; font-weight: 600 !important; letter-spacing: 0.01em !important; }
input[type="text"], input[type="number"], input[type="tel"], textarea {
    color: #000000 !important; -webkit-text-fill-color: #000000 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-2) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88em !important;
    padding: 10px 22px !important;
    transition: var(--transition) !important;
    width: 100% !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    background: var(--primary-light) !important;
    box-shadow: var(--shadow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 18px var(--primary-glow) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 30px var(--primary-glow) !important;
    transform: translateY(-2px) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--success), #059669) !important;
    border: none !important; color: white !important;
    font-weight: 600 !important; width: 100% !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 4px 16px var(--success-glow) !important;
}

/* ── Alerts ── */
.stSuccess > div { background: var(--success-light) !important; border-radius: var(--radius-sm) !important; }
.stError > div { background: var(--danger-light) !important; border-radius: var(--radius-sm) !important; }
.stInfo > div { background: var(--primary-light) !important; border-radius: var(--radius-sm) !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.8rem 0 !important; }

.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.88em !important; font-weight: 600 !important;
}

/* ─────────────────────────────────────
   CUSTOM COMPONENT STYLES
   ───────────────────────────────────── */

/* Hero */
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--primary-light);
    color: var(--primary); font-size: 0.72em; font-weight: 700;
    padding: 6px 14px; border-radius: 24px;
    letter-spacing: 0.8px; text-transform: uppercase;
    margin-bottom: 14px;
    animation: fadeInDown 0.5s ease-out;
}
.hero-title {
    font-family: 'Inter', sans-serif;
    font-size: 2.4em; font-weight: 900;
    background: linear-gradient(135deg, var(--text-1) 0%, var(--primary) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1.2px; line-height: 1.1;
    margin-bottom: 10px;
    animation: fadeInDown 0.6s ease-out;
}
.hero-sub {
    font-size: 0.92em; color: var(--text-3); line-height: 1.6;
    animation: fadeInDown 0.7s ease-out;
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Stats */
.stats-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 14px; margin: 2rem 0;
}
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px 20px;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.5s ease-out backwards;
}
.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; border-radius: var(--radius) var(--radius) 0 0;
}
.stat-card.blue::after   { background: linear-gradient(90deg, var(--primary), var(--accent)); }
.stat-card.green::after  { background: linear-gradient(90deg, var(--success), #34D399); }
.stat-card.red::after    { background: linear-gradient(90deg, var(--danger), #F97316); }
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}
.stat-icon {
    width: 42px; height: 42px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15em; margin-bottom: 14px;
}
.stat-icon.blue  { background: var(--primary-light); }
.stat-icon.green { background: var(--success-light); }
.stat-icon.red   { background: var(--danger-light); }
.stat-val {
    font-size: 1.6em; font-weight: 800;
    color: var(--text-1); letter-spacing: -0.5px;
    line-height: 1; margin-bottom: 4px;
}
.stat-lbl {
    font-size: 0.76em; color: var(--text-3);
    font-weight: 500;
}

/* Steps */
.steps-title {
    font-size: 0.72em; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--text-3); margin: 2rem 0 1rem;
}
.step-card {
    display: flex; gap: 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin: 8px 0;
    align-items: center;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    animation: fadeInUp 0.4s ease-out backwards;
}
.step-card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow);
    transform: translateX(6px);
}
.step-num {
    min-width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    color: white; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85em; flex-shrink: 0;
}
.step-icon { font-size: 1.3em; flex-shrink: 0; }
.step-t { font-weight: 700; font-size: 0.9em; color: var(--text-1); margin-bottom: 2px; }
.step-d { font-size: 0.8em; color: var(--text-3); line-height: 1.5; }

/* Net Card */
.net-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 18px;
    display: inline-flex; align-items: center; gap: 12px;
    box-shadow: var(--shadow-sm);
}
.net-dot {
    width: 10px; height: 10px;
    background: var(--success); border-radius: 50%;
    flex-shrink: 0;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 4px var(--success-glow); }
    50%      { box-shadow: 0 0 14px var(--success); }
}

/* Section Labels */
.section-label {
    font-size: 0.72em; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--primary);
    margin: 22px 0 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--primary-light);
}

/* Sidebar brand */
.sidebar-brand {
    padding: 24px 20px 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
}
.sidebar-logo {
    display: flex; align-items: center; gap: 10px; margin-bottom: 4px;
}
.logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1em;
    box-shadow: 0 4px 12px var(--primary-glow);
}
.logo-name {
    font-size: 1.15em; font-weight: 800;
    color: var(--text-1) !important; letter-spacing: -0.3px;
}
.logo-tag {
    font-size: 0.72em; color: var(--text-3) !important;
    margin-left: 48px;
}

/* Profile Table */
.p-table {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
.p-row {
    display: flex; align-items: center;
    padding: 12px 18px;
    border-bottom: 1px solid var(--border);
    font-size: 0.85em;
    transition: var(--transition);
}
.p-row:last-child { border-bottom: none; }
.p-row:hover { background: var(--surface-2); }
.p-key { width: 40%; color: var(--text-3); font-weight: 500; }
.p-val { color: var(--text-1); font-weight: 600; }

/* Registration success */
.reg-success {
    background: var(--success-light);
    border: 1px solid #A7F3D0;
    border-left: 4px solid var(--success);
    border-radius: var(--radius);
    padding: 18px 22px;
    margin: 1.5rem 0;
    display: flex; align-items: center; gap: 14px;
    animation: fadeInUp 0.5s ease-out;
}
.reg-icon {
    width: 44px; height: 44px;
    background: var(--success);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 1.2em; flex-shrink: 0;
    box-shadow: 0 4px 12px var(--success-glow);
}
.reg-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88em; color: var(--text-2);
    background: white;
    padding: 4px 12px; border-radius: 6px;
    border: 1px solid #A7F3D0;
    display: inline-block; margin-top: 4px;
    letter-spacing: 1px;
}

/* Emergency Profile */
.emergency-header {
    background: linear-gradient(135deg, #FEF2F2, #FEE2E2);
    border: 1.5px solid #FECACA;
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 1.5rem;
    animation: fadeInDown 0.4s ease-out;
}
.emergency-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--danger);
    color: white;
    font-size: 0.7em; font-weight: 700;
    padding: 5px 14px; border-radius: 20px;
    letter-spacing: 0.8px; text-transform: uppercase;
    margin-bottom: 12px;
    animation: pulse-badge 2s ease-in-out infinite;
}
@keyframes pulse-badge {
    0%, 100% { box-shadow: 0 0 8px var(--danger-glow); }
    50%      { box-shadow: 0 0 22px rgba(239,68,68,0.35); }
}
.emergency-name {
    font-size: 1.8em; font-weight: 800; color: var(--text-1);
    letter-spacing: -0.8px; line-height: 1.15;
}
.emergency-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8em; color: var(--text-3);
    margin-top: 4px;
}

.blood-badge {
    display: inline-flex; align-items: center; justify-content: center;
    background: #FEF2F2;
    border: 2.5px solid var(--danger);
    border-radius: 16px;
    padding: 16px 32px;
    font-size: 2.4em; font-weight: 900;
    color: var(--danger);
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.5px;
    box-shadow: 0 4px 18px var(--danger-glow);
    animation: fadeInUp 0.5s ease-out;
}

.detail-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    animation: fadeInUp 0.5s ease-out backwards;
}
.detail-card:hover { box-shadow: var(--shadow); }
.detail-card-label {
    font-size: 0.72em; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    color: var(--text-3);
    margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
}
.detail-card-value {
    font-size: 0.92em; font-weight: 600;
    color: var(--text-1); line-height: 1.5;
}

.contact-card {
    background: linear-gradient(135deg, var(--success-light), #D1FAE5);
    border: 1.5px solid #A7F3D0;
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    text-align: center;
    animation: fadeInUp 0.6s ease-out;
}
.contact-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8em; font-weight: 700;
    color: var(--success); letter-spacing: 1px;
    margin-bottom: 16px;
}
.call-btn {
    display: block; text-align: center;
    background: linear-gradient(135deg, var(--success), #059669);
    color: white !important; -webkit-text-fill-color: white !important;
    padding: 18px 32px;
    border-radius: var(--radius);
    font-size: 1.15em; font-weight: 700;
    text-decoration: none !important;
    letter-spacing: 0.5px;
    box-shadow: 0 6px 24px var(--success-glow);
    transition: var(--transition);
}
.call-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 36px var(--success-glow);
}

/* ── Mobile Bottom Nav ── */
.mobile-nav {
    display: none;
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid var(--border);
    padding: 8px 0 env(safe-area-inset-bottom, 20px);
    z-index: 99999;
    box-shadow: 0 -4px 24px rgba(15,23,42,0.08);
}
.mobile-nav-inner {
    display: flex; justify-content: space-around; align-items: center;
}
.mobile-nav-btn {
    display: flex; flex-direction: column;
    align-items: center; gap: 3px;
    padding: 8px 24px; border-radius: 12px;
    cursor: pointer; text-decoration: none !important;
    color: var(--text-3) !important;
    font-size: 0.68em; font-weight: 700;
    -webkit-text-fill-color: var(--text-3) !important;
    transition: var(--transition);
}
.mobile-nav-btn:active {
    color: var(--primary) !important;
    -webkit-text-fill-color: var(--primary) !important;
    background: var(--primary-light);
}
.nav-icon { font-size: 1.6em; line-height: 1; }

@media (max-width: 768px) {
    .mobile-nav { display: block !important; }
    .block-container { padding-bottom: 110px !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .hero-title { font-size: 1.8em; }
    .stats-grid { grid-template-columns: 1fr; }
    .emergency-name { font-size: 1.4em; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
ip = get_local_ip()
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
        <div class="sidebar-logo">
            <div class="logo-icon">🏥</div>
            <div class="logo-name">MediScan</div>
        </div>
        <div class="logo-tag">Emergency QR System</div>
    </div>
    """, unsafe_allow_html=True)

    default_index = 2 if st.session_state.get("from_qr") else 0
    if "_page" in st.session_state:
        options = ["🏠  Home", "📋  Register", "📷  Scanner"]
        if st.session_state["_page"] in options:
            default_index = options.index(st.session_state["_page"])

    page = st.radio("", ["🏠  Home", "📋  Register", "📷  Scanner"],
                    index=default_index, label_visibility="collapsed")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:0 4px;">
        <div class="net-card" style="width:100%;">
            <div class="net-dot"></div>
            <div>
                <div style="font-size:0.72em; color:var(--text-3); font-weight:500;">Network Address</div>
                <div style="font-family:'JetBrains Mono',monospace; color:var(--success); font-size:0.85em; font-weight:600;">{ip}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Mobile top nav buttons (hidden on desktop via sidebar) ──
m1, m2, m3 = st.columns(3)
with m1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state["_page"] = "🏠  Home"
        st.rerun()
with m2:
    if st.button("📋 Register", use_container_width=True):
        st.session_state["_page"] = "📋  Register"
        st.rerun()
with m3:
    if st.button("📷 Scanner", use_container_width=True):
        st.session_state["_page"] = "📷  Scanner"
        st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE 1 — HOME
# ══════════════════════════════════════════════════════
if page == "🏠  Home":
    st.markdown("""
    <div>
        <div class="hero-badge">🚑 Emergency System</div>
        <div class="hero-title">Medical QR<br>Identification</div>
        <div class="hero-sub">Instant emergency medical profiles — works globally, no app required</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card blue">
            <div class="stat-icon blue">⚡</div>
            <div class="stat-val">5 sec</div>
            <div class="stat-lbl">Profile Access Time</div>
        </div>
        <div class="stat-card green">
            <div class="stat-icon green">🔐</div>
            <div class="stat-val">Secure</div>
            <div class="stat-lbl">ID-Only in QR Code</div>
        </div>
        <div class="stat-card red">
            <div class="stat-icon red">📞</div>
            <div class="stat-val">1 Tap</div>
            <div class="stat-lbl">Emergency Call</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="steps-title">How It Works</div>', unsafe_allow_html=True)
    steps = [
        ("🖊️", "Register Your Profile",
         "Enter name, blood group, allergies, conditions and emergency contact"),
        ("📱", "Get Your QR Code",
         "A unique QR code is instantly generated and linked to your profile"),
        ("🖨️", "Print & Attach",
         "Print it and stick it inside your helmet or keep it in your wallet"),
        ("📷", "Scan at the Scene",
         "Rescuer scans QR with any phone — full medical profile appears instantly"),
        ("📞", "Call Emergency Contact",
         "One tap on CALL NOW dials the emergency contact immediately"),
    ]
    for i, (icon, title, desc) in enumerate(steps, 1):
        delay = 0.1 + i * 0.08
        st.markdown(f"""
        <div class="step-card" style="animation-delay:{delay}s;">
            <div class="step-num">{i}</div>
            <div class="step-icon">{icon}</div>
            <div>
                <div class="step-t">{title}</div>
                <div class="step-d">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE 2 — REGISTER
# ══════════════════════════════════════════════════════
elif page == "📋  Register":
    st.markdown("""
    <div>
        <div class="hero-badge">📋 Registration</div>
        <div class="hero-title">Create Your<br>Medical Profile</div>
        <div class="hero-sub">Fill your details once — your QR code is ready for life</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("reg_form"):
        st.markdown('<div class="section-label">Personal Information</div>',
                    unsafe_allow_html=True)
        name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")

        st.markdown('<div class="section-label">Medical Details</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            blood_group = st.selectbox(
                "Blood Group",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
            )
        with c2:
            emergency_contact = st.text_input(
                "Emergency Contact Number",
                placeholder="+91 98765 43210"
            )

        allergies = st.text_area(
            "Known Allergies",
            placeholder="e.g. Penicillin, Peanuts — write None if not applicable",
            height=80
        )
        conditions = st.text_area(
            "Medical Conditions",
            placeholder="e.g. Diabetes, Epilepsy — write None if not applicable",
            height=80
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Generate QR Code →", type="primary")

    if submitted:
        if not name.strip():
            st.error("⚠ Full name is required.")
        elif not emergency_contact.strip():
            st.error("⚠ Emergency contact number is required.")
        else:
            with st.spinner("Creating profile…"):
                user_id = insert_user(
                    name=name.strip(),
                    blood_group=blood_group,
                    allergies=allergies.strip() if allergies.strip() else "None",
                    conditions=conditions.strip() if conditions.strip() else "None",
                    emergency_contact=emergency_contact.strip()
                )
                qr_bytes = generate_qr(user_id)
                time.sleep(0.3)

            st.markdown(f"""
            <div class="reg-success">
                <div class="reg-icon">✓</div>
                <div>
                    <div style="font-weight:700; font-size:0.95em; color:var(--success);">
                        Profile registered successfully
                    </div>
                    <div style="font-size:0.8em; color:var(--text-3);">Your MediScan ID</div>
                    <div class="reg-id">{user_id}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([1, 1.1])
            with c1:
                st.image(qr_bytes, width=210)
                st.download_button(
                    "↓  Download QR Code",
                    data=qr_bytes,
                    file_name=f"MediScan_{user_id}.png",
                    mime="image/png"
                )
            with c2:
                st.markdown(f"""
                <div class="p-table">
                    <div class="p-row"><div class="p-key">Full Name</div><div class="p-val">{name}</div></div>
                    <div class="p-row"><div class="p-key">Blood Group</div><div class="p-val" style="color:var(--danger); font-size:1.05em;">{blood_group}</div></div>
                    <div class="p-row"><div class="p-key">Allergies</div><div class="p-val">{allergies or 'None'}</div></div>
                    <div class="p-row"><div class="p-key">Conditions</div><div class="p-val">{conditions or 'None'}</div></div>
                    <div class="p-row"><div class="p-key">Contact</div><div class="p-val" style="color:var(--success);">{emergency_contact}</div></div>
                    <div class="p-row"><div class="p-key">ID</div><div class="p-val" style="font-family:'JetBrains Mono',monospace; font-size:0.88em;">{user_id}</div></div>
                </div>
                <div style="font-size:0.75em; color:var(--text-3); margin-top:14px; line-height:1.9;">
                    📥 Download &nbsp;→&nbsp; 🖨 Print &nbsp;→&nbsp; 🪖 Stick on helmet
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE 3 — SCANNER
# ══════════════════════════════════════════════════════
elif page == "📷  Scanner":
    st.markdown("""
    <div>
        <div class="hero-badge">📷 Scanner</div>
        <div class="hero-title">Emergency<br>QR Scanner</div>
        <div class="hero-sub">Scan victim's QR code to retrieve full medical profile instantly</div>
    </div>
    """, unsafe_allow_html=True)

    if "scanning" not in st.session_state:
        st.session_state["scanning"] = False
    if "found_user" not in st.session_state:
        st.session_state["found_user"] = None

    if st.session_state.get("from_qr"):
        st.success("✓ QR code scanned — emergency profile loaded below")
        st.session_state["from_qr"] = False

    with st.expander("🔍  Enter ID manually (no camera needed)"):
        mid = st.text_input("MediScan ID", placeholder="MC-A3F9B2")
        if st.button("Search →"):
            if mid.strip():
                u = get_user(mid.strip().upper())
                if u:
                    st.session_state["found_user"] = u
                else:
                    st.error("No profile found for that ID.")

    if not st.session_state.get("found_user"):
        st.info("📷  Point the printed QR code toward your webcam — detection is automatic")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶  Start Camera", type="primary"):
                st.session_state["scanning"] = True
                st.session_state["found_user"] = None
        with c2:
            if st.button("■  Stop Camera"):
                st.session_state["scanning"] = False

        if st.session_state["scanning"]:
            frame_box = st.empty()
            msg_box = st.empty()
            msg_box.info("Camera active — hold QR code steady in the frame")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Cannot access camera.")
                st.session_state["scanning"] = False
            else:
                t_start = time.time()
                while st.session_state["scanning"]:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    found_id = decode_qr_from_frame(frame)
                    frm = draw_qr_box(frame.copy())
                    frm_rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
                    frame_box.image(frm_rgb, channels="RGB",
                                   use_container_width=True)
                    if found_id:
                        u = get_user(found_id)
                        if u:
                            st.session_state["found_user"] = u
                            st.session_state["scanning"] = False
                            msg_box.success(f"✓ Profile found — {found_id}")
                            break
                    if time.time() - t_start > 60:
                        msg_box.warning("Timed out. Press Start again.")
                        st.session_state["scanning"] = False
                        break
                cap.release()
                frame_box.empty()

    # ── Emergency Profile Display ────────────────────
    if st.session_state.get("found_user"):
        u = st.session_state["found_user"]

        st.markdown("---")

        # Header
        st.markdown(f"""
        <div class="emergency-header">
            <div class="emergency-badge">🆘 Emergency Medical Profile</div>
            <div class="emergency-name">👤 {u['name']}</div>
            <div class="emergency-id">MediScan ID: {u['id']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Blood Group
        st.markdown(f"""
        <div style="text-align:center; margin:1.5rem 0;">
            <div style="font-size:0.72em; font-weight:700; text-transform:uppercase;
                        letter-spacing:1.5px; color:var(--text-3); margin-bottom:10px;">
                🩸 Blood Group
            </div>
            <div class="blood-badge">{u['blood_group']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Details
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="detail-card" style="animation-delay:0.1s; border-left:3px solid var(--warn);">
                <div class="detail-card-label">⚠️ Allergies</div>
                <div class="detail-card-value">{u['allergies']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="detail-card" style="animation-delay:0.2s; border-left:3px solid var(--primary);">
                <div class="detail-card-label">🏥 Medical Conditions</div>
                <div class="detail-card-value">{u['conditions']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Emergency Contact
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="contact-card">
            <div style="font-size:0.72em; font-weight:700; text-transform:uppercase;
                        letter-spacing:1.5px; color:var(--text-3); margin-bottom:8px;">
                📞 Emergency Contact
            </div>
            <div class="contact-number">{u['emergency_contact']}</div>
            <a href="tel:{u['emergency_contact']}" class="call-btn">
                📞 &nbsp; CALL NOW
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption(f"Registered: {u['created_at']}  ·  MediScan Emergency System")

        if st.button("↩  Scan Another Profile"):
            st.session_state["found_user"] = None
            st.session_state["scanning"] = False
            st.rerun()


# ══════════════════════════════════════════════════════
#  MOBILE BOTTOM NAV
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="mobile-nav">
    <div class="mobile-nav-inner">
        <a class="mobile-nav-btn" href="?nav=home">
            <span class="nav-icon">🏠</span>
            <span>Home</span>
        </a>
        <a class="mobile-nav-btn" href="?nav=register">
            <span class="nav-icon">📋</span>
            <span>Register</span>
        </a>
        <a class="mobile-nav-btn" href="?nav=scanner">
            <span class="nav-icon">📷</span>
            <span>Scanner</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)