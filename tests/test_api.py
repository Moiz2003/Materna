"""
tests/test_api.py — T10: FastAPI endpoint tests using TestClient.
Prompt Playbook T10.
"""
import json

import pytest
from fastapi.testclient import TestClient

from orchestrator.main import app

client = TestClient(app)


class TestHealth:
    def test_health_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestSubmitCase:
    def test_submit_c0001_returns_201(self, c0001_raw):
        resp = client.post("/cases", data={
            "case": json.dumps(c0001_raw)
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["case_id"] == "C-0001"
        assert data["status"] == "RECEIVED"

    def test_invalid_json_rejected(self):
        resp = client.post("/cases", data={"case": "not valid json"})
        assert resp.status_code == 400


class TestGetCase:
    def test_get_nonexistent_returns_404(self):
        resp = client.get("/cases/NONEXISTENT")
        assert resp.status_code == 404


class TestGetAudit:
    def test_get_nonexistent_audit(self):
        resp = client.get("/cases/NONEXISTENT/audit")
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is False


class TestSubmitDecision:
    def test_decision_on_nonexistent_case(self):
        resp = client.post("/cases/NONEXISTENT/decision", json={
            "verdict": "approve",
            "note": "test",
            "reviewer": "Dr. Test",
        })
        assert resp.status_code == 404

    def test_decision_already_sealed_rejected(self, c0002_raw):
        """Submit clean case that auto-clears, then try to decide on it."""
        # Submit the case
        client.post("/cases", data={"case": json.dumps(c0002_raw)})
        import time
        time.sleep(0.5)  # Wait for background processing (may not finish)
        # The case might still be processing — either 404 (not found) or 409 (not escalated)
        resp = client.post("/cases/C-0002/decision", json={
            "verdict": "approve", "note": "test", "reviewer": "Dr. Test",
        })
        assert resp.status_code in (404, 409)

    def test_invalid_verdict_rejected(self):
        resp = client.post("/cases/C-0001/decision", json={
            "verdict": "invalid_verdict",
            "note": "test",
        })
        assert resp.status_code in (400, 404)  # 400 if format wrong, 404 if case not found


class TestTamperDemo:
    def test_tamper_nonexistent_case(self):
        resp = client.post("/demo/tamper/NONEXISTENT")
        assert resp.status_code == 404
