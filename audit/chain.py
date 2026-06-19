"""
audit/chain.py — SHA-256 hash-chained audit log.

Golden Rule 6: Every state transition appends a hash-chained AuditEntry.
Append-only JSONL at audit_log/<case_id>.jsonl.
§7 SDD, P7 Playbook.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from schemas import AuditEntry

AUDIT_LOG_DIR = Path(__file__).parent.parent / "audit_log"
GENESIS = "sha256:GENESIS"


def _ensure_dir() -> None:
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)


import re as _re

def _sanitize_id(raw: str) -> str:
    return _re.sub(r'[^A-Za-z0-9\-]', '', raw)[:64]

def _log_path(case_id: str) -> Path:
    return AUDIT_LOG_DIR / f"{_sanitize_id(case_id)}.jsonl"


def _hash_payload(payload: dict) -> str:
    """SHA-256 of canonical JSON (sorted keys, compact)."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"


def compute_hash(
    seq: int,
    case_id: str,
    actor: str,
    action: str,
    payload_hash: str,
    prev_hash: str,
) -> str:
    """
    Compute this_hash for an audit entry.

    this_hash = sha256( f"{seq}|{case_id}|{actor}|{action}|{payload_hash}|{prev_hash}" )
    """
    raw = f"{seq}|{case_id}|{actor}|{action}|{payload_hash}|{prev_hash}"
    return f"sha256:{hashlib.sha256(raw.encode()).hexdigest()}"


def reset_chain(case_id: str) -> None:
    """Clear any existing audit log for a case so a new submission starts fresh.

    Called at the start of each submission (RECEIVED). Without this, re-submitting
    the same case_id appends a second lifecycle onto the old chain — bloating it
    and mixing unrelated runs. The human-decision flow does NOT reset; it appends
    to the same submission's chain across requests.
    """
    path = _log_path(case_id)
    if path.exists():
        path.unlink()


def append_entry(
    case_id: str,
    actor: str,
    action: str,
    payload: dict,
) -> AuditEntry:
    """
    Append a hash-chained AuditEntry to the case's audit log.

    Reads the last entry's this_hash as prev_hash (or GENESIS for the first entry),
    computes the new this_hash, writes the line, and returns the AuditEntry.
    """
    _ensure_dir()
    path = _log_path(case_id)

    # Determine sequence number and previous hash
    prev_hash = GENESIS
    seq = 1
    if path.exists():
        lines = path.read_text().strip().splitlines()
        if lines:
            last = json.loads(lines[-1])
            prev_hash = last.get("this_hash", GENESIS)
            seq = last.get("seq", 0) + 1

    # Compute payload hash
    payload_hash = _hash_payload(payload)

    # Compute this hash
    this_hash = compute_hash(seq, case_id, actor, action, payload_hash, prev_hash)

    entry = AuditEntry(
        seq=seq,
        case_id=case_id,
        actor=actor,
        action=action,
        payload_hash=payload_hash,
        prev_hash=prev_hash,
        this_hash=this_hash,
        ts=datetime.now(timezone.utc),
    )

    # Append to JSONL
    with open(path, "a") as f:
        f.write(entry.model_dump_json() + "\n")

    return entry


def verify_chain(case_id: str) -> tuple[bool, int]:
    """
    Verify the entire hash chain for a case.

    Returns (ok, first_broken_seq) where ok is True if all links are intact,
    and first_broken_seq is -1 if ok, or the seq number of the first broken link.
    """
    path = _log_path(case_id)
    if not path.exists():
        return False, -1  # No log at all

    lines = path.read_text().strip().splitlines()
    if not lines:
        return False, -1

    prev = GENESIS
    for i, line in enumerate(lines):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return False, i + 1  # seq = line number (1-based)

        seq = data.get("seq", i + 1)
        expected = compute_hash(
            seq=seq,
            case_id=data.get("case_id", case_id),
            actor=data.get("actor", ""),
            action=data.get("action", ""),
            payload_hash=data.get("payload_hash", ""),
            prev_hash=prev,
        )
        actual = data.get("this_hash", "")
        if expected != actual:
            return False, seq
        prev = actual

    return True, -1
