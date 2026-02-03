# AtlasZA Document Vetter (KYC/KYB/AML + Commodities)

Local-first vetting tool to classify and review business compliance and commodity transaction documents:
- KYC (company)
- KYB (company)
- AML Declarations
- Sales Contracts
- Export Permits
- Other supporting PDFs

## What it does
1. Extracts text from PDFs locally
2. (Hybrid mode) Sends redacted text to an external LLM to:
   - classify doc type
   - extract key fields
3. Runs checklist rules + cross-document consistency checks
4. Produces a PDF report with findings

Default outcome: **NEEDS_REVIEW** (MVP behavior).

## Quick start (Mac)
### 1) Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment
```bash
cp .env.example .env
# edit .env and set LLM_API_KEY
```

### 3) Run the app
```bash
streamlit run app.py
```

Open the local URL Streamlit prints in your terminal.

## Rules / Checklists
Edit: `rules/za_default.yaml`
You can add required fields per document type and cross-document checks.

## Notes / Roadmap
- Add OCR for scanned PDFs
- Add DOCX and image support
- Add sanctions/PEP screening hooks
- Add structured JSON export for internal systems
- Better redaction + audit logs
