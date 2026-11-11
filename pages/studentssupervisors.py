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

# ─── Global CSS (hide sidebar + login screen styles) ─────────────────────────
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

    .login-title {
        font-size: 1.35rem; font-weight: 800;
        color: #0f172a; margin-bottom: 6px;
        letter-spacing: -0.02em; text-align: center;
    }
    .login-sub {
        font-size: 0.84rem; color: #64748b;
        margin-bottom: 28px; line-height: 1.5; text-align: center;
    }
    .error-box {
        background: #fff1f2; border: 1px solid #fecdd3;
        border-radius: 10px; padding: 12px 16px;
        color: #be123c; font-size: 0.82rem;
        font-weight: 600; margin-top: 12px; text-align: center;
    }
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
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #0d9488, #0f766e) !important;
        color: #ffffff !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 0.95rem !important; margin-top: 4px !important;
        box-shadow: 0 4px 14px rgba(13,148,136,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Secret hash ─────────────────────────────────────────────────────────────
# SHA-256 of: NLParto#7f9c4e8b2a1d0f5c8b3e6d2a1c4f9e7b
SUPERVISOR_HASH = "776d779e1da601c8011a53c4a0ad8cc9853a0f3fd3e29cc536b89e65e6e881c5"

def check_password(raw: str) -> bool:
    return hashlib.sha256(raw.encode()).hexdigest() == SUPERVISOR_HASH

# ─── Session state ────────────────────────────────────────────────────────────
if "supervisor_authenticated" not in st.session_state:
    st.session_state["supervisor_authenticated"] = False
if "login_failed" not in st.session_state:
    st.session_state["login_failed"] = False
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0

# ─── LOGIN SCREEN ─────────────────────────────────────────────────────────────
if not st.session_state["supervisor_authenticated"]:

    # Spacer
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div style='text-align:center; font-size:2.5rem; margin-bottom:12px'>🔐</div>", unsafe_allow_html=True)
        st.markdown('<div class="login-title">Accès Superviseur Restreint</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-sub">Cette console est réservée à l\'équipe de recherche NLParto.<br>'
            'Saisissez votre code d\'accès confidentiel pour continuer.</div>',
            unsafe_allow_html=True
        )

        entered = st.text_input(
            label="Code d'accès confidentiel",
            type="password",
            placeholder="••••••••••••••••••••",
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
            msg = "⚠️ Accès bloqué. Contactez l'équipe NLParto." if attempts >= 5 else f"❌ Code incorrect — tentative {attempts}/5. Vérifiez et réessayez."
            st.markdown(f'<div class="error-box">{msg}</div>', unsafe_allow_html=True)

    # Hard stop — do NOT load dashboard
    st.stop()

# ─── AUTHENTICATED → Logout button then dashboard ────────────────────────────
col_logout, col_title = st.columns([1, 4])
with col_logout:
    if st.button("🚪 Déconnexion", type="secondary"):
        st.session_state["supervisor_authenticated"] = False
        st.session_state["login_failed"] = False
        st.session_state["login_attempts"] = 0
        st.rerun()

# ─── Load the actual dashboard ────────────────────────────────────────────────
current_dir = Path(__file__).parent.resolve()
root_dir = current_dir.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

dash_path = root_dir / "dashboard.py"
if dash_path.exists():
    import runpy
    runpy.run_path(str(dash_path))
else:
    st.error("Le fichier dashboard.py est introuvable.")
