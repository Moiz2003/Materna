"""packet/generator.py — Professional clinical PDF (ReportLab)."""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
PACKETS_DIR = Path(__file__).parent.parent / "packets"

INVESTIGATION_LABELS = {
    "repeat_bp_4h": "Repeat blood pressure after 4 hours",
    "24h_urine_protein": "24-hour urine protein quantification",
    "ogtt": "Oral glucose tolerance test (OGTT)",
    "iron_studies": "Iron studies (ferritin, TIBC, peripheral smear)",
    "prefer_ultrasound_dating": "Re-date pregnancy by ultrasound (LMP unreliable)",
}

def _fmt(v, s=""): return "—" if v in (None, "", "None", 0) else f"{v}{s}"

def _lab_status(key, val):
    if key == "urine_protein":
        return ("ABNORMAL", "#F59E0B") if str(val) not in ("negative", "Negative", "neg", "") else ("Normal", "#059669")
    if key == "bp_systolic":
        n = float(val) if val and not isinstance(val, (int, float)) else (val or 0)
        return ("SEVERE", "#DC2626") if n >= 160 else (("HIGH", "#F59E0B") if n >= 140 else ("Normal", "#059669"))
    if key == "bp_diastolic":
        n = float(val) if val and not isinstance(val, (int, float)) else (val or 0)
        return ("SEVERE", "#DC2626") if n >= 110 else (("HIGH", "#F59E0B") if n >= 90 else ("Normal", "#059669"))
    if key == "fasting_glucose_mg_dl":
        n = float(val) if val and not isinstance(val, (int, float)) else 0
        return ("HIGH", "#F59E0B") if n >= 92 else ("Normal", "#059669")
    if key == "hb_g_dl":
        n = float(val) if val and not isinstance(val, (int, float)) else 999
        return ("LOW", "#F59E0B") if n < 11.0 else ("Normal", "#059669")
    return ("—", "#6B7280")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Flowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

class BarFlowable(Flowable):
    def __init__(self, value, max_val, width=140, height=14, color="#0D9488", label=""):
        Flowable.__init__(self); self.v = value; self.mv = max_val; self._w = width; self._h = height
        self.c = color; self.lbl = label
    def wrap(self, aw, ah): return (self._w, self._h)
    def draw(self):
        pct = min(self.v / max(self.mv, 1), 1.0)
        self.canv.setFillColor(HexColor("#E2E8F0"))
        self.canv.roundRect(0, 0, self._w, self._h, 4, fill=1, stroke=0)
        if pct > 0:
            self.canv.setFillColor(HexColor(self.c))
            self.canv.roundRect(0, 0, self._w * pct, self._h, 4, fill=1, stroke=0)
        self.canv.setFillColor(HexColor("#0F172A"))
        self.canv.setFont("Helvetica-Bold", 8)
        self.canv.drawString(self._w * pct + 6, self._h/2 - 4, f"{self.v:.1f} wk {self.lbl}")

