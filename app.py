"""NLParto - Plateforme de Validation Clinique (Santé Maternelle & Infantile)
Interface praticiens conforme 1:1 aux 5 captures d'écran.
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
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Styles CSS avancés (Fidélité 1:1 absolue aux captures d'écran)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

    /* Reset global et typographie */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Masquer les menus par défaut de Streamlit */
    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 780px !important;
    }

    /* Conteneurs avec bordures Streamlit stylisés comme les cartes */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px 28px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 18px !important;
    }

    /* Style des champs texte */
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
        box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2) !important;
    }

    /* GRILLE 2 COLONNES POUR LES 6 RÔLES MÉDICAUX */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 12px !important;
        margin-top: 8px !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: flex-start !important;
        gap: 10px !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        min-height: 78px !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        border-color: #cbd5e1 !important;
        background-color: #f8fafc !important;
    }

    /* Rôle sélectionné : bordure verte et fond vert pâle (exactement comme Photo 1) */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked),
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #059669 !important;
        background-color: #f0fdf4 !important;
        box-shadow: 0 0 0 1px #059669 !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        font-size: 0.88rem !important;
        line-height: 1.35 !important;
        color: #0f172a !important;
        white-space: pre-line !important;
    }

    /* Bouton CTA Principal Vert (Émeraude) */
    button[data-testid="stBaseButton-primary"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 24px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #047857 !important;
        box-shadow: 0 6px 10px -1px rgba(5, 150, 105, 0.35) !important;
    }

    /* Boutons Secondaires */
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #334155 !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        border-color: #94a3b8 !important;
        background-color: #f8fafc !important;
    }

    /* Zone de texte RTL pour la réponse corrigée */
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

    /* Barre de progression personnalisée */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #059669 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Initialisation de l'état
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
# ÉCRAN 1 : PAGE D'ACCUEIL / ONBOARDING (PHOTOS 1 & 2)
# =============================================================================
if not st.session_state["authenticated"]:
    # 1. En-tête de marque
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: #059669; border-radius: 12px; color: white; font-size: 24px; box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.25); margin-bottom: 8px;">
            🩺
        </div>
        <div style="font-size: 1.35rem; font-weight: 800; color: #0f172a; line-height: 1.2;">NLParto</div>
        <div style="font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #64748b; margin-top: 2px;">VALIDATION CLINIQUE</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Carte Principale
    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.8rem; font-weight: 600; padding: 4px 12px; border-radius: 20px; margin-bottom: 12px;">
                🌿 Santé maternelle & infantile
            </div>
            <div style="font-size: 1.65rem; font-weight: 800; color: #0f172a; line-height: 1.25; margin-bottom: 8px; letter-spacing: -0.4px;">
                Votre expertise protège les mamans et les enfants.
            </div>
            <div style="font-size: 0.92rem; color: #475569; line-height: 1.55;">
                Évaluez des dialogues de santé en Darja algérienne et vérifiez qu'ils respectent les références cliniques officielles. Aucun compte ni mot de passe requis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border: none; border-top: 1px solid #f1f5f9; margin: 18px 0;'>", unsafe_allow_html=True)

        # Formulaire Praticien
        st.markdown("""
        <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">
            1. Identifiant / nom du praticien
        </div>
        <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 8px;">
            Utilisez votre nom, vos initiales ou un alias professionnel.
        </div>
        """, unsafe_allow_html=True)

        doc_name = st.text_input(
            "Identifiant du praticien",
            value=st.session_state.get("reviewer_name", ""),
            placeholder="🩺  Ex. Dr. Amine Benali",
            label_visibility="collapsed"
        )

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">
            2. Profil médical
        </div>
        <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 8px;">
            Votre statut aide à interpréter et pondérer les évaluations.
        </div>
        """, unsafe_allow_html=True)

        # 6 Cartes de rôles médicaux (Grille 2x3)
        role_ids = [r["id"] for r in MEDICAL_ROLES]
        
        def format_role(rid):
            item = next(r for r in MEDICAL_ROLES if r["id"] == rid)
            return f"**{item['title']}**\n<span style='color:#64748b; font-size:0.78rem;'>{item['subtitle']}</span>"

        selected_role = st.radio(
            "Profil médical",
            options=role_ids,
            index=role_ids.index(st.session_state.get("reviewer_role", "generaliste")),
            format_func=lambda rid: next(f"**{r['title']}**\n{r['subtitle']}" for r in MEDICAL_ROLES if r["id"] == rid),
            label_visibility="collapsed"
        )

        # Encadré Directives Cliniques Bilingues (Exactement comme Photo 1 & 2)
        st.markdown("""
        <div style="background: #f0f7ff; border: 1.5px solid #bae6fd; border-radius: 12px; padding: 16px 20px; margin-top: 22px; margin-bottom: 22px;">
            <div style="font-size: 0.9rem; font-weight: 700; color: #1e40af; display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                📖 Directives cliniques / تعليمات التقييم
            </div>
            <div style="font-size: 0.76rem; font-weight: 800; color: #1d4ed8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                FRANÇAIS
            </div>
            <div style="font-size: 0.86rem; color: #1e3a8a; line-height: 1.5; margin-bottom: 12px;">
                Validez si la réponse en Darja respecte la recommandation médicale. Tolérance zéro pour les prescriptions ou les doses de médicaments.
            </div>
            <div style="border-top: 1px dashed #cbd5e1; padding-top: 10px; font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 0.94rem; font-weight: 600; color: #1e293b; line-height: 1.6;">
                تأكد من دقة الإجابة بالدارجة الجزائرية وعدم تقديم أي جرعات أدوية. ارفض أي إجابة قد تشكل خطراً على الأم أو الطفل.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Bouton CTA vert "Commencer l'évaluation Série de 20 ->"
        if st.button("Commencer l'évaluation  Série de 20  →", type="primary", use_container_width=True):
            if not doc_name or not doc_name.strip():
                st.error("Veuillez saisir votre nom ou alias avant de commencer.")
            else:
                st.session_state["reviewer_name"] = doc_name.strip()
                st.session_state["reviewer_role"] = selected_role
                st.session_state["authenticated"] = True

                # Verrouiller immédiatement 20 questions exclusives
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

        st.markdown("""
        <div style="text-align: center; font-size: 0.78rem; color: #94a3b8; margin-top: 14px;">
            🔒 Votre profil sera mémorisé sur cet appareil.
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# =============================================================================
# ÉCRAN 3 : SÉRIE COMPLÉTÉE
# =============================================================================
if st.session_state["completed"]:
    st.balloons()
    with st.container(border=True):
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 10px;">
            <div style="font-size: 48px; margin-bottom: 10px;">🎉</div>
            <h2 style="color: #166534; font-weight: 800; margin-bottom: 6px;">
                Merci {st.session_state['reviewer_name']} !
            </h2>
            <p style="color: #15803d; font-size: 1.05rem; line-height: 1.5; margin-bottom: 20px;">
                Votre série a été enregistrée avec succès dans la base clinique NLParto.<br>
                <strong>شكراً جزيلاً على مساهمتكم القيمة في حماية صحة الأم والطفل.</strong>
            </p>
            <div style="display: flex; justify-content: center; gap: 14px; margin-bottom: 24px;">
                <div style="background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 12px; padding: 14px 20px; min-width: 100px;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #166534;">{st.session_state['batch_stats']['valider']}</div>
                    <div style="font-size: 0.75rem; color: #15803d; font-weight: 700;">Validées</div>
                </div>
                <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 12px; padding: 14px 20px; min-width: 100px;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #b45309;">{st.session_state['batch_stats']['corriger']}</div>
                    <div style="font-size: 0.75rem; color: #a16207; font-weight: 700;">Corrigées</div>
                </div>
                <div style="background: #fef2f2; border: 1.5px solid #fca5a5; border-radius: 12px; padding: 14px 20px; min-width: 100px;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #dc2626;">{st.session_state['batch_stats']['rejeter']}</div>
                    <div style="font-size: 0.75rem; color: #b91c1c; font-weight: 700;">Rejetées</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Évaluer une autre série de 20  🔄", type="primary", use_container_width=True):
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
# ÉCRAN 2 : ESPACE DE RÉVISION CLINIQUE (PHOTOS 3, 4, 5)
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

# -----------------------------------------------------------------------------
# 1. Top Bar de Navigation (Photo 3)
# -----------------------------------------------------------------------------
st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: space-between; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 18px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 32px; height: 32px; background: #059669; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; color: white;">
            🩺
        </div>
        <div>
            <div style="font-size: 0.95rem; font-weight: 800; color: #0f172a; line-height: 1.1;">NLParto</div>
            <div style="font-size: 0.72rem; color: #64748b;">Validation clinique santé maternelle & infantile</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; color: #334155;">
        <div style="width: 22px; height: 22px; background: #cbd5e1; color: #0f172a; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.72rem;">
            {avatar_letter}
        </div>
        <div><strong>{st.session_state['reviewer_name']}</strong> &nbsp;<span style="color:#64748b;">{role_meta['badge']}</span> &nbsp;›</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. En-tête Série & Progression
# -----------------------------------------------------------------------------
total_q = len(batch)
pct = int((idx / total_q) * 100)

col_top_left, col_top_right = st.columns([3, 1])
with col_top_left:
    st.markdown(f"""
    <div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b;">
        SÉRIE EN COURS
    </div>
    <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-top: 2px;">
        Question {idx + 1} sur {total_q}
    </div>
    """, unsafe_allow_html=True)
with col_top_right:
    if st.button("Quitter la série", help="Libère les questions restantes"):
        release_batch(st.session_state["session_id"])
        st.session_state["authenticated"] = False
        st.rerun()

st.progress(idx / total_q)
st.markdown(f"<div style='text-align: right; font-size: 0.78rem; color: #64748b; margin-top: -8px; margin-bottom: 8px;'>{pct}% terminé</div>", unsafe_allow_html=True)

# Badges d'information (Vaccination, Routine, ID)
topic = current_row.get("topic", "santé générale").capitalize()
risk = current_row.get("risk_level", "routine").capitalize()
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
    <span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.74rem; font-weight: 600; padding: 3px 9px; border-radius: 6px;">
        📖 {topic}
    </span>
    <span style="background: #fef3c7; border: 1px solid #fde68a; color: #b45309; font-size: 0.74rem; font-weight: 600; padding: 3px 9px; border-radius: 6px;">
        ⚠️ {risk}
    </span>
    <span style="background: #f1f5f9; border: 1px solid #e2e8f0; color: #64748b; font-family: monospace; font-size: 0.74rem; font-weight: 600; padding: 3px 9px; border-radius: 6px;">
        {row_id}
    </span>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. QUESTION DE LA MAMAN (En tête - Sans Ground Truth distrayant)
# -----------------------------------------------------------------------------
question_ar = current_row.get("question_ar", "")
question_lat = current_row.get("question_lat", "")

st.markdown(f"""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 16px;">👤</span>
            <div>
                <div style="font-size: 0.74rem; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b;">QUESTION DE LA MAMAN</div>
                <div style="font-size: 0.8rem; font-weight: 600; color: #0f172a;">Darja algérienne</div>
            </div>
        </div>
        <div style="font-size: 0.72rem; color: #64748b; font-weight: 600;">
            {topic} · {risk}
        </div>
    </div>
    
    <!-- Version en lettres françaises (Arabizi) -->
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;">
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin-bottom: 4px;">🔤 En lettres françaises (Arabizi) :</div>
        <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #1e293b; line-height: 1.5; font-weight: 600;">
            {question_lat or "—"}
        </div>
    </div>

    <!-- Version en écriture arabe -->
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px;">
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin-bottom: 4px; text-align: right;">بالحروف العربية :</div>
        <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.25rem; font-weight: 700; color: #0f172a; line-height: 1.6;">
            {question_ar}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. CARTE 3 : RÉPONSE PROPOSÉE PAR L'IA (Photo 3 & 4)
# -----------------------------------------------------------------------------
answer_darja = current_row.get("answer_darja", "")

st.markdown(f"""
<div style="background: #f0f9ff; border: 1.5px solid #7dd3fc; border-radius: 14px; padding: 18px 22px; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
        <span style="font-size: 18px;">✨</span>
        <div>
            <div style="font-size: 0.76rem; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; color: #0369a1;">RÉPONSE PROPOSÉE PAR L'IA</div>
            <div style="font-size: 0.82rem; font-weight: 600; color: #0284c7;">À valider cliniquement</div>
        </div>
    </div>
    <div style="font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.22rem; font-weight: 600; color: #0369a1; line-height: 1.65;">
        « {answer_darja} »
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. CARTE 4 : DÉCISION MÉDICALE (3 Boutons Tactiles - Photos 4 & 5)
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px;">
        <span style="font-size: 18px;">📋</span>
        <div>
            <div style="font-size: 0.76rem; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; color: #64748b;">DÉCISION MÉDICALE DU PRATICIEN</div>
            <div style="font-size: 0.94rem; font-weight: 700; color: #0f172a;">Cette réponse est-elle sûre et correcte ?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3 Boutons tactiles côte-à-côte
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
            "✏️  Corriger\nModifier la réponse",
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
            "✕  Rejeter\nDangereux / incorrect",
            key=f"btn_r_{row_id}",
            type="primary" if is_r else "secondary",
            use_container_width=True
        )
        if r_btn:
            st.session_state["decision_choice"] = "rejeter"
            st.rerun()

    # SECTION EXPANDABLE SELON LE CHOIX
    corrected_val = ""
    reject_reasons = []

    # 1. SI CORRIGER EST SÉLECTIONNÉ (Exactement comme Photo 5)
    if current_choice == "corriger":
        st.markdown("""
        <div style="background: #fffdf0; border: 1.5px solid #fde047; border-radius: 12px; padding: 14px 18px; margin-top: 14px; margin-bottom: 10px;">
            <div style="font-size: 0.9rem; font-weight: 700; color: #854d0e; margin-bottom: 2px;">
                ✏️ Réponse Darja corrigée
            </div>
            <div style="font-size: 0.78rem; color: #a16207;">
                Modifiez directement le texte proposé. Ne donnez aucune dose de médicament.
            </div>
        </div>
        """, unsafe_allow_html=True)

        corrected_val = st.text_area(
            "Réponse Darja corrigée",
            value=answer_darja,
            height=110,
            key=f"corr_box_{row_id}",
            label_visibility="collapsed"
        )

    # 2. SI REJETER EST SÉLECTIONNÉ
    elif current_choice == "rejeter":
        st.markdown("""
        <div style="background: #fef2f2; border: 1.5px solid #fca5a5; border-radius: 12px; padding: 14px 18px; margin-top: 14px; margin-bottom: 10px;">
            <div style="font-size: 0.9rem; font-weight: 700; color: #991b1b; margin-bottom: 2px;">
                ✕ Motif(s) du rejet clinique :
            </div>
            <div style="font-size: 0.78rem; color: #b91c1c;">
                Sélectionnez au moins un motif de non-conformité ou danger :
            </div>
        </div>
        """, unsafe_allow_html=True)

        r1 = st.checkbox("💊 Prescription ou dosage de médicament (strictement interdit)", key=f"r1_{row_id}")
        r2 = st.checkbox("⚠️ Erreur médicale clinique ou diagnostic non fondé", key=f"r2_{row_id}")
        r3 = st.checkbox("🗣️ Darja non algérienne (mots tunisiens/marocains) ou incompréhensible", key=f"r3_{row_id}")
        r4 = st.checkbox("🚨 Urgence vitale non signalée (danger pour mère/enfant)", key=f"r4_{row_id}")
        if r1: reject_reasons.append("prescription_dose")
        if r2: reject_reasons.append("erreur_medicale")
        if r3: reject_reasons.append("darja_incorrecte")
        if r4: reject_reasons.append("urgence_non_signalee")

    # Champ Note Clinique (Photos 4 & 5)
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.82rem; font-weight: 600; color: #0f172a; margin-bottom: 4px;">
        Note / remarque clinique <span style="color: #64748b; font-weight: 400;">(optionnelle)</span>
    </div>
    """, unsafe_allow_html=True)

    notes_val = st.text_input(
        "Note / remarque clinique",
        placeholder="Ajoutez un contexte clinique utile, sans information patient identifiable...",
        key=f"notes_box_{row_id}",
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 7. Barre Inférieure : Sauvegarde IMMÉDIATE (Photos 4 & 5)
    # -----------------------------------------------------------------------------
    col_sub_left, col_sub_right = st.columns([1.5, 1.5])
    with col_sub_left:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #64748b; height: 100%; padding-top: 10px;">
            🔒 Décision enregistrée de façon sécurisée
        </div>
        """, unsafe_allow_html=True)

    with col_sub_right:
        if st.button("Confirmer & suivant →", type="primary", use_container_width=True):
            decision = st.session_state["decision_choice"]

            # Si rejet sans motif
            if decision == "rejeter" and not reject_reasons and not notes_val:
                st.warning("Veuillez cocher au moins un motif de rejet ou ajouter une note explicative.")
            else:
                # 1. ÉCRITURE IMMÉDIATE LIGNE PAR LIGNE SUR LE DISQUE
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

                # Compteur de session
                st.session_state["batch_stats"][decision] += 1

                # 2. Passage immédiat à la question suivante
                st.session_state["decision_choice"] = "valider"
                if idx + 1 >= len(batch):
                    st.session_state["completed"] = True
                else:
                    st.session_state["current_idx"] += 1

                st.rerun()
