import streamlit as st
import pandas as pd
import time
import os
import subprocess

st.set_page_config(
    page_title="Smart CV Ranker",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1rem; }

    /* Label badges */
    .label-good {
        background-color: #d4edda; color: #155724;
        padding: 4px 12px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem;
    }
    .label-potential {
        background-color: #fff3cd; color: #856404;
        padding: 4px 12px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem;
    }
    .label-bad {
        background-color: #f8d7da; color: #721c24;
        padding: 4px 12px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem;
    }

    /* Score bar */
    .score-bar-container {
        background: #e9ecef;
        border-radius: 10px;
        height: 22px;
        width: 100%;
        overflow: hidden;
    }
    .score-bar {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        transition: width 0.5s ease;
    }

    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
        border: 1px solid #f0f0f0;
    }
    .stat-card .stat-number { font-size: 2rem; font-weight: 700; }
    .stat-card .stat-label { font-size: 0.85rem; color: #666; margin-top: 4px; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="main-header">
    <h1>🧠 Smart CV Ranker</h1>
    <p>Hệ thống AI sàng lọc & xếp hạng CV thông minh dựa trên ngữ nghĩa</p>
</div>
""",
    unsafe_allow_html=True,
)


# ── Helpers ─────────────────────────────────────────────────────────────────
def _label_html(label: str) -> str:
    css = {
        "Phù hợp": "label-good",
        "Tiềm năng": "label-potential",
        "Không phù hợp": "label-bad",
    }
    cls = css.get(label, "label-bad")
    return f'<span class="{cls}">{label}</span>'


def _score_bar(score: float) -> str:
    if score >= 70:
        color = "#28a745"
    elif score >= 40:
        color = "#ffc107"
    else:
        color = "#dc3545"
    return (
        f'<div class="score-bar-container">'
        f'<div class="score-bar" style="width:{score}%;background:{color};">'
        f"{score}%</div></div>"
    )


# ── Sidebar: Cloudinary Config ──────────────────────────────────────────────
if "folder_path" not in st.session_state:
    st.session_state.folder_path = os.path.expanduser("~/Downloads/CVs")

# ── Folder Picker Logic (macOS Native) ──────────────────────────────────────
def select_folder_mac():
    """Opens a native macOS folder picker using AppleScript."""
    try:
        cmd = "osascript -e 'POSIX path of (choose folder with prompt \"Chọn thư mục chứa CV\")'"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if out:
            path = out.decode('utf-8').strip()
            st.session_state.folder_path = path
    except Exception as e:
        st.error(f"Không thể mở bảng chọn thư mục: {e}")

# ── Sidebar: Choose Folder ──────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Chọn thư mục chứa CV")
    
    col_path, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("📁 Browse"):
            select_folder_mac()
            
    with col_path:
        folder_path = st.text_input(
            "Đường dẫn thư mục", 
            value=st.session_state.folder_path,
            key="folder_input",
            help="Chọn hoặc nhập đường dẫn đầy đủ tới thư mục chứa file PDF."
        )
    
    # Update session state if user types manually
    st.session_state.folder_path = folder_path

    st.divider()
    st.header("⚙️ Cài đặt")
    threshold_good = st.slider("Ngưỡng 'Phù hợp' (%)", 50, 95, 70)
    threshold_potential = st.slider("Ngưỡng 'Tiềm năng' (%)", 20, 60, 40)

    st.divider()
    connect_btn = st.button(
        "📁 Quét Thư Mục CV", use_container_width=True, type="primary"
    )


# ── Session State ───────────────────────────────────────────────────────────
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "results" not in st.session_state:
    st.session_state.results = []
if "scan_done" not in st.session_state:
    st.session_state.scan_done = False


# ── Scan Cloudinary ─────────────────────────────────────────────────────────
if connect_btn:
    if not st.session_state.folder_path:
        st.sidebar.error("⚠️ Vui lòng chọn hoặc nhập đường dẫn thư mục!")
    else:
        with st.spinner("Đang quét thư mục & tải CV..."):
            try:
                from local_service import scan_local_pdfs
                from config import Config
                import os

                # Update thresholds
                Config.THRESHOLD_GOOD = threshold_good
                Config.THRESHOLD_POTENTIAL = threshold_potential

                progress_bar = st.progress(0, text="Đang bắt đầu quét...")

                def update_progress(current, total):
                    progress_bar.progress(
                        current / total,
                        text=f"Đang xử lý {current}/{total} CV...",
                    )
                
                # Expand path in case of ~/
                full_path = os.path.expanduser(st.session_state.folder_path)

                if not os.path.exists(full_path) or not os.path.isdir(full_path):
                     st.error(f"❌ Đường dẫn không hợp lệ hoặc không phải là thư mục: {full_path}")
                else:
                    candidates = scan_local_pdfs(full_path, progress_callback=update_progress)
                    
                    if not candidates:
                        st.warning(f"Không tìm thấy file PDF nào hoặc không thể trích xuất văn bản trong '{full_path}'.")
                    else:
                        st.session_state.candidates = candidates
                        st.session_state.scan_done = True
                        st.success(
                            f"✅ Đã tải thành công "
                            f"**{len(candidates)}** CV từ thư mục nội bộ!"
                        )
                
                progress_bar.empty()
            except Exception as e:
                st.error(f"❌ Lỗi xử lý: {e}")


# ── Main Area ───────────────────────────────────────────────────────────────
col_jd, col_status = st.columns([3, 1])

with col_jd:
    st.subheader("📝 Mô tả công việc (JD)")
    jd_text = st.text_area(
        "Dán nội dung mô tả công việc tại đây",
        height=200,
        placeholder=(
            "Ví dụ: Tuyển dụng lập trình viên Python 3 năm kinh nghiệm, "
            "thành thạo Django, REST API, PostgreSQL. Ưu tiên ứng viên "
            "có kinh nghiệm Docker, CI/CD..."
        ),
    )

with col_status:
    st.subheader("📊 Trạng thái")
    n_loaded = len(st.session_state.candidates)
    st.markdown(
        f"""
    <div class="stat-card">
        <div class="stat-number">{n_loaded}</div>
        <div class="stat-label">CV đã tải</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ── Analyze Button ──────────────────────────────────────────────────────────
st.divider()
analyze_btn = st.button(
    "🚀 Phân tích & Xếp hạng",
    use_container_width=True,
    type="primary",
    disabled=(not st.session_state.scan_done or not jd_text),
)

if analyze_btn:
    if not jd_text.strip():
        st.error("⚠️ Vui lòng nhập mô tả công việc!")
    elif not st.session_state.candidates:
        st.error("⚠️ Chưa có CV nào được quét. Hãy chọn thư mục và quét CV trước!")
    else:
        with st.spinner("🧠 AI đang phân tích CV..."):
            try:
                from ai_engine import SmartCVEngine
                from config import Config

                Config.THRESHOLD_GOOD = threshold_good
                Config.THRESHOLD_POTENTIAL = threshold_potential

                engine = SmartCVEngine()
                start_time = time.time()
                results = engine.rank_candidates(
                    jd_text, st.session_state.candidates
                )
                elapsed = round(time.time() - start_time, 2)

                st.session_state.results = results
                st.success(
                    f"✅ Phân tích hoàn tất trong **{elapsed}s** — "
                    f"**{len(results)}** ứng viên được xếp hạng."
                )
            except Exception as e:
                st.error(f"❌ Lỗi phân tích: {e}")


# ── Results Display ─────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results

    st.subheader("🏆 Bảng xếp hạng ứng viên")

    # Stats row
    n_good = sum(1 for r in results if r["label"] == "Phù hợp")
    n_potential = sum(1 for r in results if r["label"] == "Tiềm năng")
    n_bad = sum(1 for r in results if r["label"] == "Không phù hợp")
    avg_score = round(sum(r["score"] for r in results) / len(results), 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number" '
            f'style="color:#28a745">{n_good}</div>'
            f'<div class="stat-label">Phù hợp</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number" '
            f'style="color:#ffc107">{n_potential}</div>'
            f'<div class="stat-label">Tiềm năng</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number" '
            f'style="color:#dc3545">{n_bad}</div>'
            f'<div class="stat-label">Không phù hợp</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number" '
            f'style="color:#667eea">{avg_score}%</div>'
            f'<div class="stat-label">Điểm TB</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Results table
    for r in results:
        with st.container():
            cols = st.columns([0.5, 3, 2, 2, 1.5])
            with cols[0]:
                st.markdown(f"**#{r['rank']}**")
            with cols[1]:
                st.markdown(f"📄 **{r['filename']}**")
            with cols[2]:
                st.markdown(_score_bar(r["score"]), unsafe_allow_html=True)
            with cols[3]:
                st.markdown(_label_html(r["label"]), unsafe_allow_html=True)
            with cols[4]:
                st.link_button("Xem CV ↗", r["url"], use_container_width=True)

            with st.expander("Xem trước nội dung CV"):
                st.text(r.get("cv_text_preview", "Không có dữ liệu"))
            st.divider()

    # Download CSV
    df = pd.DataFrame(
        [
            {
                "Hạng": r["rank"],
                "Tên file": r["filename"],
                "Điểm (%)": r["score"],
                "Nhãn": r["label"],
                "URL": r["url"],
            }
            for r in results
        ]
    )
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Tải kết quả CSV",
        csv,
        "cv_ranking_results.csv",
        "text/csv",
        use_container_width=True,
    )
