"""NLParto — Espace Superviseurs & Recherche
Console d'administration et de suivi clinique dédiée.
URL directe : /studentssupervisors
Accès protégé par code SHA-256.
"""
import hashlib
import os
import sys
from pathlib import Path

import streamlit as st

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NLParto — Accès Superviseurs",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS (hide sidebar + style the login screen) ─────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, sans-serif !important;
        background-color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    #MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }

    /* Login card */
    .login-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 44px 48px;
        max-width: 460px;
        margin: 80px auto 0 auto;
        box-shadow: 0 4px 32px rgba(15,23,42,0.08);
        text-align: center;
    }
    .login-icon {
        width: 64px; height: 64px;
        background: linear-gradient(135deg, #0d9488, #0f766e);
        border-radius: 18px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 20px auto;
        font-size: 2rem;
        box-shadow: 0 6px 18px rgba(13,148,136,0.28);
    }
    .login-title {
        font-size: 1.35rem; font-weight: 800;
        color: #0f172a; margin-bottom: 6px;
        letter-spacing: -0.02em;
    }
    .login-sub {
        font-size: 0.84rem; color: #64748b;
        margin-bottom: 28px; line-height: 1.5;
    }
    .login-label {
        font-size: 0.78rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.05em;
        color: #475569; margin-bottom: 8px; text-align: left;
    }
    .error-box {
        background: #fff1f2; border: 1px solid #fecdd3;
        border-radius: 10px; padding: 12px 16px;
        color: #be123c; font-size: 0.82rem;
        font-weight: 600; margin-top: 12px;
    }
    /* Style the native Streamlit input */
    [data-testid="stTextInput"] input {
        font-size: 1.05rem !important;
        letter-spacing: 0.08em !important;
        text-align: center !important;
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
        padding: 12px 16px !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #0d9488 !important;
        box-shadow: 0 0 0 3px rgba(13,148,136,0.15) !important;
    }
    /* Login button */
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #0d9488, #0f766e) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 12px 0 !important;
        width: 100% !important;
        margin-top: 4px !important;
        box-shadow: 0 4px 14px rgba(13,148,136,0.3) !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        opacity: 0.92 !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Secret hash (SHA-256 of the supervisor password) ───────────────────────
# Password: NLParto#7f9c4e8b2a1d0f5c8b3e6d2a1c4f9e7b
SUPERVISOR_HASH = "776d779e1da601c8011a53c4a0ad8cc9853a0f3fd3e29cc536b89e65e6e881c5"

def check_password(raw: str) -> bool:
    return hashlib.sha256(raw.encode()).hexdigest() == SUPERVISOR_HASH

# ─── Session state init ──────────────────────────────────────────────────────
if "supervisor_authenticated" not in st.session_state:
    st.session_state["supervisor_authenticated"] = False
if "login_failed" not in st.session_state:
    st.session_state["login_failed"] = False
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0

# ─── If not authenticated → show login screen ───────────────────────────────
if not st.session_state["supervisor_authenticated"]:

    st.markdown("""
    <div class="login-card">
        <div class="login-icon">🔐</div>
        <div class="login-title">Accès Superviseur Restreint</div>
        <div class="login-sub">
            Cette console est réservée à l'équipe de recherche NLParto.<br>
            Saisissez votre code d'accès confidentiel pour continuer.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Center the input + button in a narrow column
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="login-label">Code d\'accès confidentiel</div>', unsafe_allow_html=True)
        entered = st.text_input(
            label="Code d'accès",
            type="password",
            placeholder="••••••••••••••••",
            label_visibility="collapsed",
            key="supervisor_code_input",
        )
        login_btn = st.button("Accéder au Dashboard →", type="primary", use_container_width=True)

        if login_btn:
            if check_password(entered):
                st.session_state["supervisor_authenticated"] = True
                st.session_state["login_failed"] = False
                st.session_state["login_attempts"] = 0
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["login_failed"] = True

        if st.session_state["login_failed"]:
            attempts = st.session_state["login_attempts"]
            st.markdown(f"""
            <div class="error-box">
                ❌ Code incorrect — tentative {attempts}/5.<br>
                {"⚠️ Accès bloqué. Contactez l'équipe NLParto." if attempts >= 5 else "Vérifiez votre code et réessayez."}
            </div>
            """, unsafe_allow_html=True)

    # Hard stop — do NOT load dashboard below
    st.stop()

# ─── Authenticated → load the actual dashboard ──────────────────────────────
current_dir = Path(__file__).parent.resolve()
root_dir = current_dir.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

dash_path = root_dir / "dashboard.py"
if dash_path.exists():
    import runpy
    runpy.run_path(str(dash_path))
else:
    st.error("Le fichier dashboard.py est introuvable à la racine de l'application.")
