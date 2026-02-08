from fastapi import FastAPI, UploadFile, File, Form
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber

app = FastAPI(title="AI CV Filter API")

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def calculate_similarity(job_desc, cv_text):
    documents = [job_desc, cv_text]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=3000
    )
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(similarity[0][0] * 100, 2)

@app.get("/")
def root():
    return {"status": "AI CV Filter is running"}

@app.post("/filter-cv")
async def filter_cv(
    job_description: str = Form(...),
    cv_file: UploadFile = File(...)
):
    if not cv_file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    cv_text = extract_text_from_pdf(cv_file.file)

    if not cv_text:
        return {"error": "Cannot extract text from PDF"}

    match_score = calculate_similarity(job_description, cv_text)

    return {
        "cv_filename": cv_file.filename,
        "match_score_percent": match_score,
        "cv_text_preview": cv_text[:800]
    }
