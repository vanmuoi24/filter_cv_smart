import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
from config import Config


class SmartCVEngine:
    """AI Semantic Engine using Sentence Embeddings for CV-JD matching."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.AI_MODEL_NAME
        print(f"[AI Engine] Loading model: {self.model_name} ...")
        self.model = SentenceTransformer(self.model_name)
        print("[AI Engine] Model loaded successfully.")

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
        Rank a list of candidates against a JD.

        Args:
            jd_text: The job description text.
            candidates: List of dicts with keys: 'filename', 'cv_text', 'url'.

        Returns:
            Sorted list (highest score first) with added 'score' and 'label'.
        """
        if not candidates:
            return []

        # Encode JD once
        jd_vector = self.encode_text(jd_text).reshape(1, -1)

        # Encode all CVs in batch for performance
        cv_texts = [c["cv_text"] for c in candidates]
        cv_vectors = self.model.encode(cv_texts, show_progress_bar=False)

        # Calculate similarities
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
