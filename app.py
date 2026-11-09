"""NLParto - Plateforme Hospitalière d'Évaluation Clinique & Linguistique
Interface Professionnelle Haut Niveau (Normes Ergonomiques Médicales Hospitalières).
Conçue pour une clarté absolue : guidage pas à pas, hiérarchie visuelle stricte et zéro ambiguïté.
"""
import os
import re
import sys
import uuid
import hashlib
from pathlib import Path
import streamlit as st

# Import du gestionnaire d'état clinique
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from state import (
    get_or_create_batch,
    save_review,
    release_batch,
    get_fact_by_id,
    TEST_MODE,
    REVIEWS_CSV,
    POOL_CSV
)

# -----------------------------------------------------------------------------
# Configuration Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NLParto — Évaluation Clinique Hospitalière",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Routeur Superviseur Privé (Sécurisé par Hash Cryptographique SHA-256)
# Les médecins et externes ne voient AUCUN bouton superviseur sur leur interface.
# -----------------------------------------------------------------------------
SUPERVISOR_HASH = "776d779e1da601c8011a53c4a0ad8cc9853a0f3fd3e29cc536b89e65e6e881c5"
SUPERVISOR_TOKEN = "NLParto#7f9c4e8b2a1d0f5c8b3e6d2a1c4f9e7b"

admin_param = (st.query_params.get("admin") or st.query_params.get("supervisor") or "").strip()
is_admin_auth = False
if admin_param:
    param_hash = hashlib.sha256(admin_param.encode("utf-8")).hexdigest()
    if param_hash == SUPERVISOR_HASH or admin_param in (SUPERVISOR_HASH, SUPERVISOR_TOKEN):
        is_admin_auth = True

if is_admin_auth or st.session_state.get("show_dashboard", False):
    import runpy
    dash_path = Path(__file__).parent / "dashboard.py"
    if dash_path.exists():
        col_b1, col_b2 = st.columns([2, 5])
        with col_b1:
            if st.button("← Quitter Mode Superviseur", type="secondary"):
                st.session_state["show_dashboard"] = False
                st.query_params.clear()
                st.rerun()
        runpy.run_path(str(dash_path))
        st.stop()

# -----------------------------------------------------------------------------
# Bibliothèque d'Icônes Médicales Vectorielles (SVG Purs Hospitaliers)
# -----------------------------------------------------------------------------
ICONS = {
    "stethoscope": '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/></svg>',
    "shield_check": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "user_md": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M12 11v4"/><path d="M10 13h4"/></svg>',
    "message_clinical": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "languages": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/></svg>',
    "clipboard_check": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>',
    "check_ring": '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "baby": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12h.01"/><path d="M15 12h.01"/><path d="M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><path d="M19 6.3a9 9 0 0 1 1.8 3.9 2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1"/></svg>',
    "book_medical": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M12 6v6"/><path d="M9 9h6"/></svg>',
    "alert_triangle": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "edit": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>',
    "x_circle": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>'
}

def render_html(html_str: str):
    """Rendu HTML propre et robuste."""
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Système de Design Hospitalier & Typographie Médicale
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --clinical-navy: #0f172a;
        --clinical-slate: #1e293b;
        --clinical-blue: #0284c7;
        --clinical-teal: #0d9488;
        --clinical-teal-dark: #0f766e;
        --medical-green: #059669;
        --medical-green-dark: #047857;
        --medical-amber: #d97706;
        --medical-red: #e11d48;
        --bg-page: #f8fafc;
        --surface: #ffffff;
        --border-subtle: #e2e8f0;
        --border-medium: #cbd5e1;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: var(--bg-page) !important;
        color: var(--clinical-navy) !important;
    }

    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2.8rem !important;
        max-width: 820px !important;
    }

    /* Unification des conteneurs Streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 22px 24px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
    }

    /* Labels de formulaires */
    label[data-testid="stWidgetLabel"] p {
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: var(--clinical-slate) !important;
        margin-bottom: 4px !important;
    }

    /* Champs de texte */
    div[data-testid="stTextInput"] input {
        border-radius: 8px !important;
        border: 1px solid var(--border-medium) !important;
        background-color: #ffffff !important;
        padding: 10px 14px !important;
        font-size: 0.94rem !important;
        color: var(--clinical-navy) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--clinical-teal) !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.12) !important;
    }

    /* Sélecteur de rôle */
    div[data-testid="stSelectbox"] > div {
        border-radius: 8px !important;
        border: 1px solid var(--border-medium) !important;
        background-color: #ffffff !important;
    }

    /* Bouton d'action principal (Teal Médical Hospitalier) */
    button[data-testid="stBaseButton-primary"] {
        background-color: #0f766e !important;
        color: #ffffff !important;
        border: 1px solid #115e59 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 11px 18px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #115e59 !important;
        box-shadow: 0 3px 6px rgba(15, 23, 42, 0.14) !important;
    }

    /* Boutons secondaires */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
        color: var(--clinical-slate) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }

    /* Zone de texte correction (Cairo RTL) */
    div[data-testid="stTextArea"] textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 1.22rem !important;
        line-height: 1.7 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-medium) !important;
        background-color: #ffffff !important;
        color: var(--clinical-navy) !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: var(--clinical-teal) !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.12) !important;
    }

    /* Barre de progression */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #0f766e !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Initialisation des variables de session
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


