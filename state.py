"""State management for the NLParto review app — Windows compatible.
Immediate persistence, double-review prevention, full profile tracking,
and comprehensive supervisor analytics metrics.
"""
import csv
import json
import os
import random
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LOCAL_DIR = Path(__file__).resolve().parent

TEST_MODE = os.environ.get("NLP_TEST_MODE", "true").lower() in ("true", "1", "yes")

if TEST_MODE and (LOCAL_DIR / "qa_pool_test.csv").exists():
    POOL_CSV = LOCAL_DIR / "qa_pool_test.csv"
    REVIEWS_CSV = LOCAL_DIR / "reviews_test.csv"
else:
    POOL_CSV = DATA_DIR / "qa_pool.csv"
    if not POOL_CSV.exists():
        POOL_CSV = LOCAL_DIR / "qa_pool.csv"

    REVIEWS_CSV = DATA_DIR / "reviews.csv"
    if not REVIEWS_CSV.parent.exists():
        REVIEWS_CSV = LOCAL_DIR / "reviews.csv"

FACTS_CSV = DATA_DIR / "facts_expanded.csv"
if not FACTS_CSV.exists():
    FACTS_CSV = LOCAL_DIR / "facts_expanded.csv"

BATCH_SIZE = 20

MEDICAL_ROLES = [
    {
        "id": "etudiant",
        "title": "Étudiant en médecine",
        "subtitle": "Externe — 4e à 6e année",
        "badge": "Étudiant",
    },
    {
        "id": "interne",
        "title": "Interne en médecine",
        "subtitle": "Formation clinique hospitalière",
        "badge": "Interne",
    },
    {
        "id": "resident",
        "title": "Médecin Résident",
        "subtitle": "Pédiatrie, gynécologie ou santé publique",
        "badge": "Résident",
    },
    {
        "id": "generaliste",
        "title": "Médecin Généraliste",
        "subtitle": "Soins de première ligne",
        "badge": "Médecin Généraliste",
    },
    {
        "id": "specialiste",
        "title": "Médecin Spécialiste",
        "subtitle": "Pédiatre ou gynécologue-obstétricien",
        "badge": "Spécialiste",
    },
    {
        "id": "sage_femme",
        "title": "Sage-Femme diplômée d'État",
        "subtitle": "Santé maternelle et néonatale",
        "badge": "Sage-Femme",
    },
]


