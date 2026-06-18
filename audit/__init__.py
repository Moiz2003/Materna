"""audit — SHA-256 hash-chained audit log. Golden Rule 6."""

from .chain import compute_hash, append_entry, verify_chain

__all__ = ["compute_hash", "append_entry", "verify_chain"]