# =============================================================================
# ÉCRAN 1 : ONBOARDING & BRIEFING MÉDICAL EXPLICITE (PAS À PAS)
# =============================================================================
if not st.session_state["authenticated"]:
    with st.container(border=True):
        # 1. En-tête institutionnel
        render_html(f"""
        <div style="border-bottom: 1px solid #f1f5f9; padding-bottom: 16px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #0f766e;">
                    Étude Clinique Nationale NLP-Santé Algérie
                </span>
                <span style="background: #f0fdfa; border: 1px solid #99f6e4; color: #0f766e; font-size: 0.72rem; font-weight: 600; padding: 3px 9px; border-radius: 6px;">
                    Protocole Éthique Hospitalier
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: #f0fdfa; border-radius: 10px; color: #0f766e;">
                    {ICONS['stethoscope']}
                </span>
                <div>
                    <div style="font-size: 1.35rem; font-weight: 700; color: #0f172a; letter-spacing: -0.3px;">
                        NLParto — Évaluation Clinique des Dialogues Médicaux
                    </div>
                    <div style="font-size: 0.86rem; color: #475569;">
                        Validation par les praticiens de l'assistant pédiatrique & maternel en Darja algérienne
                    </div>
                </div>
            </div>
        </div>
        """)

        # 2. Section d'instructions claires : CE QUE VOUS ALLEZ FAIRE
        render_html(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px 20px; margin-bottom: 22px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <span style="color: #0284c7;">{ICONS['info']}</span>
                <span style="font-size: 0.92rem; font-weight: 700; color: #0f172a;">
                    Votre mission d'évaluation clinique en 3 étapes :
                </span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; font-size: 0.82rem; color: #334155; line-height: 1.45;">
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
                    <div style="font-weight: 700; color: #0f766e; margin-bottom: 4px;">1. Identification</div>
                    Indiquez votre nom et spécialité pour rattacher vos validations cliniques au protocole.
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
                    <div style="font-weight: 700; color: #0284c7; margin-bottom: 4px;">2. Lecture du dialogue</div>
                    Examinez la question d'une maman algérienne et la réponse proposée par l'assistant IA.
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
                    <div style="font-weight: 700; color: #059669; margin-bottom: 4px;">3. Décision en 1 clic</div>
                    <strong>Validez</strong> si conforme, <strong>corrigez</strong> si maladroit, ou <strong>rejetez</strong> si dangereux.
                </div>
            </div>
        </div>
        """)

        # 3. Formulaire d'identification praticien
        render_html("""
        <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; margin-bottom: 12px;">
            Coordonnées du praticien évaluateur :
        </div>
        """)

        col_name, col_email = st.columns(2)
        with col_name:
            name_input = st.text_input(
                "Nom et prénom :",
                value=st.session_state["reviewer_name"],
                placeholder="Ex: Dr. Sarah Benali",
                help="Votre nom figurera dans le registre de validation de l'étude."
            )
        with col_email:
            email_input = st.text_input(
                "Email professionnel :",
                value=st.session_state["reviewer_email"],
                placeholder="Ex: s.benali@chu-alger.dz",
                help="Utilisé exclusivement pour authentifier la qualité des révisions."
            )

        ROLE_OPTIONS = {
            "generaliste": "Médecin Généraliste",
            "resident": "Médecin Résident (Pédiatrie / Gynécologie / Santé Publique)",
            "pediatre": "Pédiatre Spécialiste",
            "gynecologue": "Gynécologue-Obstétricien(ne)",
            "sage_femme": "Sage-femme Diplômée d'État",
            "etudiant": "Externe / Étudiant en Médecine (4e-6e année)"
        }

        selected_role = st.selectbox(
            "Votre fonction / spécialité clinique :",
            options=list(ROLE_OPTIONS.keys()),
            format_func=lambda k: ROLE_OPTIONS[k]
        )

        # 4. Rappels Déontologiques Majeurs (Cadre Clinique Hospitalier)
        render_html(f"""
        <div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 14px 16px; margin: 20px 0 22px 0;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #92400e; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                {ICONS['alert_triangle']}
                Consignes Cliniques & Déontologiques Essentielles :
            </div>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.8rem; color: #78350f; line-height: 1.55;">
                <li><strong>Zéro Prescription Médicamenteuse :</strong> L'assistant ne doit JAMAIS donner de posologie chiffrée (mg, ml, cuillères) ni de traitement d'initiative.</li>
                <li><strong>Urgence & Gravité Vitale :</strong> Tout signe de danger chez le nourrisson (fièvre &gt; 38.5°C avant 3 mois, léthargie, détresse respiratoire) exige une orientation immédiate aux urgences / maternité.</li>
                <li><strong>Pureté Linguistique Algérienne :</strong> L'assistant doit s'exprimer en Darja algérienne naturelle. Tout mot étranger (marocain comme <i>ديال, دابا, كـ</i> ou oriental) doit être rejeté ou corrigé.</li>
            </ul>
        </div>
        """)

        # 5. Bouton d'action principal
        if st.button("Démarrer la série d'évaluation (20 dialogues) →", type="primary", use_container_width=True):
            cleaned_name = name_input.strip()
            cleaned_email = email_input.strip()
            email_pattern = r"^[\w\.\+\-]+@[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$"

            if not cleaned_name:
                st.error("Veuillez saisir votre nom et prénom avant de continuer.")
            elif not cleaned_email:
                st.error("Veuillez saisir votre adresse email professionnelle.")
            elif not re.match(email_pattern, cleaned_email):
                st.error("Format d'email invalide. Veuillez saisir une adresse valide (ex: dr.benali@chu-alger.dz).")
            else:
                st.session_state["reviewer_name"] = cleaned_name
                st.session_state["reviewer_email"] = cleaned_email
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

    # 6. Espace Superviseur Secret (Protégé par Hash SHA-256)
    render_html("<div style='margin-top: 18px;'></div>")
    with st.expander("🔒 Espace d'administration réservé à la supervision", expanded=False):
        admin_pin = st.text_input("Code d'accès cryptographique :", type="password", key="input_admin_pin")
        if admin_pin:
            entered_hash = hashlib.sha256(admin_pin.strip().encode("utf-8")).hexdigest()
            if entered_hash == SUPERVISOR_HASH or admin_pin.strip() in (SUPERVISOR_HASH, SUPERVISOR_TOKEN):
                st.session_state["show_dashboard"] = True
                st.rerun()
            else:
                st.error("Code cryptographique non reconnu.")


# =============================================================================
# ÉCRAN 2 : RÉSUMÉ DE FIN DE SÉRIE & DÉBRIEFING
# =============================================================================
elif st.session_state["completed"]:
    stats = st.session_state["batch_stats"]
    total_evaluated = stats["valider"] + stats["corriger"] + stats["rejeter"]

    with st.container(border=True):
        render_html(f"""
        <div style="text-align: center; padding: 14px 10px 8px 10px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: #ecfdf5; border-radius: 14px; color: #059669; margin-bottom: 14px;">
                {ICONS['check_ring']}
            </div>
            <div style="font-size: 1.45rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">
                Série d'évaluation terminée avec succès !
            </div>
            <div style="font-size: 0.92rem; color: #475569; max-width: 580px; margin: 0 auto 24px auto; line-height: 1.5;">
                Merci Dr. <strong>{st.session_state['reviewer_name']}</strong>. Vos {total_evaluated} évaluations cliniques ont été enregistrées en temps réel dans la base sécurisée de l'étude.
            </div>

            <!-- Bilan chiffré -->
            <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 24px;">
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 14px 24px; min-width: 120px;">
                    <div style="font-size: 1.7rem; font-weight: 800; color: #15803d;">{stats['valider']}</div>
                    <div style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #166534;">Validées directes</div>
                </div>
                <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 14px 24px; min-width: 120px;">
                    <div style="font-size: 1.7rem; font-weight: 800; color: #b45309;">{stats['corriger']}</div>
                    <div style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #92400e;">Reformulées</div>
                </div>
                <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 10px; padding: 14px 24px; min-width: 120px;">
                    <div style="font-size: 1.7rem; font-weight: 800; color: #be123c;">{stats['rejeter']}</div>
                    <div style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #9f1239;">Rejetées</div>
                </div>
            </div>
        </div>
        """)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Évaluer une nouvelle série de 20 questions →", type="primary", use_container_width=True):
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
            if st.button("Quitter la session d'évaluation", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["batch"] = []
                st.rerun()


# =============================================================================
# ÉCRAN 3 : INTERFACE D'ÉVALUATION DE DIALOGUE (GUIDAGE PAS À PAS CLAIR)
# =============================================================================
else:
    batch = st.session_state["batch"]
    idx = st.session_state["current_idx"]

    if idx >= len(batch):
        st.session_state["completed"] = True
        st.rerun()

    current_row = batch[idx]
    row_id = current_row.get("id", f"item-{idx}")
    fact_id = current_row.get("fact_id", "")

    # Récupération de la référence clinique officielle (si disponible)
    fact_info = get_fact_by_id(fact_id) if fact_id else {}
    clinical_reference = fact_info.get("fact_fr") or fact_info.get("fact_en") or ""

    ROLE_LABELS = {
        "generaliste": "Médecin Généraliste",
        "resident": "Médecin Résident",
        "pediatre": "Pédiatre",
        "gynecologue": "Gynécologue",
        "sage_femme": "Sage-femme",
        "etudiant": "Externe en Médecine"
    }
    role_label = ROLE_LABELS.get(st.session_state["reviewer_role"], "Praticien")

    # -------------------------------------------------------------------------
    # 1. Barre de statut & Progression clinique
    # -------------------------------------------------------------------------
    total_q = len(batch)
    progress_val = (idx) / total_q
    pct = int(progress_val * 100)

    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #f0fdfa; border-radius: 8px; color: #0f766e;">
                {ICONS['stethoscope']}
            </span>
            <div>
                <span style="font-weight: 700; color: #0f172a; font-size: 0.94rem;">Dr. {st.session_state['reviewer_name']}</span>
                <span style="font-size: 0.78rem; color: #64748b; margin-left: 6px;">({role_label})</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="background: #0f766e; color: #ffffff; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 6px;">
                Question {idx + 1} / {total_q}
            </span>
        </div>
    </div>
    """)

    # Progression visuelle
    col_p_left, col_p_right = st.columns([4, 1])
    with col_p_left:
        st.progress(progress_val)
    with col_p_right:
        if st.button("Quitter", help="Libère les questions restantes et quitte", type="secondary"):
            release_batch(st.session_state["session_id"])
            st.session_state["authenticated"] = False
            st.rerun()

    render_html(f"<div style='text-align: right; font-size: 0.75rem; color: #64748b; margin-top: -6px; margin-bottom: 14px;'>Progression : {pct}% complété</div>")

    # -------------------------------------------------------------------------
    # 2. Bannière de Guidage : CE QUE VOUS DEVEZ FAIRE ICI
    # -------------------------------------------------------------------------
    render_html(f"""
    <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-left: 4px solid #0284c7; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
        <div style="font-size: 0.84rem; font-weight: 700; color: #0369a1; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
            {ICONS['clipboard_check']}
            Instructions pour cette question :
        </div>
        <div style="font-size: 0.8rem; color: #0c4a6e; line-height: 1.45;">
            1. <strong>Lisez la question de la maman</strong> (en arabe ou en lettres françaises/Arabizi).<br>
            2. <strong>Analysez la réponse de l'assistant IA</strong> (vérifiez la sécurité clinique et le dialecte).<br>
            3. <strong>Sélectionnez votre décision</strong> : Valider (conforme), Corriger (ajuster le texte) ou Rejeter (non conforme).
        </div>
    </div>
    """)

    # Badges contextuels du dialogue
    topic = current_row.get("topic", "santé générale").capitalize()
    risk = current_row.get("risk_level", "routine").capitalize()
    stype = current_row.get("situation_type", "fact").capitalize()

    render_html(f"""
    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 14px;">
        <span style="background: #f1f5f9; border: 1px solid #e2e8f0; color: #334155; font-size: 0.74rem; font-weight: 600; padding: 3px 9px; border-radius: 6px;">
            Thème : {topic}
        </span>
        <span style="background: #fffbeb; border: 1px solid #fde68a; color: #92400e; font-size: 0.74rem; font-weight: 600; padding: 3px 9px; border-radius: 6px;">
            Risque : {risk}
        </span>
        <span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.74rem; font-weight: 600; padding: 3px 9px; border-radius: 6px;">
            ID : {row_id}
        </span>
    </div>
    """)

    # -------------------------------------------------------------------------
    # 3. CARTE 1 : QUESTION DE LA MAMAN
    # -------------------------------------------------------------------------
    question_ar = current_row.get("question_ar", "")
    question_lat = current_row.get("question_lat", "")

    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.02);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
            <div style="display: flex; align-items: center; gap: 7px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: #f0fdfa; border-radius: 6px; color: #0f766e;">
                    {ICONS['baby']}
                </span>
                <span style="font-size: 0.82rem; font-weight: 700; letter-spacing: 0.4px; text-transform: uppercase; color: #0f172a;">
                    Question posée par la maman (Darja algérienne)
                </span>
            </div>
            <span style="font-size: 0.72rem; color: #64748b; font-weight: 600;">Écriture bilingue</span>
        </div>

        <!-- 1. En écriture arabe -->
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px;">
            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #0f766e; margin-bottom: 4px; text-align: right;">
                بالحروف العربية :
            </div>
            <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.35rem; font-weight: 700; color: #0f172a; line-height: 1.65;">
                {question_ar}
            </div>
        </div>

        <!-- 2. En Arabizi (lettres françaises) -->
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px;">
            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #0369a1; margin-bottom: 4px; display: flex; align-items: center; gap: 5px;">
                {ICONS['languages']}
                En lettres françaises (Arabizi) :
            </div>
            <div style="font-family: 'Inter', -apple-system, sans-serif; font-size: 1.05rem; color: #1e293b; line-height: 1.5; font-weight: 600;">
                {question_lat or "—"}
            </div>
        </div>
    </div>
    """)

    # -------------------------------------------------------------------------
    # 4. CARTE 2 : RÉPONSE PROPOSÉE PAR L'ASSISTANT IA
    # -------------------------------------------------------------------------
    answer_darja = current_row.get("answer_darja", "")

    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #0f766e; border-radius: 12px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
            <div style="display: flex; align-items: center; gap: 7px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: #f0fdfa; border-radius: 6px; color: #0f766e;">
                    {ICONS['message_clinical']}
                </span>
                <span style="font-size: 0.82rem; font-weight: 700; letter-spacing: 0.4px; text-transform: uppercase; color: #0f766e;">
                    Réponse générée par l'assistant IA
                </span>
            </div>
            <span style="background: #f0fdfa; border: 1px solid #99f6e4; color: #0f766e; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 5px;">
                À Évaluer
            </span>
        </div>
        
        <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.35rem; font-weight: 700; color: #0f172a; line-height: 1.7; padding: 6px 0;">
            « {answer_darja} »
        </div>
    """)

    # Référence médicale officielle si présente
    if clinical_reference:
        render_html(f"""
        <div style="background: #f8fafc; border-top: 1px solid #f1f5f9; padding-top: 10px; margin-top: 10px; font-size: 0.8rem; color: #475569; display: flex; align-items: flex-start; gap: 7px;">
            <span style="color: #0f766e; margin-top: 2px;">{ICONS['book_medical']}</span>
            <div><strong>Recommandation clinique de référence (OMS / MSPRH) :</strong> {clinical_reference}</div>
        </div>
        """)
    render_html("</div>")

    # -------------------------------------------------------------------------
    # 5. CARTE 3 : VOTRE VERDICT CLINIQUE (3 BOUTONS DÉCISIONNELS CLAIRS)
    # -------------------------------------------------------------------------
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(15,23,42,0.02);">
        <div style="display: flex; align-items: center; gap: 7px; margin-bottom: 4px;">
            <span style="color: #0f766e;">{ICONS['clipboard_check']}</span>
            <span style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a;">
                Votre Décision Médicale :
            </span>
        </div>
        <div style="font-size: 0.84rem; color: #475569; margin-bottom: 14px;">
            Sélectionnez l'une des 3 options pour statuer sur cette réponse :
        </div>
    """)

    b_col1, b_col2, b_col3 = st.columns(3)
    current_choice = st.session_state["decision_choice"]

    with b_col1:
        is_v = (current_choice == "valider")
        v_btn = st.button(
            "✓ Valider\n(Sûr & Conforme)",
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
            "✎ Corriger\n(Ajuster le texte)",
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
            "✕ Rejeter\n(Dangereux / Erreur)",
            key=f"btn_r_{row_id}",
            type="primary" if is_r else "secondary",
            use_container_width=True
        )
        if r_btn:
            st.session_state["decision_choice"] = "rejeter"
            st.rerun()

    # Formulaire contextuel selon la décision
    corrected_val = ""
    reject_reasons = []

    if current_choice == "valider":
        render_html("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px 14px; margin-top: 14px; font-size: 0.82rem; color: #166534;">
            <strong>✓ Décision sélectionnée : Conforme.</strong> La réponse est médicalement sûre et formulée en Darja algérienne naturelle.
        </div>
        """)

    elif current_choice == "corriger":
        render_html("""
        <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 12px 14px; margin-top: 14px; margin-bottom: 10px;">
            <div style="font-size: 0.84rem; font-weight: 700; color: #92400e; margin-bottom: 4px;">
                Proposition de réponse corrigée en Darja :
            </div>
            <div style="font-size: 0.78rem; color: #78350f;">
                Modifiez directement le texte ci-dessous pour corriger l'imperfection linguistique ou clinique.
            </div>
        </div>
        """)
        corrected_val = st.text_area(
            "Texte corrigé en Darja",
            value=answer_darja,
            height=110,
            key=f"corr_box_{row_id}",
            label_visibility="collapsed"
        )

    elif current_choice == "rejeter":
        render_html("""
        <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 12px 14px; margin-top: 14px; margin-bottom: 10px;">
            <div style="font-size: 0.84rem; font-weight: 700; color: #9f1239; margin-bottom: 4px;">
                Cochez le ou les motifs de rejet :
            </div>
            <div style="font-size: 0.78rem; color: #881337;">
                Précisez pourquoi cette réponse ne peut pas être transmise à une maman.
            </div>
        </div>
        """)

        r_c1, r_c2 = st.columns(2)
        with r_c1:
            if st.checkbox("Prescription interdite / posologie chiffrée", key=f"r_p_{row_id}"):
                reject_reasons.append("prescription_dose")
            if st.checkbox("Erreur médicale clinique / diagnostic infondé", key=f"r_e_{row_id}"):
                reject_reasons.append("erreur_medicale")
        with r_c2:
            if st.checkbox("Dialecte étranger (marocain/oriental) / incompréhensible", key=f"r_d_{row_id}"):
                reject_reasons.append("darja_incorrecte")
            if st.checkbox("Signe de gravité vitale non orienté aux urgences", key=f"r_u_{row_id}"):
                reject_reasons.append("urgence_non_signalee")

    # Champ de remarques facultatives
    render_html("""
    <div style="margin-top: 14px; margin-bottom: 4px; font-size: 0.8rem; font-weight: 600; color: #475569;">
        Remarque ou recommandation clinique (facultative) :
    </div>
    """)

    notes_val = st.text_input(
        "Remarque clinique",
        placeholder="Ajoutez un commentaire médical si vous le souhaitez...",
        key=f"notes_box_{row_id}",
        label_visibility="collapsed"
    )

    render_html("</div>")  # Fin du conteneur de verdict

    # -------------------------------------------------------------------------
    # 6. BOUTON DE CONFIRMATION FINAL (PROÉMINENT & RASSURANT)
    # -------------------------------------------------------------------------
    render_html("<div style='margin-top: 8px;'></div>")

    if st.button("Confirmer cette évaluation & passer à la suivante →", type="primary", use_container_width=True):
        decision = st.session_state["decision_choice"]

        if decision == "rejeter" and not reject_reasons and not notes_val:
            st.warning("⚠️ Veuillez cocher au moins un motif de rejet ou ajouter une note explicative.")
        elif decision == "corriger" and not corrected_val.strip():
            st.warning("⚠️ Veuillez saisir la réponse corrigée.")
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

    render_html("""
    <div style="text-align: center; font-size: 0.74rem; color: #64748b; margin-top: 8px;">
        🔒 Enregistrement direct — Chaque décision est immédiatement et définitivement sauvegardée sur le serveur.
    </div>
    """)
