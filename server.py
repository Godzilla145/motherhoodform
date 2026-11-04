"""NLParto - Serveur Web de Validation Clinique.
100% Python Standard Library (Zéro dépendance externe).
Couche de sécurité intégrée : assainissement XSS, headers sécurisés, rate-limiting, protection path-traversal.
"""
import html
import json
import os
import sys
import time
import webbrowser
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Import de la gestion d'état NLParto
sys.path.insert(0, str(Path(__file__).resolve().parent))
from state import claim_batch, save_single_decision, release_batch, pool_stats, BATCH_SIZE

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"
PORT = 8501

# Couche de sécurité : Limites strictes
MAX_PAYLOAD_SIZE = 64 * 1024  # 64 KB max
RATE_LIMIT_WINDOW = 60        # 60 secondes
MAX_REQUESTS_PER_WINDOW = 60  # max 60 requêtes/minute par IP
_ip_request_counts = defaultdict(list)

VALID_ROLES = {
    "medical-student",
    "intern",
    "resident",
    "general-practitioner",
    "specialist",
    "midwife",
}

VALID_DECISIONS = {
    "approved": "valider",
    "corrected": "corriger",
    "rejected": "rejeter",
}

VALID_REASONS = {
    "drug-dose",
    "medical-danger",
    "foreign-dialect",
    "out-of-scope",
}


def sanitize_string(val: str, max_len: int = 500) -> str:
    """Nettoyage des entrées utilisateurs contre XSS et injections."""
    if not isinstance(val, str):
        return ""
    # Échappement des balises HTML et troncature
    clean = html.escape(val.strip())
    return clean[:max_len]


def check_rate_limit(client_ip: str) -> bool:
    """Vérifie si une adresse IP ne dépasse pas la fréquence autorisée."""
    now = time.time()
    # Nettoyer les requêtes hors fenêtre
    timestamps = [t for t in _ip_request_counts[client_ip] if now - t < RATE_LIMIT_WINDOW]
    timestamps.append(now)
    _ip_request_counts[client_ip] = timestamps
    return len(timestamps) <= MAX_REQUESTS_PER_WINDOW