def _read_facts():
    """Load facts index by fact_id."""
    if not FACTS_CSV.exists():
        return {}
    facts = {}
    try:
        with open(FACTS_CSV, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                facts[r.get("fact_id", "")] = r
    except Exception as e:
        print(f"[State] Warning reading facts: {e}")
    return facts


def _read_pool():
    """Read the entire qa_pool.csv safely."""
    if not POOL_CSV.exists():
        return []
    with open(POOL_CSV, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _write_pool(rows):
    """Write rows back to qa_pool.csv safely."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    for col in [
        "reviewer_id", "reviewer_name", "reviewer_email", "reviewer_role",
        "review_decision", "review_notes", "corrected_answer", "reviewed_at"
    ]:
        if col not in fieldnames:
            fieldnames.append(col)

    tmp_path = POOL_CSV.with_suffix(".tmp")
    with open(tmp_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    
    if os.path.exists(POOL_CSV):
        os.replace(tmp_path, POOL_CSV)
    else:
        os.rename(tmp_path, POOL_CSV)


def claim_batch(
    session_id: str,
    reviewer_name: str,
    reviewer_role: str,
    reviewer_email: str = "",
    batch_size: int = BATCH_SIZE
):
    """Reserve a batch of pending rows exclusively for this reviewer."""
    rows = _read_pool()
    if not rows:
        return []

    pending = [r for r in rows if r.get("review_status") == "pending"]
    if not pending:
        return []

    chosen = random.sample(pending, min(batch_size, len(pending)))
    batch_ids = {r["id"] for r in chosen}
    facts_dict = _read_facts()

    for r in rows:
        if r["id"] in batch_ids:
            r["review_status"] = "in_progress"
            r["reviewer_id"] = session_id
            r["reviewer_name"] = reviewer_name
            r["reviewer_email"] = reviewer_email
            r["reviewer_role"] = reviewer_role

    _write_pool(rows)

    enriched = []
    for item in chosen:
        row_dict = dict(item)
        fid = row_dict.get("fact_id", "")
        fact_info = facts_dict.get(fid, {})

        if fact_info.get("fact_fr"):
            row_dict["fact_fr"] = fact_info["fact_fr"]
        elif row_dict.get("fact_fr"):
            pass
        else:
            topic = row_dict.get("topic", "")
            if topic == "vaccination":
                row_dict["fact_fr"] = "À l'âge de 2 mois, le nourrisson reçoit les vaccins prévus par le calendrier national algérien. Une réaction locale ou une fièvre modérée peut survenir; les signes inhabituels doivent être évalués par un professionnel."
            elif topic == "danger_signs":
                row_dict["fact_fr"] = "Les signes de danger chez la femme enceinte ou le nouveau-né nécessitent une orientation immédiate vers les urgences médicales ou la maternité, sans délai et sans automédication."
            elif topic == "nutrition":
                row_dict["fact_fr"] = "L'allaitement maternel exclusif est recommandé jusqu'à 6 mois révolus. L'introduction précoce de substituts sans avis médical augmente les risques d'infection digestive et de carence."
            else:
                row_dict["fact_fr"] = "Toute situation clinique présentant des symptômes inhabituels chez la mère ou l'enfant doit faire l'objet d'un examen médical direct par un praticien qualifié."

        source = fact_info.get("source") or fact_info.get("source_status") or "Ministère de la Santé — Guide de prise en charge clinique"
        if "Calendrier" in str(source) or row_dict.get("topic") == "vaccination":
            row_dict["fact_source"] = "Ministère de la Santé — Calendrier national de vaccination"
        elif "Pocket" in str(source) or "pocket" in str(source):
            row_dict["fact_source"] = "OMS / Ministère de la Santé — Prise en charge hospitalière de l'enfant"
        elif "sen-mn" in str(source) or "Nouveau-nés" in str(source):
            row_dict["fact_source"] = "Ministère de la Santé — Soins aux nouveau-nés et santé néonatale"
        else:
            row_dict["fact_source"] = str(source).replace(".pdf", "").replace("_", " ")

        enriched.append(row_dict)

    return enriched


get_or_create_batch = claim_batch


def save_single_decision(
    row_id: str,
    decision: str,
    corrected_text: str = "",
    reject_reasons: list = None,
    notes: str = "",
    session_id: str = "",
    reviewer_name: str = "",
    reviewer_role: str = "",
    reviewer_email: str = ""
):
    """Immediately persists a single decision for one question."""
    now_str = time.strftime("%Y-%m-%dT%H:%M:%S")
    reject_reasons = reject_reasons or []

    # 1. Update qa_pool.csv
    rows = _read_pool()
    found = False
    for r in rows:
        if r["id"] == row_id:
            r["review_status"] = "reviewed"
            r["reviewer_id"] = session_id
            r["reviewer_name"] = reviewer_name
            r["reviewer_email"] = reviewer_email
            r["reviewer_role"] = reviewer_role
            r["review_decision"] = decision
            r["review_notes"] = notes or ""
            r["corrected_answer"] = corrected_text or ""
            r["reviewed_at"] = now_str
            found = True
            break
    if found:
        _write_pool(rows)

    # 2. Append to reviews.csv
    write_header = not REVIEWS_CSV.exists()
    with open(REVIEWS_CSV, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow([
                "row_id",
                "session_id",
                "reviewer_name",
                "reviewer_email",
                "reviewer_role",
                "decision",
                "corrected_text",
                "reject_reasons",
                "notes",
                "timestamp"
            ])
        w.writerow([
            row_id,
            session_id,
            reviewer_name,
            reviewer_email,
            reviewer_role,
            decision,
            corrected_text or "",
            ";".join(reject_reasons) if reject_reasons else "",
            notes or "",
            now_str
        ])
    return True


save_review = save_single_decision


def release_batch(session_id: str):
    """Release unreviewed in_progress rows back to pending if user leaves early."""
    rows = _read_pool()
    changed = False
    for r in rows:
        if r.get("review_status") == "in_progress" and r.get("reviewer_id") == session_id:
            r["review_status"] = "pending"
            r["reviewer_id"] = ""
            changed = True
    if changed:
        _write_pool(rows)


def pool_stats():
    """Return stats on total, pending, in_progress, reviewed rows."""
    rows = _read_pool()
    statuses = [r.get("review_status", "pending") for r in rows]
    return {
        "total": len(rows),
        "pending": statuses.count("pending"),
        "in_progress": statuses.count("in_progress"),
        "reviewed": statuses.count("reviewed"),
    }


def get_dashboard_metrics():
    """Consolidated supervisor analytics for the review dashboard."""
    # 1. Pool progress
    pool_rows = _read_pool()
    pool_total = len(pool_rows)
    pool_statuses = [r.get("review_status", "pending") for r in pool_rows]
    pool_reviewed = pool_statuses.count("reviewed")
    pool_in_progress = pool_statuses.count("in_progress")
    pool_pending = pool_statuses.count("pending")

    # 2. Review records
    reviews = []
    if REVIEWS_CSV.exists():
        with open(REVIEWS_CSV, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            reviews = list(reader)

    total_reviews = len(reviews)
    decisions = {"valider": 0, "corriger": 0, "rejeter": 0}
    reject_reasons = {}
    reviewers = {}

    for r in reviews:
        dec = (r.get("decision") or "").lower().strip()
        if dec in decisions:
            decisions[dec] += 1
        
        name = (r.get("reviewer_name") or "Anonyme").strip() or "Anonyme"
        email = (r.get("reviewer_email") or "").strip() or "Non renseigné"
        role = (r.get("reviewer_role") or "generaliste").strip()
        ts = r.get("timestamp") or r.get("reviewed_at") or ""

        rev_key = (name.lower(), email.lower())
        if rev_key not in reviewers:
            reviewers[rev_key] = {
                "name": name,
                "email": email,
                "role": role,
                "total": 0,
                "valider": 0,
                "corriger": 0,
                "rejeter": 0,
                "last_active": ts
            }
        reviewers[rev_key]["total"] += 1
        if dec in reviewers[rev_key]:
            reviewers[rev_key][dec] += 1
        if ts and ts > reviewers[rev_key]["last_active"]:
            reviewers[rev_key]["last_active"] = ts

        reasons = r.get("reject_reasons") or ""
        if reasons:
            for reason in reasons.split(";"):
                reason = reason.strip()
                if reason:
                    reject_reasons[reason] = reject_reasons.get(reason, 0) + 1

    reviewer_list = sorted(reviewers.values(), key=lambda x: x["total"], reverse=True)

    return {
        "pool_total": pool_total,
        "pool_reviewed": pool_reviewed,
        "pool_pending": pool_pending,
        "pool_in_progress": pool_in_progress,
        "total_reviews": total_reviews,
        "decisions": decisions,
        "reviewer_list": reviewer_list,
        "reviewers": reviewer_list,
        "reject_reasons": reject_reasons,
        "recent_reviews": list(reversed(reviews[-50:])) if reviews else [],
        "reviews_file_path": str(REVIEWS_CSV)
    }


get_statistics = get_dashboard_metrics
