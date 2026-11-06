"""NLParto - Plateforme de Validation Clinique & Dashboard Superviseur
Design Médical Professionnel inspiré des composants 21st.dev (Thème Emerald Slate & Approval Card).
Zéro gradient IA superflu, icônes vectorielles médicales pures, ergonomie hospitalière directe.
"""
import os
import sys
import uuid
from pathlib import Path
import streamlit as st

# Import du gestionnaire d'état
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from state import (
    get_or_create_batch,
    save_review,
    release_batch,
    TEST_MODE,
    REVIEWS_CSV,
    POOL_CSV
)

# -----------------------------------------------------------------------------
# Configuration Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NLParto — Revue Clinique & Dashboard",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Bibliothèque d'Icônes Vectorielles Médicales (SVG Purs & Précis — ZÉRO Emoji)
# -----------------------------------------------------------------------------
ICONS = {
    "stethoscope": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/></svg>',
    "shield_check": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "user_md": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M12 11v4"/><path d="M10 13h4"/></svg>',
    "message_clinical": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "languages": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/></svg>',
    "clipboard_check": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>',
    "check_ring": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "baby": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M9 12h.01"/><path d="M15 12h.01"/><path d="M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><path d="M19 6.3a9 9 0 0 1 1.8 3.9 2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1"/></svg>',
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
    "users": '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
}

