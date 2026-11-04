"""NLParto - Plateforme de Validation Clinique (Santé Maternelle & Infantile)
Interface praticiens ergonomique, calme et adaptée aux médecins algériens.
"""
import streamlit as st
import uuid
import re
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
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)


def render_html(html_str: str):
    """Rendu HTML sécurisé sans risque d'interprétation Markdown (pas d'indentation en bloc de code)."""
    # Nettoyage des lignes pour éviter le déclenchement de blocs de code CommonMark (4 espaces après ligne vide)
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Styles CSS calmes et ergonomiques
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Reset global et typographie douce */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 760px !important;
    }

    /* Cartes blanches douces */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 22px 24px !important;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 16px !important;
    }

    /* Champs de saisie */
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
        padding: 12px 14px !important;
        font-size: 0.95rem !important;
        color: #0f172a !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #059669 !important;
        box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.15) !important;
    }

    /* Grille rôles médicaux */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
        margin-top: 8px !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: flex-start !important;
        gap: 10px !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        min-height: 72px !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        border-color: #cbd5e1 !important;
        background-color: #f8fafc !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked),
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #059669 !important;
        background-color: #f0fdf4 !important;
        box-shadow: 0 0 0 1px #059669 !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        font-size: 0.86rem !important;
        line-height: 1.35 !important;
        color: #0f172a !important;
        white-space: pre-line !important;
    }

    /* Bouton principal vert médical */
    button[data-testid="stBaseButton-primary"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px !important;
        box-shadow: 0 2px 4px -1px rgba(5, 150, 105, 0.2) !important;
        transition: all 0.15s ease !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #047857 !important;
        box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.3) !important;
    }

    /* Boutons secondaires */
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #334155 !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        transition: all 0.15s ease !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        border-color: #94a3b8 !important;
        background-color: #f8fafc !important;
    }

    /* Zone de texte de correction RTL */
    div[data-testid="stTextArea"] textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 1.15rem !important;
        line-height: 1.65 !important;
        border-radius: 10px !important;
        border: 1.5px solid #fde047 !important;
        background-color: #fffef7 !important;
        color: #0f172a !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #eab308 !important;
        box-shadow: 0 0 0 2px rgba(234, 179, 8, 0.2) !important;
    }

    /* Barre de progression émeraude */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #059669 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# État de la session
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
# ÉCRAN 1 : PAGE D'ACCUEIL / IDENTIFICATION DU PRATICIEN
# =============================================================================
if not st.session_state["authenticated"]:
    # En-tête calme
    render_html("""
    <div style="text-align: center; margin-bottom: 22px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: #059669; border-radius: 10px; color: white; font-size: 22px; margin-bottom: 8px;">
            🩺
        </div>
        <div style="font-size: 1.3rem; font-weight: 700; color: #0f172a; line-height: 1.2;">NLParto</div>
        <div style="font-size: 0.72rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #64748b; margin-top: 2px;">
            Validation Clinique &middot; Santé Maternelle & Infantile
        </div>
    </div>
    """)

    with st.container(border=True):
        render_html("""
        <div style="margin-bottom: 18px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.78rem; font-weight: 600; padding: 3px 10px; border-radius: 16px; margin-bottom: 10px;">
                🌿 Espace praticiens de santé
            </div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #0f172a; line-height: 1.3; margin-bottom: 6px;">
                Évaluation médicale des dialogues en Darja
            </div>
            <div style="font-size: 0.9rem; color: #475569; line-height: 1.5;">
                Vérifiez la pertinence et la sécurité des réponses proposées aux mamans. Aucun mot de passe requis.
            </div>
        </div>
        <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 16px 0;">
        <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">
            1. Nom ou identifiant du praticien
        </div>
        <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 8px;">
            Nom, initiales ou titre professionnel.
        </div>
        """)

        doc_name = st.text_input(
            "Identifiant du praticien",
            value=st.session_state.get("reviewer_name", ""),
            placeholder="Ex. Dr. Amine Benali",
            label_visibility="collapsed"
        )

        render_html("""
        <div style="margin-top: 16px; margin-bottom: 6px;">
            <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">
                2. Profil médical
            </div>
            <div style="font-size: 0.8rem; color: #64748b;">
                Permet d'adapter l'analyse de vos retours.
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

        # Directives cliniques
        render_html("""
        <div style="background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 14px 18px; margin-top: 18px; margin-bottom: 18px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #1e40af; margin-bottom: 6px;">
                📋 Consignes de validation
            </div>
            <div style="font-size: 0.84rem; color: #1e3a8a; line-height: 1.5; margin-bottom: 8px;">
                Approuvez si la réponse est bienveillante et médicalement sûre. Tolérance zéro pour la prescription ou le dosage de médicaments.
            </div>
            <div style="border-top: 1px dashed #cbd5e1; padding-top: 8px; font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 0.92rem; font-weight: 600; color: #1e293b; line-height: 1.6;">
                تأكد من سلامة الإجابة وعدم تقديم أي جرعات أدوية. ارفض أي نصيحة قد تضر بصحة الأم أو الطفل.
            </div>
        </div>
        """)

        if st.button("Commencer l'évaluation (Série de 20 questions) →", type="primary", use_container_width=True):
            if not doc_name or not doc_name.strip():
                st.error("Veuillez renseigner votre nom ou identifiant.")
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
# ÉCRAN 3 : SÉRIE TERMINÉE
# =============================================================================
if st.session_state["completed"]:
    st.balloons()
    with st.container(border=True):
        render_html(f"""
        <div style="text-align: center; padding: 20px 10px;">
            <div style="font-size: 40px; margin-bottom: 8px;">🎉</div>
            <h2 style="color: #065f46; font-size: 1.4rem; font-weight: 700; margin-bottom: 6px;">
                Merci {st.session_state['reviewer_name']} !
            </h2>
            <p style="color: #047857; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                Vos évaluations ont été enregistrées avec succès.<br>
                <strong style="font-family: 'Cairo', sans-serif;">شكراً جزيلاً على مساهمتكم في دعم صحة الأم والطفل.</strong>
            </p>
            <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 20px;">
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 12px 18px; min-width: 90px;">
                    <div style="font-size: 1.4rem; font-weight: 700; color: #065f46;">{st.session_state['batch_stats']['valider']}</div>
                    <div style="font-size: 0.72rem; color: #047857; font-weight: 600;">Validées</div>
                </div>
                <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 12px 18px; min-width: 90px;">
                    <div style="font-size: 1.4rem; font-weight: 700; color: #92400e;">{st.session_state['batch_stats']['corriger']}</div>
                    <div style="font-size: 0.72rem; color: #b45309; font-weight: 600;">Corrigées</div>
                </div>
                <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; padding: 12px 18px; min-width: 90px;">
                    <div style="font-size: 1.4rem; font-weight: 700; color: #991b1b;">{st.session_state['batch_stats']['rejeter']}</div>
                    <div style="font-size: 0.72rem; color: #b91c1c; font-weight: 600;">Rejetées</div>
                </div>
            </div>
        </div>
        """)

        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Évaluer une autre série de 20 questions 🔄", type="primary", use_container_width=True):
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
# ÉCRAN 2 : ESPACE D'ÉVALUATION CLINIQUE (ERGONOMIE MÉDICALE MAXIMALE)
# =============================================================================
batch = st.session_state.get("batch", [])
if not batch:
    st.info("Toutes les questions disponibles ont été évaluées !")
    st.stop()

idx = st.session_state["current_idx"]
if idx >= len(batch):
    st.session_state["completed"] = True
    st.rerun()

current_row = batch[idx]
row_id = current_row["id"]
role_meta = next((r for r in MEDICAL_ROLES if r["id"] == st.session_state["reviewer_role"]), MEDICAL_ROLES[3])
avatar_letter = (st.session_state["reviewer_name"] or "D")[0].upper()

# 1. Barre de navigation compacte
render_html(f"""
<div style="display: flex; align-items: center; justify-content: space-between; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 14px; margin-bottom: 14px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 18px;">🩺</span>
        <span style="font-size: 0.9rem; font-weight: 700; color: #0f172a;">NLParto</span>
        <span style="font-size: 0.72rem; color: #64748b; border-left: 1px solid #cbd5e1; padding-left: 8px;">Validation Clinique</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #334155;">
        <div style="width: 20px; height: 20px; background: #e2e8f0; color: #0f172a; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.7rem;">
            {avatar_letter}
        </div>
        <span><strong>{st.session_state['reviewer_name']}</strong> ({role_meta['badge']})</span>
    </div>
</div>
""")

# 2. Progression de la série
total_q = len(batch)
pct = int((idx / total_q) * 100)

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
render_html(f"<div style='text-align: right; font-size: 0.75rem; color: #64748b; margin-top: -8px; margin-bottom: 12px;'>{pct}% terminé</div>")

# Badges thématiques
topic = current_row.get("topic", "santé générale").capitalize()
risk = current_row.get("risk_level", "routine").capitalize()
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px;">
    <span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.74rem; font-weight: 600; padding: 2px 8px; border-radius: 6px;">
        📖 {topic}
    </span>
    <span style="background: #fef3c7; border: 1px solid #fde68a; color: #b45309; font-size: 0.74rem; font-weight: 600; padding: 2px 8px; border-radius: 6px;">
        ⚠️ {risk}
    </span>
    <span style="background: #f1f5f9; border: 1px solid #e2e8f0; color: #64748b; font-family: monospace; font-size: 0.74rem; font-weight: 600; padding: 2px 8px; border-radius: 6px;">
        {row_id}
    </span>
</div>
""")

