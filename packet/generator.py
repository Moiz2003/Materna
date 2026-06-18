"""
packet/generator.py — Sealed PDF review packet (ReportLab).

Generates a tamper-evident PDF with: case summary, GA/discordance,
risk flags + evidence, imaging observations (decision-support),
guideline result, HUMAN DECISION block, and final hash footer.
Golden Rule 4: No autonomous diagnostic/treatment claims.
§6.8 SDD, P12 Playbook.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PACKETS_DIR = Path(__file__).parent.parent / "packets"

# Human-readable names for the investigation codes used in antenatal_rules.yaml.
# This is what turns the guideline output into a readable prescription/work-up.
INVESTIGATION_LABELS = {
    "repeat_bp_4h": "Repeat blood pressure after 4 hours",
    "24h_urine_protein": "24-hour urine protein quantification",
    "ogtt": "Oral glucose tolerance test (OGTT)",
    "iron_studies": "Iron studies (ferritin, TIBC, peripheral smear)",
    "prefer_ultrasound_dating": "Re-date pregnancy by ultrasound (LMP unreliable)",
}


def _fmt(value: Any, suffix: str = "") -> str:
    """Render a value for the packet — blanks/None become 'Not recorded'."""
    if value in (None, "", "None", 0):
        return "Not recorded"
    return f"{value}{suffix}"

# ---------------------------------------------------------------------------
# ReportLab imports — graceful fallback if not installed
# ---------------------------------------------------------------------------

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True

    COLOR_PRIMARY = HexColor("#0e7490")
    COLOR_DANGER = HexColor("#dc2626")
    COLOR_WARNING = HexColor("#f59e0b")
    COLOR_SUCCESS = HexColor("#059669")
    COLOR_MUTED = HexColor("#6b7280")
    COLOR_BG = HexColor("#f8fafc")
except ImportError:
    HAS_REPORTLAB = False
    COLOR_PRIMARY = None
    COLOR_DANGER = None
    COLOR_WARNING = None
    COLOR_SUCCESS = None
    COLOR_MUTED = None
    COLOR_BG = None
    logger.warning("ReportLab not installed — PDF generation disabled. Install with: pip install reportlab")


# ---------------------------------------------------------------------------
# Build packet
# ---------------------------------------------------------------------------

async def build_packet(
    case: dict,
    findings: list,
    flags: list,
    decision: dict,
    final_hash: str,
    compliance: dict | None = None,
    plan: dict | None = None,
) -> str:
    """
    Build a sealed PDF review packet and return the file path.

    Args:
        case: Raw case dict
        findings: List of Finding dicts
        flags: List of RiskFlag dicts
        decision: HumanDecision dict
        final_hash: Final SHA-256 hash from audit chain
        compliance: ComplianceResult dict (fallback for the work-up section)
        plan: Approved treatment plan dict (impression/investigations/treatment)

    Returns:
        Relative path to the generated PDF (e.g., 'packets/C-0001.pdf')
    """
    compliance = compliance or {}
    if not HAS_REPORTLAB:
        # Create a placeholder text file instead
        return _build_text_packet(case, findings, flags, decision, final_hash, compliance, plan)

    PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    case_id = case.get("case_id", "unknown")
    pdf_path = PACKETS_DIR / f"{case_id}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Antenatal Review Packet — {case_id}",
        author="Antenatal Review Board",
        subject="Synthetic / Decision-Support Only",
    )

    styles = getSampleStyleSheet()
    story = []

    # --- Header ---
    story.append(_section_header(case_id, styles))
    story.append(_disclaimer(styles))
    story.append(Spacer(1, 5 * mm))

    # --- Case Summary ---
    story.append(_section_title("1. Case Summary", styles))
    story.append(_case_summary_table(case, findings, styles))
    story.append(Spacer(1, 5 * mm))

    # --- GA & Discordance ---
    story.append(_section_title("2. Gestational Age & Discordance", styles))
    story.append(_ga_discordance_section(findings, styles))
    story.append(Spacer(1, 5 * mm))

    # --- Risk Flags ---
    story.append(_section_title("3. Risk Flags", styles))
    story.append(_risk_flags_section(flags, styles))
    story.append(Spacer(1, 5 * mm))

    # --- Imaging (decision-support) ---
    story.append(_section_title("4. Imaging Observations", styles))
    story.append(_imaging_section(findings, styles))
    story.append(Spacer(1, 5 * mm))

    # --- Guideline Result ---
    story.append(_section_title("5. Guideline Compliance", styles))
    story.append(_guideline_section(compliance, flags, styles))
    story.append(Spacer(1, 5 * mm))

    # --- Advised Treatment & Work-up (the approved plan) ---
    story.append(_section_title("6. Advised Treatment & Planned Investigations", styles))
    story.append(_prescription_section(compliance, findings, decision, styles, plan))
    story.append(Spacer(1, 5 * mm))

    # --- HUMAN DECISION ---
    story.append(_section_title("7. Human Decision", styles))
    story.append(_human_decision_section(decision, styles))
    story.append(Spacer(1, 10 * mm))

    # --- Footer ---
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_MUTED))
    story.append(Spacer(1, 3 * mm))
    story.append(_footer(final_hash, styles))

    try:
        doc.build(story)
        logger.info(f"PDF packet generated: {pdf_path}")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        # Fall back to text packet
        return _build_text_packet(case, findings, flags, decision, final_hash)

    return f"packets/{case_id}.pdf"


def _build_text_packet(case, findings, flags, decision, final_hash, compliance=None, plan=None) -> str:
    """Fallback: generate a .txt packet instead of PDF."""
    import json
    PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    case_id = case.get("case_id", "unknown")
    txt_path = PACKETS_DIR / f"{case_id}.txt"

    plan = plan or {}
    investigations = plan.get("investigations") or [
        INVESTIGATION_LABELS.get(c, c.replace("_", " "))
        for c in (compliance or {}).get("missing_investigations", []) or []
    ]
    treatment = plan.get("treatment") or []
    lines = [
        "=" * 60,
        f"ANTENATAL REVIEW BOARD — REVIEW PACKET",
        f"Case ID: {case_id}",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"SYNTHETIC DATA — DECISION-SUPPORT ONLY — NOT FOR CLINICAL USE",
        "=" * 60,
        "",
        "--- CASE SUMMARY ---",
        json.dumps(case, indent=2, default=str),
        "",
        "--- FINDINGS ---",
        json.dumps(findings, indent=2, default=str),
        "",
        "--- RISK FLAGS ---",
        json.dumps(flags, indent=2, default=str),
        "",
        "--- GUIDELINE COMPLIANCE ---",
        json.dumps(compliance or {}, indent=2, default=str),
        "",
        "--- ADVISED TREATMENT & PLANNED INVESTIGATIONS ---",
        f"  Impression: {plan.get('impression', '—')}",
        "  Treatment:",
        ("\n".join(f"    {i+1}. {t}" for i, t in enumerate(treatment)) if treatment
         else "    —"),
        "  Investigations:",
        ("\n".join(f"    {i+1}. {x}" for i, x in enumerate(investigations)) if investigations
         else "    None indicated."),
        f"  Plan iterations with OB: {plan.get('iteration', 1)}",
        f"  OB instruction: {(decision or {}).get('note', '') or '—'}",
        "",
        "--- HUMAN DECISION ---",
        json.dumps(decision, indent=2, default=str),
        "",
        "--- AUDIT ---",
        f"Final Hash: {final_hash}",
        "Tamper-evident: verify via audit chain.",
    ]
    txt_path.write_text("\n".join(lines))
    return f"packets/{case_id}.txt"


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _section_header(case_id: str, styles) -> Paragraph:
    """Document header."""
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=COLOR_PRIMARY,
        spaceAfter=2 * mm,
        alignment=TA_CENTER,
    )
    return Paragraph(
        f"Antenatal Review Board<br/>Review Packet — {case_id}",
        header_style,
    )


def _disclaimer(styles) -> Paragraph:
    """Decision-support disclaimer."""
    disc_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=COLOR_MUTED,
        alignment=TA_CENTER,
    )
    return Paragraph(
        "<b>SYNTHETIC DATA — DECISION-SUPPORT ONLY — NOT FOR CLINICAL USE</b>",
        disc_style,
    )


def _section_title(title: str, styles) -> Paragraph:
    """Section title."""
    title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=COLOR_PRIMARY,
        spaceBefore=3 * mm,
        spaceAfter=2 * mm,
    )
    return Paragraph(title, title_style)


def _case_summary_table(case: dict, findings: list, styles) -> Table:
    """Case summary table."""
    demo = case.get("demographics", {}) or {}
    vitals = case.get("vitals", {}) or {}
    labs = case.get("labs", {}) or {}
    bp_s, bp_d = vitals.get("bp_systolic"), vitals.get("bp_diastolic")
    bp = f"{bp_s}/{bp_d}" if (bp_s or bp_d) else "Not recorded"
    data = [
        ["Field", "Value"],
        ["Case ID", case.get("case_id", "N/A")],
        ["Age", _fmt(demo.get("age"))],
        ["Parity", _fmt(demo.get("parity"))],
        ["LMP Date", _fmt(case.get("lmp_date"))],
        ["Ultrasound Date", _fmt(case.get("usg_date"))],
        ["BP", bp],
        ["Urine Protein", _fmt(labs.get("urine_protein"))],
        ["Fasting Glucose", _fmt(labs.get("fasting_glucose_mg_dl"), " mg/dL")],
        ["Hb", _fmt(labs.get("hb_g_dl"), " g/dL")],
    ]
    return _styled_table(data)


def _ga_discordance_section(findings: list, styles) -> Paragraph:
    """GA and discordance text."""
    text_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
    )

    if not findings:
        return Paragraph("No GA data available.", text_style)

    f = findings[0] if isinstance(findings[0], dict) else {}
    ga_lmp = f.get("ga_lmp_weeks", "N/A")
    ga_usg = f.get("ga_usg_weeks", "N/A")
    disc = f.get("discordance_weeks", "N/A")
    discordant = f.get("discordant", False)

    color = COLOR_DANGER if discordant else COLOR_SUCCESS
    status = "DISCREPANT ⚠" if discordant else "CONCORDANT ✓"

    disc_style = ParagraphStyle(
        "Discordance",
        parent=text_style,
        textColor=color,
    )

    return Paragraph(
        f"<b>GA (LMP):</b> {ga_lmp} weeks<br/>"
        f"<b>GA (Ultrasound):</b> {ga_usg} weeks<br/>"
        f"<b>Discordance:</b> {disc} weeks — <b>{status}</b><br/>"
        f"<i>Dating discordance ≥ 2.0 weeks: prefer ultrasound dating (DATE-004).</i>",
        disc_style,
    )


def _risk_flags_section(flags: list, styles) -> Table | Paragraph:
    """Risk flags table or 'none' message."""
    text_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10)

    if not flags:
        return Paragraph("<b>No risk flags fired.</b>", text_style)

    data = [["Flag", "Severity", "Rule Ref", "Evidence"]]
    for f in flags:
        fd = f if isinstance(f, dict) else f.model_dump()
        evidence_str = ", ".join(f"{k}={v}" for k, v in fd.get("evidence", {}).items())
        data.append([
            fd.get("type", "").replace("_", " ").title(),
            fd.get("severity", "moderate").upper(),
            fd.get("rule_ref", ""),
            evidence_str,
        ])

    return _styled_table(data)


def _imaging_section(findings: list, styles) -> Paragraph:
    """Imaging observations — labelled decision-support."""
    text_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10)

    if not findings:
        return Paragraph("No imaging data.", text_style)

    f = findings[0] if isinstance(findings[0], dict) else {}
    observations = f.get("imaging_observations", "No observations recorded.")
    confidence = f.get("imaging_confidence", "N/A")

    ds_style = ParagraphStyle(
        "DecisionSupport",
        parent=text_style,
        fontSize=10,
        textColor=COLOR_MUTED,
    )

    return Paragraph(
        f"<b>Confidence:</b> {confidence}<br/><br/>"
        f"<b>Observations:</b><br/>{observations}<br/><br/>"
        f"<i>⚠ DECISION-SUPPORT ONLY — not a diagnosis. "
        f"Must be reviewed by a qualified clinician.</i>",
        ds_style,
    )


def _guideline_section(compliance: dict, flags: list, styles) -> Paragraph:
    """Guideline compliance section — uses the real ComplianceResult."""
    text_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10)
    compliance = compliance or {}

    veto = bool(compliance.get("veto"))
    compliant = bool(compliance.get("compliant"))
    rule_refs = compliance.get("rule_refs", []) or [
        (f if isinstance(f, dict) else {}).get("rule_ref", "") for f in (flags or [])
    ]
    rule_refs = [r for r in rule_refs if r]
    notes = compliance.get("notes", "")

    veto_style = ParagraphStyle(
        "Veto", parent=text_style, textColor=COLOR_DANGER if veto else COLOR_SUCCESS,
    )

    return Paragraph(
        f"<b>Rules referenced:</b> {', '.join(rule_refs) if rule_refs else '—'}<br/>"
        f"<b>Compliant:</b> {'Yes' if compliant else 'No'}<br/>"
        f"<b>Veto:</b> {'⚠ YES — human review required' if veto else 'No'}<br/>"
        + (f"<b>Notes:</b> {notes}<br/>" if notes else "")
        + "<i>Verdict computed deterministically from antenatal_rules.yaml.</i>",
        veto_style,
    )


def _prescription_section(compliance: dict, findings: list, decision: dict,
                          styles, plan: dict | None = None) -> Paragraph:
    """Advised treatment & planned investigations — the OB-approved plan.

    Prefers the approved treatment plan (impression + investigations + treatment,
    possibly AI-drafted and OB-revised over several iterations). Falls back to the
    deterministic guideline work-up if no plan is present.
    """
    text_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=15)
    compliance = compliance or {}
    plan = plan or {}

    investigations = list(plan.get("investigations") or [])
    treatment = list(plan.get("treatment") or [])

    # Fallback: derive investigations from the guideline result if no plan exists
    if not investigations and not treatment:
        for code in compliance.get("missing_investigations", []) or []:
            investigations.append(INVESTIGATION_LABELS.get(code, code.replace("_", " ")))
        f = findings[0] if findings and isinstance(findings[0], dict) else {}
        if f.get("discordant"):
            rec = INVESTIGATION_LABELS["prefer_ultrasound_dating"]
            if rec not in investigations:
                investigations.append(rec)

    parts: list[str] = []
    impression = plan.get("impression")
    if impression:
        parts.append(f"<b>Clinical impression:</b> {impression}")

    if treatment:
        parts.append("<b>Advised treatment / management:</b><br/>" +
                     "<br/>".join(f"&nbsp;&nbsp;{i+1}. {t}" for i, t in enumerate(treatment)))

    if investigations:
        parts.append("<b>Planned investigations:</b><br/>" +
                     "<br/>".join(f"&nbsp;&nbsp;{i+1}. {x}" for i, x in enumerate(investigations)))

    if not parts:
        parts.append("<b>No further investigations or treatment indicated.</b>")

    if plan.get("iteration", 1) > 1:
        parts.append(f"<i>Plan revised {plan['iteration']} time(s) with the reviewing "
                     f"obstetrician before approval.</i>")

    note = (decision or {}).get("note", "")
    if note:
        parts.append(f"<b>Reviewing OB instruction:</b> {note}")

    parts.append(
        "<i>AI-drafted decision-support, reviewed and approved by the named "
        "obstetrician — whose approval is the binding management decision.</i>"
    )
    return Paragraph("<br/><br/>".join(parts), text_style)


def _human_decision_section(decision: dict, styles) -> Paragraph:
    """Human decision block — the only clinical judgement in the packet."""
    text_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10)

    reviewer = decision.get("reviewer", "Unknown")
    verdict = decision.get("verdict", "N/A").upper()
    note = decision.get("note", "")
    decided_at = decision.get("decided_at", "")

    verdict_color = COLOR_SUCCESS if verdict == "APPROVE" else COLOR_WARNING

    dec_style = ParagraphStyle(
        "Decision",
        parent=text_style,
        fontSize=11,
        textColor=verdict_color,
    )

    return Paragraph(
        f"<b>Reviewer:</b> {reviewer}<br/>"
        f"<b>Verdict:</b> <font color='{verdict_color}'>{verdict}</font><br/>"
        f"<b>Note:</b> {note}<br/>"
        f"<b>Decided at:</b> {decided_at}<br/><br/>"
        f"<i>This is the ONLY clinical judgement in this packet. "
        f"All preceding sections are decision-support only. "
        f"The human reviewer holds final authority.</i>",
        dec_style,
    )


def _footer(final_hash: str, styles) -> Paragraph:
    """Footer with final hash and tamper-evidence note."""
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=7,
        textColor=COLOR_MUTED,
        alignment=TA_CENTER,
    )
    return Paragraph(
        f"Final Hash: {final_hash}<br/>"
        f"Tamper-evident: verify via audit chain (GET /cases/{{id}}/audit). "
        f"Any alteration breaks SHA-256 linkage.",
        footer_style,
    )


def _styled_table(data: list[list[str]]) -> Table:
    """Create a consistently styled table."""
    t = Table(data, colWidths=[40 * mm, 120 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), COLOR_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_MUTED),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_BG, white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t
