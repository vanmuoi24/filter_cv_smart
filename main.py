from fastapi import FastAPI, UploadFile, File, Form
from pdf_extractor import extract_text_from_pdf
from ai_engine import SmartCVEngine

app = FastAPI(title="AI Smart CV Ranker API")

# Load AI engine at startup
engine = SmartCVEngine()


@app.get("/")
def root():
    return {"status": "Smart CV Ranker API is running"}


@app.post("/filter-cv")
async def filter_cv(
    job_description: str = Form(...),
    cv_file: UploadFile = File(...),
):
    """Filter a single CV against a job description using AI semantic matching."""
    if not cv_file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    cv_bytes = await cv_file.read()
    cv_text = extract_text_from_pdf(cv_bytes)

    if not cv_text:
        return {"error": "Cannot extract text from PDF"}

    match_score = engine.calculate_similarity(job_description, cv_text)

    from config import Config

    return {
        "cv_filename": cv_file.filename,
        "match_score_percent": match_score,
        "label": Config.get_label(match_score),
        "cv_text_preview": cv_text[:800],
    }