async def build_packet(case, findings, flags, decision, final_hash, compliance=None, plan=None):
    if not HAS_REPORTLAB: return _text_fallback(case, findings, flags, decision, final_hash, compliance, plan)
    PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    cid = case.get("case_id", "unknown")
    path = PACKETS_DIR / f"{cid}.pdf"
    comp = compliance or {}; pl = plan or {}
    fdata = {}
    if findings and findings[0]:
        fdata = findings[0]
        if hasattr(fdata, 'model_dump'):
            fdata = fdata.model_dump()
        elif not isinstance(fdata, dict):
            fdata = {}
    styles = getSampleStyleSheet()
    story = []

    # Header
    hs = ParagraphStyle("H", parent=styles["Heading1"], fontSize=18, textColor=HexColor("#0D9488"), spaceAfter=2*mm, alignment=TA_CENTER)
    story.append(Paragraph(f"Antenatal Review Board<br/>Review Packet — {cid}", hs))
    ds = ParagraphStyle("D", parent=styles["Normal"], fontSize=8, textColor=HexColor("#6B7280"), alignment=TA_CENTER)
    story.append(Paragraph("<b>SYNTHETIC DATA — DECISION-SUPPORT ONLY — NOT FOR CLINICAL USE</b>", ds))
    story.append(Spacer(1, 5*mm))

    # Section styles
    sec = lambda t: Paragraph(t, ParagraphStyle("S", parent=styles["Heading2"], fontSize=13, textColor=HexColor("#0D9488"), spaceBefore=4*mm, spaceAfter=2*mm))
    body = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, leading=14)
    small = ParagraphStyle("Sm", parent=styles["Normal"], fontSize=8, textColor=HexColor("#6B7280"))

    # 1. Vitals & Labs
    story.append(sec("1. Patient Vitals & Laboratory Values"))
    demo = case.get("demographics", {}) or {}
    v = case.get("vitals", {}) or {}
    l = case.get("labs", {}) or {}
    bp_s, bp_d = v.get("bp_systolic"), v.get("bp_diastolic")
    bp = f"{_fmt(bp_s)}/{_fmt(bp_d)}"
    s1_l, s1_c = _lab_status("bp_systolic", bp_s); s2_l, s2_c = _lab_status("bp_diastolic", bp_d)
    bp_badge = "ABNORMAL" if s1_l != "Normal" or s2_l != "Normal" else "Normal"
    rows = [["Measurement", "Value", "Normal Range", "Status"]]
    for label, val, norm, badge in [
        ("Age", _fmt(demo.get("age"), " yrs"), "—", "—"),
        ("Parity", _fmt(demo.get("parity")), "—", "—"),
        ("LMP Date", _fmt(case.get("lmp_date")), "—", "—"),
        ("USG Date", _fmt(case.get("usg_date")), "—", "—"),
        ("Blood Pressure", bp, "< 140/90 mmHg", bp_badge),
        ("Urine Protein", _fmt(l.get("urine_protein")), "Negative", _lab_status("urine_protein", l.get("urine_protein"))[0]),
        ("Fasting Glucose", _fmt(l.get("fasting_glucose_mg_dl"), " mg/dL"), "70–91 mg/dL", _lab_status("fasting_glucose_mg_dl", l.get("fasting_glucose_mg_dl"))[0]),
        ("Haemoglobin", _fmt(l.get("hb_g_dl"), " g/dL"), "11.0–16.0 g/dL", _lab_status("hb_g_dl", l.get("hb_g_dl"))[0]),
    ]:
        rows.append([label, val, norm, badge])
    t = Table(rows, colWidths=[48*mm, 36*mm, 40*mm, 30*mm])
    tcmds = [("BACKGROUND", (0,0), (-1,0), HexColor("#0D9488")), ("TEXTCOLOR", (0,0), (-1,0), white),
             ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,0), 9),
             ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"), ("FONTSIZE", (0,1), (-1,-1), 8),
             ("GRID", (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
             ("ROWBACKGROUNDS", (0,1), (-1,-1), [HexColor("#F8FAFC"), white]),
             ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("TOPPADDING", (0,0), (-1,-1), 5),
             ("BOTTOMPADDING", (0,0), (-1,-1), 5), ("LEFTPADDING", (0,0), (-1,-1), 6)]
    for i, row in enumerate(rows[1:], start=1):
        st = row[3]
        if st in ("ABNORMAL","SEVERE","HIGH","LOW"):
            tcmds += [("BACKGROUND",(3,i),(3,i), HexColor("#FEE2E2")), ("TEXTCOLOR",(3,i),(3,i), HexColor("#DC2626"))]
        elif st == "Normal":
            tcmds += [("BACKGROUND",(3,i),(3,i), HexColor("#D1FAE5")), ("TEXTCOLOR",(3,i),(3,i), HexColor("#059669"))]
    t.setStyle(TableStyle(tcmds))
    story.append(t)
    story.append(Spacer(1, 4*mm))

    # 2. GA & Discordance
    story.append(sec("2. Gestational Age & Discordance"))
    ga_l = fdata.get("ga_lmp_weeks") or 0; ga_u = fdata.get("ga_usg_weeks") or 0
    disc = fdata.get("discordance_weeks") or 0; disc_flag = fdata.get("discordant", False)
    max_ga = max(ga_l, ga_u, 1) * 1.2
    if ga_l:
        story.append(Paragraph(f"GA (LMP): {ga_l:.1f} weeks", body))
        story.append(BarFlowable(ga_l, max_ga, color="#0D9488", label="LMP"))
        story.append(Spacer(1, 2))
    if ga_u:
        story.append(Paragraph(f"GA (Ultrasound): {ga_u:.1f} weeks", body))
        story.append(BarFlowable(ga_u, max_ga, color="#6366F1", label="USG"))
        story.append(Spacer(1, 3))
    dc = "#DC2626" if disc_flag else "#059669"
    dl = "DISCREPANT" if disc_flag else "CONCORDANT"
    story.append(Paragraph(f"<b>Discordance: {disc:.1f} weeks — <font color='{dc}'>{dl}</font></b>", body))
    story.append(Paragraph("<i>Threshold: ≥ 2.0 weeks. Prefer ultrasound dating (DATE-004).</i>", small))
    story.append(Spacer(1, 4*mm))

    # 3. Risk Flags
    if flags:
        story.append(sec("3. Risk Flags"))
        frows = [["Rule", "Type", "Severity", "Evidence"]]
        for fl in flags:
            fd = fl if isinstance(fl, dict) else fl.model_dump()
            sev = fd.get("severity","moderate").upper()
            ev = ", ".join(f"{k}={v}" for k,v in fd.get("evidence",{}).items())
            frows.append([fd.get("rule_ref",""), fd.get("type","").replace("_"," ").title(), sev, ev])
        ft = Table(frows, colWidths=[22*mm, 52*mm, 22*mm, 62*mm])
        fcmds = [("BACKGROUND",(0,0),(-1,0), HexColor("#0D9488")), ("TEXTCOLOR",(0,0),(-1,0), white),
                 ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),8),
                 ("GRID",(0,0),(-1,-1),0.5, HexColor("#E2E8F0")),
                 ("ROWBACKGROUNDS",(0,1),(-1,-1),[HexColor("#F8FAFC"), white]),
                 ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("TOPPADDING",(0,0),(-1,-1),5),
                 ("BOTTOMPADDING",(0,0),(-1,-1),5), ("LEFTPADDING",(0,0),(-1,-1),5)]
        for i, row in enumerate(frows[1:], start=1):
            if row[2] == "HIGH":
                fcmds += [("BACKGROUND",(2,i),(2,i), HexColor("#FEE2E2")), ("TEXTCOLOR",(2,i),(2,i), HexColor("#DC2626"))]
            elif row[2] == "MODERATE":
                fcmds += [("BACKGROUND",(2,i),(2,i), HexColor("#FEF3C7")), ("TEXTCOLOR",(2,i),(2,i), HexColor("#F59E0B"))]
        ft.setStyle(TableStyle(fcmds))
        story.append(ft)
        story.append(Spacer(1, 4*mm))

    # 4. Compliance
    story.append(sec("4. Guideline Compliance"))
    veto = bool(comp.get("veto")); compliant = bool(comp.get("compliant"))
    missing = comp.get("missing_investigations",[]); rr = comp.get("rule_refs",[])
    vr = ", ".join(rr) if rr else "—"
    vc = "#DC2626" if veto else "#059669"
    vt = "YES — Human review required" if veto else "No"
    story.append(Paragraph(f"<b>Rules:</b> {vr}<br/><b>Compliant:</b> {'Yes' if compliant else 'No'}<br/><b>Veto:</b> <font color='{vc}'>{vt}</font>", body))
    if missing: story.append(Paragraph(f"<b>Missing:</b> {', '.join(missing)}", body))
    story.append(Paragraph("<i>Verdict computed deterministically from antenatal_rules.yaml.</i>", small))
    story.append(Spacer(1, 4*mm))

    # 5. Treatment
    story.append(sec("5. Advised Treatment & Planned Investigations"))
    inv = list(pl.get("investigations") or []); tx = list(pl.get("treatment") or [])
    if not inv and not tx:
        for code in (comp or {}).get("missing_investigations",[]) or []:
            inv.append(INVESTIGATION_LABELS.get(code, code.replace("_"," ")))
    p = []
    if pl.get("impression"): p.append(f"<b>Impression:</b> {pl['impression']}")
    if tx: p.append(f"<b>Treatment:</b><br/>" + "<br/>".join(f"&nbsp;&nbsp;{i+1}. {t}" for i,t in enumerate(tx)))
    if inv: p.append(f"<b>Investigations:</b><br/>" + "<br/>".join(f"&nbsp;&nbsp;{i+1}. {x}" for i,x in enumerate(inv)))
    if pl.get("iteration",1) > 1: p.append(f"Plan revised {pl['iteration']}× with OB.")
    if decision.get("note"): p.append(f"<b>OB instruction:</b> {decision['note']}")
    story.append(Paragraph("<br/><br/>".join(p), body))
    story.append(Spacer(1, 5*mm))

    # 6. Decision
    story.append(sec("6. Human Decision"))
    rv = decision.get("reviewer","—"); ve = decision.get("verdict","—").upper()
    nt = decision.get("note",""); dt = decision.get("decided_at","")
    dc = HexColor("#059669" if ve == "APPROVE" else "#F59E0B")
    story.append(Paragraph(f"<b>Reviewer:</b> {rv}<br/><b>Verdict:</b> <font color='{dc}'>{ve}</font><br/>"
                          f"<b>Note:</b> {nt}<br/><b>Decided:</b> {dt}", body))
    story.append(Paragraph("<i>The ONLY clinical judgement in this packet. Human reviewer holds final authority.</i>", small))
    story.append(Spacer(1, 8*mm))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#E2E8F0")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(f"Final Hash: {final_hash}<br/>Tamper-evident: any alteration breaks SHA-256 chain.", small))

    try:
        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm,
                                title=f"Antenatal Review — {cid}", author="Materna")
        doc.build(story)
        logger.info(f"PDF: {path}")
    except Exception as e:
        import traceback; traceback.print_exc()
        logger.error(f"PDF failed: {e}")
        return _text_fallback(case, findings, flags, decision, final_hash, comp, pl)
    return f"packets/{cid}.pdf"

def _text_fallback(case, findings, flags, decision, final_hash, comp=None, plan=None):
    import json
    PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    cid = case.get("case_id","unknown")
    p = PACKETS_DIR / f"{cid}.txt"
    p.write_text("\n".join(["MATERNA REVIEW", f"Case: {cid}", json.dumps(case, indent=2, default=str), "",
                            json.dumps(findings, indent=2, default=str), "", json.dumps(flags, indent=2, default=str), "",
                            json.dumps(decision, indent=2, default=str), "", f"Hash: {final_hash}"]))
    return f"packets/{cid}.txt"
