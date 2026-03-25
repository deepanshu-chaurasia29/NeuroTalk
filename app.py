import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import re
from datetime import datetime
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
import data_manager
from prompts import SCENARIOS
from auth import create_user, login_user, update_streak, update_user_stats, find_user

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key="AIzaSyCjLtnsLz3gkJ3Xj9Mc7rC3ZJu3olPGkiI") if api_key else None

st.set_page_config(
    page_title="AI Social Anxiety Coach",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load external CSS
# ---------------------------------------------------------------------------
def load_css():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------------------------
# Login state
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None


# ---------------------------------------------------------------------------
# Login / Signup page
# ---------------------------------------------------------------------------
def show_login_page():
    st.markdown(
        """
        <style>
        /* ==================== LOGIN PAGE ONLY ==================== */

        /* 1. Full page background */
        .stApp {
            background-color: #050505 !important;
        }

        /* 2. Login card – middle column */
        .stMainBlockContainer [data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
            background: #111111;
            border: 1px solid #1a2e1a;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 0 60px rgba(26,244,154,0.06);
        }

        /* 3. App title */
        .login-title {
            font-size: 2rem !important;
            color: #1AF49A !important;
            font-weight: bold !important;
            text-align: center;
            -webkit-text-fill-color: #1AF49A !important;
        }

        /* 4. Tagline */
        .login-tagline {
            color: #9599A6 !important;
            text-align: center;
            font-size: 0.9rem !important;
            -webkit-text-fill-color: #9599A6 !important;
        }

        /* 5. Tab buttons */
        .stMainBlockContainer .stTabs [data-baseweb="tab-list"] button {
            color: #666 !important;
            font-weight: 500;
            background: transparent !important;
            border-bottom: 2px solid transparent;
        }
        .stMainBlockContainer .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            color: #ffffff !important;
            border-bottom: 2px solid #1AF49A !important;
        }
        .stMainBlockContainer .stTabs [data-baseweb="tab-highlight"] {
            background-color: #1AF49A !important;
        }

        /* 6. Input fields */
        .stMainBlockContainer .stTextInput > div > div > input {
            background-color: #1a1a1a !important;
            border: 1px solid #2a2a2a !important;
            color: #ffffff !important;
            border-radius: 8px !important;
        }
        .stMainBlockContainer .stTextInput > div > div > input:focus {
            border-color: #1AF49A !important;
            box-shadow: 0 0 0 2px rgba(26,244,154,0.15) !important;
        }
        .stMainBlockContainer .stTextInput > div > div > input::placeholder {
            color: #555 !important;
        }
        .stMainBlockContainer .stTextInput label {
            color: #9599A6 !important;
        }

        /* 7. Login / Signup button */
        .stMainBlockContainer .stButton > button {
            background: #1AF49A !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            width: 100%;
            font-size: 1rem !important;
            border: none !important;
            padding: 0.6rem 1rem !important;
            transition: all 0.3s ease !important;
        }
        .stMainBlockContainer .stButton > button:hover {
            background: #15d888 !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 20px rgba(26,244,154,0.3) !important;
        }

        /* 8. Error messages */
        .stMainBlockContainer .stAlert [data-testid="stNotificationContentError"] {
            background: #1a0000 !important;
            border-left: 3px solid #ff4444 !important;
            color: #ff6666 !important;
        }
        .stMainBlockContainer div[data-baseweb="notification"] .st-emotion-cache-1gulkj5,
        .stMainBlockContainer .stException,
        .stMainBlockContainer [data-testid="stNotification"][data-type="error"] {
            background: #1a0000 !important;
            border-left: 3px solid #ff4444 !important;
            color: #ff6666 !important;
        }

        /* 9. Success messages */
        .stMainBlockContainer .stAlert [data-testid="stNotificationContentSuccess"] {
            background: #0a1a0a !important;
            border-left: 3px solid #1AF49A !important;
            color: #1AF49A !important;
        }
        .stMainBlockContainer div[data-baseweb="notification"] .st-emotion-cache-1aehpvj,
        .stMainBlockContainer [data-testid="stNotification"][data-type="success"] {
            background: #0a1a0a !important;
            border-left: 3px solid #1AF49A !important;
            color: #1AF49A !important;
        }

        /* Hide sidebar on login page */
        section[data-testid="stSidebar"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown(
            '<div style="text-align:center;font-size:4rem;margin-bottom:0;">\U0001f9e0</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="login-title" style="margin-top:0;padding-top:0;">AI Social Anxiety Coach</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="login-tagline">Build confidence through practice</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align:center;margin-bottom:24px;">'
            '<span style="background:#0d2818;color:#4ade80;padding:6px 14px;'
            'border-radius:20px;font-size:0.8rem;border:1px solid #166534;">'
            '\U0001f3c6 HustlerDevs | VisionX Hackathon</span></div>',
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["\U0001f511 Login", "\u2728 Create Account"])

        with tab1:
            email = st.text_input("Email", placeholder="you@email.com", key="login_email")
            password = st.text_input(
                "Password", type="password", placeholder="Your password", key="login_pw"
            )
            login_btn = st.button("Login \u2192", use_container_width=True, key="login_btn")

            if login_btn:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    with st.spinner("Logging in..."):
                        user = login_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.current_user = user
                        st.toast(f"Welcome back, {user['name'].split()[0]}! \U0001f44b")
                        st.rerun()
                    else:
                        st.error("\u274c Invalid email or password")

        with tab2:
            name = st.text_input("Full Name", placeholder="Jisu Kumar", key="signup_name")
            s_email = st.text_input("Email ", placeholder="you@email.com", key="signup_email")
            s_password = st.text_input(
                "Password ", type="password", placeholder="Min 6 characters", key="signup_pw"
            )
            confirm = st.text_input(
                "Confirm Password", type="password", placeholder="Repeat password", key="signup_confirm"
            )
            signup_btn = st.button(
                "Create Account \u2192", use_container_width=True, key="signup_btn"
            )

            if signup_btn:
                if not all([name, s_email, s_password, confirm]):
                    st.error("Please fill in all fields")
                elif len(name.strip()) < 2:
                    st.error("Name must be at least 2 characters")
                elif "@" not in s_email or "." not in s_email:
                    st.error("Please enter a valid email")
                elif len(s_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif s_password != confirm:
                    st.error("Passwords do not match")
                else:
                    try:
                        with st.spinner("Creating your account..."):
                            user = create_user(name, s_email, s_password)
                        st.session_state.logged_in = True
                        st.session_state.current_user = user
                        st.session_state.is_new_user = True
                        st.toast("Account created! \U0001f389")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))


# ---------------------------------------------------------------------------
# Session‑state defaults
# ---------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = list(SCENARIOS.keys())[0]
if "round_number" not in st.session_state:
    st.session_state.round_number = 0
if "session_started" not in st.session_state:
    st.session_state.session_started = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "🎯 Practice"

# --- Session tracking data (silent, for dashboard) ---
if "session_data" not in st.session_state:
    st.session_state.session_data = []
if "total_rounds" not in st.session_state:
    st.session_state.total_rounds = 0
if "average_confidence" not in st.session_state:
    st.session_state.average_confidence = 0.0
if "best_score" not in st.session_state:
    st.session_state.best_score = 0
if "worst_score" not in st.session_state:
    st.session_state.worst_score = 0
if "scenarios_practiced" not in st.session_state:
    st.session_state.scenarios_practiced = []
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------------------------------------------------------------------------
# Shared helpers — parse & render
# ---------------------------------------------------------------------------

def _extract_confidence_score(text: str):
    patterns = [
        r"(?:Score|Confidence)[\s:=]*(\d{1,2})\s*(?:/|out of)\s*10",
        r"(\d{1,2})\s*(?:/|out of)\s*10",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                score = int(match.group(1))
                if 0 <= score <= 10:
                    return score
            except ValueError:
                pass
    return None


def _score_color(score: int) -> str:
    if score <= 4:
        return "#ef4444"
    elif score <= 7:
        return "#eab308"
    else:
        return "#22c55e"


def _render_confidence_bar(score: int) -> str:
    color = _score_color(score)
    pct = score * 10
    return (
        f'<div class="confidence-container">'
        f'  <div class="confidence-label">Confidence Score '
        f'    <span class="confidence-score-text" style="color:{color}">{score}/10</span>'
        f"  </div>"
        f'  <div class="confidence-bar-bg">'
        f'    <div class="confidence-bar-fill" style="width:{pct}%;background:{color};"></div>'
        f"  </div>"
        f"</div>"
    )


def _split_ai_response(text: str):
    score = _extract_confidence_score(text)
    feedback = text
    improved = None
    coaching_note = None

    fb_start = text.find("---FEEDBACK---")
    if fb_start != -1:
        fb_content_start = text.find("\n", fb_start)
        fb_content_start = (fb_content_start + 1) if fb_content_start != -1 else fb_start + len("---FEEDBACK---")
        fb_end = len(text)
        for end_marker in ["CONFIDENCE SCORE", "---IMPROVED RESPONSE---"]:
            idx = text.find(end_marker, fb_content_start)
            if idx != -1 and idx < fb_end:
                fb_end = idx
        feedback = text[fb_content_start:fb_end].strip()

    imp_start = text.find("---IMPROVED RESPONSE---")
    if imp_start != -1:
        imp_content_start = text.find("\n", imp_start)
        imp_content_start = (imp_content_start + 1) if imp_content_start != -1 else imp_start + len("---IMPROVED RESPONSE---")
        imp_end = text.find("---COACHING NOTE---", imp_content_start)
        if imp_end == -1:
            imp_end = len(text)
        improved = text[imp_content_start:imp_end].strip()

    cn_start = text.find("---COACHING NOTE---")
    if cn_start != -1:
        cn_content_start = text.find("\n", cn_start)
        cn_content_start = (cn_content_start + 1) if cn_content_start != -1 else cn_start + len("---COACHING NOTE---")
        coaching_note = text[cn_content_start:].strip()

    return feedback, improved, coaching_note, score


def _extract_feedback_points(feedback_text: str) -> list:
    points = re.findall(r"\d+\.\s*(.+?)(?=\n\d+\.|$)", feedback_text, re.DOTALL)
    return [p.strip() for p in points if p.strip()]


def _nl2br(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = text.replace("\n", "<br>")
    return text


def _render_ai_message(content: str, is_opening: bool = False):
    if is_opening:
        html = (
            f'<div class="chat-bubble-ai">'
            f'<span class="bubble-label bubble-label-ai">🤖 AI Coach</span>'
            f"{_nl2br(content)}"
            f"</div>"
        )
        st.markdown(html, unsafe_allow_html=True)
        return

    feedback, improved, coaching_note, score = _split_ai_response(content)

    feedback_html = (
        f'<div class="chat-bubble-ai">'
        f'<span class="bubble-label bubble-label-ai">🤖 AI Coach</span>'
        f'<div class="feedback-box">{_nl2br(feedback)}</div>'
    )

    if score is not None:
        feedback_html += _render_confidence_bar(score)

    if improved:
        feedback_html += (
            f'<div class="improved-box">'
            f'<span class="improved-box-title">✨ Improved Version</span>'
            f"{_nl2br(improved)}"
            f"</div>"
        )

    if coaching_note:
        feedback_html += (
            f'<div style="margin-top:12px;padding:12px 16px;'
            f'border-radius:8px;background:#111;color:#a0a0a0;'
            f'font-style:italic;line-height:1.7;">'
            f"{_nl2br(coaching_note)}"
            f"</div>"
        )

    feedback_html += "</div>"
    st.markdown(feedback_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar  (shared)
# ---------------------------------------------------------------------------
def run_main_app():
    with st.sidebar:
        # ── User Profile ──────────────────────────────────────────
        user = st.session_state.get("current_user")
        if user:
            name = user.get("name", "User")
            email = user.get("email", "")
            level = user.get("level", "Beginner")
            level_emojis = {"Beginner": "🌱", "Intermediate": "⚡", "Advanced": "🎯", "Expert": "🏆"}
            emoji = level_emojis.get(level, "🌱")
            initial = name[0].upper() if name else "?"

            st.markdown(
                f'<div class="sb-profile">'
                f'  <div class="sb-avatar">{initial}</div>'
                f'  <div class="sb-user-info">'
                f'    <div class="sb-user-name">{name}</div>'
                f'    <div class="sb-user-email">{email}</div>'
                f'    <span class="sb-level-badge">{emoji} {level}</span>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Quick stats row
            sessions = user.get("total_sessions", 0)
            rounds = user.get("total_rounds", 0)
            avg = user.get("average_score", 0)

            st.markdown(
                f'<div class="sb-stats-row">'
                f'  <div class="sb-stat"><div class="sb-stat-val">{sessions}</div><div class="sb-stat-lbl">Sessions</div></div>'
                f'  <div class="sb-stat"><div class="sb-stat-val">{rounds}</div><div class="sb-stat-lbl">Rounds</div></div>'
                f'  <div class="sb-stat"><div class="sb-stat-val">{avg}</div><div class="sb-stat-lbl">Avg Score</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Streak card
            streak = user.get("current_streak", 0)
            longest = user.get("longest_streak", 0)
            if streak == 0:
                streak_msg = "Start your streak today!"
            elif streak >= 7:
                streak_msg = "One week warrior! 💪"
            elif streak >= 3:
                streak_msg = "You're on fire! 🔥"
            else:
                streak_msg = "Keep it going!"

            st.markdown(
                f'<div class="streak-card">'
                f'<span class="fire-pulse">🔥</span> '
                f'<span class="streak-number">{streak}</span>'
                f'<div class="streak-label">Day Streak</div>'
                f'<div class="streak-msg">{streak_msg}</div>'
                f'<div class="streak-record">🏅 Longest: {longest} days</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Page navigation
        page = st.radio(
            "Navigate",
            ["🎯 Practice", "📊 My Dashboard"],
            index=["🎯 Practice", "📊 My Dashboard"].index(st.session_state.current_page),
            label_visibility="collapsed",
        )
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()

        st.markdown("---")

        if st.session_state.current_page == "🎯 Practice":
            selected_scenario = st.selectbox(
                "Choose a Scenario",
                list(SCENARIOS.keys()),
                index=list(SCENARIOS.keys()).index(st.session_state.current_scenario),
            )
            if selected_scenario != st.session_state.current_scenario:
                st.session_state.current_scenario = selected_scenario
                st.session_state.chat_history = []
                st.session_state.round_number = 0
                st.session_state.session_started = False
                st.session_state.session_data = []
                st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()

            st.markdown("---")
            if st.button("🔄 Start New Session", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.round_number = 0
                st.session_state.session_started = False
                st.session_state.session_data = []
                st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()

            st.markdown("---")
            st.markdown(
                f'<div class="round-badge">🔁 Round {st.session_state.round_number}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        if st.checkbox("🗑️ Clear All Data"):
            st.warning("Are you sure? This will delete all history.")
            if st.button("Yes, clear it", key="confirm_clear"):
                _email = st.session_state.get("current_user", {}).get("email", "")
                data_manager.clear_all_data(_email)
                st.session_state.session_data = []
                st.rerun()

        st.markdown("---")
        st.markdown(
            '<p class="sidebar-footer">'
            "Built by <strong>Team HustlerDevs</strong></p>",
            unsafe_allow_html=True,
        )

        # Logout button
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.toast("See you next time! \U0001f44b")
            st.session_state.clear()
            st.rerun()

    # Page router (inside run_main_app, outside sidebar)
    if st.session_state.current_page == "🎯 Practice":
        render_practice_page()
    else:
        render_dashboard_page()


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║                         PAGE: PRACTICE                                 ║
# ╚═════════════════════════════════════════════════════════════════════════╝

def render_practice_page():
    if st.session_state.get("current_user"):
        user_name = st.session_state.current_user.get("name", "").split()[0]
        st.markdown(
            f'<div style="text-align:right;color:#4ade80;font-size:0.9rem;margin-bottom:-10px;">'
            f'👋 Welcome, {user_name}</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="main-header">🧠 AI Social Anxiety Coach</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="sub-header">Scenario: <span>{st.session_state.current_scenario}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    scenario_data = SCENARIOS[st.session_state.current_scenario]

    if not st.session_state.session_started:
        opening_msg = scenario_data["opening"]
        st.session_state.chat_history.append({"role": "ai", "content": opening_msg})
        st.session_state.session_started = True

    # Display chat history
    for i, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "ai":
            _render_ai_message(msg["content"], is_opening=(i == 0))
        else:
            st.markdown(
                f'<div class="chat-bubble-user">'
                f'<span class="bubble-label bubble-label-user">🧑 You</span>'
                f'{_nl2br(msg["content"])}'
                f"</div>",
                unsafe_allow_html=True,
            )

    # Gemini call helper
    def get_ai_response(user_message: str) -> str:
        try:
            gemini_history = []
            for msg in st.session_state.chat_history:
                role = "model" if msg["role"] == "ai" else "user"
                gemini_history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])],
                    )
                )
            chat = client.chats.create(
                model="gemini-2.5-flash",
                history=gemini_history,
                config=types.GenerateContentConfig(
                    system_instruction=scenario_data["system"],
                ),
            )
            response = chat.send_message(message=user_message)
            return response.text
        except Exception as e:
            return (
                f"⚠️ **Oops! Something went wrong.**\n\n"
                f"I wasn't able to get a response from the AI. "
                f"Please check your API key in the `.env` file and try again.\n\n"
                f"*Error details: {e}*"
            )

    # User input
    with st.container():
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input(
                "Your response",
                placeholder="Type your response here...",
                key="user_input",
                label_visibility="collapsed",
            )
        with col2:
            submit = st.button("Send ▶", use_container_width=True)

    if submit and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.round_number += 1

        with st.spinner("Coach is thinking... 🤔"):
            ai_reply = get_ai_response(user_input)

        st.session_state.chat_history.append({"role": "ai", "content": ai_reply})

        # --- Silent session data tracking ---
        feedback_text, improved_text, _, parsed_score = _split_ai_response(ai_reply)
        feedback_points = _extract_feedback_points(feedback_text) if feedback_text else []

        round_data = {
            "round": st.session_state.round_number,
            "scenario": st.session_state.current_scenario,
            "user_message": user_input,
            "confidence_score": parsed_score,
            "feedback_points": feedback_points,
            "improved_response": improved_text or "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.session_data.append(round_data)

        st.session_state.total_rounds = len(st.session_state.session_data)
        scores = [d["confidence_score"] for d in st.session_state.session_data if d["confidence_score"] is not None]
        avg_score = 0.0
        if scores:
            avg_score = round(sum(scores) / len(scores), 1)
            st.session_state.average_confidence = avg_score
            st.session_state.best_score = max(scores)
            st.session_state.worst_score = min(scores)
        if st.session_state.current_scenario not in st.session_state.scenarios_practiced:
            st.session_state.scenarios_practiced.append(st.session_state.current_scenario)
            
        current_session = {
            "session_id": st.session_state.session_id,
            "date": st.session_state.session_start_time,
            "scenario": st.session_state.current_scenario,
            "rounds": st.session_state.session_data,
            "average_score": avg_score,
            "total_rounds": st.session_state.total_rounds
        }
        _email = st.session_state.get("current_user", {}).get("email", "")
        data_manager.save_session(current_session, _email)

        # --- Update user auth stats (streak, XP, level, responses) ---
        cur_user = st.session_state.get("current_user")
        if cur_user:
            email = cur_user.get("email", "")
            old_level = cur_user.get("level", "Beginner")
            best_s = max(scores) if scores else 0
            update_streak(email)
            update_user_stats(
                email,
                rounds=1,
                avg_score=avg_score,
                best=best_s,
                user_response=user_input,
                scenario=st.session_state.current_scenario,
            )
            # Refresh session state with latest user data
            refreshed = find_user(email)
            if refreshed:
                st.session_state.current_user = refreshed
                new_streak = refreshed.get("current_streak", 0)
                new_level = refreshed.get("level", "Beginner")
                st.toast(f"🔥 {new_streak} day streak!")
                if new_level != old_level:
                    st.toast(f"🎉 Level Up! You are now {new_level}!")

        st.rerun()
    elif submit and not user_input:
        st.warning("Please type a response before submitting.")


# ╔═════════════════════════════════════════════════════════════════════════╗
# ║                         PAGE: DASHBOARD                               ║
# ╚═════════════════════════════════════════════════════════════════════════╝

def _render_current_session_tab():
    data = st.session_state.session_data

    # ── Empty state ──────────────────────────────────────────────────────
    if not data:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">🧠</div>
                <div class="empty-state-title">No practice data yet!</div>
                <div class="empty-state-text">
                    Go to the <strong>Practice</strong> tab and start a session 🎯
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="dash-section-title">Quick Start</div>',
            unsafe_allow_html=True,
        )
        scenario_icons = {
            "Job Interview": "💼",
            "Public Speaking": "🎤",
            "Casual Social Conversation": "💬",
            "Group Discussion": "🗣️",
            "Job Rejection Recovery": "💙",
        }
        cols = st.columns(5)
        for col, (name, icon) in zip(cols, scenario_icons.items()):
            with col:
                st.markdown(
                    f'<div class="scenario-card">'
                    f'<div class="scenario-card-icon">{icon}</div>'
                    f'<div class="scenario-card-name">{name}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
        return

    # ── SECTION 1: Stats Overview ────────────────────────────────────────
    scores = [d["confidence_score"] for d in data if d["confidence_score"] is not None]
    avg_conf = round(sum(scores) / len(scores), 1) if scores else 0
    best_s = max(scores) if scores else 0
    unique_scenarios = list(set(d["scenario"] for d in data))

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, str(len(data)), "Total Rounds Practiced"),
        (c2, f"{avg_conf}/10", "Average Confidence"),
        (c3, f"{best_s}/10", "Best Score Achieved"),
        (c4, str(len(unique_scenarios)), "Scenarios Practiced"),
    ]
    for col, value, label in cards:
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-card-value">{value}</div>'
                f'<div class="stat-card-label">{label}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── SECTION 2: Confidence Score Progress Chart ───────────────────────
    st.markdown(
        '<div class="dash-section-title">Confidence Score Progress</div>',
        unsafe_allow_html=True,
    )
    rounds_with_scores = [(d["round"], d["confidence_score"]) for d in data if d["confidence_score"] is not None]
    if rounds_with_scores:
        r_nums, r_scores = zip(*rounds_with_scores)
        if PLOTLY_AVAILABLE:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=list(r_nums),
                y=list(r_scores),
                mode="lines+markers",
                line=dict(color="#1AF49A", width=3),
                marker=dict(size=10, color="#1AF49A", line=dict(color="#111111", width=2)),
                fill="tozeroy",
                fillcolor="rgba(26,244,154,0.08)",
                hovertemplate="Round %{x}<br>Score: %{y}/10<extra></extra>",
            ))
            fig_line.update_layout(
                plot_bgcolor="#111111",
                paper_bgcolor="#111111",
                font=dict(color="#9599A6", family="Inter"),
                xaxis=dict(
                    title="Round",
                    gridcolor="#2a2a2a",
                    dtick=1,
                ),
                yaxis=dict(
                    title="Score",
                    range=[0, 10.5],
                    gridcolor="#2a2a2a",
                    dtick=1,
                ),
                margin=dict(l=40, r=20, t=20, b=40),
                height=350,
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            import pandas as pd
            st.line_chart(pd.DataFrame({"Score": list(r_scores)}, index=list(r_nums)))
    else:
        st.info("Confidence scores will appear here after your first practice round.")

    # ── SECTION 3: Round‑by‑Round History ────────────────────────────────
    st.markdown(
        '<div class="dash-section-title">Round‑by‑Round History</div>',
        unsafe_allow_html=True,
    )

    table_rows = ""
    for d in data:
        sc = d["confidence_score"]
        if sc is not None:
            # using colored badges for scores
            sc_color = _score_color(sc)
            bg_color = sc_color + "25" # 15% opacity hex
            sc_html = f'<span style="background:{bg_color};color:{sc_color};padding:4px 8px;border-radius:12px;font-weight:700;font-size:0.8rem;">{sc}/10</span>'
        else:
            sc_html = '<span style="color:#666">—</span>'

        user_trunc = (d["user_message"][:50] + "…") if len(d["user_message"]) > 50 else d["user_message"]
        imp_trunc = (d["improved_response"][:50] + "…") if len(d["improved_response"]) > 50 else d["improved_response"]

        user_trunc = user_trunc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        imp_trunc = imp_trunc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        table_rows += (
            f"<tr>"
            f'<td style="text-align:center;color:#9599A6;font-weight:600">{d["round"]}</td>'
            f'<td><span style="background:#1a1a1a;padding:2px 8px;border-radius:4px;color:#9599A6;font-size:0.75rem;">{d["scenario"]}</span></td>'
            f"<td style='text-align:center'>{sc_html}</td>"
            f"<td>{user_trunc}</td>"
            f"<td>{imp_trunc}</td>"
            f'<td style="color:#9599A6;font-size:0.75rem">{d["timestamp"]}</td>'
            f"</tr>"
        )

    st.markdown(
        f"""
        <div style="overflow-x:auto;border-radius:10px;border:1px solid #1e1e1e;margin-bottom:24px;">
        <table class="custom-dash-table">
            <thead>
                <tr>
                    <th style="width:5%;text-align:center">Round</th>
                    <th style="width:15%">Scenario</th>
                    <th style="width:10%;text-align:center">Score</th>
                    <th style="width:30%">Your Response</th>
                    <th style="width:30%">Improved</th>
                    <th style="width:10%">Time</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── SECTION 4: Scenario Breakdown Bar Chart ──────────────────────────
    st.markdown(
        '<div class="dash-section-title">Practice Distribution by Scenario</div>',
        unsafe_allow_html=True,
    )
    from collections import Counter
    scenario_counts = Counter(d["scenario"] for d in data)
    scenarios_sorted = sorted(scenario_counts.items(), key=lambda x: x[1], reverse=True)
    s_names, s_counts = zip(*scenarios_sorted) if scenarios_sorted else ([], [])

    if PLOTLY_AVAILABLE:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=list(s_counts),
            y=list(s_names),
            orientation="h",
            marker=dict(
                color="#1AF49A",
                line=dict(color="#111111", width=1),
            ),
            hovertemplate="%{y}: %{x} rounds<extra></extra>",
        ))
        fig_bar.update_layout(
            plot_bgcolor="#111111",
            paper_bgcolor="#111111",
            font=dict(color="#9599A6", family="Inter"),
            xaxis=dict(title="Rounds", gridcolor="#2a2a2a", dtick=1),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=20, r=20, t=10, b=40),
            height=250,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        import pandas as pd
        st.bar_chart(pd.DataFrame({"Rounds": list(s_counts)}, index=list(s_names)))

    # ── SECTION 5: Best Responses Gallery ────────────────────────────────
    st.markdown(
        '<div class="dash-section-title">Best Responses</div>',
        unsafe_allow_html=True,
    )
    scored_rounds = [d for d in data if d["confidence_score"] is not None]
    top_rounds = sorted(scored_rounds, key=lambda x: x["confidence_score"], reverse=True)[:3]

    if top_rounds:
        for d in top_rounds:
            user_escaped = d["user_message"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            imp_escaped = d["improved_response"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            badge_color = _score_color(d["confidence_score"])
            
            st.markdown(
                f"""
                <div class="best-card">
                    <div class="best-card-header">
                        <span class="best-card-scenario">{d["scenario"]}</span>
                        <span class="best-card-badge" style="color:{badge_color};border-color:{badge_color};background:{badge_color}25">{d["confidence_score"]}/10</span>
                    </div>
                    <div class="best-card-section-label">Your Response</div>
                    <div class="best-card-text">{user_escaped}</div>
                    <div class="best-card-section-label" style="margin-top:16px">Improved Version</div>
                    <div class="best-card-improved">{imp_escaped if imp_escaped else '<em style="color:#555">Not available</em>'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Your top responses will appear here after you practice a few rounds.")


def _render_growth_story():
    """Render the Before vs After growth comparison section."""
    st.markdown(
        '<div class="dash-section-title">Your Growth Story 📈</div>',
        unsafe_allow_html=True,
    )
    user = st.session_state.get("current_user")
    if not user:
        st.info("Log in to see your growth story.")
        return

    first = user.get("first_response", {})
    latest = user.get("latest_response", {})

    if not first.get("text") or not latest.get("text") or first.get("text") == latest.get("text"):
        st.markdown(
            '<div style="text-align:center;padding:30px;color:#777;">'
            '✨ Complete more sessions to see your growth!</div>',
            unsafe_allow_html=True,
        )
        return

    first_text = first["text"][:200] + ("…" if len(first["text"]) > 200 else "")
    latest_text = latest["text"][:200] + ("…" if len(latest["text"]) > 200 else "")
    first_score = first.get("score", 0)
    latest_score = latest.get("score", 0)
    improvement = latest_score - first_score

    first_text_esc = first_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    latest_text_esc = latest_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    imp_sign = f"+{improvement}" if improvement > 0 else str(improvement)
    imp_color = "#1AF49A" if improvement > 0 else ("#ff6666" if improvement < 0 else "#999")

    st.markdown(
        f'''
        <div class="growth-container">
            <div class="growth-card growth-card-first">
                <div class="growth-card-label" style="color:#999;">📝 Your First Response</div>
                <div class="growth-card-text" style="color:#aaa;">{first_text_esc}</div>
                <div style="color:#666;font-size:0.8rem;">Scenario: {first.get("scenario", "—")}</div>
                <div style="margin-top:8px;">
                    <span style="background:#2a2a2a;color:#999;padding:4px 10px;border-radius:12px;font-weight:700;font-size:0.85rem;">{first_score}/10</span>
                </div>
            </div>
            <div class="growth-arrow">
                <div class="growth-arrow-icon">→</div>
                <div class="growth-improvement" style="color:{imp_color};">{imp_sign} pts</div>
            </div>
            <div class="growth-card growth-card-latest">
                <div class="growth-card-label" style="color:#4ade80;">🚀 Your Latest Response</div>
                <div class="growth-card-text" style="color:#d0d0d0;">{latest_text_esc}</div>
                <div style="color:#6b7a6b;font-size:0.8rem;">Scenario: {latest.get("scenario", "—")}</div>
                <div style="margin-top:8px;">
                    <span style="background:rgba(26,244,154,0.15);color:#1AF49A;padding:4px 10px;border-radius:12px;font-weight:700;font-size:0.85rem;">{latest_score}/10</span>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def _render_progress_section(user: dict):
    """Render the Your Progress section: level badge, XP bar, streak, improvement."""
    st.markdown(
        '<div class="dash-section-title">Your Progress</div>',
        unsafe_allow_html=True,
    )
    if not user:
        st.info("Log in to see your progress.")
        return

    # --- Level & XP ---
    level = user.get("level", "Beginner")
    xp = user.get("xp", 0)
    level_emojis = {"Beginner": "🌱", "Intermediate": "⚡", "Advanced": "🎯", "Expert": "🏆"}
    level_thresholds = {"Beginner": (0, 100), "Intermediate": (100, 300), "Advanced": (300, 600), "Expert": (600, 600)}
    emoji = level_emojis.get(level, "🌱")
    low, high = level_thresholds.get(level, (0, 100))
    if level == "Expert":
        pct = 100
        xp_to_next = "Max level reached! 🎉"
    else:
        progress = xp - low
        needed = high - low
        pct = min(int((progress / needed) * 100), 100) if needed > 0 else 0
        xp_to_next = f"{high - xp} XP to next level"

    # --- Streak ---
    streak = user.get("current_streak", 0)
    longest = user.get("longest_streak", 0)

    # --- Improvement ---
    user_email = user.get("email", "")
    all_data = data_manager.load_all_sessions(user_email)
    sessions = all_data.get("sessions", [])
    if len(sessions) >= 2:
        first_avg = sessions[0].get("average_score", 0) or 0
        latest_avg = sessions[-1].get("average_score", 0) or 0
        diff = round(latest_avg - first_avg, 1)
        diff_sign = f"+{diff}" if diff > 0 else str(diff)
        diff_color = "#1AF49A" if diff > 0 else ("#ff6666" if diff < 0 else "#999")
        improvement_html = (
            f'<div class="prog-imp-val" style="color:{diff_color}">{diff_sign} pts</div>'
            f'<div class="prog-imp-lbl">since your first session</div>'
            f'<div style="color:#666;font-size:0.75rem;margin-top:4px;">'
            f'First: {first_avg}/10 → Latest: {latest_avg}/10</div>'
        )
    elif len(sessions) == 1:
        improvement_html = '<div class="prog-imp-lbl">Complete more sessions to see your growth!</div>'
    else:
        improvement_html = '<div class="prog-imp-lbl">Start practicing to track your improvement!</div>'

    st.markdown(
        f'''
        <div class="prog-grid">
            <div class="prog-card prog-level-card">
                <div class="prog-level-emoji">{emoji}</div>
                <div class="prog-level-name">{level}</div>
                <div class="prog-xp-bar-bg"><div class="prog-xp-bar-fill" style="width:{pct}%"></div></div>
                <div class="prog-xp-text">{xp} XP · {xp_to_next}</div>
            </div>
            <div class="prog-card">
                <div class="prog-streak-icon"><span class="fire-pulse">🔥</span></div>
                <div class="prog-streak-val">{streak}</div>
                <div class="prog-streak-lbl">Day Streak</div>
                <div class="prog-streak-record">🏅 Longest: {longest} days</div>
            </div>
            <div class="prog-card">
                <div class="prog-imp-icon">📈</div>
                {improvement_html}
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def render_dashboard_page():
    user = st.session_state.get("current_user", {})
    user_email = user.get("email", "")
    first_name = user.get("name", "User").split()[0]

    st.markdown(
        f'<div class="main-header" style="text-align:left">Welcome back, {first_name}! 👋</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="sub-header" style="text-align:left;display:flex;justify-content:space-between;">'
        f'<span>📊 Your Practice Dashboard</span>'
        f'<span>{datetime.now().strftime("%B %d, %Y")}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    # Quick Actions
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("▶ Continue Practice", use_container_width=True):
            st.session_state.current_page = "🎯 Practice"
            st.rerun()
    with c2:
        if st.button("🔄 New Scenario", use_container_width=True):
            st.session_state.current_page = "🎯 Practice"
            st.session_state.chat_history = []
            st.session_state.round_number = 0
            st.session_state.session_started = False
            st.session_state.session_data = [] # Reset data
            st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S") # New id
            st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
    with c3:
        report_text = data_manager.generate_report(user_email)
        st.download_button(
            label="⬇ Download Report",
            data=report_text,
            file_name=f"ai_coach_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")

    # ── Your Progress section ─────────────────────────────────
    _render_progress_section(user)

    st.markdown("---")

    tab1, tab2 = st.tabs(["🎯 Current Session", "📈 All Time Stats"])
    
    with tab1:
        _render_current_session_tab()
        
    with tab2:
        with st.spinner("Loading your stats..."):
            all_data = data_manager.load_all_sessions(user_email)
            if not all_data.get("sessions"):
                st.info("No all-time data found yet. Complete a few rounds to start tracking!")
            else:
                stats = data_manager.get_overall_stats(user_email)
                st.markdown('<div class="dash-section-title">All Time Overview</div>', unsafe_allow_html=True)
                
                tr = stats["all_time_rounds"]
                avg = f'{stats["all_time_avg_score"]}/10' if tr > 0 else '—'
                best = f'{stats["all_time_best_score"]}/10' if tr > 0 else '—'
                most = stats["most_practiced_scenario"] if tr > 0 else '—'
                ts = str(stats["total_sessions"]) if tr > 0 else '—'
                trend = stats["improvement_trend"] if tr > 0 else '—'
                
                st.markdown(
                    f'''
                    <div class="metric-grid">
                        <div class="stat-card">
                            <div class="stat-card-value">{tr if tr > 0 else '—'}</div>
                            <div class="stat-card-label">Total Rounds Practiced</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-card-value">{avg}</div>
                            <div class="stat-card-label">Average Score</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-card-value">{best}</div>
                            <div class="stat-card-label">Best Score Ever</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-card-value" style="font-size:1.4rem;margin-top:10px">{ts}</div>
                            <div class="stat-card-label" style="margin-top:12px">Total Sessions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-card-value" style="font-size:1.4rem;margin-top:10px">{most}</div>
                            <div class="stat-card-label" style="margin-top:12px">Top Scenario</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-card-value" style="font-size:1.4rem;margin-top:10px">{trend}</div>
                            <div class="stat-card-label" style="margin-top:12px">Improvement Trend</div>
                        </div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            # --- Weekly Progress Chart ---
            st.markdown('<div class="dash-section-title">Your Progress This Week</div>', unsafe_allow_html=True)
            weekly_data = data_manager.get_weekly_data(user_email)
            if any(weekly_data["avg_scores"]):
                if PLOTLY_AVAILABLE:
                    fig_weekly = go.Figure()
                    fig_weekly.add_trace(go.Scatter(
                        x=weekly_data["dates"],
                        y=weekly_data["avg_scores"],
                        mode="lines+markers",
                        line=dict(color="#1AF49A", width=3, dash='solid'),
                        marker=dict(size=10, color="#1AF49A", line=dict(color="#111111", width=2)),
                        fill="tozeroy",
                        fillcolor="rgba(26,244,154,0.08)",
                        hovertemplate="Date: %{x}<br>Avg Score: %{y}/10<extra></extra>",
                    ))
                    
                    # Trend line using Simple Linear Regression
                    nonzero_pts = [(i, val) for i, val in enumerate(weekly_data["avg_scores"]) if val > 0]
                    if len(nonzero_pts) > 1:
                        sum_x = sum(pt[0] for pt in nonzero_pts)
                        sum_y = sum(pt[1] for pt in nonzero_pts)
                        sum_xy = sum(pt[0] * pt[1] for pt in nonzero_pts)
                        sum_xx = sum(pt[0] * pt[0] for pt in nonzero_pts)
                        n = len(nonzero_pts)
                        denominator = (n * sum_xx - sum_x * sum_x)
                        if denominator != 0:
                            m = (n * sum_xy - sum_x * sum_y) / denominator
                            b = (sum_y - m * sum_x) / n
                            trend_y = [m * i + b for i in range(7)]
                            fig_weekly.add_trace(go.Scatter(
                                x=weekly_data["dates"],
                                y=trend_y,
                                mode="lines",
                                line=dict(color="#9599A6", width=2, dash='dot'),
                                name="Trend",
                                hoverinfo="skip"
                            ))
                    
                    fig_weekly.update_layout(
                        plot_bgcolor="#111111",
                        paper_bgcolor="#111111",
                        font=dict(color="#9599A6", family="Inter"),
                        xaxis=dict(title="Date", gridcolor="#2a2a2a", tickangle=-45),
                        yaxis=dict(title="Average Score", range=[0, 10.5], gridcolor="#2a2a2a", dtick=1),
                        margin=dict(l=40, r=20, t=20, b=40),
                        height=300,
                        showlegend=False
                    )
                    st.plotly_chart(fig_weekly, use_container_width=True)
                else:
                    import pandas as pd
                    chart_df = pd.DataFrame({"Avg Score": weekly_data["avg_scores"]}, index=weekly_data["dates"])
                    st.line_chart(chart_df)
            else:
                st.info("No scores recorded in the last 7 days.")

    # ── Growth Story (Before vs After) ──
    _render_growth_story()

    # ── AI Insights (Bottom of Dashboard) ──
    insights = data_manager.get_insights(user_email)
    if insights:
        st.markdown('<div class="dash-section-title">AI Insights</div>', unsafe_allow_html=True)
        i_cols = st.columns(3)
        for col, insight in zip(i_cols, insights[:3]):
            with col:
                st.markdown(
                    f'<div class="stat-card" style="text-align:left">'
                    f'<div class="stat-card-value" style="font-size:1.1rem;color:#1AF49A;margin-bottom:12px">{insight["title"]}</div>'
                    f'<div class="stat-card-label" style="line-height:1.6;color:#d0d0d0">{insight["text"]}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Onboarding screen (shown once after signup)
# ---------------------------------------------------------------------------
def show_onboarding():
    user = st.session_state.get("current_user", {})
    first_name = user.get("name", "User").split()[0]

    st.markdown(
        f'''
        <div class="onboard-wrap">
            <div class="onboard-emoji">🎉</div>
            <div class="onboard-title">Welcome, {first_name}!</div>
            <div class="onboard-subtitle">Your confidence journey starts now.</div>

            <div class="onboard-cards">
                <div class="onboard-card">
                    <div class="onboard-card-icon">🎭</div>
                    <div class="onboard-card-text">Pick a Scenario</div>
                </div>
                <div class="onboard-card">
                    <div class="onboard-card-icon">💬</div>
                    <div class="onboard-card-text">Chat with AI Coach</div>
                </div>
                <div class="onboard-card">
                    <div class="onboard-card-icon">📊</div>
                    <div class="onboard-card-text">Track Progress</div>
                </div>
            </div>

            <div class="onboard-stats">
                <span>🌱 Beginner</span>
                <span>·</span>
                <span>0 XP</span>
                <span>·</span>
                <span>🔥 0 Streak</span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("Start Practicing 🚀", use_container_width=True, key="onboard_start"):
            st.session_state.is_new_user = False
            st.session_state.current_page = "🎯 Practice"
            st.rerun()


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------
if st.session_state.logged_in:
    if st.session_state.get("is_new_user"):
        show_onboarding()
    else:
        run_main_app()
else:
    show_login_page()