# -----------------------------------------------------------------------------
# 3. CARTE PRINCIPALE : QUESTION DE LA MAMAN (Sans Ground Truth distrayant)
# -----------------------------------------------------------------------------
question_ar = current_row.get("question_ar", "")
question_lat = current_row.get("question_lat", "")

render_html(f"""
<div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="font-size: 16px;">👤</span>
            <span style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #475569;">Question de la maman</span>
            <span style="background: #f1f5f9; color: #64748b; font-size: 0.72rem; font-weight: 600; padding: 1px 6px; border-radius: 4px;">Darja</span>
        </div>
        <div style="font-size: 0.74rem; color: #64748b; font-weight: 600;">
            {topic} &middot; {risk}
        </div>
    </div>

    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;">
        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #047857; margin-bottom: 4px;">
            🔤 En lettres françaises (Arabizi) :
        </div>
        <div style="font-family: 'Inter', -apple-system, sans-serif; font-size: 1.12rem; color: #0f172a; line-height: 1.55; font-weight: 600;">
            {question_lat or "—"}
        </div>
    </div>

    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px;">
        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #047857; margin-bottom: 4px; text-align: right;">
            بالحروف العربية :
        </div>
        <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.25rem; font-weight: 700; color: #0f172a; line-height: 1.65;">
            {question_ar}
        </div>
    </div>
</div>
""")

