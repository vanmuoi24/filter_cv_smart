import os
from pathlib import Path
from pdf_extractor import extract_text_from_pdf

def scan_local_pdfs(folder_path, progress_callback=None):
    """
    Scans a local directory for PDF files and extracts text from them.

    Args:
        folder_path (str): The path to the directory containing PDFs.
        progress_callback (callable, optional): A function to call with (current, total)
                                                to report progress.

    Returns:
        list[dict]: A list of candidates with filename, cv_text, and url (local path).
    """
    candidates = []
    
    # Expand user path (e.g., ~/)
    folder = Path(folder_path).expanduser()
    
    if not folder.exists() or not folder.is_dir():
        print(f"[Local Scanner] Error: Directory '{folder_path}' does not exist.")
        return candidates

    pdf_files = list(folder.glob("*.pdf"))
    total_files = len(pdf_files)
    
    if total_files == 0:
        print(f"[Local Scanner] No PDF files found in '{folder_path}'.")
        return candidates

    print(f"[Local Scanner] Found {total_files} PDF files. Starting extraction...")

    for index, pdf_path in enumerate(pdf_files):
        try:
            # Extract text
            text = extract_text_from_pdf(pdf_path)
            
            # Add to candidates only if text was found
            if text.strip():
                candidates.append({
                    "filename": pdf_path.name,
                    "cv_text": text,
                    "url": str(pdf_path.absolute()) # Storing local path as URL
                })
            else:
                print(f"[Local Scanner] Warning: No text extracted from {pdf_path.name}")
        
        except Exception as e:
            print(f"[Local Scanner] Failed to process {pdf_path.name}: {e}")

        # Update progress
        if progress_callback:
            progress_callback(index + 1, total_files)

    print(f"[Local Scanner] Completed. Extracted {len(candidates)} CVs.")
    return candidates