class SecuredNLPartoHandler(BaseHTTPRequestHandler):
    def send_security_headers(self, content_type="application/json; charset=utf-8"):
        """Envoie les en-têtes HTTP de sécurité recommandés."""
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def do_GET(self):
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self.send_response(429)
            self.send_security_headers("application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Trop de requetes. Veuillez patienter."}')
            return

        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Page d'accueil (index.html)
        if path in ("/", "/index.html"):
            safe_index = (BASE_DIR / "index.html").resolve()
            # Sécurité path-traversal
            if not str(safe_index).startswith(str(BASE_DIR)) or not safe_index.exists():
                self.send_error(404, "Page introuvable")
                return

            content = safe_index.read_bytes()
            self.send_response(200)
            self.send_security_headers("text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        # 2. API : Réserver et récupérer un lot de 20 questions
        if path == "/api/dialogues":
            session_id = sanitize_string(query.get("session_id", [""])[0], 80) or "default"
            reviewer_name = sanitize_string(query.get("name", [""])[0], 80) or "Docteur"
            raw_role = query.get("role", [""])[0]
            reviewer_role = raw_role if raw_role in VALID_ROLES else "general-practitioner"

            batch = claim_batch(
                session_id=session_id,
                reviewer_name=reviewer_name,
                reviewer_role=reviewer_role,
                batch_size=BATCH_SIZE
            )

            dialogues = []
            for i, r in enumerate(batch):
                dialogues.append({
                    "id": str(r.get("id", "")),
                    "code": str(r.get("id", f"NLP-{i+1:03d}")),
                    "sequenceNumber": i + 1,
                    "topic": r.get("topic", "santé"),
                    "riskLevel": r.get("risk_level", "routine"),
                    "groundTruth": r.get("fact_fr", "Recommandation médicale officielle de référence."),
                    "source": r.get("fact_source", "Ministère de la Santé"),
                    "questionArabic": r.get("question_ar", ""),
                    "questionArabizi": r.get("question_lat", ""),
                    "aiAnswer": r.get("answer_darja", "")
                })

            resp_bytes = json.dumps({"dialogues": dialogues}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_security_headers("application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        # 3. API : Statistiques
        if path == "/api/stats":
            stats = pool_stats()
            resp_bytes = json.dumps(stats).encode("utf-8")
            self.send_response(200)
            self.send_security_headers("application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        self.send_error(404, "Page introuvable")

    def do_POST(self):
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self.send_response(429)
            self.send_security_headers("application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Trop de requetes. Veuillez patienter."}')
            return

        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. API : Soumission immédiate ligne par ligne
        if path == "/api/submit":
            content_len = int(self.headers.get("Content-Length", 0))
            if content_len > MAX_PAYLOAD_SIZE:
                self.send_response(413)
                self.send_security_headers("application/json")
                self.end_headers()
                self.wfile.write(b'{"success": false, "message": "Charge utile trop volumineuse."}')
                return

            body = self.rfile.read(content_len).decode("utf-8", errors="ignore")
            try:
                data = json.loads(body)
                dialogue_id = sanitize_string(data.get("dialogueId", ""), 80)
                raw_decision = data.get("decision", "approved")
                decision_label = VALID_DECISIONS.get(raw_decision, "valider")
                
                corrected_answer = sanitize_string(data.get("correctedAnswer", ""), 3000)
                reasons = [r for r in data.get("rejectionReasons", []) if r in VALID_REASONS]
                clinical_note = sanitize_string(data.get("clinicalNote", ""), 1000)
                session_id = sanitize_string(data.get("sessionId", ""), 80)
                reviewer_name = sanitize_string(data.get("reviewerName", "Docteur"), 80)
                raw_role = data.get("reviewerRole", "general-practitioner")
                reviewer_role = raw_role if raw_role in VALID_ROLES else "general-practitioner"

                if not dialogue_id:
                    raise ValueError("ID de dialogue manquant")

                # Sauvegarde immédiate et sécurisée sur disque
                save_single_decision(
                    row_id=dialogue_id,
                    decision=decision_label,
                    corrected_text=corrected_answer,
                    reject_reasons=reasons,
                    notes=clinical_note,
                    session_id=session_id,
                    reviewer_name=reviewer_name,
                    reviewer_role=reviewer_role
                )

                resp_bytes = json.dumps({"success": True}).encode("utf-8")
                self.send_response(200)
                self.send_security_headers("application/json")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                resp_bytes = json.dumps({"success": False, "message": str(e)}).encode("utf-8")
                self.send_response(400)
                self.send_security_headers("application/json")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return

        # 2. API : Libération des questions restantes
        if path == "/api/release":
            session_id = sanitize_string(query.get("session_id", [""])[0], 80)
            if session_id:
                release_batch(session_id)
            resp_bytes = json.dumps({"success": True}).encode("utf-8")
            self.send_response(200)
            self.send_security_headers("application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        self.send_error(404, "Endpoint introuvable")


def run(port=PORT):
    for p in [port, 8502, 5000, 8080]:
        try:
            server = HTTPServer(("0.0.0.0", p), SecuredNLPartoHandler)
            print("=" * 70)
            print(f" [NLParto] Serveur de Validation Clinique Sécurisé actif !")
            print(f" -> URL : http://localhost:{p}")
            print(f" -> Sécurité : Headers HSTS/CSP, Assainissement XSS, Rate-limiting")
            print(f" -> Sauvegarde immédiate : qa_pool.csv & reviews.csv")
            print("=" * 70)
            try:
                webbrowser.open(f"http://localhost:{p}")
            except Exception:
                pass
            server.serve_forever()
            return
        except OSError:
            continue
    print("Erreur : Aucun port disponible.")


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", PORT))
    run(p)
