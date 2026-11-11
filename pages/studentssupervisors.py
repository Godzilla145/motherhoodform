"""NLParto — Espace Superviseurs & Recherche
Console d'administration et de suivi clinique dédiée.
URL directe : /studentssupervisors
"""
import os
import sys
from pathlib import Path
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="NLParto — Dashboard Superviseurs",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Masquer complètement la barre latérale pour préserver la discrétion
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Résolution des imports vers la racine
current_dir = Path(__file__).parent.resolve()
root_dir = current_dir.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Exécution du dashboard
dash_path = root_dir / "dashboard.py"
if dash_path.exists():
    import runpy
    runpy.run_path(str(dash_path))
else:
    st.error("Le fichier dashboard.py est introuvable à la racine de l'application.")

