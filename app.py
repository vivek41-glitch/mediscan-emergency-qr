import streamlit as st
import cv2
import socket
import time
from database import init_db, insert_user, get_user
from qr_generator import generate_qr
from scanner import decode_qr_from_frame, draw_qr_box

st.set_page_config(
    page_title="MediScan",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

scanned_id = st.query_params.get("scan", None)
if scanned_id:
    user = get_user(scanned_id)
    if user:
        st.session_state["found_user"] = user
        st.session_state["from_qr"] = True

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary:      #0066FF;
    --primary-light:#EBF3FF;
    --primary-dark: #0052CC;
    --danger:       #E63946;
    --danger-light: #FFF0F1;
    --success:      #0A9E6E;
    --success-light:#E6F7F2;
    --bg:           #F4F7FC;
    --surface:      #FFFFFF;
    --surface2:     #F8FAFF;
    --border:       #E2E8F5;
    --border2:      #C8D6EE;
    --text1:        #0F1C3F;
    --text2:        #4A5878;
    --text3:        #8896B3;
    --shadow:       0 2px 12px rgba(0,30,100,0.08);
    --shadow-lg:    0 8px 32px rgba(0,30,100,0.12);
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text1) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 960px !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text1) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92em !important;
    padding: 11px 15px !important;
    transition: all 0.2s !important;
    box-shadow: var(--shadow) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(0,102,255,0.1) !important;
}
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border2) !important;
    border-radius: 10px !important;
}
label {
    color: var(--text2) !important;
    font-size: 0.8em !important;
    font-weight: 600 !important;
}

.stButton > button {
    background: var(--surface) !important;
    border: 1.5px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text2) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88em !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    width: 100% !important;
    box-shadow: var(--shadow) !important;
}
.stButton > button:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    background: var(--primary-light) !important;
}
.stButton > button[kind="primary"] {
    background: var(--primary) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(0,102,255,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--primary-dark) !important;
    box-shadow: 0 8px 28px rgba(0,102,255,0.4) !important;
    transform: translateY(-2px) !important;
}
.stDownloadButton > button {
    background: var(--success) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    width: 100% !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 16px rgba(10,158,110,0.3) !important;
}

.stSuccess > div { background: var(--success-light) !important; border-radius: 10px !important; }
.stError > div { background: var(--danger-light) !important; border-radius: 10px !important; }
.stInfo > div { background: var(--primary-light) !important; border-radius: 10px !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 2rem 0 !important; }

.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1.5px solid var(--border2) !important;
    border-radius: 10px !important;
    font-size: 0.88em !important;
    font-weight: 600 !important;
}

/* Page header */
.page-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--primary-light);
    color: var(--primary);
    font-size: 0.72em;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.page-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2em;
    font-weight: 800;
    color: var(--text1);
    letter-spacing: -0.8px;
    line-height: 1.15;
    margin-bottom: 8px;
}
.page-sub { font-size: 0.9em; color: var(--text3); }

/* Stats */
.stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 2rem 0;
}
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 20px;
    box-shadow: var(--shadow);
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--primary);
    border-radius: 16px 16px 0 0;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
.stat-icon-wrap {
    width: 44px; height: 44px;
    background: var(--primary-light);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2em; margin-bottom: 14px;
}
.stat-value { font-size: 1.6em; font-weight: 800; color: var(--text1); letter-spacing: -0.5px; line-height: 1; }
.stat-label { font-size: 0.78em; color: var(--text3); margin-top: 5px; font-weight: 500; }

/* Steps */
.how-title { font-size: 0.72em; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: var(--text3); margin: 2rem 0 1rem; }
.step-row {
    display: flex; gap: 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px 18px; margin: 8px 0;
    align-items: center;
    box-shadow: var(--shadow);
    transition: all 0.2s;
}
.step-row:hover { border-color: var(--primary); box-shadow: var(--shadow-lg); transform: translateX(4px); }
.step-bubble {
    min-width: 34px; height: 34px;
    background: var(--primary); color: white;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85em; flex-shrink: 0;
}
.step-t { font-weight: 700; font-size: 0.92em; color: var(--text1); margin-bottom: 2px; }
.step-d { font-size: 0.8em; color: var(--text3); line-height: 1.5; }

/* Net card */
.net-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px 18px;
    display: inline-flex; align-items: center; gap: 12px;
    box-shadow: var(--shadow);
}
.net-dot {
    width: 10px; height: 10px;
    background: var(--success); border-radius: 50%; flex-shrink: 0;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 4px var(--success); }
    50% { box-shadow: 0 0 14px var(--success); }
}

/* Form */
.section-label {
    font-size: 0.72em; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--primary); margin: 20px 0 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--primary-light);
}

/* Sidebar brand */
.sidebar-brand { padding: 24px 20px 18px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }
.sidebar-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.logo-icon {
    width: 36px; height: 36px;
    background: var(--primary); border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1em;
}
.logo-name { font-size: 1.2em; font-weight: 800; color: var(--text1) !important; letter-spacing: -0.3px; }
.logo-tag { font-size: 0.72em; color: var(--text3) !important; margin-left: 46px; }

