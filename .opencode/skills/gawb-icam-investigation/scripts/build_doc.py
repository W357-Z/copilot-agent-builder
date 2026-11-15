"""build_doc.py - create branded GAWB ICAM artefact DOCX files from JSON data.

Usage:
    python build_doc.py <type> <data.json> <out.docx> [charts_dir]

Types:
    plan      Scoping and Investigation Plan
    evidence  PEEPO Evidence Log
    appendixc Analysis of Contributory Factors worksheet (MPR-INT-0214 App C)
    cap       Corrective Action Plan
    witness   Incident Witness Statement (MPR-INT-0214 App D style)

charts_dir (optional): directory containing skill-rendered PNG charts; when
present, appendixc embeds icam-chart.png.

Exit codes: 0 ok, 2 usage error, 3 data error, 1 unexpected failure.
Stdlib only; no network.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_docx as L  # noqa: E402

TYPES = ("plan", "evidence", "appendixc", "cap", "witness")

APP_C_SOURCE = "MPR-INT-0214 Appendix C (controlled source; verify against current issue)"


def fail(code, message):
    sys.stderr.write("build_doc: %s\n" % message)
    sys.stderr.flush()
    sys.exit(code)


# ---------------------------------------------------------------- taxonomy --
# Factor legends transcribed from MPR-INT-0214 Appendix C and verified
# against the source extract (codes and ratings match DF1-14, IT1-14,
# WF1-23, HF1-23 and the OR code set). Confirm against the current
# controlled issue before formal use in a report.
DF_LEGEND = [
    ("DF1", "Detection systems / procedures"),
    ("DF2", "Protection systems / procedures"),
    ("DF3", "Warning systems / procedures"),
    ("DF4", "Guards or barriers"),
    ("DF5", "Recovery systems / procedures"),
    ("DF6", "Escape systems / procedures"),
    ("DF7", "Rescue systems / procedures"),
    ("DF8", "PPE"),
    ("DF9", "Hazard identification"),
    ("DF10", "Risk management"),
    ("DF11", "Safe work procedure"),
    ("DF12", "Supervision"),
    ("DF13", "Other (specify)"),
    ("DF14", "Other (specify)"),
]
DF_RATING = "Absent / Some failure / Complete failure"

IT_LEGEND = [
    ("IT1", "Supervision"),
    ("IT2", "Authority"),
    ("IT3", "Operating speed"),
    ("IT4", "Equipment use"),
    ("IT5", "PPE"),
    ("IT6", "Work procedure followed"),
    ("IT7", "Change management"),
    ("IT8", "Equipment / material handling"),
    ("IT9", "Horseplay"),
    ("IT10", "Hazard recognition"),
    ("IT11", "Hazard management"),
    ("IT12", "Work method"),
    ("IT13", "Occupational hygiene practices"),
    ("IT14", "Other (specify)"),
]
IT_RATING = "Absent / Inadequate / unsuitable (IT4-5 also: exceeded limits, misuse; IT6: partially / not followed)"

WF_LEGEND = [
    ("WF1", "Lighting"), ("WF2", "Weather"),
    ("WF3", "Gas / dust / fumes / contaminants"), ("WF4", "Noise"),
    ("WF5", "Wildlife"), ("WF6", "Surface gradient / conditions"),
    ("WF7", "Workspace access / restriction"), ("WF8", "Housekeeping"),
    ("WF9", "Tools / equipment condition / availability"),
    ("WF10", "Task planning / preparation"),
    ("WF11", "Routine / non routine task"),
    ("WF12", "Abnormal operational situation / condition"),
    ("WF13", "Risk perception / management"),
    ("WF14", "Work procedures"), ("WF15", "Permit to Work"),
    ("WF16", "Chemical"), ("WF17", "Ventilation"),
    ("WF18", "Material availability and suitability"),
    ("WF19", "Fire and or / explosion"),
    ("WF20", "Congestion / restriction / access"),
    ("WF21", "Equipment Integrity"), ("WF22", "Radiation"),
    ("WF23", "Other (specify)"),
]
WF_RATING = "Some / significant"

HF_LEGEND = [
    ("HF1", "Complacency / motivation"), ("HF2", "Drugs / alcohol"),
    ("HF3", "Familiarity with task"), ("HF4", "Fatigue"),
    ("HF5", "Time pressure"), ("HF6", "Peer pressure"),
    ("HF7", "Physical capabilities"), ("HF8", "Mental capabilities"),
    ("HF9", "Physical stress"), ("HF10", "Mental stress"),
    ("HF11", "Confidence level"), ("HF12", "Secondary goals / external factors"),
    ("HF13", "Personal issues"), ("HF14", "Distraction / pre-occupation"),
    ("HF15", "Experience / knowledge / skill for task"),
    ("HF16", "Competency"), ("HF17", "Behavioural beliefs"),
    ("HF18", "Personality / attitude"), ("HF19", "Poor communication"),
    ("HF20", "Poor shift patterns / overtime working"),
    ("HF21", "Situational awareness"),
    ("HF22", "Passive tolerance of violations"),
    ("HF23", "Perceived licence to operate"),
]
HF_RATING = "Some / significant"

ORG_LEGEND = [
    ("HW", "Hardware"), ("TR", "Training"), ("OR", "Organisation"),
    ("CO", "Communications"), ("IG", "Incompatible goals"),
    ("PR", "Procedures"), ("MM", "Maintenance Management"),
    ("MS", "Management Systems"), ("SU", "Supervision"),
    ("DE", "Design"), ("RM", "Risk Management"),
    ("MC", "Management of Change"), ("CM", "Contractor Management"),
    ("OC", "Organisational Culture"), ("RI", "Regulatory Influence"),
    ("OL", "Organisational Learning"), ("VM", "Vehicle Management"),
]
ORG_RATING = "Contributing"

CATEGORIES = [
    ("ABSENT / FAILED DEFENCES",
     "Defence factors that allowed the outcome: the last-minute protection "
     "measures designed to avoid or mitigate the event. Check question: does "
     "the item describe the equipment, work process, control measure, "
     "detection system or procedure which normally prevents this event or "
     "limits the consequences?",
     DF_LEGEND, DF_RATING, "absent_failed"),
    ("INDIVIDUAL / TEAM ACTIONS",
     "Errors or violations that led directly to the event, committed "
     "actively by people in direct contact with the equipment. Check "
     "question: does the item tell you about an error or violation of a "
     "standard or procedure made in the presence of a hazard?",
     IT_LEGEND, IT_RATING, "individual_team"),
    ("TASK / ENVIRONMENTAL CONDITIONS",
     "Conditions existing immediately prior to or at the time of the event "
     "that directly influence human and equipment performance: task demands, "
     "work environment, individual capabilities and human factors. Check "
     "question: does this item describe something about task demands, work "
     "environment, individual capabilities or human factors that promoted "
     "errors / violations or undermined the defences?",
     WF_LEGEND + HF_LEGEND, WF_RATING + " (workplace factors) / "
     + HF_RATING + " (human factors)", "task_env"),
    ("ORGANISATIONAL FACTORS",
     "Underlying organisational factors which produce the task / "
     "environmental conditions: fallible management decisions, processes and "
     "practices. Check question: does this item identify a standard "
     "organisational factor present before the event which resulted in the "
     "task / environmental conditions or allowed them to go unaddressed?",
     ORG_LEGEND, ORG_RATING, "organisational"),
]


def s(v):
    return "" if v is None else str(v)


def get(d, *path):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            raise L.DocxFillError("missing data key: %s" % "/".join(path))
        cur = cur[key]
    return cur


def opt(d, *path):
    try:
        return get(d, *path)
    except L.DocxFillError:
        return None


def doc_header(body, data, title, subtitle):
    meta = data.get("meta", {})
    L.banner(body, title, subtitle)
    refline = "Report %s  |  %s" % (s(meta.get("report_no", "")) or "not set",
                                    s(meta.get("classification", "")) or "")
    if meta.get("privileged"):
        refline += "  |  LEGALLY PRIVILEGED - handle per LPP protocol"
    L.para(body, refline, bold=True, size=17, colour=L.BRAND_GREY)
    if s(meta.get("note", "")):
        L.para(body, s(meta["note"]), italic=True, size=15, colour=L.BRAND_GREY)


# ------------------------------------------------------------------ plan ----
def build_plan(data, body, parts, charts_dir):
    inc = data.get("incident", {}) if isinstance(data.get("incident"), dict) else {}
    plan = data.get("plan", {}) if isinstance(data.get("plan"), dict) else {}
    if not plan:
        raise L.DocxFillError("missing data key: plan")
    doc_header(body, data, "INCIDENT INVESTIGATION PLAN",
               "Scoping and investigation plan per MPR-INT-0214")

    L.heading(body, "1. Incident Summary", 1)
    pairs = [("Title", s(inc.get("title"))),
             ("Incident type", s(inc.get("type"))),
             ("Date and time", "%s %s" % (s(inc.get("date")), s(inc.get("time")))),
             ("INC reference", s(inc.get("inx_ref"))),
             ("Classification", s(data.get("meta", {}).get("classification"))),
             ("Location", " / ".join(x for x in (s(inc.get("building")),
                                                 s(inc.get("location"))) if x)),
             ("Involved parties", s(inc.get("involved_parties"))),
             ("Basic event", s(inc.get("basic_event"))),
             ("Injury / damage / impact", s(inc.get("injuries"))),
             ("Immediate actions taken", s(inc.get("immediate_actions")))]
    L.kv_table(body, [(k, v) for k, v in pairs if v])

    L.heading(body, "2. Scope", 1)
    L.para(body, s(get(data, "plan", "scope")))
    L.heading(body, "3. Objectives", 1)
    L.para(body, s(get(data, "plan", "objectives")))

    L.heading(body, "4. Team and Approval", 1)
    L.kv_table(body, [
        ("Investigation team", s(get(data, "plan", "team"))),
        ("Approval path", s(get(data, "plan", "approval_path")))])

    L.heading(body, "5. Methodology", 1)
    L.para(body, s(get(data, "plan", "method")))
    cls = s(data.get("meta", {}).get("classification", ""))
    if "Level 4" in cls or "Level 5" in cls:
        L.para(body, "ICAM analysis is mandatory for Level 4 and Level 5 "
                     "investigations (MPR-INT-0214).", bold=True)

    L.heading(body, "6. Timeframes", 1)
    targets = [("Level 1 - 2 / Level 3", "25 working days"),
               ("Level 4", "30 working days (50 with extension)"),
               ("Level 5", "60 working days (35 initial report)")]
    cls = s(data.get("meta", {}).get("classification", ""))
    m = re.search(r"Level\s*([1-5])", cls)
    lvl_n = m.group(1) if m else ""
    rows = []
    for lvl, tgt in targets:
        hit = lvl_n and (lvl_n in ("1", "2") and "1 - 2" in lvl
                         or lvl.replace("Level", "").strip().startswith(lvl_n)
                         or lvl.endswith("Level %s" % lvl_n))
        rows.append([lvl, tgt, "TARGET" if hit else ""])
    L.table(body, ["Classification", "Investigation completion target", "This plan"],
            rows, fracs=[2, 3, 1])
    L.kv_table(body, [
        ("Planned timeframe (days)", s(get(data, "plan", "timeframe_days"))),
        ("Planned completion date", s(get(data, "plan", "due_date")))])

    L.heading(body, "7. Legal Privilege", 1)
    lpp = s(get(data, "plan", "lpp")).strip().lower()
    if lpp in ("yes", "true", "1"):
        L.para(body, "This investigation is conducted under legal privilege. "
                     "Mark all artefacts accordingly and route evidence through "
                     "the privileged channel; do not circulate outside the "
                     "approved distribution list.")
    else:
        L.para(body, "Legal privilege has not been claimed for this "
                     "investigation. Reassess with Legal Services before "
                     "interviews are recorded if the incident may attract "
                     "regulatory enforcement.")

    L.heading(body, "8. Evidence Collection Approach", 1)
    L.checklist(body, [
        "Photograph the scene before anything is moved (multiple angles).",
        "Isolate involved equipment: do not clean, repair or relocate.",
        "Record environmental conditions (weather, lighting, noise).",
        "Collect records: procedures, risk assessments, maintenance and "
        "training history, monitoring data.",
        "Interview witnesses separately using the skill interview guide "
        "(Appendix D statement form per witness).",
        "Log every item in the PEEPO Evidence Log with source and status "
        "(fact or assumption)."])

    L.heading(body, "9. Plan Sign-off", 1)
    L.kv_table(body, [("Prepared by (lead investigator)", ""),
                      ("Prepared date", s(data.get("meta", {}).get("prepared_date"))),
                      ("Approved by", ""),
                      ("Approval date", "")])


# -------------------------------------------------------------- evidence ----
def build_evidence(data, body, parts, charts_dir):
    rows_in = data.get("evidence")
    if not isinstance(rows_in, list) or not rows_in:
        raise L.DocxFillError("missing data key: evidence (non-empty list)")
    peepo = data.get("peepo") if isinstance(data.get("peepo"), dict) else {}

    def refs_for(key):
        out = []
        for it in (peepo.get(key) or []):
            ref = it.get("ref") if isinstance(it, dict) else ""
            if ref and ref not in out:
                out.append(ref)
        return ", ".join(out)

    doc_header(body, data, "PEEPO EVIDENCE LOG",
               "Evidence register: People, Environment, Equipment, Procedures, "
               "Organisation")

    L.heading(body, "1. Evidence Register", 1)
    rows = [[s(e.get("id")), s(e.get("description")), s(e.get("type")),
             s(e.get("source")), s(e.get("status")), s(e.get("location")),
             s(e.get("collected_by")), s(e.get("collected_at"))] for e in rows_in]
    L.table(body, ["ID", "Description", "Type", "Source", "Status",
                   "Location", "Collected by", "Collected at"],
            rows, fracs=[0.7, 2.6, 1.0, 1.4, 0.9, 1.6, 1.3, 1.0], size=15)
    L.para(body, "Status values: Fact (directly observed or verifiable) or "
                 "Assumption (to be validated before the analysis is "
                 "finalised). Every assumption entering the ICAM chart must "
                 "be resolved or declared in the report assumptions "
                 "section.", italic=True, size=15, colour=L.BRAND_GREY)

    L.heading(body, "2. Collection Checklist", 1)
    L.checklist(body, [
        "Scene photographs taken before disturbance (multi-angle).",
        "Physical equipment isolated and preserved as found.",
        "Environmental conditions documented at time of event.",
        "Documents: procedures, risk assessments, maintenance, training.",
        "Witness statements recorded on Appendix D forms, separately.",
        "Digital evidence preserved with metadata and chain of custody.",
        "Privileged items routed through the LPP channel (if claimed)."])

    L.heading(body, "3. PEEPO Coverage Check", 1)
    L.table(body, ["Category", "Prompts addressed with evidence", "Evidence IDs"],
            [["People", "Human factors: fatigue, competency, hazard "
                        "recognition, situational awareness, procedure "
                        "adherence.", refs_for("people")],
             ["Environment", "Physical conditions: weather, lighting, "
                             "noise, surfaces, workspace access.", refs_for("environment")],
             ["Equipment", "Tools and technology: design, condition, "
                           "maintenance, availability, displays and "
                           "controls.", refs_for("equipment")],
             ["Procedures", "Work-as-prescribed vs work-as-done: "
                            "procedure quality, availability, permits.", refs_for("procedures")],
             ["Organisation", "Factors behind the above: risk management, "
                              "resourcing, communication, culture, "
                              "planning.", refs_for("organisation")]],
            fracs=[1.2, 4.0, 1.0], size=15)

    entries = []
    for key, label in (("people", "People"), ("environment", "Environment"),
                       ("equipment", "Equipment"), ("procedures", "Procedures"),
                       ("organisation", "Organisation")):
        for it in (peepo.get(key) or []):
            if isinstance(it, dict):
                entries.append([label, s(it.get("text")), s(it.get("ref"))])
            else:
                entries.append([label, s(it), ""])
    if entries:
        L.heading(body, "4. PEEPO Analysis Entries", 1)
        L.para(body, "Contributing-factor observations classified by PEEPO "
                     "column, cross-referenced to the evidence register and "
                     "mirrored on the PEEPO chart in the report.", size=15)
        L.table(body, ["Category", "Observation / contributing factor",
                       "Evidence IDs"], entries, fracs=[1.2, 4.0, 1.0],
                size=15)


# ------------------------------------------------------------- appendixc ----
def build_appendixc(data, body, parts, charts_dir):
    factors = data.get("factors")
    if not isinstance(factors, dict) or not factors:
        raise L.DocxFillError("missing data key: factors")
    basic = s(data.get("incident", {}).get("basic_event"))
    doc_header(body, data, "ANALYSIS OF CONTRIBUTORY FACTORS",
               "Appendix C worksheet - event: " + (basic or "not set"))

    for title, blurb, legend, rating, key in CATEGORIES:
        L.heading(body, title, 1)
        L.para(body, blurb, size=15, italic=True, colour=L.BRAND_GREY)
        sel = factors.get(key, [])
        if not isinstance(sel, list):
            sel = []
        if sel:
            rows = [[s(f.get("code")), s(f.get("text")),
                     s(f.get("reason")), s(f.get("rating", ""))] for f in sel]
            L.table(body, ["Code", "Factor identified", "Reason (evidence-based)",
                           "Rating"], rows, fracs=[0.7, 3.0, 3.0, 1.0], size=15)
        else:
            L.para(body, "No factors identified in this category.", size=15)
        L.heading(body, "Code legend - " + title, 2)
        legend_rows = [[code, name] for code, name in legend]
        half = (len(legend_rows) + 1) // 2
        left, right = legend_rows[:half], legend_rows[half:]
        merged = []
        for i in range(half):
            a = left[i]
            b = right[i] if i < len(right) else ["", ""]
            merged.append([a[0], a[1], b[0], b[1]])
        L.table(body, ["Code", "Factor", "Code", "Factor"], merged,
                fracs=[0.6, 2.0, 0.6, 2.0], size=14, banded=False)
        L.para(body, "Ratings: " + rating, size=14, italic=True,
               colour=L.BRAND_GREY)

    chart_path = os.path.join(charts_dir, "icam-chart.png") if charts_dir else None
    if chart_path and os.path.isfile(chart_path):
        L.heading(body, "Selected Factors Chart", 1)
        L.insert_png_body(body, parts, chart_path, width_cm=16.5)
        L.para(body, "Chart generated by the skill chart renderer from the "
                     "factors above; regenerate after any factor change.",
               size=14, italic=True, colour=L.BRAND_GREY, align="center")

    L.para(body, "Legend and check questions transcribed from " + APP_C_SOURCE
           + ".", size=13, italic=True, colour=L.BRAND_GREY)


# ------------------------------------------------------------------ cap -----
def build_cap(data, body, parts, charts_dir):
    rows_in = data.get("cap")
    if not isinstance(rows_in, list) or not rows_in:
        raise L.DocxFillError("missing data key: cap (non-empty list)")
    recs = data.get("recommendations") if isinstance(
        data.get("recommendations"), list) else []
    doc_header(body, data, "CORRECTIVE ACTION PLAN (CAP)",
               "Corrective and preventive actions per the hierarchy of "
               "controls")

    L.heading(body, "1. Hierarchy of Controls Reference", 1)
    L.table(body, ["#", "Control type", "Description", "Effectiveness"],
            [["1", "Elimination", "Remove the hazard completely", "Highest"],
             ["2", "Substitution", "Replace with something less hazardous",
              "High"],
             ["3", "Engineering", "Physically isolate people from the hazard",
              "Medium-High"],
             ["4", "Administrative", "Change how people work (procedures, "
                                     "training, signage, supervision)",
              "Medium-Low"],
             ["5", "PPE", "Protect the individual", "Lowest"]],
            fracs=[0.4, 1.4, 3.4, 1.2], size=15)

    L.heading(body, "2. Corrective Actions", 1)
    rows = []
    for i, c in enumerate(rows_in, 1):
        ctrl = s(c.get("control_type"))
        if not ctrl and i - 1 < len(recs):
            ctrl = s(recs[i - 1].get("control_type"))
        rows.append([str(i), s(c.get("recommendation")), ctrl,
                     s(c.get("dept")), s(c.get("person")), s(c.get("due")),
                     s(c.get("status", "Open"))])
    L.table(body, ["#", "Corrective action", "Control type", "Department / area",
                   "Person responsible", "Due date", "Status"],
            rows, fracs=[0.4, 3.2, 1.4, 1.5, 1.5, 1.0, 0.9], size=15)

    L.heading(body, "3. Quality Checklist (verify each action)", 1)
    L.checklist(body, [
        "Addresses the root cause, not just the symptom.",
        "Specific and measurable: completion is verifiable.",
        "Single accountable owner assigned.",
        "Due date realistic given complexity and resources.",
        "Control sits as high on the hierarchy of controls as practical.",
        "Sustainable without constant attention.",
        "Does not create new risks (unintended consequences considered).",
        "Verification method defined (post-implementation review)."])

    L.heading(body, "4. Verification Plan", 1)
    L.kv_table(body, [("How effectiveness will be verified", ""),
                      ("Verification owner", ""),
                      ("Verification due date", "")])
    L.para(body, "Weak actions to avoid unless they genuinely address the "
                 "cause: retrain all workers, remind workers to be careful, "
                 "add more warning signs, increase supervision (vague).",
           size=15, italic=True, colour=L.BRAND_GREY)


# -------------------------------------------------------------- witness -----
def build_witness(data, body, parts, charts_dir):
    w = data.get("witness") if isinstance(data.get("witness"), dict) else {}
    statement = s(w.get("statement")).strip()
    if not statement:
        raise L.DocxFillError("missing data key: witness.statement")
    inc = data.get("incident", {}) if isinstance(data.get("incident"), dict) else {}
    when = s(w.get("date_time")) or "%s %s" % (s(inc.get("date")),
                                               s(inc.get("time")))
    where = s(w.get("location")) or s(inc.get("location"))
    doc_header(body, data, "INCIDENT WITNESS STATEMENT",
               "Per MPR-INT-0214 Appendix D - record only what you observed "
               "or did")

    L.kv_table(body, [
        ("Incident date and time", when),
        ("Incident location", where),
        ("Statement date", s(data.get("meta", {}).get("prepared_date")))])

    L.heading(body, "Statement", 1)
    L.para(body, "Please provide as much detail as possible regarding what "
                 "occurred - capture only information that you observed or "
                 "actions you took (do not include assumptions about what "
                 "could have happened). Include information about events "
                 "leading up to the incident, the incident, and what "
                 "occurred afterwards.", size=15, italic=True,
           colour=L.BRAND_GREY)
    for chunk in statement.split("\n\n"):
        chunk = chunk.strip()
        if chunk:
            L.para(body, chunk)

    L.heading(body, "Declaration and Signature", 1)
    L.para(body, "I declare that this statement is true and accurate to the "
                 "best of my knowledge.", size=15)
    L.kv_table(body, [
        ("Witness name (print)", s(w.get("name"))),
        ("Occupation / role", s(w.get("occupation")) +
         (" (employer: %s)" % s(w.get("employer")) if s(w.get("employer")) else "")),
        ("Witness signature", ""),
        ("Date", "")])
    L.para(body, "Privacy: statements contain personal information. Store in "
                 "the restricted investigation file and disclose only per "
                 "procedure and legal advice.", size=13, italic=True,
           colour=L.BRAND_GREY)


BUILDERS = {
    "plan": build_plan,
    "evidence": build_evidence,
    "appendixc": build_appendixc,
    "cap": build_cap,
    "witness": build_witness,
}

TITLES = {
    "plan": "Incident Investigation Plan",
    "evidence": "PEEPO Evidence Log",
    "appendixc": "Analysis of Contributory Factors",
    "cap": "Corrective Action Plan",
    "witness": "Incident Witness Statement",
}


def main(argv):
    if len(argv) < 3 or len(argv) > 4:
        sys.stderr.write(__doc__)
        return 2
    kind, data_path, out_path = argv[0], argv[1], argv[2]
    charts_dir = argv[3] if len(argv) == 4 else None
    if kind not in TYPES:
        sys.stderr.write("build_doc: unknown type %r; expected one of %s\n"
                         % (kind, ", ".join(TYPES)))
        return 2
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        sys.stderr.write("build_doc: cannot read data file: %s\n" % e)
        return 3
    except ValueError as e:
        sys.stderr.write("build_doc: data file is not valid JSON: %s\n" % e)
        return 3
    if not isinstance(data, dict):
        sys.stderr.write("build_doc: data root must be a JSON object\n")
        return 3

    parts, doc, body = L.open_doc(TITLES[kind])
    try:
        BUILDERS[kind](data, body, parts, charts_dir)
        L.save_doc(parts, doc, out_path)
    except L.DocxFillError as e:
        sys.stderr.write("build_doc: data error: %s\n" % e)
        return 3
    print(json.dumps({"written": os.path.abspath(out_path), "type": kind}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception as e:  # unexpected
        sys.stderr.write("build_doc: unexpected failure: %r\n" % e)
        sys.exit(1)
