import json
import os
import collections
from datetime import datetime, timedelta

DATA_FILE = "user_data.json"


def _load_store() -> dict:
    """Load the entire data store."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}


def _save_store(store: dict) -> None:
    """Save the entire data store."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
    except Exception:
        pass


def load_all_sessions(user_email: str) -> dict:
    store = _load_store()
    user_data = store.get(user_email.lower().strip(), {})
    return {"sessions": user_data.get("sessions", [])}


def save_session(session_data: dict, user_email: str) -> None:
    store = _load_store()
    key = user_email.lower().strip()
    if key not in store:
        store[key] = {"sessions": []}

    sessions = store[key].get("sessions", [])
    session_id = session_data.get("session_id")
    updated = False

    for i, s in enumerate(sessions):
        if s.get("session_id") == session_id:
            sessions[i] = session_data
            updated = True
            break

    if not updated:
        sessions.append(session_data)

    store[key]["sessions"] = sessions
    _save_store(store)


def get_overall_stats(user_email: str) -> dict:
    data = load_all_sessions(user_email)
    sessions = data.get("sessions", [])

    all_time_rounds = 0
    total_score_sum = 0.0
    scored_rounds_count = 0
    all_time_best_score = 0
    scenario_counts = {}
    recent_scores = []

    for session in sessions:
        all_time_rounds += session.get("total_rounds", 0)
        scenario = session.get("scenario", "Unknown")
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + session.get("total_rounds", 0)

        for r in session.get("rounds", []):
            score = r.get("confidence_score")
            if score is not None:
                total_score_sum += score
                scored_rounds_count += 1
                if score > all_time_best_score:
                    all_time_best_score = score
                recent_scores.append(score)

    all_time_avg_score = round(total_score_sum / scored_rounds_count, 1) if scored_rounds_count > 0 else 0.0
    most_practiced_scenario = max(scenario_counts, key=scenario_counts.get) if scenario_counts else "None"
    total_sessions = len(sessions)

    improvement_trend = "Not enough data"
    if len(recent_scores) >= 10:
        recent_5 = sum(recent_scores[-5:]) / 5
        prev_5 = sum(recent_scores[-10:-5]) / 5
        if recent_5 > prev_5:
            improvement_trend = "📈 Improving"
        elif recent_5 < prev_5:
            improvement_trend = "📉 Dipping"
        else:
            improvement_trend = "➡️ Steady"
    elif len(recent_scores) >= 2:
        if recent_scores[-1] >= recent_scores[-2]:
            improvement_trend = "📈 Improving"
        else:
            improvement_trend = "📉 Dipping"

    return {
        "all_time_rounds": all_time_rounds,
        "all_time_avg_score": all_time_avg_score,
        "all_time_best_score": all_time_best_score,
        "most_practiced_scenario": most_practiced_scenario,
        "total_sessions": total_sessions,
        "improvement_trend": improvement_trend,
    }


def clear_all_data(user_email: str) -> None:
    store = _load_store()
    key = user_email.lower().strip()
    if key in store:
        del store[key]
        _save_store(store)


def get_weekly_data(user_email: str) -> dict:
    data = load_all_sessions(user_email)
    sessions = data.get("sessions", [])

    today = datetime.now().date()
    days_data = {(today - timedelta(days=i)).strftime("%Y-%m-%d"): [] for i in range(6, -1, -1)}

    for session in sessions:
        session_date_str = session.get("date", "")
        if not session_date_str:
            continue
        try:
            date_obj = datetime.strptime(session_date_str.split()[0], "%Y-%m-%d").date()
            date_key = date_obj.strftime("%Y-%m-%d")
            if date_key in days_data:
                for r in session.get("rounds", []):
                    score = r.get("confidence_score")
                    if score is not None:
                        days_data[date_key].append(score)
        except Exception:
            pass

    weekly_stats = {"dates": [], "avg_scores": []}
    for d_key, scores in days_data.items():
        weekly_stats["dates"].append(d_key)
        if scores:
            weekly_stats["avg_scores"].append(round(sum(scores) / len(scores), 1))
        else:
            weekly_stats["avg_scores"].append(0.0)

    return weekly_stats


