import time
from collections import defaultdict

import requests
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Interview Prep",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .block-container { padding: 1.5rem 2rem; }
    h1, h2, h3 { color: #f0f0f0; }
    .card {
        background: #1a1d27; border: 1px solid #2c2f3a; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1.2rem;
    }
    .card-title { font-size: 1.25rem; font-weight: 600; color: #e0e0e0; margin-bottom: 0.5rem; }
    .card-label { font-size: 0.8rem; color: #8b8fa3; text-transform: uppercase; letter-spacing: 0.5px; }
    .card-value { font-size: 1rem; color: #f0f0f0; }
    .stat-box {
        background: #1a1d27; border: 1px solid #2c2f3a; border-radius: 12px;
        padding: 1.2rem; text-align: center;
    }
    .stat-number { font-size: 1.8rem; font-weight: 700; color: #7c8cff; }
    .stat-label { font-size: 0.8rem; color: #8b8fa3; }
    .feedback-good { border-left: 4px solid #2ecc71; }
    .feedback-miss { border-left: 4px solid #e67e22; }
    .stTextArea textarea {
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        background: #0e1117; color: #e0e0e0; border: 1px solid #2c2f3a;
        border-radius: 8px; font-size: 0.9rem;
    }
    .stButton > button {
        border-radius: 8px; font-weight: 500; padding: 0.4rem 1.2rem;
        border: none; transition: all 0.2s;
    }
    .stButton > button:hover { transform: translateY(-1px); opacity: 0.9; }
    div[data-testid="stSidebar"] {
        background: #0e1117; border-right: 1px solid #1e2030;
    }
    hr { border-color: #2c2f3a; margin: 1.5rem 0; }
    a { color: #7c8cff; }
    .stSelectbox > div > div {
        background: #1a1d27; border: 1px solid #2c2f3a; border-radius: 8px; color: #e0e0e0;
    }
    .timer-card {
        background: #1a1d27; border: 2px solid #7c8cff; border-radius: 12px;
        padding: 0.8rem 1.5rem; text-align: center; margin-bottom: 1rem;
    }
    .timer-text { font-size: 2rem; font-weight: 700; color: #7c8cff; font-family: monospace; }
    .metric-green { color: #2ecc71; font-weight: 700; }
    .metric-red { color: #e74c3c; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Session State ───────────────────────────────────────────────────────────

defaults = {
    "page": "Home",
    "questions": [],
    "current_question": None,
    "user_code": "",
    "feedback": None,
    "hint": None,
    "solution": None,
    "history": [],
    "user_id": "guest",
    "selected_topic": "arrays",
    "selected_difficulty": "medium",
    "stats": {"attempted": 0, "avg_score": 0, "total_scores": []},
    "mock_questions": [],
    "mock_answers": {},
    "mock_start_time": None,
    "mock_submitted": False,
    "questions_loaded": False,
    "history_loaded": False,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def qid(q: dict) -> str:
    return q.get("id") or q.get("_id") or ""


def api_get(path: str) -> dict | list | None:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None


def api_post(path: str, payload: dict) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None


def fetch_questions(topic=None, difficulty=None):
    t = topic or st.session_state.selected_topic
    d = difficulty or st.session_state.selected_difficulty
    url = f"/questions/?topic={t}&difficulty={d}"
    with st.spinner("Loading questions\u2026"):
        data = api_get(url)
    if data is not None:
        st.session_state.questions = data if isinstance(data, list) else []
        st.session_state.questions_loaded = True
    else:
        st.warning("API returned no data.")


def pick_question(q):
    st.session_state.current_question = q
    st.session_state.user_code = ""
    st.session_state.feedback = None
    st.session_state.hint = None
    st.session_state.solution = None
    st.session_state.page = "Practice"


def render_question_card(q: dict):
    st.markdown(f'<div class="card-title">{q.get("title", "")}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<span style="display:inline-block;background:#2c2f3a;border-radius:6px;padding:0.1rem 0.6rem;font-size:0.75rem;margin-right:0.4rem;">{q.get("difficulty", "").upper()}</span>'
        f'<span style="display:inline-block;background:#2c2f3a;border-radius:6px;padding:0.1rem 0.6rem;font-size:0.75rem;">{q.get("topic", "").replace("_", " ").title()}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="card"><div class="card-label">Description</div><div class="card-value">{q.get("description", "")}</div></div>',
        unsafe_allow_html=True,
    )
    if q.get("constraints"):
        st.markdown(
            f'<div class="card"><div class="card-label">Constraints</div><div class="card-value">{q["constraints"]}</div></div>',
            unsafe_allow_html=True,
        )
    ex_in = q.get("example_input")
    ex_out = q.get("example_output")
    if ex_in or ex_out:
        ex_html = '<div class="card"><div class="card-label">Example</div><div class="card-value">'
        if ex_in:
            ex_html += f"<b>Input:</b> {ex_in}<br>"
        if ex_out:
            ex_html += f"<b>Output:</b> {ex_out}"
        ex_html += "</div></div>"
        st.markdown(ex_html, unsafe_allow_html=True)


def save_session(question_id, topic, score):
    uid = st.session_state.user_id
    api_post(
        f"/history/{uid}?topic={topic}&question_id={question_id}&score={score}",
        {},
    )

def load_history():
    uid = st.session_state.user_id
    data = api_get(f"/history/{uid}")
    if data and isinstance(data, list) and len(data):
        st.session_state.history = [
            {
                "question": s.get("question_id", ""),
                "score": s.get("score", 0),
                "topic": s.get("topic", "unknown"),
                "timestamp": s.get("timestamp", ""),
            }
            for s in data
        ]
        scores = [h["score"] for h in st.session_state.history]
        st.session_state.stats["attempted"] = len(scores)
        st.session_state.stats["total_scores"] = scores
        st.session_state.stats["avg_score"] = round(sum(scores) / len(scores), 1) if scores else 0
    st.session_state.history_loaded = True

def handle_feedback(q_id: str):
    code = st.session_state.user_code.strip()
    if not code:
        st.warning("Please write some code before submitting.")
        return
    payload = {"question_id": q_id, "user_code": code, "language": "python"}
    with st.spinner("Evaluating your solution\u2026"):
        data = api_post("/feedback/", payload)
    if data:
        st.session_state.feedback = data
        st.session_state.stats["attempted"] += 1
        score = 0
        fb = data.get("feedback", "")
        for line in fb.split("\n"):
            if "rating" in line.lower() and "10" in line.lower():
                try:
                    score = int([c for c in line if c.isdigit()][0]) * 10
                except (IndexError, ValueError):
                    score = 0
        st.session_state.stats["total_scores"].append(score)
        if st.session_state.stats["total_scores"]:
            st.session_state.stats["avg_score"] = round(
                sum(st.session_state.stats["total_scores"])
                / len(st.session_state.stats["total_scores"]),
                1,
            )
        topic = (st.session_state.current_question.get("topic", "unknown")
                 if st.session_state.current_question else "unknown")
        st.session_state.history.append(
            {
                "question": q_id,
                "score": score,
                "topic": topic,
                "timestamp": time.strftime("%Y-%m-%d %H:%M"),
            }
        )
        save_session(q_id, topic, score)
        st.success("Feedback received!")


def handle_hint(q_id: str):
    code = st.session_state.user_code.strip()
    payload = {"question_id": q_id, "user_code": code or None}
    with st.spinner("Generating hint\u2026"):
        data = api_post(f"/questions/{q_id}/hint", payload)
    if data:
        st.session_state.hint = data["hint"]


def handle_solution(q_id: str):
    payload = {"question_id": q_id, "language": "python"}
    with st.spinner("Generating solution\u2026"):
        data = api_post(f"/questions/{q_id}/solution", payload)
    if data:
        st.session_state.solution = data["solution_code"]


# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>&#9889; Interview Prep</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigation")

    if st.button("\U0001f3e0 Home", use_container_width=True):
        st.session_state.page = "Home"; st.rerun()
    if st.button("\U0001f4dd Practice", use_container_width=True):
        st.session_state.page = "Practice"; st.rerun()
    if st.button("\U0001f4c8 Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"; st.rerun()
    if st.button("\U0001f3af Mock Interview", use_container_width=True):
        st.session_state.page = "Mock Interview"; st.rerun()
    if st.button("\U0001f4ca History", use_container_width=True):
        st.session_state.page = "History"; st.rerun()

    st.markdown("---")
    st.markdown("### Settings")
    topic = st.selectbox(
        "Topic",
        ["arrays", "strings", "trees", "graphs", "dynamic_programming"],
        index=["arrays", "strings", "trees", "graphs", "dynamic_programming"].index(
            st.session_state.get("selected_topic", "arrays")
        ),
        key="sb_topic",
    )
    diff = st.selectbox(
        "Difficulty",
        ["easy", "medium", "hard"],
        index=["easy", "medium", "hard"].index(
            st.session_state.get("selected_difficulty", "medium")
        ),
        key="sb_difficulty",
    )
    st.session_state.selected_topic = topic
    st.session_state.selected_difficulty = diff

    if st.button("\U0001f504 Refresh Questions", use_container_width=True):
        fetch_questions()
        st.session_state.page = "Home"
        st.rerun()

    st.markdown("---")
    s = st.session_state.stats
    st.markdown(
        f'<div class="stat-box"><div class="stat-number">{s["attempted"]}</div><div class="stat-label">Attempted</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="stat-box"><div class="stat-number">{s["avg_score"]}</div><div class="stat-label">Avg Score</div></div>',
        unsafe_allow_html=True,
    )

# ─── PAGES ───────────────────────────────────────────────────────────────────

page = st.session_state.page

# ====================== HOME ======================

if page == "Home":
    if not st.session_state.history_loaded:
        load_history()
    if not st.session_state.questions_loaded and not st.session_state.questions:
        topic = st.session_state.selected_topic
        with st.spinner("Loading questions\u2026"):
            data = api_get(f"/questions/?topic={topic}")
        if data is not None:
            st.session_state.questions = data if isinstance(data, list) else []
            st.session_state.questions_loaded = True

    col1, col2, col3 = st.columns(3)
    s = st.session_state.stats
    with col1:
        st.markdown(
            f'<div class="stat-box"><div class="stat-number">{s["attempted"]}</div><div class="stat-label">Questions Attempted</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="stat-box"><div class="stat-number">{s["avg_score"]}</div><div class="stat-label">Average Score</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="stat-box"><div class="stat-number">{len(st.session_state.history)}</div><div class="stat-label">Sessions Saved</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("## \U0001f680 Start Practicing")
    st.markdown("Pick a topic to get started:")

    topics = [
        ("Arrays", "arrays"),
        ("Strings", "strings"),
        ("Trees", "trees"),
        ("Graphs", "graphs"),
        ("DP", "dynamic_programming"),
    ]
    cols = st.columns(5)
    for i, (label, val) in enumerate(topics):
        with cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.selected_topic = val
                st.session_state.selected_difficulty = "medium"
                fetch_questions()
                if st.session_state.questions:
                    pick_question(st.session_state.questions[0])
                else:
                    st.session_state.page = "Practice"
                st.rerun()

    if st.session_state.questions:
        st.markdown("### \U0001f4c2 Recently Loaded Questions")
        cols_q = st.columns(2)
        for idx, q in enumerate(st.session_state.questions[:6]):
            with cols_q[idx % 2]:
                title = q.get("title", "Untitled")
                diff = q.get("difficulty", "").upper()
                top = q.get("topic", "").replace("_", " ").title()
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-title">{title}</div>'
                    f'<div class="card-value" style="font-size:0.85rem;color:#8b8fa3;">{diff} \u00b7 {top}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if st.button(f"Solve \u2192", key=f"home_q_{idx}"):
                    pick_question(q)
                    st.rerun()

# ====================== PRACTICE ======================

elif page == "Practice":
    q = st.session_state.current_question
    st.markdown("## \U0001f4dd Practice")

    if not q:
        st.markdown(
            '<div class="card"><div class="card-title">No question selected</div>'
            '<div class="card-value">Use the sidebar to select a topic & difficulty, then click a question from the Home page.</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("\u2190 Back to Home"):
            st.session_state.page = "Home"; st.rerun()
    else:
        render_question_card(q)

        st.markdown("### \u270d\ufe0f Your Solution")
        code = st.text_area(
            "Code editor",
            value=st.session_state.user_code,
            height=220,
            placeholder="def solution(...):\n    # Write your code here",
            label_visibility="collapsed",
            key="code_editor",
        )
        st.session_state.user_code = code

        q_id = qid(q)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("\U0001f4a1 Get Hint", use_container_width=True):
                handle_hint(q_id)
        with col_b:
            if st.button("\u2705 Submit Answer", use_container_width=True, type="primary"):
                handle_feedback(q_id)
        with col_c:
            if st.button("\U0001f4d6 View Solution", use_container_width=True):
                handle_solution(q_id)

        if st.session_state.hint:
            st.markdown(
                f'<div class="card feedback-good"><div class="card-title">\U0001f4a1 Hint</div>'
                f'<div class="card-value">{st.session_state.hint}</div></div>',
                unsafe_allow_html=True,
            )

        if st.session_state.solution:
            st.markdown(
                f'<div class="card"><div class="card-title">\U0001f4d6 Model Solution</div>'
                f'<pre style="background:#0e1117;padding:1rem;border-radius:8px;overflow-x:auto;font-size:0.85rem;">{st.session_state.solution}</pre></div>',
                unsafe_allow_html=True,
            )

        fb = st.session_state.feedback
        if fb:
            fb_text = fb.get("feedback", "")
            score_str = ""
            for line in fb_text.split("\n"):
                if line.strip().lower().startswith(("3.", "rating")):
                    score_str = line.strip()
            st.markdown(
                f'<div class="card feedback-good"><div class="card-title">\u2705 Feedback</div>'
                f'<div class="card-value">{fb_text}</div></div>',
                unsafe_allow_html=True,
            )
            if score_str:
                st.markdown(
                    f'<div class="card feedback-miss"><div class="card-title">\U0001f4ca Score</div>'
                    f'<div class="card-value">{score_str}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        if st.button("\u2190 Back to Home"):
            st.session_state.page = "Home"; st.rerun()

# ====================== DASHBOARD ======================

elif page == "Dashboard":
    st.markdown("## \U0001f4c8 Progress Dashboard")

    history = st.session_state.history
    s = st.session_state.stats

    if not history:
        st.markdown(
            '<div class="card"><div class="card-title">No data yet</div>'
            '<div class="card-value">Complete practice sessions to see your progress here.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        # Metric cards
        best = max(s["total_scores"]) if s["total_scores"] else 0

        # Find weakest topic
        topic_scores = defaultdict(list)
        for h in history:
            t = h.get("topic", "unknown")
            topic_scores[t].append(h.get("score", 0))
        topic_avg = {t: sum(v)/len(v) for t, v in topic_scores.items()}
        weakest = min(topic_avg, key=topic_avg.get) if topic_avg else "N/A"
        weakest_score = topic_avg.get(weakest, 0)

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.markdown(
                f'<div class="stat-box"><div class="stat-number">{s["attempted"]}</div><div class="stat-label">Total Attempted</div></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f'<div class="stat-box"><div class="stat-number">{s["avg_score"]}</div><div class="stat-label">Average Score</div></div>',
                unsafe_allow_html=True,
            )
        with col_c:
            st.markdown(
                f'<div class="stat-box"><div class="stat-number">{best}</div><div class="stat-label">Best Score</div></div>',
                unsafe_allow_html=True,
            )
        with col_d:
            st.markdown(
                f'<div class="stat-box"><div class="stat-number" style="color:#e74c3c;">{weakest_score:.0f}</div><div class="stat-label">Weakest: {weakest.replace("_"," ").title()}</div></div>',
                unsafe_allow_html=True,
            )

        # Bar chart: scores by topic
        chart_data = {"topic": [], "avg_score": []}
        for t, avg in sorted(topic_avg.items()):
            chart_data["topic"].append(t.replace("_", " ").title())
            chart_data["avg_score"].append(avg)
        import pandas as pd
        df = pd.DataFrame(chart_data)
        st.markdown("### Scores by Topic")
        st.bar_chart(df, x="topic", y="avg_score", color="#7c8cff")

        # Per-question table
        st.markdown("### Recent Activity")
        st.markdown(
            '<div class="card" style="padding:0.5rem 1.5rem;">'
            '<table style="width:100%;border-collapse:collapse;">'
            "<tr><th style='text-align:left;padding:0.5rem;color:#8b8fa3;font-size:0.8rem;'>Question</th>"
            "<th style='text-align:center;padding:0.5rem;color:#8b8fa3;font-size:0.8rem;'>Topic</th>"
            "<th style='text-align:center;padding:0.5rem;color:#8b8fa3;font-size:0.8rem;'>Score</th>"
            "<th style='text-align:right;padding:0.5rem;color:#8b8fa3;font-size:0.8rem;'>Date</th></tr>",
            unsafe_allow_html=True,
        )
        for h in reversed(history[-20:]):
            sc = h.get("score", 0)
            color = "#2ecc71" if sc >= 70 else "#e67e22" if sc >= 40 else "#e74c3c"
            st.markdown(
                f"<tr><td style='padding:0.5rem;'>{h.get('question', '')[:30]}</td>"
                f"<td style='text-align:center;padding:0.5rem;color:#8b8fa3;'>{h.get('topic', '')}</td>"
                f"<td style='text-align:center;padding:0.5rem;color:{color};font-weight:600;'>{sc}</td>"
                f"<td style='text-align:right;padding:0.5rem;color:#8b8fa3;'>{h.get('timestamp', '')}</td></tr>",
                unsafe_allow_html=True,
            )
        st.markdown("</table></div>", unsafe_allow_html=True)

# ====================== MOCK INTERVIEW ======================

elif page == "Mock Interview":
    st.markdown("## \U0001f3af Mock Interview")

    mq = st.session_state.mock_questions

    if not mq:
        st.markdown(
            '<div class="card"><div class="card-title">Start a Mock Interview</div>'
            '<div class="card-value">Select a topic below to begin a 30-minute timed mock interview with 5 questions.</div></div>',
            unsafe_allow_html=True,
        )
        topic = st.selectbox(
            "Select Topic",
            ["arrays", "strings", "trees", "graphs", "dynamic_programming"],
            key="mock_topic",
        )
        if st.button("\U0001f3af Start Mock Interview", use_container_width=True, type="primary"):
            with st.spinner("Fetching questions\u2026"):
                data = api_get(f"/questions/?topic={topic}")
            if data and len(data) >= 3:
                st.session_state.mock_questions = data[:5]
                st.session_state.mock_answers = {}
                st.session_state.mock_start_time = time.time()
                st.session_state.mock_submitted = False
                st.rerun()
            else:
                st.error(f"Need at least 3 questions for topic '{topic}', got {len(data) if data else 0}.")
    else:
        # Timer
        elapsed = time.time() - st.session_state.mock_start_time
        remaining = max(0, 1800 - int(elapsed))  # 30 minutes
        mins, secs = divmod(remaining, 60)

        # Auto-submit if time's up
        if remaining <= 0 and not st.session_state.mock_submitted:
            st.session_state.mock_submitted = True
            st.warning("Time\u2019s up! Auto-submitting your answers.")
            st.rerun()

        timer_color = "#e74c3c" if remaining < 300 else "#7c8cff"
        st.markdown(
            f'<div class="timer-card"><div class="timer-text" style="color:{timer_color};">{mins:02d}:{secs:02d}</div>'
            f'<div class="card-label">Time Remaining</div></div>',
            unsafe_allow_html=True,
        )

        if st.session_state.mock_submitted:
            st.markdown("### \U0001f3c6 Results")
            # Evaluate with AI
            items = []
            for i, q in enumerate(mq):
                ans = st.session_state.mock_answers.get(i, "")
                items.append({
                    "question_id": qid(q),
                    "title": q.get("title", ""),
                    "description": q.get("description", ""),
                    "answer": ans,
                })
            with st.spinner("Evaluating your answers with AI..."):
                eval_data = api_post("/feedback/batch-eval", {"language": "python", "items": items})
            total = 0
            ai_results = eval_data.get("results", []) if eval_data else []
            for i, q in enumerate(mq):
                ai_score = ai_results[i]["score"] // 10 if i < len(ai_results) else 0
                fb = ai_results[i].get("feedback", "") if i < len(ai_results) else ""
                total += ai_score
                color = "#2ecc71" if ai_score >= 7 else "#e67e22" if ai_score >= 4 else "#e74c3c"
                st.markdown(
                    f'<div class="card" style="border-left: 4px solid {color};">'
                    f'<div class="card-title">Q{i+1}: {q.get("title", "")} '
                    f'<span style="float:right;color:{color};">{ai_score}/10</span></div>'
                    f'<div class="card-value" style="font-size:0.85rem;">{q.get("description", "")[:120]}...</div>'
                    f'<details><summary style="color:#8b8fa3;cursor:pointer;">Feedback</summary>'
                    f'<p style="font-size:0.85rem;margin-top:0.5rem;">{fb}</p></details>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div class="stat-box"><div class="stat-number">{total}/50</div>'
                f'<div class="stat-label">Total Score</div></div>',
                unsafe_allow_html=True,
            )

            if st.button("\U0001f504 Start New Mock Interview"):
                st.session_state.mock_questions = []
                st.session_state.mock_answers = {}
                st.session_state.mock_start_time = None
                st.session_state.mock_submitted = False
                st.rerun()

        else:
            # Render questions
            for i, q in enumerate(mq):
                with st.expander(f"Q{i+1}: {q.get('title', '')}", expanded=i == 0):
                    st.markdown(
                        f'<div class="card-value" style="font-size:0.9rem;">{q.get("description", "")}</div>',
                        unsafe_allow_html=True,
                    )
                    if q.get("constraints"):
                        st.markdown(
                            f'<div class="card" style="padding:0.8rem;"><span class="card-label">Constraints:</span> '
                            f'<span class="card-value">{q["constraints"]}</span></div>',
                            unsafe_allow_html=True,
                        )
                    ans = st.text_area(
                        f"Your answer for Q{i+1}",
                        value=st.session_state.mock_answers.get(i, ""),
                        height=120,
                        key=f"mock_ans_{i}",
                        placeholder="Write your solution here...",
                    )
                    st.session_state.mock_answers[i] = ans

            if st.button("\U0001f4e4 Submit All Answers", use_container_width=True, type="primary"):
                st.session_state.mock_submitted = True
                st.success("Submitted! Scroll down to see your results.")
                st.rerun()

# ====================== HISTORY ======================

elif page == "History":
    st.markdown("## \U0001f4ca History")

    if not st.session_state.history:
        st.markdown(
            '<div class="card"><div class="card-title">No history yet</div>'
            '<div class="card-value">Complete a practice session and your results will appear here.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="card" style="padding:0.5rem 1.5rem;">'
            '<table style="width:100%;border-collapse:collapse;">'
            "<tr><th style='text-align:left;padding:0.5rem;color:#8b8fa3;font-size:0.8rem;'>Question</th>"
            "<th style='text-align:center;padding:0.5rem;color:#8b8fa3;font-size:0.8rem;'>Score</th>"
            "<th style='text-align:right;padding:0.5rem;color:#8b8fa3;font-size:0.8rem;'>Date</th></tr>",
            unsafe_allow_html=True,
        )
        for h in reversed(st.session_state.history):
            sc = h.get("score", 0)
            color = "#2ecc71" if sc >= 70 else "#e67e22" if sc >= 40 else "#e74c3c"
            st.markdown(
                f"<tr><td style='padding:0.5rem;'>{h.get('question', '')}</td>"
                f"<td style='text-align:center;padding:0.5rem;color:{color};font-weight:600;'>{sc}</td>"
                f"<td style='text-align:right;padding:0.5rem;color:#8b8fa3;'>{h.get('timestamp', '')}</td></tr>",
                unsafe_allow_html=True,
            )
        st.markdown("</table></div>", unsafe_allow_html=True)

        s = st.session_state.stats
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(
                f'<div class="stat-box"><div class="stat-number">{s["attempted"]}</div><div class="stat-label">Total Attempted</div></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f'<div class="stat-box"><div class="stat-number">{s["avg_score"]}</div><div class="stat-label">Average Score</div></div>',
                unsafe_allow_html=True,
            )
        with col_c:
            best = max(s["total_scores"]) if s["total_scores"] else 0
            st.markdown(
                f'<div class="stat-box"><div class="stat-number">{best}</div><div class="stat-label">Best Score</div></div>',
                unsafe_allow_html=True,
            )

        if st.button("Clear History"):
            st.session_state.history = []
            st.session_state.stats = {"attempted": 0, "avg_score": 0, "total_scores": []}
            st.rerun()
