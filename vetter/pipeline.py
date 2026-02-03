import os
import re
from typing import List, Dict, Any
from vetter.extract import extract_pdf_text
from vetter.llm import chat_json, LLMError
from vetter.rules import load_rules, required_fields_for, cross_doc_checks
from vetter.schemas import DocResult, BatchResult
from vetter.report import render_pdf

REDACT_PATTERNS = [
    (re.compile(r"\b\d{13}\b"), "[REDACTED_ID]"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[REDACTED_EMAIL]"),
]

SYSTEM = """You are a compliance document analysis assistant.
Return ONLY valid JSON with doc_type, fields, notes.
Doc types: KYC_COMPANY, KYB_COMPANY, AML_DECLARATION, SALES_CONTRACT, EXPORT_PERMIT, OTHER"""

def redact(text: str) -> str:
    out = text
    for pat, rep in REDACT_PATTERNS:
        out = pat.sub(rep, out)
    return out

def llm_classify_and_extract(text: str, filename: str, rules: dict, settings) -> Dict[str, Any]:
    user = f"Classify and extract from document: {filename}\n\nText: {text[:3000]}"
    data = chat_json(settings.llm_base_url, settings.llm_api_key, settings.llm_model, SYSTEM, user)
    return {"doc_type": (data.get("doc_type") or "OTHER").upper(), "fields": data.get("fields", {}), "notes": ""}

def apply_rules(doc_type: str, fields: dict, rules: dict) -> List[str]:
    missing = []
    for req in required_fields_for(doc_type, rules):
        v = fields.get(req)
        if v is None or (isinstance(v, str) and not v.strip()):
            missing.append(req)
    return sorted(list(set(missing)))

def apply_cross_doc_checks(docs: List[DocResult], rules: dict) -> List[str]:
    findings = []
    checks = cross_doc_checks(rules)
    for chk in checks:
        field = chk.get("field")
        name = chk.get("name", field)
        values = [d.fields.get(field) for d in docs if d.fields.get(field)]
        if len(set(str(v) for v in values)) > 1:
            findings.append(f"{name}: inconsistent across documents")
    return findings

def run_vetting(paths: List[str], rules_path: str, settings) -> BatchResult:
    rules = load_rules(rules_path)
    documents: List[DocResult] = []
    findings: List[str] = []

    for path in paths:
        filename = os.path.basename(path)
        try:
            raw_text = extract_pdf_text(path, settings.max_chars_per_doc)
            send_text = redact(raw_text) if settings.redact_before_sending else raw_text
            llm_out = llm_classify_and_extract(send_text, filename, rules, settings)
            doc_type, fields = llm_out["doc_type"], llm_out["fields"]
        except Exception as e:
            doc_type, fields = "OTHER", {}
            findings.append(f"{filename}: error -> {str(e)[:100]}")
        
        missing = apply_rules(doc_type, fields, rules)
        documents.append(DocResult(filename=filename, doc_type=doc_type, fields=fields, missing_fields=missing, decision="NEEDS_REVIEW"))

    findings.extend(apply_cross_doc_checks(documents, rules))
    decision = "NEEDS_REVIEW"
    summary = "Vetting completed. Review findings and missing fields."
    report_path = os.path.join("outputs", "atlasza_vetting_report.pdf")
    render_pdf(report_path, decision, summary, findings, documents)

    return BatchResult(decision=decision, summary=summary, findings=findings, documents=documents, report_path=report_path)
