"""Unit Test Suite for the NLParto Review Application.
Tests state management, immediate persistence, anti-duplicate locking,
security sanitization, rate limiting, and API handlers.
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Importer l'application
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

import state
import server


class TestNLPartoState(unittest.TestCase):
    def setUp(self):
        """Créer un environnement de test isolé pour ne pas affecter les vraies données."""
        self.test_dir = tempfile.mkdtemp()
        self.orig_pool = state.POOL_CSV
        self.orig_reviews = state.REVIEWS_CSV

        self.test_pool = Path(self.test_dir) / "qa_pool.csv"
        self.test_reviews = Path(self.test_dir) / "reviews.csv"

        state.POOL_CSV = self.test_pool
        state.REVIEWS_CSV = self.test_reviews

        # Créer un pool de test avec 10 questions factices
        with open(self.test_pool, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=[
                "id", "situation_type", "expected_behavior", "topic", "fact_id",
                "question_ar", "question_lat", "answer_darja", "risk_level",
                "review_status", "reviewer_id", "reviewer_name", "reviewer_role"
            ])
            w.writeheader()
            for i in range(1, 11):
                w.writerow({
                    "id": f"TEST-{i:03d}",
                    "situation_type": "general_fact",
                    "expected_behavior": "answer_from_fact",
                    "topic": "vaccination",
                    "fact_id": "FACT-VAX-001",
                    "question_ar": f"سؤال تجريبي رقم {i}",
                    "question_lat": f"Question test {i}",
                    "answer_darja": f"جواب تجريبي رقم {i}",
                    "risk_level": "routine",
                    "review_status": "pending",
                    "reviewer_id": "",
                    "reviewer_name": "",
                    "reviewer_role": ""
                })

    def tearDown(self):
        state.POOL_CSV = self.orig_pool
        state.REVIEWS_CSV = self.orig_reviews
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_pool_stats(self):
        """Vérifie le comptage initial."""
        stats = state.pool_stats()
        self.assertEqual(stats["total"], 10)
        self.assertEqual(stats["pending"], 10)
        self.assertEqual(stats["reviewed"], 0)

    def test_claim_batch_and_anti_duplicate(self):
        """Vérifie qu'aucun médecin ne reçoit les mêmes questions qu'un autre."""
        # Session A réserve 5 questions
        batch_a = state.claim_batch("session_A", "Dr. A", "general-practitioner", batch_size=5)
        self.assertEqual(len(batch_a), 5)
        ids_a = {r["id"] for r in batch_a}

        # Session B réserve 5 questions
        batch_b = state.claim_batch("session_B", "Dr. B", "specialist", batch_size=5)
        self.assertEqual(len(batch_b), 5)
        ids_b = {r["id"] for r in batch_b}

        # Aucune intersection entre session A et session B
        self.assertEqual(len(ids_a.intersection(ids_b)), 0, "Doublon détecté entre deux médecins !")

        # Il ne reste plus aucune question en attente
        batch_c = state.claim_batch("session_C", "Dr. C", "intern", batch_size=5)
        self.assertEqual(len(batch_c), 0, "Une question déjà réservée a été réattribuée !")

    def test_save_single_decision_immediate(self):
        """Vérifie l'enregistrement direct et immédiat question par question."""
        batch = state.claim_batch("session_A", "Dr. A", "general-practitioner", batch_size=2)
        q1 = batch[0]

        # Sauvegarde immédiate
        state.save_single_decision(
            row_id=q1["id"],
            decision="corriger",
            corrected_text="Réponse corrigée sans médicament.",
            reject_reasons=[],
            notes="Remarque test",
            session_id="session_A",
            reviewer_name="Dr. A",
            reviewer_role="general-practitioner"
        )

        # Vérifier mise à jour dans qa_pool.csv
        rows = state._read_pool()
        target = next(r for r in rows if r["id"] == q1["id"])
        self.assertEqual(target["review_status"], "reviewed")
        self.assertEqual(target["review_decision"], "corriger")
        self.assertEqual(target["corrected_answer"], "Réponse corrigée sans médicament.")

        # Vérifier ajout dans reviews.csv
        self.assertTrue(self.test_reviews.exists())
        with open(self.test_reviews, newline="", encoding="utf-8-sig") as f:
            reviews = list(csv.DictReader(f))
            self.assertEqual(len(reviews), 1)
            self.assertEqual(reviews[0]["row_id"], q1["id"])
            self.assertEqual(reviews[0]["decision"], "corriger")

    def test_release_batch(self):
        """Vérifie que quitter libère les questions non évaluées."""
        state.claim_batch("session_leave", "Dr. Leave", "resident", batch_size=4)
        stats = state.pool_stats()
        self.assertEqual(stats["in_progress"], 4)

        state.release_batch("session_leave")
        stats_after = state.pool_stats()
        self.assertEqual(stats_after["in_progress"], 0)
        self.assertEqual(stats_after["pending"], 10)


class TestSecurityLayer(unittest.TestCase):
    def test_sanitize_string(self):
        """Vérifie la neutralisation des injections XSS."""
        raw = '<script>alert("XSS")</script>Dr. Amine'
        clean = server.sanitize_string(raw, 100)
        self.assertNotIn("<script>", clean)
        self.assertIn("&lt;script&gt;", clean)
        self.assertIn("Dr. Amine", clean)

    def test_sanitize_max_length(self):
        """Vérifie le respect des longueurs maximales."""
        very_long = "A" * 1000
        clean = server.sanitize_string(very_long, max_len=100)
        self.assertEqual(len(clean), 100)

    def test_whitelisting(self):
        """Vérifie que les valeurs inconnues sont rejetées ou filtrées."""
        self.assertIn("general-practitioner", server.VALID_ROLES)
        self.assertNotIn("hacker-role", server.VALID_ROLES)
        self.assertIn("approved", server.VALID_DECISIONS)
        self.assertNotIn("delete-database", server.VALID_DECISIONS)

    def test_rate_limiting(self):
        """Vérifie la protection contre le flooding."""
        test_ip = "192.168.1.99"
        server._ip_request_counts[test_ip] = []

        # En dessous de la limite (60 req/min)
        for _ in range(50):
            self.assertTrue(server.check_rate_limit(test_ip))

        # Dépassement de la limite
        for _ in range(15):
            server.check_rate_limit(test_ip)
        self.assertFalse(server.check_rate_limit(test_ip))


if __name__ == "__main__":
    unittest.main(verbosity=2)
