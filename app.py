"""NLParto - Plateforme de Validation Clinique (Santé Maternelle & Infantile)
Fidélité absolue au design Figma Make : Icônes vectorielles Lucide naturelles, ZÉRO emoji, typographie médicale calme.
"""
import streamlit as st
import uuid
from state import (
    claim_batch,
    save_single_decision,
    release_batch,
    pool_stats,
    MEDICAL_ROLES,
    BATCH_SIZE
)

# -----------------------------------------------------------------------------
# Configuration de la page
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NLParto — Validation Clinique",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# -----------------------------------------------------------------------------
# Bibliothèque d'Icônes Naturelles Lucide (SVG Vectoriels - Zéro Emoji)
# -----------------------------------------------------------------------------
ICONS = {
    "stethoscope": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "message": '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><polyline points="20 6 9 17 4 12"/></svg>',
    "edit": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>',
    "x": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "languages": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/></svg>',
    "arrow_right": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "file_text": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>',
    "check_check": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block"><path d="M18 6 7 17l-5-5"/><path d="m22 10-7.5 7.5L13 16"/></svg>'
}


def render_html(html_str: str):
    """Rendu HTML sécurisé sans déclenchement de blocs de code markdown."""
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Styles CSS calmes conformes au design Figma Make
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 740px !important;
    }

    /* Conteneurs de cartes */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 20px 22px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 14px !important;
    }

    /* Champs de texte */
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 10px 14px !important;
        font-size: 0.92rem !important;
        color: #0f172a !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #047857 !important;
        box-shadow: 0 0 0 2px rgba(4, 120, 87, 0.12) !important;
    }

    /* Grille 2 colonnes pour les 6 rôles */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        margin-top: 6px !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: flex-start !important;
        gap: 8px !important;
        cursor: pointer !important;
        transition: all 0.12s ease-in-out !important;
        min-height: 68px !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        border-color: #cbd5e1 !important;
        background-color: #f8fafc !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked),
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #047857 !important;
        background-color: #f0fdf4 !important;
        box-shadow: 0 0 0 1px #047857 !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        font-size: 0.84rem !important;
        line-height: 1.3 !important;
        color: #0f172a !important;
        white-space: pre-line !important;
    }

    /* Bouton principal vert médical Figma */
    button[data-testid="stBaseButton-primary"] {
        background-color: #047857 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 11px 18px !important;
        font-size: 0.94rem !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #065f46 !important;
    }

    /* Boutons secondaires */
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #334155 !important;
        font-weight: 600 !important;
        padding: 11px 14px !important;
        transition: all 0.12s ease !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        border-color: #94a3b8 !important;
        background-color: #f8fafc !important;
    }

    /* Zone de texte RTL */
    div[data-testid="stTextArea"] textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 1.15rem !important;
        line-height: 1.65 !important;
        border-radius: 10px !important;
        border: 1px solid #fde047 !important;
        background-color: #fffef7 !important;
        color: #0f172a !important;
    }

    div[data-testid="stProgress"] > div > div > div {
        background-color: #047857 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Gestion d'état
# -----------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]

if "reviewer_name" not in st.session_state:
    st.session_state["reviewer_name"] = ""

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
# ÉCRAN 1 : ACCUEIL / ONBOARDING (FIDÉLITÉ FIGMA MAKE - ZÉRO EMOJI)
# =============================================================================
if not st.session_state["authenticated"]:
    render_html(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: #047857; border-radius: 10px; color: white; margin-bottom: 8px;">
            {ICONS['stethoscope']}
        </div>
        <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a; line-height: 1.15;">NLParto</div>
        <div style="font-size: 0.7rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #64748b; margin-top: 2px;">
            Validation Clinique &middot; Santé Maternelle & Infantile
        </div>
    </div>
    """)

    with st.container(border=True):
        render_html(f"""
        <div style="margin-bottom: 16px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; font-size: 0.76rem; font-weight: 600; padding: 2px 8px; border-radius: 6px; margin-bottom: 8px;">
                {ICONS['shield']}
                Santé maternelle & infantile
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a; line-height: 1.3; margin-bottom: 4px;">
                Validation clinique des dialogues de santé
            </div>
            <div style="font-size: 0.86rem; color: #475569; line-height: 1.45;">
                Évaluez la conformité médicale et la sécurité des réponses générées en Darja algérienne. Aucun mot de passe requis.
            </div>
        </div>
        <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 14px 0;">
        <div style="font-size: 0.84rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">
            1. Identifiant / nom du praticien
        </div>
        <div style="font-size: 0.78rem; color: #64748b; margin-bottom: 8px;">
            Utilisez votre nom ou vos initiales professionnelles.
        </div>
        """)

        doc_name = st.text_input(
            "Identifiant du praticien",
            value=st.session_state.get("reviewer_name", ""),
            placeholder="Ex. Dr. Amine Benali",
            label_visibility="collapsed"
        )

        render_html("""
        <div style="margin-top: 14px; margin-bottom: 4px;">
            <div style="font-size: 0.84rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">
                2. Profil médical
            </div>
            <div style="font-size: 0.78rem; color: #64748b;">
                Permet de pondérer les évaluations cliniques.
            </div>
        </div>
        """)

        role_ids = [r["id"] for r in MEDICAL_ROLES]
        selected_role = st.radio(
            "Profil médical",
            options=role_ids,
            index=role_ids.index(st.session_state.get("reviewer_role", "generaliste")),
            format_func=lambda rid: next(f"**{r['title']}**\n{r['subtitle']}" for r in MEDICAL_ROLES if r["id"] == rid),
            label_visibility="collapsed"
        )

        render_html(f"""
        <div style="background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 12px 16px; margin-top: 16px; margin-bottom: 16px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #0369a1; display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                {ICONS['file_text']}
                Directives cliniques / تعليمات التقييم
            </div>
            <div style="font-size: 0.82rem; color: #0c4a6e; line-height: 1.45; margin-bottom: 6px;">
                <strong>Français :</strong> Validez si la réponse respecte la recommandation médicale. Tolérance zéro pour les prescriptions ou posologies de médicaments.
            </div>
            <div style="border-top: 1px dashed #cbd5e1; padding-top: 6px; font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 0.9rem; font-weight: 600; color: #0c4a6e; line-height: 1.55;">
                تأكد من صحة المعلومة بالدارجة الجزائرية وعدم تقديم أي جرعات أدوية. ارفض أي إجابة قد تشكل خطراً على صحة الأم أو الطفل.
            </div>
        </div>
        """)

        if st.button("Commencer l'évaluation  · Série de 20 questions →", type="primary", use_container_width=True):
            if not doc_name or not doc_name.strip():
                st.error("Veuillez renseigner votre identifiant avant de continuer.")
            else:
                st.session_state["reviewer_name"] = doc_name.strip()
                st.session_state["reviewer_role"] = selected_role
                st.session_state["authenticated"] = True

                st.session_state["batch"] = claim_batch(
                    session_id=st.session_state["session_id"],
                    reviewer_name=st.session_state["reviewer_name"],
                    reviewer_role=st.session_state["reviewer_role"],
                    batch_size=BATCH_SIZE
                )
                st.session_state["current_idx"] = 0
                st.session_state["completed"] = False
                st.session_state["decision_choice"] = "valider"
                st.session_state["batch_stats"] = {"valider": 0, "corriger": 0, "rejeter": 0}
                st.rerun()

    st.stop()


# =============================================================================
# ÉCRAN 3 : SÉRIE TERMINÉE (ZÉRO EMOJI)
# =============================================================================
if st.session_state["completed"]:
    with st.container(border=True):
        render_html(f"""
        <div style="text-align: center; padding: 18px 10px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; color: #047857; margin-bottom: 10px;">
                {ICONS['check_check']}
            </div>
            <h2 style="color: #065f46; font-size: 1.35rem; font-weight: 700; margin-bottom: 4px;">
                Merci {st.session_state['reviewer_name']} !
            </h2>
            <p style="color: #047857; font-size: 0.92rem; line-height: 1.45; margin-bottom: 18px;">
                Vos évaluations ont été enregistrées avec succès dans la base clinique NLParto.<br>
                <strong style="font-family: 'Cairo', sans-serif;">شكراً جزيلاً على مساهمتكم في دعم صحة الأم والطفل.</strong>
            </p>
            <div style="display: flex; justify-content: center; gap: 10px; margin-bottom: 18px;">
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 16px; min-width: 85px;">
                    <div style="font-size: 1.35rem; font-weight: 700; color: #065f46;">{st.session_state['batch_stats']['valider']}</div>
                    <div style="font-size: 0.72rem; color: #047857; font-weight: 600;">Validées</div>
                </div>
                <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 10px 16px; min-width: 85px;">
                    <div style="font-size: 1.35rem; font-weight: 700; color: #92400e;">{st.session_state['batch_stats']['corriger']}</div>
                    <div style="font-size: 0.72rem; color: #b45309; font-weight: 600;">Corrigées</div>
                </div>
                <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 10px 16px; min-width: 85px;">
                    <div style="font-size: 1.35rem; font-weight: 700; color: #991b1b;">{st.session_state['batch_stats']['rejeter']}</div>
                    <div style="font-size: 0.72rem; color: #b91c1c; font-weight: 600;">Rejetées</div>
                </div>
            </div>
        </div>
        """)

        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Évaluer une autre série de 20 questions →", type="primary", use_container_width=True):
                st.session_state["batch"] = claim_batch(
                    session_id=st.session_state["session_id"],
                    reviewer_name=st.session_state["reviewer_name"],
                    reviewer_role=st.session_state["reviewer_role"],
                    batch_size=BATCH_SIZE
                )
                st.session_state["current_idx"] = 0
                st.session_state["completed"] = False
                st.session_state["decision_choice"] = "valider"
                st.session_state["batch_stats"] = {"valider": 0, "corriger": 0, "rejeter": 0}
                st.rerun()
        with col2:
            if st.button("Changer de praticien", use_container_width=True):
                st.session_state["authenticated"] = False
                st.rerun()

    st.stop()


# =============================================================================
# ÉCRAN 2 : ESPACE D'ÉVALUATION CLINIQUE (FIDÉLITÉ FIGMA MAKE - ZÉRO EMOJI)
# =============================================================================
batch = st.session_state.get("batch", [])
if not batch:
    st.info("Toutes les questions disponibles ont été évaluées.")
    st.stop()

idx = st.session_state["current_idx"]
if idx >= len(batch):
    st.session_state["completed"] = True
    st.rerun()

current_row = batch[idx]
row_id = current_row["id"]
role_meta = next((r for r in MEDICAL_ROLES if r["id"] == st.session_state["reviewer_role"]), MEDICAL_ROLES[3])
avatar_letter = (st.session_state["reviewer_name"] or "D")[0].upper()

# 1. En-tête supérieur compact
render_html(f"""
<div style="display: flex; align-items: center; justify-content: space-between; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 14px; margin-bottom: 12px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; background: #047857; border-radius: 6px; color: white;">
            {ICONS['stethoscope']}
        </span>
        <span style="font-size: 0.88rem; font-weight: 700; color: #0f172a;">NLParto</span>
        <span style="font-size: 0.72rem; color: #64748b; border-left: 1px solid #e2e8f0; padding-left: 8px;">Validation Clinique</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; color: #334155;">
        <span style="font-weight: 700; color: #0f172a;">{st.session_state['reviewer_name']}</span>
        <span style="color: #64748b;">({role_meta['badge']})</span>
    </div>
</div>
""")

# 2. Compteur & Sortie
total_q = len(batch)
pct = int((idx / total_q) * 100)

col_top_left, col_top_right = st.columns([3, 1])
with col_top_left:
    render_html(f"""
    <div style="font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b;">
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
render_html(f"<div style='text-align: right; font-size: 0.74rem; color: #64748b; margin-top: -8px; margin-bottom: 12px;'>{pct}% terminé</div>")

# Badges de métadonnées
topic = current_row.get("topic", "santé générale").capitalize()
risk = current_row.get("risk_level", "routine").capitalize()
render_html(f"""
<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 12px;">
    <span style="background: #f1f5f9; border: 1px solid #e2e8f0; color: #475569; font-size: 0.72rem; font-weight: 600; padding: 2px 7px; border-radius: 5px;">
        {topic}
    </span>
    <span style="background: #fef3c7; border: 1px solid #fde68a; color: #92400e; font-size: 0.72rem; font-weight: 600; padding: 2px 7px; border-radius: 5px;">
        {risk}
    </span>
    <span style="background: #f8fafc; border: 1px solid #e2e8f0; color: #64748b; font-family: monospace; font-size: 0.72rem; font-weight: 600; padding: 2px 7px; border-radius: 5px;">
        {row_id}
    </span>
</div>
""")

# -----------------------------------------------------------------------------
# 3. SECTION 1 : QUESTION DE LA MAMAN (REGARD TOMBE DIRECTEMENT ICI)
# -----------------------------------------------------------------------------
question_ar = current_row.get("question_ar", "")
question_lat = current_row.get("question_lat", "")

render_html(f"""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.02);">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #f1f5f9; border-radius: 5px; color: #475569;">
                {ICONS['user']}
            </span>
            <span style="font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #475569;">Question de la maman</span>
        </div>
        <span style="font-size: 0.72rem; color: #64748b; font-weight: 600;">Darja algérienne</span>
    </div>

    <!-- 1. En lettres françaises (Arabizi) -->
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #047857; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
            {ICONS['languages']}
            En lettres françaises (Arabizi) :
        </div>
        <div style="font-family: 'Inter', -apple-system, sans-serif; font-size: 1.1rem; color: #0f172a; line-height: 1.55; font-weight: 600;">
            {question_lat or "—"}
        </div>
    </div>

    <!-- 2. En écriture arabe (Cairo) -->
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #047857; margin-bottom: 4px; text-align: right;">
            بالحروف العربية :
        </div>
        <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.25rem; font-weight: 700; color: #0f172a; line-height: 1.65;">
            {question_ar}
        </div>
    </div>
</div>
""")

# -----------------------------------------------------------------------------
# 4. SECTION 2 : RÉPONSE PROPOSÉE PAR L'ASSISTANT
# -----------------------------------------------------------------------------
answer_darja = current_row.get("answer_darja", "")

render_html(f"""
<div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #e0f2fe;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #0284c7; border-radius: 5px; color: white;">
                {ICONS['message']}
            </span>
            <span style="font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #0369a1;">Réponse proposée par l'assistant</span>
        </div>
        <span style="background: #e0f2fe; color: #0369a1; font-size: 0.7rem; font-weight: 600; padding: 1px 6px; border-radius: 4px;">À évaluer</span>
    </div>
    <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.25rem; font-weight: 600; color: #0c4a6e; line-height: 1.7; padding: 4px 0;">
        « {answer_darja} »
    </div>
</div>
""")

# -----------------------------------------------------------------------------
# 5. SECTION 3 : DÉCISION MÉDICALE DU PRATICIEN
# -----------------------------------------------------------------------------
with st.container(border=True):
    render_html("""
    <div style="margin-bottom: 10px;">
        <div style="font-size: 0.74rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b;">Votre évaluation clinique :</div>
        <div style="font-size: 0.9rem; font-weight: 600; color: #0f172a; margin-top: 1px;">Cette réponse est-elle médicale et sûre pour la mère et l'enfant ?</div>
    </div>
    """)

    b_col1, b_col2, b_col3 = st.columns(3)
    current_choice = st.session_state["decision_choice"]

    with b_col1:
        is_v = (current_choice == "valider")
        v_btn = st.button(
            "Valider\nConforme & sûr",
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
            "Corriger\nModifier le texte",
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
            "Rejeter\nDangereux / erroné",
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
        render_html(f"""
        <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 10px 14px; margin-top: 12px; margin-bottom: 6px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #92400e; display: flex; align-items: center; gap: 5px;">
                {ICONS['edit']}
                Correction de la réponse en Darja :
            </div>
            <div style="font-size: 0.74rem; color: #b45309; margin-top: 2px;">
                Modifiez le texte. Tolérance zéro pour les prescriptions ou posologies de médicaments.
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
        render_html(f"""
        <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 10px 14px; margin-top: 12px; margin-bottom: 6px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #991b1b; display: flex; align-items: center; gap: 5px;">
                {ICONS['x']}
                Motif(s) du rejet clinique :
            </div>
            <div style="font-size: 0.74rem; color: #b91c1c; margin-top: 2px;">
                Sélectionnez au moins un motif de non-conformité :
            </div>
        </div>
        """)

        r1 = st.checkbox("Prescription de médicament / posologie interdite", key=f"r1_{row_id}")
        r2 = st.checkbox("Erreur médicale ou danger clinique", key=f"r2_{row_id}")
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

    # Bouton de confirmation immédiate
    col_sub_left, col_sub_right = st.columns([1.5, 1.5])
    with col_sub_left:
        render_html("""
        <div style="display: flex; align-items: center; font-size: 0.76rem; color: #64748b; height: 100%; padding-top: 8px;">
            Enregistrement immédiat sur disque
        </div>
        """)

    with col_sub_right:
        if st.button("Confirmer & question suivante →", type="primary", use_container_width=True):
            decision = st.session_state["decision_choice"]

            if decision == "rejeter" and not reject_reasons and not notes_val:
                st.warning("Veuillez cocher au moins un motif de rejet ou ajouter une note.")
            else:
                save_single_decision(
                    row_id=row_id,
                    decision=decision,
                    corrected_text=corrected_val if decision == "corriger" else "",
                    reject_reasons=reject_reasons if decision == "rejeter" else [],
                    notes=notes_val,
                    session_id=st.session_state["session_id"],
                    reviewer_name=st.session_state["reviewer_name"],
                    reviewer_role=st.session_state["reviewer_role"]
                )

                st.session_state["batch_stats"][decision] += 1
                st.session_state["decision_choice"] = "valider"
                if idx + 1 >= len(batch):
                    st.session_state["completed"] = True
                else:
                    st.session_state["current_idx"] += 1

                st.rerun()
