import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration for Smart CV Ranker."""

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
    CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "cv_uploads")

    # AI Model
    AI_MODEL_NAME = os.getenv(
        "AI_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Scoring thresholds (%)
    THRESHOLD_GOOD = int(os.getenv("THRESHOLD_GOOD", "70"))
    THRESHOLD_POTENTIAL = int(os.getenv("THRESHOLD_POTENTIAL", "40"))

    # Performance
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "5"))

    # Cache
    CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

    @classmethod
    def get_label(cls, score: float) -> str:
        """Return a Vietnamese label based on the match score."""
        if score >= cls.THRESHOLD_GOOD:
            return "Phù hợp"
        elif score >= cls.THRESHOLD_POTENTIAL:
            return "Tiềm năng"
        else:
            return "Không phù hợp"

    @classmethod
    def ensure_cache_dir(cls):
        """Create cache directory if it doesn't exist."""
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
