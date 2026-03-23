import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
from config import Config


class SmartCVEngine:
    """AI Semantic Engine using Sentence Embeddings for CV-JD matching."""

    def __init__(self):
        print("[AI Engine] Initializing TF-IDF Vectorizer...")
        self.vectorizer = TfidfVectorizer(
            stop_words=None,  # Or add 'english' if needed, but project is multilingual
            token_pattern=r"(?u)\b\w\w+\b",
        )
        print("[AI Engine] TF-IDF Engine ready.")

    def encode_text(self, text: str) -> np.ndarray:
        """Convert text to a semantic vector embedding."""
        return self.model.encode(text, show_progress_bar=False)

    def calculate_similarity(self, jd_text: str, cv_text: str) -> float:
        """
        Calculate cosine similarity between JD and CV texts.

        Returns:
            Score as a percentage (0-100).
        """
        jd_vector = self.encode_text(jd_text).reshape(1, -1)
        cv_vector = self.encode_text(cv_text).reshape(1, -1)
        similarity = sklearn_cosine(jd_vector, cv_vector)[0][0]
        return round(float(similarity) * 100, 2)

    def rank_candidates(
        self, jd_text: str, candidates: list[dict]
    ) -> list[dict]:
        """
        Rank candidates against a JD using TF-IDF.
        """
        if not candidates:
            return []

        # Combine JD and all CV texts for the corpus to compute IDF properly
        cv_texts = [c["cv_text"] for c in candidates]
        corpus = [jd_text] + cv_texts

        # Fit and transform the entire corpus
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        # JD is the first row, CVs are the rest
        jd_vector = tfidf_matrix[0:1]
        cv_vectors = tfidf_matrix[1:]

        # Calculate cosine similarities
        similarities = sklearn_cosine(jd_vector, cv_vectors)[0]

        results = []
        for i, candidate in enumerate(candidates):
            score = round(float(similarities[i]) * 100, 2)
            results.append(
                {
                    "filename": candidate["filename"],
                    "url": candidate.get("url", ""),
                    "score": score,
                    "label": Config.get_label(score),
                    "cv_text_preview": candidate["cv_text"][:500],
                }
            )

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)

        # Add rank
        for i, r in enumerate(results):
            r["rank"] = i + 1

        return results
