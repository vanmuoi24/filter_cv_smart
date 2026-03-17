# 🧠 Smart CV Ranker

Hệ thống AI sàng lọc & xếp hạng CV thông minh dựa trên ngữ nghĩa.

## Tính năng

- **AI Semantic Matching**: Sử dụng mô hình `paraphrase-multilingual-MiniLM-L12-v2` để hiểu ngữ nghĩa đa ngôn ngữ
- **Cloudinary Integration**: Tự động quét và tải CV (PDF) từ Cloudinary
- **Streamlit Dashboard**: Giao diện web trực quan với bảng xếp hạng
- **Multi-threading**: Tải song song nhiều CV để tăng tốc
- **Caching**: Lưu cache text đã trích xuất để không phải scan lại
- **Auto-labeling**: Gắn nhãn "Phù hợp" / "Tiềm năng" / "Không phù hợp"

## Cài đặt

```bash
# Clone & di chuyển vào thư mục
cd filter_cv_smart

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Cài đặt thư viện
pip install -r requirements.txt
```

## Cấu hình

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Cập nhật thông tin Cloudinary trong `.env`:

```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_FOLDER=cv_uploads
```

## Chạy ứng dụng

### Streamlit Dashboard (Recommended)

```bash
streamlit run app.py
```

Truy cập: http://localhost:8501

### FastAPI (Alternative)

```bash
uvicorn main:app --reload
```

Truy cập: http://localhost:8000/docs

## Kiến trúc

```
filter_cv_smart/
├── app.py                  # Streamlit dashboard
├── main.py                 # FastAPI API (alternative)
├── config.py               # Configuration & env vars
├── pdf_extractor.py        # PDF text extraction (pdfplumber)
├── ai_engine.py            # AI Sentence Embedding engine
├── cloudinary_service.py   # Cloudinary integration + caching
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
└── cache/                  # Auto-generated text cache
```

## Công nghệ

| Component | Technology |
|-----------|-----------|
| AI Model | `paraphrase-multilingual-MiniLM-L12-v2` |
| PDF Parser | `pdfplumber` |
| Cloud Storage | Cloudinary SDK |
| Web UI | Streamlit |
| API | FastAPI |