def get_insights(user_email: str) -> list:
    data = load_all_sessions(user_email)
    sessions = data.get("sessions", [])

    if not sessions:
        return []

    insights = []
    scenario_scores = collections.defaultdict(list)
    recent_trend_scores = []
    all_feedback = []

    for session in sessions:
        scenario = session.get("scenario", "Unknown")
        for r in session.get("rounds", []):
            score = r.get("confidence_score")
            if score is not None:
                scenario_scores[scenario].append(score)
                recent_trend_scores.append(score)
            fb = r.get("feedback_points", [])
            if fb:
                all_feedback.extend(fb)

    # 1. Focus Area
    if scenario_scores:
        lowest_scenario = min(scenario_scores.keys(), key=lambda k: sum(scenario_scores[k]) / len(scenario_scores[k]))
        insights.append({
            "title": "🎯 Focus Area",
            "text": f"Your average score in **{lowest_scenario}** is lower than others. Consider dedicating your next session to this scenario to build confidence.",
        })

    # 2. Your Trend
    if len(recent_trend_scores) >= 4:
        recent_3 = sum(recent_trend_scores[-3:]) / 3
        prev_3 = sum(recent_trend_scores[-6:-3]) / 3 if len(recent_trend_scores) >= 6 else sum(recent_trend_scores[:-3]) / len(recent_trend_scores[:-3])
        if recent_3 > prev_3 + 0.5:
            insights.append({"title": "📈 Your Trend", "text": "Great job! Your confidence scores are trending upwards. Keep up the consistent practice – you're visibly improving."})
        elif recent_3 < prev_3 - 0.5:
            insights.append({"title": "📉 Your Trend", "text": "Scores took a slight dip recently. Don't worry! Progress isn't perfectly linear. Take a deep breath and try a simpler scenario next."})
        else:
            insights.append({"title": "➡️ Your Trend", "text": "You're holding steady! To break through to the next level, try focusing on the specific feedback points the AI gave you in recent rounds."})
    elif len(recent_trend_scores) >= 2:
        if recent_trend_scores[-1] > recent_trend_scores[-2]:
            insights.append({"title": "📈 Your Trend", "text": "Your latest score improved compared to the previous one. Keep that momentum going in the next round!"})
        elif recent_trend_scores[-1] < recent_trend_scores[-2]:
            insights.append({"title": "📉 Your Trend", "text": "Your latest score dipped slightly. That's completely normal when trying new techniques. Keep trying!"})
        else:
            insights.append({"title": "➡️ Your Trend", "text": "You're maintaining a steady score. Great consistency!"})
    else:
        insights.append({"title": "📊 Your Trend", "text": "Complete a few more practice rounds to unlock your personalized improvement trend analysis!"})

    # 3. Pro Tip
    if all_feedback:
        fb_text = " ".join(all_feedback).lower()
        if "eye contact" in fb_text:
            tip = "The coach frequently mentions eye contact. Try looking directly at the camera while speaking."
        elif "filler" in fb_text or "um " in fb_text or "uh " in fb_text or "like" in fb_text:
            tip = "Try to pause silently instead of using filler words like 'um' or 'uh'. A deep breath works wonders."
        elif "fast" in fb_text or "pace" in fb_text or "rush" in fb_text:
            tip = "Your speaking pace might be a bit fast. Slow down to give your words more impact and stay relaxed."
        elif "structure" in fb_text or "organize" in fb_text or "star" in fb_text:
            tip = "Use the STAR method (Situation, Task, Action, Result) to give your answers more structured clarity."
        elif "tone" in fb_text or "enthusiasm" in fb_text or "energy" in fb_text:
            tip = "Try injecting a bit more enthusiasm into your tone to sound more engaging and confident."
        else:
            tip = "Always take a brief 2-second pause before answering to gather your thoughts. It makes you appear more thoughtful."

        insights.append({"title": "💡 Pro Tip", "text": tip})

    return insights


def generate_report(user_email: str) -> str:
    data = load_all_sessions(user_email)
    sessions = data.get("sessions", [])
    stats = get_overall_stats(user_email)

    report = []
    report.append("=== AI Social Anxiety Coach — Practice Report ===")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("Team: HustlerDevs | VisionX Hackathon")
    report.append("")

    report.append("OVERALL STATS")
    report.append("-------------")
    report.append(f"Total Sessions: {stats.get('total_sessions', 0)}")
    report.append(f"Total Rounds: {stats.get('all_time_rounds', 0)}")
    report.append(f"Average Score: {stats.get('all_time_avg_score', 0)}/10")
    report.append(f"Best Score: {stats.get('all_time_best_score', 0)}/10")
    report.append("")

    report.append("SESSION HISTORY")
    report.append("---------------")
    for s in reversed(sessions):
        report.append(f"• Session: {s.get('date')} | Scenario: {s.get('scenario')} | Rounds: {s.get('total_rounds')} | Avg Score: {s.get('average_score')}/10")
    report.append("")

    report.append("TOP IMPROVED RESPONSES")
    report.append("----------------------")
    all_scored_rounds = []
    for s in sessions:
        for r in s.get("rounds", []):
            if r.get("confidence_score") is not None:
                r_copy = r.copy()
                r_copy["scenario"] = s.get("scenario")
                all_scored_rounds.append(r_copy)

    top_rounds = sorted(all_scored_rounds, key=lambda x: x.get("confidence_score", 0), reverse=True)[:3]

    if not top_rounds:
        report.append("No scored responses yet.")
    else:
        for i, r in enumerate(top_rounds, 1):
            report.append(f"#{i} — {r.get('scenario')} (Score: {r.get('confidence_score')}/10)")
            report.append(f"Your Response: {r.get('user_message')}")
            report.append(f"AI Improved Version: {r.get('improved_response')}")
            report.append("")

    return "\n".join(report)
