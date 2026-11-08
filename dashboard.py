"""NLParto - Dashboard Superviseur Dédié (Console de Suivi Clinique)
Application indépendante réservée à l'équipe de recherche & supervision.
Permet d'auditer en temps réel qui évalue, combien de dialogues sont validés,
les motifs de rejet et d'exporter les résultats consolidés au format CSV.
"""
import os
import sys
from pathlib import Path
import streamlit as st

# Import du gestionnaire d'état
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from state import (
    get_dashboard_metrics,
    REVIEWS_CSV,
    POOL_CSV,
    TEST_MODE
)

st.set_page_config(
    page_title="NLParto — Dashboard Superviseur",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Icônes Vectorielles Médicales & Dashboard (SVG Purs)
# -----------------------------------------------------------------------------
ICONS = {
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
    "users": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "shield_check": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "alert_triangle": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
}

def render_html(html_str: str):
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)

# CSS Thème Emerald Slate
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-main: #f8fafc;
        --surface: #ffffff;
        --border-default: #e2e8f0;
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --primary-emerald: #059669;
        --primary-emerald-dark: #047857;
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
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 860px !important;
    }

    button[data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# En-tête Superviseur
# -----------------------------------------------------------------------------
render_html(f"""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px 24px; box-shadow: 0 1px 3px rgba(15,23,42,0.03); margin-bottom: 20px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <div style="display: flex; align-items: center; gap: 9px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; background: #0f172a; border-radius: 8px; color: #38bdf8;">
                {ICONS['chart']}
            </span>
            <div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; letter-spacing: -0.3px;">
                    NLParto — Dashboard Superviseur
                </div>
                <div style="font-size: 0.78rem; color: #64748b;">
                    Suivi de l'évaluation clinique & activité des praticiens
                </div>
            </div>
        </div>
        <span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; font-size: 0.72rem; font-weight: 600; padding: 4px 9px; border-radius: 6px;">
            Mode Supervision
        </span>
    </div>
</div>
""")

# -----------------------------------------------------------------------------
# Récupération des Métriques
# -----------------------------------------------------------------------------
metrics = get_dashboard_metrics()
total_rev = metrics.get("total_reviews", 0)
dec = metrics.get("decisions", {"valider": 0, "corriger": 0, "rejeter": 0})
val_pct = int((dec["valider"] / total_rev * 100)) if total_rev > 0 else 0
cor_pct = int(((dec["corriger"] + dec["rejeter"]) / total_rev * 100)) if total_rev > 0 else 0
reviewers_data = metrics.get("reviewer_list") or metrics.get("reviewers") or []
active_doctors = len(reviewers_data)

# 4 Cartes KPI
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; border-top: 3px solid #059669;">
        <div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Total Évaluées</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-top: 4px;">{total_rev:,}</div>
        <div style="font-size: 0.72rem; color: #059669; font-weight: 500; margin-top: 2px;">pool: {metrics['pool_total']}</div>
    </div>
    """)
with kpi2:
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; border-top: 3px solid #10b981;">
        <div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Conformes</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #059669; margin-top: 4px;">{val_pct}%</div>
        <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{dec['valider']} validées directes</div>
    </div>
    """)
with kpi3:
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; border-top: 3px solid #f59e0b;">
        <div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Corrigées / Rejets</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #d97706; margin-top: 4px;">{cor_pct}%</div>
        <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{dec['corriger']} corr. | {dec['rejeter']} rejets</div>
    </div>
    """)
with kpi4:
    render_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; border-top: 3px solid #3b82f6;">
        <div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Praticiens Actifs</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #1d4ed8; margin-top: 4px;">{active_doctors}</div>
        <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">contributeurs inscrits</div>
    </div>
    """)

# -----------------------------------------------------------------------------
# Tableau des Annotateurs (Nom, Email, Rôle, Volume, Qualité)
# -----------------------------------------------------------------------------
render_html(f"""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-top: 18px; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 7px;">
            {ICONS['users']}
            Activité par Praticien / Évaluateur
        </div>
        <span style="font-size: 0.75rem; color: #64748b;">{active_doctors} contributeur(s)</span>
    </div>
""")

