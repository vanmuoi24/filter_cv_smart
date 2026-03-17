import os
import hashlib
import json
import requests
import cloudinary
import cloudinary.api
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import Config
from pdf_extractor import extract_text_from_pdf


def configure_cloudinary(
    cloud_name: str = None,
    api_key: str = None,
    api_secret: str = None,
):
    """Initialize Cloudinary SDK with credentials."""
    cloudinary.config(
        cloud_name=cloud_name or Config.CLOUDINARY_CLOUD_NAME,
        api_key=api_key or Config.CLOUDINARY_API_KEY,
        api_secret=api_secret or Config.CLOUDINARY_API_SECRET,
        secure=True,
    )


def list_pdf_files(folder: str = None) -> list[dict]:
    """
    List all PDF files in a Cloudinary folder.

    Returns:
        List of dicts with keys: 'public_id', 'url', 'filename'.
    """
    folder = folder or Config.CLOUDINARY_FOLDER
    results = []

    try:
        response = cloudinary.api.resources(
            type="upload",
            prefix=folder,
            resource_type="raw",
            max_results=500,
        )

        for resource in response.get("resources", []):
            public_id = resource["public_id"]
            url = resource["secure_url"]
            filename = public_id.split("/")[-1]

            if filename.lower().endswith(".pdf"):
                results.append(
                    {
                        "public_id": public_id,
                        "url": url,
                        "filename": filename,
                    }
                )
    except Exception as e:
        print(f"[Cloudinary] Error listing files: {e}")

    return results


def _get_cache_path(public_id: str) -> str:
    """Get the cache file path for a given public_id."""
    Config.ensure_cache_dir()
    hashed = hashlib.md5(public_id.encode()).hexdigest()
    return os.path.join(Config.CACHE_DIR, f"{hashed}.json")


def _load_from_cache(public_id: str) -> str | None:
    """Load extracted text from cache if available."""
    cache_path = _get_cache_path(public_id)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("text")
        except Exception:
            pass
    return None


def _save_to_cache(public_id: str, text: str):
    """Save extracted text to cache."""
    cache_path = _get_cache_path(public_id)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(
                {"public_id": public_id, "text": text}, f, ensure_ascii=False
            )
    except Exception as e:
        print(f"[Cache] Error saving cache: {e}")


def download_and_extract(pdf_info: dict) -> dict | None:
    """
    Download a single PDF from Cloudinary and extract its text.
    Uses cache if available.

    Args:
        pdf_info: Dict with 'public_id', 'url', 'filename'.

    Returns:
        Dict with 'filename', 'url', 'cv_text', or None on failure.
    """
    public_id = pdf_info["public_id"]
    filename = pdf_info["filename"]
    url = pdf_info["url"]

    # Check cache first
    cached_text = _load_from_cache(public_id)
    if cached_text:
        print(f"[Cache] Hit for: {filename}")
        return {
            "filename": filename,
            "url": url,
            "cv_text": cached_text,
        }

    # Download from Cloudinary
    try:
        print(f"[Download] Downloading: {filename} ...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        pdf_bytes = response.content
    except Exception as e:
        print(f"[Download] Error downloading {filename}: {e}")
        return None

    # Extract text
    text = extract_text_from_pdf(pdf_bytes)
    if not text:
        print(f"[Extract] No text extracted from: {filename}")
        return None

    # Save to cache
    _save_to_cache(public_id, text)

    return {
        "filename": filename,
        "url": url,
        "cv_text": text,
    }


def download_all_pdfs(
    pdf_list: list[dict],
    max_workers: int = None,
    progress_callback=None,
) -> list[dict]:
    """
    Download and extract text from all PDFs using multi-threading.

    Args:
        pdf_list: List of dicts from list_pdf_files().
        max_workers: Number of parallel threads.
        progress_callback: Optional callable(current, total) for progress.

    Returns:
        List of dicts with 'filename', 'url', 'cv_text'.
    """
    max_workers = max_workers or Config.MAX_WORKERS
    results = []
    total = len(pdf_list)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pdf = {
            executor.submit(download_and_extract, pdf): pdf
            for pdf in pdf_list
        }

        for i, future in enumerate(as_completed(future_to_pdf), 1):
            result = future.result()
            if result:
                results.append(result)

            if progress_callback:
                progress_callback(i, total)

    print(
        f"[Cloudinary] Successfully processed {len(results)}/{total} PDFs."
    )
    return results
