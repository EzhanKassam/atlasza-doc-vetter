import os
import uuid
import streamlit as st
from vetter.config import load_settings
from vetter.pipeline import run_vetting

st.set_page_config(page_title="AtlasZA Document Vetter", layout="wide")

settings = load_settings()

st.title("AtlasZA – KYC/KYB/AML + Commodities Document Vetter")
st.caption("Runs locally. Hybrid mode: local extraction + optional external AI for classification/extraction.")

with st.expander("Settings (read-only)", expanded=False):
    st.write({
        "LLM_PROVIDER": settings.llm_provider,
        "LLM_MODEL": settings.llm_model,
        "REDACT_BEFORE_SENDING": settings.redact_before_sending,
        "MAX_CHARS_PER_DOC": settings.max_chars_per_doc
    })

uploaded = st.file_uploader(
    "Upload PDF documents",
    type=["pdf"],
    accept_multiple_files=True
)

run_btn = st.button("Run Vetting", type="primary", disabled=not uploaded)

if run_btn:
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    batch_id = str(uuid.uuid4())[:8]
    batch_dir = os.path.join("uploads", batch_id)
    os.makedirs(batch_dir, exist_ok=True)

    paths = []
    for f in uploaded:
        path = os.path.join(batch_dir, f.name)
        with open(path, "wb") as out:
            out.write(f.getbuffer())
        paths.append(path)

    with st.spinner("Extracting, classifying, checking rules, generating PDF report..."):
        result = run_vetting(paths, rules_path="rules/za_default.yaml", settings=settings)

    st.subheader("Outcome")
    st.success(f"Decision: {result.decision}")
    st.write(result.summary)

    st.subheader("Flags / Findings")
    if result.findings:
        for item in result.findings:
            st.warning(item)
    else:
        st.write("No findings.")

    st.subheader("Per-document results")
    for doc in result.documents:
        with st.expander(f"{doc.filename} — {doc.doc_type} — {doc.decision}", expanded=False):
            st.write("Missing fields:", doc.missing_fields or "None")
            st.write("Extracted fields:")
            st.json(doc.fields)

    st.subheader("PDF Report")
    st.write("Download the generated report:")
    with open(result.report_path, "rb") as f:
        st.download_button(
            label="Download PDF report",
            data=f,
            file_name=os.path.basename(result.report_path),
            mime="application/pdf"
        )
