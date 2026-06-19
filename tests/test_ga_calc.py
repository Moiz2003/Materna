"""
tests/test_ga_calc.py — T2: Unit tests for tools/ga_calc.py.
Covers all GA math, discordance, boundary cases.
Prompt Playbook T2 — §2 Automated Testing.
"""
from datetime import date

import pytest

from tools.ga_calc import (
    ga_from_lmp, ga_from_ultrasound, discordance_weeks, is_discordant,
)


class TestGaFromLmp:
    def test_known_pair(self):
        """LMP 2025-12-01, ref 2026-06-10 → 191 days / 7 = 27.285..."""
        ga = ga_from_lmp(date(2025, 12, 1), date(2026, 6, 10))
        assert 27.2 <= ga <= 27.4, f"Expected ~27.3, got {ga}"

    def test_exact_weeks(self):
        """Exactly 14 days → 2.0 weeks."""
        ga = ga_from_lmp(date(2026, 1, 1), date(2026, 1, 15))
        assert ga == 2.0

    def test_future_lmp_rejected(self):
        """LMP in the future relative to reference date → ValueError."""
        with pytest.raises(ValueError):
            ga_from_lmp(date(2026, 6, 10), date(2026, 6, 1))

    def test_same_day_zero(self):
        """LMP == ref → 0.0 weeks."""
        ga = ga_from_lmp(date(2026, 1, 1), date(2026, 1, 1))
        assert ga == 0.0


class TestGaFromUltrasound:
    def test_bpd_known_value(self):
        """BPD 58mm → (2*58 + 44.2)/7 = 160.2/7 ≈ 22.9"""
        ga = ga_from_ultrasound("BPD", 58)
        assert 22.8 <= ga <= 23.0, f"Expected ~22.9, got {ga}"

    def test_bpd_48mm(self):
        """BPD 48mm → (2*48 + 44.2)/7 = 140.2/7 ≈ 20.0"""
        ga = ga_from_ultrasound("BPD", 48)
        assert 19.9 <= ga <= 20.2

    def test_crl_known_value(self):
        """CRL 10mm → (10 + 42)/7 = 52/7 ≈ 7.4"""
        ga = ga_from_ultrasound("CRL", 10)
        assert 7.3 <= ga <= 7.5, f"Expected ~7.4, got {ga}"

    def test_crl_45mm(self):
        """CRL 45mm → (45 + 42)/7 = 87/7 ≈ 12.4"""
        ga = ga_from_ultrasound("CRL", 45)
        assert 12.3 <= ga <= 12.5

    def test_unsupported_type_raises(self):
        """XYZ not a valid type → ValueError."""
        for t in ("XYZ", "INVALID"):
            with pytest.raises(ValueError):
                ga_from_ultrasound(t, 50)

    def test_non_positive_mm_raises(self):
        """Zero or negative mm → ValueError."""
        for v in (0, -1):
            with pytest.raises(ValueError):
                ga_from_ultrasound("BPD", v)

    def test_rounds_to_one_decimal(self):
        """Output is rounded to 1 decimal place."""
        ga = ga_from_ultrasound("BPD", 60)
        assert ga == round(ga, 1)


class TestDiscordance:
    def test_symmetry(self):
        """abs(27.3 - 23.0) == abs(23.0 - 27.3)."""
        d1 = discordance_weeks(27.3, 23.0)
        d2 = discordance_weeks(23.0, 27.3)
        assert d1 == d2

    def test_rounding(self):
        """Discordance rounded to 1 dp."""
        d = discordance_weeks(27.333, 23.0)
        assert d == round(abs(27.333 - 23.0), 1)

    def test_no_discordance(self):
        """Same GA → 0.0."""
        assert discordance_weeks(20.0, 20.0) == 0.0

    def test_c0001_vector(self):
        """C-0001: 27.3 vs 23.0 → 4.3."""
        d = discordance_weeks(27.3, 23.0)
        assert d == 4.3


class TestIsDiscordant:
    def test_below_threshold(self):
        """1.9 weeks → False."""
        assert is_discordant(1.9) is False

    def test_at_threshold(self):
        """2.0 weeks → True."""
        assert is_discordant(2.0) is True

    def test_above_threshold(self):
        """2.1 weeks → True."""
        assert is_discordant(2.1) is True

    def test_custom_threshold(self):
        """Custom threshold of 3.0: 2.5 → False, 3.0 → True."""
        assert is_discordant(2.5, threshold=3.0) is False
        assert is_discordant(3.0, threshold=3.0) is True

    def test_c0001_is_discordant(self):
        """4.3 weeks → True."""
        assert is_discordant(4.3) is True