if not reviewers_data:
    render_html("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 24px 0;">
        Aucune évaluation enregistrée pour le moment.
    </div>
    </div>
    """)
else:
    table_html = """
    <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: left;">
        <thead>
            <tr style="border-bottom: 2px solid #f1f5f9; color: #475569;">
                <th style="padding: 8px 6px;">Praticien</th>
                <th style="padding: 8px 6px;">Email Professionnel</th>
                <th style="padding: 8px 6px;">Rôle</th>
                <th style="padding: 8px 6px; text-align: center;">Total</th>
                <th style="padding: 8px 6px; text-align: center; color: #059669;">Validé</th>
                <th style="padding: 8px 6px; text-align: center; color: #d97706;">Corrigé</th>
                <th style="padding: 8px 6px; text-align: center; color: #e11d48;">Rejeté</th>
                <th style="padding: 8px 6px; text-align: right;">Dernière activité</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in reviewers_data:
        r_name = r["name"] or "Dr. Anonyme"
        r_email = r["email"] if r["email"] else "—"
        r_role = r["role"].capitalize() if r["role"] else "Non renseigné"
        last_act = r["last_active"][:16].replace("T", " ") if r["last_active"] else "—"

        table_html += f"""
            <tr style="border-bottom: 1px solid #f8fafc;">
                <td style="padding: 9px 6px; font-weight: 600; color: #0f172a;">{r_name}</td>
                <td style="padding: 9px 6px; color: #3b82f6; font-family: monospace; font-size: 0.78rem;">{r_email}</td>
                <td style="padding: 9px 6px;"><span style="background: #f1f5f9; color: #334155; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;">{r_role}</span></td>
                <td style="padding: 9px 6px; text-align: center; font-weight: 700; color: #0f172a;">{r['total']}</td>
                <td style="padding: 9px 6px; text-align: center; font-weight: 600; color: #059669;">{r['valider']}</td>
                <td style="padding: 9px 6px; text-align: center; font-weight: 600; color: #d97706;">{r['corriger']}</td>
                <td style="padding: 9px 6px; text-align: center; font-weight: 600; color: #e11d48;">{r['rejeter']}</td>
                <td style="padding: 9px 6px; text-align: right; color: #64748b; font-size: 0.74rem;">{last_act}</td>
            </tr>
        """
    table_html += """
        </tbody>
    </table>
    </div>
    """
    render_html(table_html)

# -----------------------------------------------------------------------------
# Analyse des Rejets & Déontologie Médicale
# -----------------------------------------------------------------------------
render_html(f"""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 7px;">
            {ICONS['alert_triangle']}
            Analyse Déontologique des Rejets & Non-Conformités
        </div>
        <span style="font-size: 0.75rem; color: #e11d48; font-weight: 600;">{dec['rejeter']} rejet(s)</span>
    </div>
    <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 12px;">
        Distribution des risques cliniques ou linguistiques identifiés.
    </div>
""")

REASON_MAP = {
    "prescription_dose": "Prescription de médicament / posologie interdite",
    "erreur_medicale": "Erreur médicale clinique ou diagnostic non fondé",
    "darja_incorrecte": "Dialecte non-algérien ou incompréhensible",
    "urgence_non_signalee": "Signe de danger vital non pris en compte",
    "medical-danger": "Danger médical / orientation urgente omise"
}

if not metrics["reject_reasons"]:
    render_html("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.82rem; padding: 12px 0;">
        Aucun rejet avec motif enregistré pour le moment.
    </div>
    </div>
    """)
else:
    for r_code, r_count in metrics["reject_reasons"].items():
        r_name = REASON_MAP.get(r_code, r_code)
        pct_bar = int((r_count / max(1, dec["rejeter"])) * 100)
        render_html(f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 3px;">
                <span style="font-weight: 600; color: #334155;">{r_name}</span>
                <span style="font-weight: 700; color: #e11d48;">{r_count} cas ({pct_bar}%)</span>
            </div>
            <div style="width: 100%; height: 6px; background: #fee2e2; border-radius: 3px; overflow: hidden;">
                <div style="width: {pct_bar}%; height: 100%; background: #e11d48;"></div>
            </div>
        </div>
        """)
    render_html("</div>")

# -----------------------------------------------------------------------------
# Journal Récent (50 dernières décisions)
# -----------------------------------------------------------------------------
render_html(f"""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 7px;">
            {ICONS['activity']}
            Journal des Dernières Évaluations
        </div>
        <span style="font-size: 0.72rem; color: #64748b;">(30 plus récentes)</span>
    </div>
""")

if not metrics["recent_reviews"]:
    render_html("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.82rem; padding: 16px 0;">
        Aucune donnée récente.
    </div>
    </div>
    """)
else:
    log_html = """
    <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: left;">
        <thead>
            <tr style="border-bottom: 2px solid #f1f5f9; color: #475569;">
                <th style="padding: 7px 6px;">ID</th>
                <th style="padding: 7px 6px;">Praticien</th>
                <th style="padding: 7px 6px; text-align: center;">Décision</th>
                <th style="padding: 7px 6px;">Notes / Correction</th>
                <th style="padding: 7px 6px; text-align: right;">Horodatage</th>
            </tr>
        </thead>
        <tbody>
    """
    for item in metrics["recent_reviews"][:30]:
        dec_val = item.get("decision", "").lower()
        if dec_val == "valider":
            dec_badge = '<span style="background: #ecfdf5; color: #047857; font-weight: 700; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem;">VALIDÉ</span>'
        elif dec_val == "corriger":
            dec_badge = '<span style="background: #fffbeb; color: #b45309; font-weight: 700; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem;">CORRIGÉ</span>'
        else:
            dec_badge = '<span style="background: #fff1f2; color: #be123c; font-weight: 700; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem;">REJETÉ</span>'

        detail = item.get("corrected_text") or item.get("notes") or item.get("reject_reasons") or "—"
        if len(detail) > 50:
            detail = detail[:50] + "..."

        q_id = item.get("row_id") or item.get("item_id") or "—"
        r_name = item.get("reviewer_name") or "Anonyme"
        ts = item.get("timestamp") or item.get("reviewed_at") or ""

        log_html += f"""
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 7px 6px; font-family: monospace; font-size: 0.75rem; color: #475569;">{q_id}</td>
                <td style="padding: 7px 6px; font-weight: 600; color: #0f172a;">{r_name}</td>
                <td style="padding: 7px 6px; text-align: center;">{dec_badge}</td>
                <td style="padding: 7px 6px; color: #475569; font-size: 0.76rem;">{detail}</td>
                <td style="padding: 7px 6px; text-align: right; color: #94a3b8; font-size: 0.72rem;">{ts[:16].replace('T', ' ')}</td>
            </tr>
        """
    log_html += """
        </tbody>
    </table>
    </div>
    """
    render_html(log_html)

# -----------------------------------------------------------------------------
# Export des Données CSV
# -----------------------------------------------------------------------------
if REVIEWS_CSV.exists():
    with open(REVIEWS_CSV, "r", encoding="utf-8-sig") as f:
        csv_data = f.read()

    st.download_button(
        label="Exporter les évaluations consolidées (CSV) ↓",
        data=csv_data,
        file_name="nlparto_clinical_reviews.csv",
        mime="text/csv",
        use_container_width=True
    )
