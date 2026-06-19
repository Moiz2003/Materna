"""
tools/ga_calc.py — Deterministic gestational-age math.

Golden Rule 5: Pure functions. No LLM. No network.
§10.2 SDD, P3 Playbook.
"""

from __future__ import annotations

from datetime import date


def ga_from_lmp(lmp_date: date, ref_date: date) -> float:
    """Gestational age in weeks from LMP: (ref - lmp).days / 7."""
    if lmp_date > ref_date:
        raise ValueError("LMP date cannot be in the future relative to reference date")
    return (ref_date - lmp_date).days / 7.0


def ga_from_ultrasound(meas_type: str, value_mm: float) -> float:
    """
    Gestational age in weeks from ultrasound biometry.

    Supported types: BPD (biparietal diameter), CRL (crown-rump length).
    Uses Hadlock-style approximations. Cite: Hadlock et al., Radiology 1984.

    BPD formula: GA(days) ≈ 2 × BPD_mm + 44.2  →  GA(weeks) = GA(days) / 7
      - BPD 48mm ≈ 20.1wk, BPD 58mm ≈ 22.9wk, BPD 72mm ≈ 26.9wk
    CRL formula: GA(days) ≈ CRL_mm + 42  →  GA(weeks) = GA(days) / 7
      - CRL 10mm ≈ 7.4wk, CRL 45mm ≈ 12.4wk
    """
    if value_mm <= 0:
        raise ValueError("Measurement value must be positive")
    if meas_type == "BPD":
        return round((2.0 * value_mm + 44.2) / 7.0, 1)
    elif meas_type == "CRL":
        return round((value_mm + 42.0) / 7.0, 1)
    elif meas_type == "FL":
        return round((value_mm * 0.21 + 6.4), 1)
    elif meas_type == "HC":
        return round((value_mm * 0.33 + 7.2), 1)
    elif meas_type == "AC":
        return round((value_mm * 0.18 + 8.8), 1)
    else:
        raise ValueError(f"Unsupported measurement type: {meas_type}. Supported: BPD, CRL, FL, HC, AC")


def discordance_weeks(ga_lmp: float, ga_usg: float) -> float:
    """Absolute difference between LMP and USG GA, rounded to 1 decimal place."""
    return round(abs(ga_lmp - ga_usg), 1)


def is_discordant(diff_weeks: float, threshold: float = 2.0) -> bool:
    """True if discordance >= threshold weeks."""
    return diff_weeks >= threshold