# -----------------------------------------------------------------------------
# 4. CARTE SECONDAIRE : RÉPONSE PROPOSÉE PAR L'ASSISTANT
# -----------------------------------------------------------------------------
answer_darja = current_row.get("answer_darja", "")

render_html(f"""
<div style="background: #f0f9ff; border: 1.5px solid #7dd3fc; border-radius: 12px; padding: 18px 20px; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid #e0f2fe;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="font-size: 16px;">💬</span>
            <span style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #0369a1;">Réponse proposée par l'assistant</span>
        </div>
        <span style="background: #e0f2fe; color: #0284c7; font-size: 0.72rem; font-weight: 600; padding: 1px 6px; border-radius: 4px;">À évaluer</span>
    </div>
    <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.25rem; font-weight: 600; color: #0c4a6e; line-height: 1.7; padding: 4px 0;">
        « {answer_darja} »
    </div>
</div>
""")

# -----------------------------------------------------------------------------
# 5. CARTE DÉCISION MÉDICALE DU PRATICIEN
# -----------------------------------------------------------------------------
with st.container(border=True):
    render_html("""
    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 12px;">
        <span style="font-size: 16px;">📋</span>
        <div>
            <div style="font-size: 0.76rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b;">Décision médicale</div>
            <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a;">Cette réponse est-elle sûre et correcte ?</div>
        </div>
    </div>
    """)

    b_col1, b_col2, b_col3 = st.columns(3)
    current_choice = st.session_state["decision_choice"]

    with b_col1:
        is_v = (current_choice == "valider")
        v_btn = st.button(
            "✓  Valider\nApprouvé",
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
            "✏️  Corriger\nModifier le texte",
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
            "✕  Rejeter\nDangereux / erroné",
            key=f"btn_r_{row_id}",
            type="primary" if is_r else "secondary",
            use_container_width=True
        )
        if r_btn:
            st.session_state["decision_choice"] = "rejeter"
            st.rerun()

    corrected_val = ""
    reject_reasons = []

    # Section dynamique selon le bouton actif
    if current_choice == "corriger":
        render_html("""
        <div style="background: #fffdf0; border: 1.5px solid #fde047; border-radius: 10px; padding: 12px 16px; margin-top: 14px; margin-bottom: 8px;">
            <div style="font-size: 0.86rem; font-weight: 700; color: #854d0e; margin-bottom: 2px;">
                ✏️ Correction de la réponse en Darja
            </div>
            <div style="font-size: 0.78rem; color: #a16207;">
                Modifiez le texte directement. Tolérance zéro pour les doses de médicaments.
            </div>
        </div>
        """)

        corrected_val = st.text_area(
            "Réponse Darja corrigée",
            value=answer_darja,
            height=110,
            key=f"corr_box_{row_id}",
            label_visibility="collapsed"
        )

    elif current_choice == "rejeter":
        render_html("""
        <div style="background: #fef2f2; border: 1.5px solid #fca5a5; border-radius: 10px; padding: 12px 16px; margin-top: 14px; margin-bottom: 8px;">
            <div style="font-size: 0.86rem; font-weight: 700; color: #991b1b; margin-bottom: 2px;">
                ✕ Motif(s) du rejet :
            </div>
            <div style="font-size: 0.78rem; color: #b91c1c;">
                Sélectionnez la raison du non-respect clinique :
            </div>
        </div>
        """)

        r1 = st.checkbox("💊 Prescription ou dosage de médicament (interdit)", key=f"r1_{row_id}")
        r2 = st.checkbox("⚠️ Erreur médicale clinique ou diagnostic non fondé", key=f"r2_{row_id}")
        r3 = st.checkbox("🗣️ Darja incorrecte / mots non algériens", key=f"r3_{row_id}")
        r4 = st.checkbox("🚨 Urgence vitale non signalée (danger vital)", key=f"r4_{row_id}")
        if r1: reject_reasons.append("prescription_dose")
        if r2: reject_reasons.append("erreur_medicale")
        if r3: reject_reasons.append("darja_incorrecte")
        if r4: reject_reasons.append("urgence_non_signalee")

    render_html("""
    <div style="margin-top: 14px; margin-bottom: 4px; font-size: 0.82rem; font-weight: 600; color: #0f172a;">
        Note ou remarque clinique <span style="color: #64748b; font-weight: 400;">(optionnelle)</span>
    </div>
    """)

    notes_val = st.text_input(
        "Note / remarque clinique",
        placeholder="Ajoutez un contexte clinique si nécessaire...",
        key=f"notes_box_{row_id}",
        label_visibility="collapsed"
    )

    render_html("<div style='margin-top: 16px;'></div>")

    # Barre de confirmation
    col_sub_left, col_sub_right = st.columns([1.5, 1.5])
    with col_sub_left:
        render_html("""
        <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #64748b; height: 100%; padding-top: 10px;">
            🔒 Enregistrement immédiat sur disque
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