def render_html(html_str: str):
    """Rendu HTML direct et propre sans artefacts markdown."""
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CSS Thème Emerald Slate (Tokens 21st.dev) : Calme, Hospitalier, Zéro Dégradé IA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #f8fafc;
        --surface: #ffffff;
        --border-default: #e2e8f0;
        --border-subtle: #f1f5f9;
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --primary-emerald: #059669;
        --primary-emerald-dark: #047857;
        --accent-teal: #0d9488;
        --warn-amber: #d97706;
        --danger-rose: #e11d48;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }

    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1.0rem !important;
        padding-bottom: 2.8rem !important;
        max-width: 780px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 8px !important;
        border: 1px solid var(--border-default) !important;
        background-color: #ffffff !important;
        padding: 9px 12px !important;
        font-size: 0.9rem !important;
        color: var(--text-primary) !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--primary-emerald) !important;
        box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.12) !important;
    }

    button[data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: var(--text-primary) !important;
    }

    button[data-testid="stBaseButton-primary"] {
        background-color: var(--primary-emerald) !important;
        color: #ffffff !important;
        border: 1px solid var(--primary-emerald-dark) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        box-shadow: 0 1px 2px rgba(5, 150, 105, 0.2) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: var(--primary-emerald-dark) !important;
    }

    div[data-testid="stTextArea"] textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 1.18rem !important;
        line-height: 1.65 !important;
        border-radius: 8px !important;
        border: 1px solid #fde68a !important;
        background-color: #fffefb !important;
        color: #0f172a !important;
    }

    div[data-testid="stProgress"] > div > div > div {
        background-color: var(--primary-emerald) !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Initialisation de la session
# -----------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]

if "reviewer_name" not in st.session_state:
    st.session_state["reviewer_name"] = ""

if "reviewer_email" not in st.session_state:
    st.session_state["reviewer_email"] = ""

if "reviewer_role" not in st.session_state:
    st.session_state["reviewer_role"] = "generaliste"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "batch" not in st.session_state:
    st.session_state["batch"] = []

if "current_idx" not in st.session_state:
    st.session_state["current_idx"] = 0

if "completed" not in st.session_state:
    st.session_state["completed"] = False

if "decision_choice" not in st.session_state:
    st.session_state["decision_choice"] = "valider"

if "batch_stats" not in st.session_state:
    st.session_state["batch_stats"] = {"valider": 0, "corriger": 0, "rejeter": 0}



# -----------------------------------------------------------------------------
# En-tête Médical Officiel (100% Dédié Praticiens & Évaluateurs)
# -----------------------------------------------------------------------------
render_html(f"""
<div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; margin-bottom: 16px; border-bottom: 1px solid #e2e8f0;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #059669; border-radius: 8px; color: white;">
            {ICONS['stethoscope']}
        </span>
        <div>
            <span style="font-weight: 700; font-size: 1.15rem; color: #0f172a; letter-spacing: -0.3px;">NLParto</span>
            <span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.72rem; font-weight: 600; padding: 2px 7px; border-radius: 5px; margin-left: 6px;">
                Évaluation Clinique
            </span>
        </div>
    </div>
    <span style="color: #64748b; font-size: 0.78rem;">
        Santé Maternelle &amp; Infantile
    </span>
</div>
""")

# -------------------------------------------------------------------------
# ÉCRAN D'ACCUEIL / IDENTIFICATION
# -------------------------------------------------------------------------
if not st.session_state["authenticated"]:
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 24px; box-shadow: 0 1px 3px rgba(15,23,42,0.03); margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <span style="display: inline-flex; align-items: center; gap: 5px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.74rem; font-weight: 600; padding: 3px 8px; border-radius: 6px;">
                {ICONS['shield_check']}
                Protocole Clinique Officiel
            </span>
            <span style="background: #f1f5f9; border: 1px solid #e2e8f0; color: #475569; font-size: 0.7rem; font-weight: 600; padding: 3px 8px; border-radius: 5px;">
                Mode Test Isolé (reviews_test.csv)
            </span>
        </div>
        <div style="font-size: 1.2rem; font-weight: 700; color: #0f172a; line-height: 1.35; margin-bottom: 4px;">
            Validation clinique des dialogues en Darja algérienne
        </div>
        <div style="font-size: 0.86rem; color: #475569; line-height: 1.45; margin-bottom: 18px;">
            Évaluez la pertinence et la sécurité des réponses proposées aux mamans. Aucun mot de passe requis.
        </div>
        <hr style="border: none; border-top: 1px solid #f1f5f9; margin-bottom: 16px;">
        <div style="font-size: 0.84rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">
            1. Identifiant & Coordonnées du praticien
        </div>
        <div style="font-size: 0.78rem; color: #64748b; margin-bottom: 8px;">
            Ces informations permettent le suivi déontologique dans le tableau de bord superviseur.
        </div>
    </div>
    """)

    col_name, col_email = st.columns(2)
    with col_name:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #334155; margin-bottom: 4px;'>Nom & Prénom du praticien :</div>", unsafe_allow_html=True)
        name_input = st.text_input(
            "Nom & Prénom",
            value=st.session_state["reviewer_name"],
            placeholder="Ex: Dr. Sarah Benali",
            label_visibility="collapsed"
        )

    with col_email:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #334155; margin-bottom: 4px;'>Email professionnel :</div>", unsafe_allow_html=True)
        email_input = st.text_input(
            "Email professionnel",
            value=st.session_state["reviewer_email"],
            placeholder="Ex: s.benali@chu-alger.dz",
            label_visibility="collapsed"
        )

    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 22px; box-shadow: 0 1px 3px rgba(15,23,42,0.03); margin-top: 12px; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; background: #ecfdf5; border-radius: 4px; color: #059669;">
                {ICONS['user_md']}
            </span>
            <span style="font-size: 0.84rem; font-weight: 700; color: #0f172a;">2. Spécialité médicale</span>
        </div>
        <div style="font-size: 0.78rem; color: #64748b;">
            Sélectionnez votre profil d'exercice pour la traçabilité clinique.
        </div>
    </div>
    """)

    ROLE_OPTIONS = {
        "generaliste": "Médecin Généraliste",
        "resident": "Médecin Résident (Pédiatrie / Gynécologie / Santé Publique)",
        "pediatre": "Pédiatre Spécialiste",
        "gynecologue": "Gynécologue-Obstétricien(ne)",
        "sage_femme": "Sage-femme Diplômée d'État",
        "etudiant": "Externe / Étudiant en Médecine (4e-6e année)"
    }

    selected_role = st.selectbox(
        "Votre rôle médical",
        options=list(ROLE_OPTIONS.keys()),
        format_func=lambda k: ROLE_OPTIONS[k],
        label_visibility="collapsed"
    )

    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 22px; box-shadow: 0 1px 3px rgba(15,23,42,0.03); margin-top: 12px; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; background: #f1f5f9; border-radius: 4px; color: #475569;">
                {ICONS['clipboard_check']}
            </span>
            <span style="font-size: 0.84rem; font-weight: 700; color: #0f172a;">3. Consignes déontologiques clés</span>
        </div>
        <ul style="font-size: 0.82rem; color: #334155; line-height: 1.5; margin: 8px 0 0 18px; padding: 0;">
            <li><strong>Zéro posologie :</strong> L'assistant ne doit jamais prescrire de doses chiffrées en mg ou ml.</li>
            <li><strong>Urgence vitale :</strong> Tout signe de danger impose une orientation immédiate vers les urgences.</li>
            <li><strong>Darja naturelle :</strong> Vérifiez l'authenticité algérienne de l'expression.</li>
        </ul>
    </div>
    """)

    if st.button("Démarrer la série d'évaluation clinique →", type="primary", use_container_width=True):
        if not name_input.strip():
            st.error("Veuillez saisir votre nom ou identifiant professionnel.")
        else:
            st.session_state["reviewer_name"] = name_input.strip()
            st.session_state["reviewer_email"] = email_input.strip()
            st.session_state["reviewer_role"] = selected_role
            batch = get_or_create_batch(
                st.session_state["session_id"],
                st.session_state["reviewer_name"],
                st.session_state["reviewer_role"],
                reviewer_email=st.session_state["reviewer_email"],
                batch_size=20
            )
            if not batch:
                st.warning("Aucune question en attente de révision dans le pool actuel.")
            else:
                st.session_state["batch"] = batch
                st.session_state["current_idx"] = 0
                st.session_state["authenticated"] = True
                st.session_state["completed"] = False
                st.session_state["decision_choice"] = "valider"
                st.rerun()

# -------------------------------------------------------------------------
# ÉCRAN DE FIN DE SÉRIE
# -------------------------------------------------------------------------
elif st.session_state["completed"]:
    stats = st.session_state["batch_stats"]

    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px 24px; text-align: center; box-shadow: 0 1px 3px rgba(15,23,42,0.03); margin-top: 14px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: #ecfdf5; border-radius: 12px; color: #059669; margin-bottom: 12px;">
            {ICONS['check_ring']}
        </div>
        <div style="font-size: 1.3rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">
            Série d'évaluation complétée
        </div>
        <div style="font-size: 0.88rem; color: #475569; margin-bottom: 22px;">
            Merci Dr. {st.session_state['reviewer_name']}. Vos évaluations ont été persistées immédiatement.
        </div>
        <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 24px;">
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 12px 18px; min-width: 100px;">
                <div style="font-size: 1.4rem; font-weight: 700; color: #047857;">{stats['valider']}</div>
                <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: #065f46;">Validées</div>
            </div>
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 12px 18px; min-width: 100px;">
                <div style="font-size: 1.4rem; font-weight: 700; color: #b45309;">{stats['corriger']}</div>
                <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: #92400e;">Corrigées</div>
            </div>
            <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 12px 18px; min-width: 100px;">
                <div style="font-size: 1.4rem; font-weight: 700; color: #be123c;">{stats['rejeter']}</div>
                <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: #9f1239;">Rejetées</div>
            </div>
        </div>
    </div>
    """)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("Évaluer une nouvelle série (20 questions) →", type="primary", use_container_width=True):
            batch = get_or_create_batch(
                st.session_state["session_id"],
                st.session_state["reviewer_name"],
                st.session_state["reviewer_role"],
                reviewer_email=st.session_state["reviewer_email"],
                batch_size=20
            )
            st.session_state["batch"] = batch
            st.session_state["current_idx"] = 0
            st.session_state["completed"] = False
            st.session_state["decision_choice"] = "valider"
            st.session_state["batch_stats"] = {"valider": 0, "corriger": 0, "rejeter": 0}
            st.rerun()

    with col_b2:
        if st.button("Terminer la session", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["batch"] = []
            st.rerun()

# -------------------------------------------------------------------------
# ÉCRAN DE QUESTION À ÉVALUER
# -------------------------------------------------------------------------
else:
    batch = st.session_state["batch"]
    idx = st.session_state["current_idx"]

    if idx >= len(batch):
        st.session_state["completed"] = True
        st.rerun()

    current_row = batch[idx]
    row_id = current_row.get("id", f"item-{idx}")

    ROLE_LABELS = {
        "generaliste": "Médecin Généraliste",
        "resident": "Résident",
        "pediatre": "Pédiatre",
        "gynecologue": "Gynécologue",
        "sage_femme": "Sage-femme",
        "etudiant": "Externe"
    }
    role_label = ROLE_LABELS.get(st.session_state["reviewer_role"], "Praticien")

    # 1. Barre supérieure du praticien
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: #ecfdf5; border-radius: 6px; color: #059669;">
                {ICONS['stethoscope']}
            </span>
            <div>
                <span style="font-weight: 700; color: #0f172a; font-size: 0.88rem;">{st.session_state['reviewer_name']}</span>
                <span style="font-size: 0.74rem; color: #64748b; margin-left: 4px;">({role_label})</span>
            </div>
        </div>
        <span style="background: #f1f5f9; border: 1px solid #e2e8f0; color: #475569; font-size: 0.7rem; font-weight: 600; padding: 2px 7px; border-radius: 5px;">
            Test Isolé
        </span>
    </div>
    """)

    # 2. Progression
    total_q = len(batch)
    pct = int(((idx) / total_q) * 100)

    col_top_left, col_top_right = st.columns([3, 1])
    with col_top_left:
        render_html(f"""
        <div style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b;">
            Série en cours
        </div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">
            Question {idx + 1} sur {total_q}
        </div>
        """)
    with col_top_right:
        if st.button("Quitter", help="Libère les questions restantes"):
            release_batch(st.session_state["session_id"])
            st.session_state["authenticated"] = False
            st.rerun()

    st.progress(idx / total_q)
    render_html(f"<div style='text-align: right; font-size: 0.74rem; color: #64748b; margin-top: -6px; margin-bottom: 12px;'>{pct}% validé</div>")

    topic = current_row.get("topic", "santé générale").capitalize()
    risk = current_row.get("risk_level", "routine").capitalize()
    stype = current_row.get("situation_type", "fact").capitalize()

    render_html(f"""
    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 14px;">
        <span style="background: #f1f5f9; border: 1px solid #e2e8f0; color: #334155; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 5px;">
            {topic}
        </span>
        <span style="background: #fffbeb; border: 1px solid #fde68a; color: #92400e; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 5px;">
            {risk}
        </span>
        <span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 5px;">
            {stype}
        </span>
        <span style="background: #ffffff; border: 1px solid #e2e8f0; color: #64748b; font-family: monospace; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 5px;">
            {row_id}
        </span>
    </div>
    """)

    # ---------------------------------------------------------------------
    # SECTION 1 : QUESTION DE LA MAMAN (ORDRE RIGOUREUX : ARABE 1ER, FRANÇAIS 2E)
    # ---------------------------------------------------------------------
    question_ar = current_row.get("question_ar", "")
    question_lat = current_row.get("question_lat", "")

    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(15,23,42,0.02);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #ecfdf5; border-radius: 5px; color: #059669;">
                    {ICONS['baby']}
                </span>
                <span style="font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #334155;">Question posée par la maman</span>
            </div>
            <span style="font-size: 0.72rem; color: #64748b; font-weight: 600;">Darja algérienne</span>
        </div>

        <!-- 1. Écriture arabe en Cairo (Premier encadré) -->
        <div style="background: #fcfdfd; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
            <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #059669; margin-bottom: 4px; text-align: right;">
                بالحروف العربية :
            </div>
            <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.25rem; font-weight: 700; color: #0f172a; line-height: 1.65;">
                {question_ar}
            </div>
        </div>

        <!-- 2. Arabizi en lettres françaises (Deuxième encadré - French in Darja) -->
        <div style="background: #fcfdfd; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
            <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #059669; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                {ICONS['languages']}
                En lettres françaises (Arabizi) :
            </div>
            <div style="font-family: 'Inter', -apple-system, sans-serif; font-size: 1.08rem; color: #0f172a; line-height: 1.55; font-weight: 600;">
                {question_lat or "—"}
            </div>
        </div>
    </div>
    """)

    # ---------------------------------------------------------------------
    # SECTION 2 : TRANSCRIPTION DE LA RÉPONSE DE L'ASSISTANT
    # ---------------------------------------------------------------------
    answer_darja = current_row.get("answer_darja", "")

    render_html(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0d9488; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid #edf2f7;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #0d9488; border-radius: 5px; color: white;">
                    {ICONS['message_clinical']}
                </span>
                <span style="font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #0f766e;">Réponse proposée par l'assistant</span>
            </div>
            <span style="background: #ccfbf1; color: #0f766e; font-size: 0.7rem; font-weight: 600; padding: 2px 7px; border-radius: 4px;">Avis clinique requis</span>
        </div>
        <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.25rem; font-weight: 600; color: #0f172a; line-height: 1.7; padding: 4px 0;">
            « {answer_darja} »
        </div>
    </div>
    """)

    # ---------------------------------------------------------------------
    # SECTION 3 : DÉCISION MÉDICALE DU PRATICIEN (PATTERN APPROVAL CARD 21ST.DEV)
    # ---------------------------------------------------------------------
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 20px 14px 20px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(15,23,42,0.02);">
        <div style="font-size: 0.74rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b; margin-bottom: 2px;">
            Évaluation Déontologique & Médicale
        </div>
        <div style="font-size: 0.94rem; font-weight: 600; color: #0f172a;">
            Cette réponse respecte-t-elle les protocoles cliniques et la sécurité de la mère et du nouveau-né ?
        </div>
    </div>
    """)

    b_col1, b_col2, b_col3 = st.columns(3)
    current_choice = st.session_state["decision_choice"]

    with b_col1:
        is_v = (current_choice == "valider")
        v_btn = st.button(
            "Valider\n(Conforme & sûr)",
            key=f"btn_v_{row_id}",
            type="primary" if is_v else "secondary",
            use_container_width=True
        )
        if v_btn:
            st.session_state["decision_choice"] = "valider"
            st.rerun()

    with b_col2:
        is_c = (current_choice == "corriger")
        c_btn = st.button(
            "Corriger\n(Modifier le texte)",
            key=f"btn_c_{row_id}",
            type="primary" if is_c else "secondary",
            use_container_width=True
        )
        if c_btn:
            st.session_state["decision_choice"] = "corriger"
            st.rerun()

    with b_col3:
        is_r = (current_choice == "rejeter")
        r_btn = st.button(
            "Rejeter\n(Dangereux / erroné)",
            key=f"btn_r_{row_id}",
            type="primary" if is_r else "secondary",
            use_container_width=True
        )
        if r_btn:
            st.session_state["decision_choice"] = "rejeter"
            st.rerun()

    corrected_val = ""
    reject_reasons = []

    if current_choice == "corriger":
        render_html("""
        <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 10px 14px; margin-top: 12px; margin-bottom: 6px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #92400e;">
                Correction de la réponse en Darja :
            </div>
            <div style="font-size: 0.74rem; color: #b45309; margin-top: 1px;">
                Modifiez directement le texte. Tolérance zéro pour les prescriptions ou posologies de médicaments.
            </div>
        </div>
        """)

        corrected_val = st.text_area(
            "Réponse Darja corrigée",
            value=answer_darja,
            height=100,
            key=f"corr_box_{row_id}",
            label_visibility="collapsed"
        )

    elif current_choice == "rejeter":
        render_html("""
        <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 10px 14px; margin-top: 12px; margin-bottom: 6px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #9f1239;">
                Motif(s) du rejet clinique :
            </div>
            <div style="font-size: 0.74rem; color: #be123c; margin-top: 1px;">
                Sélectionnez au moins un motif de non-conformité :
            </div>
        </div>
        """)

        r1 = st.checkbox("Prescription de médicament / posologie interdite", key=f"r1_{row_id}")
        r2 = st.checkbox("Erreur médicale clinique ou diagnostic non fondé", key=f"r2_{row_id}")
        r3 = st.checkbox("Dialecte non-algérien ou incompréhensible", key=f"r3_{row_id}")
        r4 = st.checkbox("Signe de danger vital non pris en compte", key=f"r4_{row_id}")
        if r1: reject_reasons.append("prescription_dose")
        if r2: reject_reasons.append("erreur_medicale")
        if r3: reject_reasons.append("darja_incorrecte")
        if r4: reject_reasons.append("urgence_non_signalee")

    render_html("""
    <div style="margin-top: 12px; margin-bottom: 4px; font-size: 0.8rem; font-weight: 600; color: #334155;">
        Remarque clinique <span style="color: #94a3b8; font-weight: 400;">(facultatif)</span>
    </div>
    """)

    notes_val = st.text_input(
        "Remarque clinique",
        placeholder="Ajoutez un contexte clinique si nécessaire...",
        key=f"notes_box_{row_id}",
        label_visibility="collapsed"
    )

    render_html("<div style='margin-top: 14px;'></div>")

    col_sub_left, col_sub_right = st.columns([1.5, 1.5])
    with col_sub_left:
        render_html("""
        <div style="display: flex; align-items: center; font-size: 0.76rem; color: #64748b; height: 100%; padding-top: 8px;">
            Enregistrement immédiat dans reviews_test.csv
        </div>
        """)

    with col_sub_right:
        if st.button("Confirmer l'évaluation & question suivante →", type="primary", use_container_width=True):
            decision = st.session_state["decision_choice"]

            if decision == "rejeter" and not reject_reasons and not notes_val:
                st.warning("Veuillez cocher au moins un motif de rejet ou ajouter une note.")
            elif decision == "corriger" and not corrected_val.strip():
                st.warning("Veuillez saisir la réponse corrigée.")
            else:
                save_review(
                    row_id=row_id,
                    decision=decision,
                    corrected_text=corrected_val.strip() if decision == "corriger" else "",
                    reject_reasons=reject_reasons,
                    notes=notes_val.strip(),
                    session_id=st.session_state["session_id"],
                    reviewer_name=st.session_state["reviewer_name"],
                    reviewer_role=st.session_state["reviewer_role"],
                    reviewer_email=st.session_state["reviewer_email"]
                )

                st.session_state["batch_stats"][decision] += 1
                st.session_state["current_idx"] += 1
                st.session_state["decision_choice"] = "valider"
                st.rerun()
