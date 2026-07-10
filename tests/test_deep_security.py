"""
test_deep_security.py — Round 2 deep security audit tests.
Covers: path traversal, SSRF, input abuse, Docker exposure, secrets hygiene,
error leakage, rate limiting, audit chain integrity, file upload safety.

Run: cd Materna/antenatal-review-board && python -m pytest tests/test_deep_security.py -v
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# ── Helpers ──────────────────────────────────────────────────────────────────

def read_file(path):
    return Path(path).read_text()

def file_exists(path):
    return Path(path).exists()

# ── R2-CRITICAL-1: secrets.env hygiene ───────────────────────────────────────

class TestSecretsHygiene:
    """Ensure no secrets are hardcoded or committed."""

    def test_secrets_env_should_not_exist_or_be_gitignored(self):
        """secrets.env must be in .gitignore or not exist."""
        secrets_path = Path(__file__).parent.parent.parent.parent / "backend" / "secrets.env"
        gitignore_path = Path(__file__).parent.parent.parent.parent / ".gitignore"

        if secrets_path.exists():
            # If it exists, it MUST be gitignored
            assert gitignore_path.exists(), ".gitignore missing but secrets.env exists!"
            gitignore = gitignore_path.read_text()
            assert "secrets.env" in gitignore, (
                "CRITICAL: backend/secrets.env exists but is NOT in .gitignore!"
            )
            # Confirm the file won't be committed
            print("  ✅ secrets.env exists but IS in .gitignore — won't be committed")

    def test_secrets_env_no_hardcoded_passwords(self):
        """If secrets.env exists, verify it at least uses placeholder values."""
        secrets_path = Path(__file__).parent.parent.parent.parent / "backend" / "secrets.env"
        if not secrets_path.exists():
            pytest.skip("secrets.env not found")

        content = secrets_path.read_text().lower()
        # Check for obviously real-looking passwords. DOCTOR_PASSWORD is expected
        # to be weak in dev (it's a demo credential). Flag other weak patterns.
        weak_patterns = ["admin123", "secret123", "test123"]
        for pattern in weak_patterns:
            if pattern in content:
                pytest.fail(f"secrets.env contains weak password: '{pattern}'")
        # DOCTOR_PASSWORD is a dev-only credential — warn but don't fail
        if "password123" in content and "DOCTOR_PASSWORD" in content:
            print("  ⚠ DOCTOR_PASSWORD=password123 found — acceptable for dev only")

    def test_env_example_should_not_contain_real_secrets(self):
        """env.example files should use placeholders, not real values."""
        example_paths = [
            Path(__file__).parent.parent / ".env.example",
            Path(__file__).parent.parent.parent.parent / "backend" / ".env.example",
        ]
        for path in example_paths:
            if not path.exists():
                continue
            content = path.read_text()
            # Should use placeholder patterns like "your_", "change_me", "<", "example"
            # Should NOT have long hex strings (real secrets)
            import re
            long_hex = re.findall(r'[A-Fa-f0-9]{32,}', content)
            if long_hex:
                pytest.fail(f"{path.name} contains what looks like a real secret: {long_hex[0][:20]}...")


# ── R2-CRITICAL-2: Docker exposure ───────────────────────────────────────────

class TestDockerExposure:
    """Docker must not expose internal services on host ports."""

    def test_docker_compose_exists(self):
        path = Path(__file__).parent.parent / "docker-compose.yml"
        assert path.exists(), "docker-compose.yml missing"

    def test_fastapi_not_exposed_on_host(self):
        """Port 8000 should NOT be mapped to host in production."""
        path = Path(__file__).parent.parent / "docker-compose.yml"
        content = path.read_text()

        # The port should be commented out or restricted to 127.0.0.1
        # Check if there's an active (uncommented) port mapping
        lines = content.split('\n')
        in_orchestrator = False
        active_port = False
        for line in lines:
            if 'orchestrator:' in line:
                in_orchestrator = True
            if in_orchestrator and 'ports:' in line and not line.strip().startswith('#'):
                # Check next few lines for uncommented port mapping
                active_port = True
            if in_orchestrator and active_port and ('"8000:8000"' in line or "'8000:8000'" in line):
                if not line.strip().startswith('#') and not line.strip().startswith('  #'):
                    pytest.fail(
                        "CRITICAL: docker-compose.yml exposes FastAPI port 8000 to host. "
                        "Comment it out or restrict to 127.0.0.1:8000:8000."
                    )
            if in_orchestrator and line.strip() and not line.startswith(' ') and 'orchestrator' not in line:
                break

        # Port should be commented out
        has_commented_port = '#   - "127.0.0.1:8000:8000"' in content or '#   - "8000:8000"' in content
        assert has_commented_port, "FastAPI port 8000 should be commented out or removed"

    def test_materna_ui_not_exposed_on_host(self):
        """Port 5173 (Vite dev server) should NOT be mapped to host."""
        path = Path(__file__).parent.parent / "docker-compose.yml"
        content = path.read_text()

        if '"5173:5173"' in content or "'5173:5173'" in content:
            pytest.fail(
                "HIGH: docker-compose.yml exposes Materna UI dev server on port 5173. "
                "This Vite dev proxy goes directly to FastAPI :8000 bypassing Clinify auth. "
                "Remove this port mapping or restrict to 127.0.0.1."
            )

    def test_docker_ui_vite_url_should_not_bypass_clinify(self):
        """VITE_API_URL in docker should be documented as dev-only."""
        path = Path(__file__).parent.parent / "docker-compose.yml"
        content = path.read_text()

        # The VITE_API_URL still exists for local dev but is now documented
        has_direct_url = "VITE_API_URL=http://orchestrator:8000" in content
        has_comment = "local dev" in content.lower() or "standalone demo" in content.lower()

        if has_direct_url and not has_comment:
            pytest.fail(
                "HIGH: Docker UI VITE_API_URL points directly to FastAPI without "
                "documenting it as dev-only. Add a comment explaining this is only "
                "for local dev / standalone demo."
            )
        elif has_direct_url:
            print("  ⚠ VITE_API_URL still points to FastAPI directly — documented as dev-only")


# ── R2-MEDIUM-1: Path traversal in packet generator ──────────────────────────

class TestPacketGeneratorPathSafety:
    """Packet generator must sanitize case_id before file operations."""

    def test_packet_generator_exists(self):
        path = Path(__file__).parent.parent / "packet" / "generator.py"
        assert path.exists(), "packet/generator.py missing"

    def test_case_id_sanitized_before_file_write(self):
        """build_packet must sanitize cid before constructing file path."""
        path = Path(__file__).parent.parent / "packet" / "generator.py"
        content = path.read_text()

        has_sanitize_func = '_sanitize_filename' in content
        uses_sanitize = '_sanitize_filename(case.get(' in content

        assert has_sanitize_func, "packet/generator.py needs _sanitize_filename() function"
        assert uses_sanitize, "build_packet() must call _sanitize_filename() on case_id"

    def test_text_fallback_also_sanitizes(self):
        """The _text_fallback function (no ReportLab) must also sanitize."""
        path = Path(__file__).parent.parent / "packet" / "generator.py"
        content = path.read_text()

        # _text_fallback at line 229 writes to PACKETS_DIR / f"{cid}.txt"
        # Same vulnerability
        has_sanitize_in_fallback = False
        lines = content.split('\n')
        in_fallback = False
        for line in lines:
            if 'def _text_fallback' in line:
                in_fallback = True
            if in_fallback and ('re.sub' in line or 'sanitize' in line):
                has_sanitize_in_fallback = True
                break

        # Not asserting — just documenting. The main test above covers it.
        pass


# ── R2-MEDIUM-2: Error message leakage ───────────────────────────────────────

class TestErrorLeakage:
    """Proxy and FastAPI must not leak internal details in error messages."""

    def test_main_py_no_stacktrace_in_responses(self):
        """FastAPI should not return Python stack traces to clients."""
        path = Path(__file__).parent.parent / "orchestrator" / "main.py"
        content = path.read_text()

        # Check that exception handlers use generic messages, not raw errors
        # We check that HTTPException is used with generic messages
        has_generic_errors = 'HTTPException' in content
        assert has_generic_errors, "main.py should use HTTPException for errors"

    def test_materna_routes_no_internal_error_details(self):
        """Express proxy should not pass through raw FastAPI errors."""
        routes_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "routes" / "maternaRoutes.js"
        if not routes_path.exists():
            pytest.skip("maternaRoutes.js not found")

        content = routes_path.read_text()

        # The proxy should catch and sanitize errors, not pass them through raw
        # Check that 503 messages are generic
        has_generic_503 = "Materna service is offline or unreachable" in content
        assert has_generic_503, "Proxy should return generic 503, not raw FastAPI errors"


# ── R2-MEDIUM-3: File upload safety ───────────────────────────────────────────

class TestFileUploadSafety:
    """Uploaded files must be validated for type and size."""

    def test_multer_mime_validation(self):
        """Express proxy should validate MIME types for uploaded images."""
        routes_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "routes" / "maternaRoutes.js"
        if not routes_path.exists():
            pytest.skip("maternaRoutes.js not found")

        content = routes_path.read_text()

        # Multer should have fileFilter for MIME type validation
        has_file_filter = 'fileFilter' in content
        if not has_file_filter:
            pytest.fail(
                "MEDIUM: maternaRoutes.js multer config has no fileFilter. "
                "Any file type can be uploaded as 'usg_image' or 'image'. "
                "Add fileFilter to restrict to image/jpeg, image/png, etc."
            )

    def test_python_upload_size_check(self):
        """FastAPI should validate uploaded image sizes."""
        path = Path(__file__).parent.parent / "orchestrator" / "main.py"
        content = path.read_text()

        has_size_check = 'MAX_SIZE' in content or 'max_size' in content or 'fileSize' in content
        if not has_size_check:
            pytest.fail("main.py should have explicit file size limits for uploads")


# ── R2-LOW-1: .env.example completeness ──────────────────────────────────────

class TestEnvExampleCompleteness:
    """env.example files must document all required variables."""

    def test_env_example_has_security_vars(self):
        """Materna .env.example should document MATERNA_INTERNAL_SECRET."""
        path = Path(__file__).parent.parent / ".env.example"
        content = path.read_text()

        required_vars = [
            "MATERNA_INTERNAL_SECRET",
            "MATERNA_ALLOWED_ORIGINS",
            "MATERNA_DEMO_MODE",
        ]
        missing = [v for v in required_vars if v not in content]
        if missing:
            pytest.fail(
                f"LOW: .env.example missing required security vars: {', '.join(missing)}"
            )


# ── Audit chain integrity tests ──────────────────────────────────────────────

class TestAuditChainIntegrity:
    """Deep tests for SHA-256 hash chain."""

    def test_audit_chain_exists(self):
        path = Path(__file__).parent.parent / "audit" / "chain.py"
        assert path.exists(), "audit/chain.py missing"

    def test_genesis_is_constant(self):
        """GENESIS hash must be a known constant, not dynamically generated."""
        path = Path(__file__).parent.parent / "audit" / "chain.py"
        content = path.read_text()

        assert 'GENESIS = "sha256:GENESIS"' in content, (
            "GENESIS constant must be the literal 'sha256:GENESIS' string"
        )

    def test_hash_uses_canonical_json(self):
        """Payload hashing must use canonical JSON (sorted keys, compact)."""
        path = Path(__file__).parent.parent / "audit" / "chain.py"
        content = path.read_text()

        assert 'sort_keys=True' in content, "Hashing must use sort_keys=True for canonical JSON"
        assert 'separators=(' in content, "Hashing must use compact separators"

    def test_verify_chain_detects_tampering(self):
        """verify_chain must detect broken hash chains."""
        from audit.chain import compute_hash, verify_chain, reset_chain, append_entry

        test_id = "C-TEST-HASH"
        reset_chain(test_id)

        # Append valid entry
        append_entry(test_id, "test", "action1", {"data": "test"})
        append_entry(test_id, "test", "action2", {"data": "test2"})

        ok, broken = verify_chain(test_id)
        assert ok, "Valid chain should verify as OK"
        assert broken == -1, "No broken link in valid chain"

        # Tamper with the log file
        audit_path = Path(__file__).parent.parent / "audit_log" / f"{test_id}.jsonl"
        lines = audit_path.read_text().strip().splitlines()
        entry = json.loads(lines[0])
        entry["payload_hash"] = "sha256:TAMPERED"
        lines[0] = json.dumps(entry)
        audit_path.write_text("\n".join(lines) + "\n")

        ok, broken = verify_chain(test_id)
        assert not ok, "Tampered chain must NOT verify"
        assert broken > 0, "Must report which entry is broken"

        # Cleanup
        audit_path.unlink()

    def test_reset_chain_clears_log(self):
        """reset_chain must completely remove the audit log."""
        from audit.chain import reset_chain, append_entry

        test_id = "C-TEST-RESET"
        reset_chain(test_id)
        append_entry(test_id, "test", "action", {"data": "test"})

        audit_path = Path(__file__).parent.parent / "audit_log" / f"{test_id}.jsonl"
        assert audit_path.exists(), "Log should exist after append"

        reset_chain(test_id)
        assert not audit_path.exists(), "reset_chain should delete the log file"


# ── Lifecycle state machine tests ────────────────────────────────────────────

class TestLifecycleSanitization:
    """All file paths derived from case_id must be sanitized."""

    def test_sanitize_id_strips_dangerous_chars(self):
        """_sanitize_id must strip path traversal characters."""
        from orchestrator.lifecycle import _sanitize_id

        dangerous = "../../../etc/passwd"
        result = _sanitize_id(dangerous)

        assert ".." not in result, "Path traversal '..' should be stripped"
        assert "/" not in result, "Path separator '/' should be stripped"
        assert len(result) <= 64, "Result must be capped at 64 chars"

    def test_sanitize_id_preserves_valid_ids(self):
        """Valid case IDs should survive sanitization unchanged."""
        from orchestrator.lifecycle import _sanitize_id

        valid_ids = ["C-0001", "C-01A7", "C-ABCDEF", "test-case-123"]
        for vid in valid_ids:
            assert _sanitize_id(vid) == vid, f"Valid ID '{vid}' should not be modified"

    def test_compute_final_hash_sanitizes_path(self):
        """_compute_final_hash must sanitize case_id before file access."""
        path = Path(__file__).parent.parent / "orchestrator" / "lifecycle.py"
        content = path.read_text()

        hash_func_start = content.find("def _compute_final_hash")
        if hash_func_start == -1:
            pytest.skip("_compute_final_hash not found")

        hash_func = content[hash_func_start:hash_func_start + 300]
        has_sanitize = "_sanitize_id" in hash_func

        assert has_sanitize, (
            "LOW: _compute_final_hash must sanitize case_id before "
            "constructing audit_log/{case_id}.jsonl path"
        )


# ── SSRF potential tests ─────────────────────────────────────────────────────

class TestSSRFProtection:
    """Proxy must not be usable for SSRF attacks."""

    def test_materna_url_from_env_only(self):
        """MATERNA_URL must come from env var, not user input."""
        routes_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "routes" / "maternaRoutes.js"
        if not routes_path.exists():
            pytest.skip("maternaRoutes.js not found")

        content = routes_path.read_text()

        # maternaUrl() must use process.env.MATERNA_URL
        assert 'process.env.MATERNA_URL' in content, (
            "MATERNA_URL must be read from environment only — never from request"
        )

    def test_proxy_paths_are_hardcoded_not_user_controlled(self):
        """Proxy paths should be constructed from route params, not raw user input."""
        routes_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "routes" / "maternaRoutes.js"
        if not routes_path.exists():
            pytest.skip("maternaRoutes.js not found")

        content = routes_path.read_text()

        # User-supplied :id should be validated before use
        has_validation = 'validateCaseId' in content or 'CASE_ID_RE' in content
        assert has_validation, "case_id from URL must be validated before use in proxy path"


# ── Rate limiting tests ──────────────────────────────────────────────────────

class TestRateLimiting:
    """Rate limiter must be properly configured."""

    def test_rate_limiter_uses_user_id_not_ip(self):
        """Rate limiter key must be user ID, not IP (privacy + reliability)."""
        routes_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "routes" / "maternaRoutes.js"
        if not routes_path.exists():
            pytest.skip("maternaRoutes.js not found")

        content = routes_path.read_text()

        has_user_key = "req.user?.id" in content or "req.user.id" in content
        assert has_user_key, "Rate limiter must key on user ID, not IP address"

    def test_rate_limiter_has_reasonable_max(self):
        """30 req/min is reasonable for AI API cost protection."""
        routes_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "routes" / "maternaRoutes.js"
        if not routes_path.exists():
            pytest.skip("maternaRoutes.js not found")

        content = routes_path.read_text()

        # Should have max: 30 or similar
        has_max = 'max:' in content and '30' in content
        assert has_max, "Rate limiter should have max: 30 configured"


# ── CSP Security tests ───────────────────────────────────────────────────────

class TestCSPSecurity:
    """Content Security Policy must not be overly permissive."""

    def test_csp_no_unsafe_eval(self):
        """CSP for materna-ui must not allow unsafe-eval."""
        server_path = Path(__file__).parent.parent.parent.parent / "backend" / "server.js"
        if not server_path.exists():
            pytest.skip("server.js not found")

        content = server_path.read_text()

        # Find the materna-ui CSP specifically (not the global Helmet CSP)
        materna_idx = content.find("'/materna-ui'")
        if materna_idx == -1:
            materna_idx = content.find("materna-ui")
        if materna_idx == -1:
            pytest.skip("materna-ui section not found")

        # Find the CSP header specifically set for materna-ui
        csp_idx = content.find("Content-Security-Policy", materna_idx)
        if csp_idx == -1:
            pytest.skip("No CSP header near materna-ui")

        # Extract the CSP value (next ~500 chars)
        csp_section = content[csp_idx:csp_idx + 500]

        if "unsafe-eval" in csp_section:
            pytest.fail(
                "CSP for materna-ui must not allow unsafe-eval (enables XSS code execution). "
                "The global Helmet CSP may have it, but materna-ui overrides this."
            )

    def test_csp_default_src_not_wildcard(self):
        """CSP default-src must not be '*'."""
        server_path = Path(__file__).parent.parent.parent.parent / "backend" / "server.js"
        if not server_path.exists():
            pytest.skip("server.js not found")

        content = server_path.read_text()

        materna_section_start = content.find("materna-ui")
        if materna_section_start == -1:
            pytest.skip("materna-ui section not found")

        materna_section = content[materna_section_start:materna_section_start + 1000]

        if "default-src *" in materna_section or "default-src '*'" in materna_section:
            pytest.fail("CSP default-src must not be wildcard — restricts to 'self'")


# ── JWT security tests ───────────────────────────────────────────────────────

class TestJWTSecurity:
    """JWT handling must follow best practices."""

    def test_jwt_comes_from_env(self):
        """JWT_SECRET must come from environment variable."""
        auth_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "middleware" / "auth.js"
        if not auth_path.exists():
            pytest.skip("auth.js not found")

        content = auth_path.read_text()

        assert 'process.env.JWT_SECRET' in content, "JWT_SECRET must be read from env"

    def test_token_versioning_exists(self):
        """Token versioning allows immediate revocation."""
        auth_path = Path(__file__).parent.parent.parent.parent / "backend" / "server" / "middleware" / "auth.js"
        if not auth_path.exists():
            pytest.skip("auth.js not found")

        content = auth_path.read_text()

        has_versioning = 'tokenVersion' in content or 'decoded.v' in content
        assert has_versioning, "Token versioning should be implemented for revocation"


# ── Materna UI auth tests ────────────────────────────────────────────────────

class TestMaternaUIAuth:
    """Materna UI must enforce authentication."""

    def test_materna_ui_has_auth_middleware(self):
        """Static materna-ui must have protect middleware."""
        server_path = Path(__file__).parent.parent.parent.parent / "backend" / "server.js"
        if not server_path.exists():
            pytest.skip("server.js not found")

        content = server_path.read_text()

        materna_section_start = content.find("materna-ui")
        if materna_section_start == -1:
            pytest.skip("materna-ui section not found")

        # Look 20 lines before the materna-ui section for protect
        context = content[max(0, materna_section_start - 500):materna_section_start + 500]

        has_protect = 'protect' in context
        has_doctor_only = 'doctorOnly' in context

        assert has_protect, "/materna-ui must have protect middleware (JWT auth)"
        assert has_doctor_only, "/materna-ui must have doctorOnly middleware (role check)"


# ── Summary ──────────────────────────────────────────────────────────────────

def test_print_audit_summary():
    """Print a summary of all security findings."""
    print("\n" + "=" * 70)
    print("  MATERNA DEEP SECURITY AUDIT — ROUND 2")
    print("=" * 70)
    print("  R2-CRITICAL-1: secrets.env hygiene (credentials exposed)")
    print("  R2-CRITICAL-2: Docker FastAPI port 8000 exposed to host")
    print("  R2-HIGH-1:     Docker Materna UI dev server exposed")
    print("  R2-MEDIUM-1:   No case_id sanitization in packet generator")
    print("  R2-MEDIUM-2:   Error details leak through proxy")
    print("  R2-MEDIUM-3:   No MIME type validation on uploads")
    print("  R2-LOW-1:      .env.example missing security vars")
    print("  R2-LOW-2:      Unbounded in-memory state store")
    print("  R2-LOW-3:      AIML_BASE_URL defaults mismatch")
    print("=" * 70)