/* profile table */
.p-table { background: var(--surface2); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
.p-row { display: flex; align-items: center; padding: 11px 16px; border-bottom: 1px solid var(--border); font-size: 0.85em; }
.p-row:last-child { border-bottom: none; }
.p-key { width: 40%; color: var(--text3); font-weight: 500; }
.p-val { color: var(--text1); font-weight: 600; }

/* reg success */
.reg-box {
    background: var(--success-light); border: 1px solid #A7E8D4;
    border-left: 4px solid var(--success); border-radius: 14px;
    padding: 18px 22px; margin: 1.5rem 0;
    display: flex; align-items: center; gap: 14px;
}
.reg-box-icon {
    width: 40px; height: 40px; background: var(--success);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    color: white; font-size: 1.1em; flex-shrink: 0;
}
.reg-box-id {
    font-family: 'JetBrains Mono', monospace; font-size: 0.88em;
    color: var(--text2); background: white;
    padding: 3px 10px; border-radius: 6px;
    border: 1px solid #A7E8D4; display: inline-block; margin-top: 4px; letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ══ SIDEBAR ════════════════════════════════════════════════
ip = get_local_ip()
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
        <div class="sidebar-logo">
            <div class="logo-icon">🏥</div>
            <div class="logo-name">MediScan</div>
        </div>
        <div class="logo-tag">Emergency QR Identification System</div>
    </div>
    """, unsafe_allow_html=True)

    default_index = 2 if st.session_state.get("from_qr") else 0
    page = st.radio("", ["🏠  Home", "📋  Register", "📷  Scanner"], index=default_index, label_visibility="collapsed")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:0 4px;">
        <div class="net-card" style="width:100%;">
            <div class="net-dot"></div>
            <div>
                <div style="font-size:0.72em; color:var(--text3);">Network Address</div>
                <div style="font-family:monospace; color:var(--success); font-size:0.85em; font-weight:600;">{ip}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 1 — HOME
# ══════════════════════════════════════════════════════════
if page == "🏠  Home":
    st.markdown("""
    <div>
        <div class="page-badge">🚑 Emergency System</div>
        <div class="page-title">Medical QR<br>Identification</div>
        <div class="page-sub">Instant victim identification at accident scenes — no internet required</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-icon-wrap">⚡</div>
            <div class="stat-value">5 sec</div>
            <div class="stat-label">Profile Access Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon-wrap">🔐</div>
            <div class="stat-value">Secure</div>
            <div class="stat-label">ID Only in QR</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon-wrap">📞</div>
            <div class="stat-value">1 Tap</div>
            <div class="stat-label">Emergency Call</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="how-title">How it works</div>', unsafe_allow_html=True)
    steps = [
        ("🖊", "Register Your Profile", "Enter name, blood group, allergies, conditions and emergency contact"),
        ("📱", "Get Your QR Code", "A unique QR code is instantly generated and linked to your profile"),
        ("🖨", "Print & Attach", "Print it and stick it inside your helmet or keep it in your wallet"),
        ("📷", "Scan at Scene", "Rescuer scans QR with any phone — full medical profile appears instantly"),
        ("📞", "Call Emergency Contact", "One tap on CALL NOW dials the emergency contact immediately"),
    ]
    for i, (icon, title, desc) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="step-row">
            <div class="step-bubble">{i}</div>
            <div style="font-size:1.2em; margin:0 4px;">{icon}</div>
            <div>
                <div class="step-t">{title}</div>
                <div class="step-d">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="net-card" style="margin-top:2rem;">
        <div class="net-dot"></div>
        <div>
            <div style="font-size:0.78em; color:var(--text3);">App running on your network</div>
            <div style="font-family:monospace; color:var(--text1); font-size:0.88em; font-weight:500;">http://{ip}:PORT</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — REGISTER
# ══════════════════════════════════════════════════════════
elif page == "📋  Register":
    st.markdown("""
    <div>
        <div class="page-badge">📋 Registration</div>
        <div class="page-title">Create Your<br>Medical Profile</div>
        <div class="page-sub">Fill your details once — your QR code is ready for life</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("reg_form"):
        st.markdown('<div class="section-label">Personal Information</div>', unsafe_allow_html=True)
        name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")

        st.markdown('<div class="section-label">Medical Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            blood_group = st.selectbox("Blood Group", ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"])
        with c2:
            emergency_contact = st.text_input("Emergency Contact Number", placeholder="+91 98765 43210")

        allergies = st.text_area("Known Allergies", placeholder="e.g. Penicillin, Peanuts — write None if not applicable", height=80)
        conditions = st.text_area("Medical Conditions", placeholder="e.g. Diabetes, Epilepsy — write None if not applicable", height=80)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Generate QR Code →", type="primary")

    if submitted:
        if not name.strip():
            st.error("⚠ Full name is required.")
        elif not emergency_contact.strip():
            st.error("⚠ Emergency contact number is required.")
        else:
            port = 8501  # ← Change to your terminal port

            with st.spinner("Creating profile..."):
                user_id = insert_user(
                    name=name.strip(),
                    blood_group=blood_group,
                    allergies=allergies.strip() if allergies.strip() else "None",
                    conditions=conditions.strip() if conditions.strip() else "None",
                    emergency_contact=emergency_contact.strip()
                )
                qr_bytes = generate_qr(user_id, port=port)
                time.sleep(0.3)

            st.markdown(f"""
            <div class="reg-box">
                <div class="reg-box-icon">✓</div>
                <div>
                    <div style="font-weight:700; font-size:0.92em; color:var(--success);">Profile registered successfully</div>
                    <div style="font-size:0.8em; color:var(--text3);">Your MediScan ID</div>
                    <div class="reg-box-id">{user_id}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([1, 1.1])
            with c1:
                st.image(qr_bytes, width=210)
                st.download_button("↓  Download QR Code", data=qr_bytes, file_name=f"MediScan_{user_id}.png", mime="image/png")
            with c2:
                st.markdown(f"""
                <div class="p-table">
                    <div class="p-row"><div class="p-key">Full Name</div><div class="p-val">{name}</div></div>
                    <div class="p-row"><div class="p-key">Blood Group</div><div class="p-val" style="color:#E63946; font-size:1.05em;">{blood_group}</div></div>
                    <div class="p-row"><div class="p-key">Allergies</div><div class="p-val">{allergies or 'None'}</div></div>
                    <div class="p-row"><div class="p-key">Conditions</div><div class="p-val">{conditions or 'None'}</div></div>
                    <div class="p-row"><div class="p-key">Contact</div><div class="p-val" style="color:#0A9E6E;">{emergency_contact}</div></div>
                    <div class="p-row"><div class="p-key">ID</div><div class="p-val" style="font-family:monospace; font-size:0.88em;">{user_id}</div></div>
                </div>
                <div style="font-size:0.75em; color:#8896B3; margin-top:12px; line-height:1.8;">
                    📥 Download &nbsp;→&nbsp; 🖨 Print &nbsp;→&nbsp; 🪖 Stick on helmet
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — SCANNER
# ══════════════════════════════════════════════════════════
elif page == "📷  Scanner":
    st.markdown("""
    <div>
        <div class="page-badge">📷 Scanner</div>
        <div class="page-title">Emergency<br>QR Scanner</div>
        <div class="page-sub">Scan victim's QR code to retrieve full medical profile instantly</div>
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
        mid = st.text_input("MediScan ID", placeholder="MS-A3F9B2")
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
                    frame_box.image(frm_rgb, channels="RGB", use_container_width=True)
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

    # ══ EMERGENCY CARD — pure Streamlit, no HTML ════════════
    if st.session_state["found_user"]:
        u = st.session_state["found_user"]

        st.markdown("---")

        # Top alert bar
        st.error(f"🆘  EMERGENCY MEDICAL PROFILE  ·  {u['id']}")

        # Name
        st.markdown(f"# 👤 {u['name']}")
        st.caption(f"MediScan ID: {u['id']}")

        st.markdown("---")

        # Blood group — big
        st.markdown("### 🩸 Blood Group")
        st.markdown(
            f"<div style='display:inline-block; background:#FFF0F1; border:2px solid #E63946;"
            f"border-radius:14px; padding:14px 28px; font-size:2.2em; font-weight:800;"
            f"color:#E63946; font-family:Plus Jakarta Sans,sans-serif; letter-spacing:-0.5px;'>"
            f"{u['blood_group']}</div>",
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Allergies and Conditions side by side
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**⚠️ Allergies**")
            st.warning(u['allergies'])
        with c2:
            st.markdown("**🏥 Medical Conditions**")
            st.info(u['conditions'])

        st.markdown("---")

        # Emergency contact
        st.markdown("### 📞 Emergency Contact")
        st.markdown(
            f"<div style='font-family:JetBrains Mono,monospace; font-size:1.8em; font-weight:700;"
            f"color:#0A9E6E; letter-spacing:1px; margin-bottom:14px;'>{u['emergency_contact']}</div>",
            unsafe_allow_html=True
        )

        # CALL NOW — simple anchor, always works on phone
        st.markdown(
            f"<a href='tel:{u['emergency_contact']}' style='"
            f"display:block; text-align:center; background:#0A9E6E; color:white;"
            f"padding:18px; border-radius:14px; font-size:1.2em; font-weight:700;"
            f"text-decoration:none; letter-spacing:0.5px;"
            f"box-shadow:0 6px 20px rgba(10,158,110,0.4);'>"
            f"📞 &nbsp; CALL NOW</a>",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.caption(f"Registered: {u['created_at']}  ·  MediScan Emergency System")

        if st.button("↩  Scan Another Profile"):
            st.session_state["found_user"] = None
            st.session_state["scanning"] = False
            st.rerun()