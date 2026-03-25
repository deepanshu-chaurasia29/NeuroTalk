import json
import hashlib
import uuid
import os
from datetime import datetime, timedelta

FILE = "users.json"


def load_users() -> list:
    """Load users from users.json and return the users list."""
    try:
        if not os.path.exists(FILE):
            return []
        with open(FILE, "r") as f:
            data = json.load(f)
        return data.get("users", [])
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users: {e}")
        return []


def save_users(users: list) -> None:
    """Save users list to users.json with indent=2."""
    try:
        with open(FILE, "w") as f:
            json.dump({"users": users}, f, indent=2)
    except IOError as e:
        print(f"Error saving users: {e}")


def find_user(email: str) -> dict | None:
    """Find a user by email (case-insensitive). Returns user dict or None."""
    try:
        users = load_users()
        email_lower = email.lower().strip()
        for user in users:
            if user.get("email", "").lower() == email_lower:
                return user
        return None
    except Exception as e:
        print(f"Error finding user: {e}")
        return None


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 and return the hex string."""
    try:
        return hashlib.sha256(password.encode()).hexdigest()
    except Exception as e:
        print(f"Error hashing password: {e}")
        return ""


def create_user(name: str, email: str, password: str) -> dict:
    """Create a new user. Raises ValueError if email already exists."""
    try:
        if find_user(email):
            raise ValueError("Email already registered")

        user = {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "email": email.lower().strip(),
            "password": hash_password(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_sessions": 0,
            "total_rounds": 0,
            "best_score": 0,
            "average_score": 0.0,
            "current_streak": 0,
            "longest_streak": 0,
            "last_practice_date": "",
            "level": "Beginner",
            "xp": 0,
            "first_response": {"text": "", "score": 0, "scenario": ""},
            "latest_response": {"text": "", "score": 0, "scenario": ""}
        }

        users = load_users()
        users.append(user)
        save_users(users)
        return user
    except ValueError:
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        raise


def login_user(email: str, password: str) -> dict | None:
    """Authenticate a user. Returns user dict on success, None on failure."""
    try:
        user = find_user(email)
        if user is None:
            return None

        if user.get("password") != hash_password(password):
            return None

        # Update last_login
        users = load_users()
        for u in users:
            if u.get("email") == user["email"]:
                u["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                break
        save_users(users)

        user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        return user
    except Exception as e:
        print(f"Error during login: {e}")
        return None


def update_streak(email: str) -> int:
    """Update the user's practice streak. Returns current streak."""
    try:
        users = load_users()
        user = None
        for u in users:
            if u.get("email", "").lower() == email.lower().strip():
                user = u
                break

        if user is None:
            return 0

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        last_practice = user.get("last_practice_date", "")

        if last_practice == today:
            # Already practiced today, streak unchanged
            return user.get("current_streak", 0)
        elif last_practice == yesterday:
            user["current_streak"] = user.get("current_streak", 0) + 1
        else:
            user["current_streak"] = 1

        user["last_practice_date"] = today

        if user["current_streak"] > user.get("longest_streak", 0):
            user["longest_streak"] = user["current_streak"]

        save_users(users)
        return user["current_streak"]
    except Exception as e:
        print(f"Error updating streak: {e}")
        return 0


def update_user_stats(email: str, rounds: int,
                      avg_score: float, best: int,
                      user_response: str = "",
                      scenario: str = "") -> None:
    """Update user statistics after a session."""
    try:
        users = load_users()
        user = None
        for u in users:
            if u.get("email", "").lower() == email.lower().strip():
                user = u
                break

        if user is None:
            return

        # Increment sessions
        user["total_sessions"] = user.get("total_sessions", 0) + 1

        # Add rounds
        old_total_rounds = user.get("total_rounds", 0)
        user["total_rounds"] = old_total_rounds + rounds

        # Recalculate running average score
        old_avg = user.get("average_score", 0.0)
        total_sessions = user["total_sessions"]
        if total_sessions > 1:
            user["average_score"] = round(
                ((old_avg * (total_sessions - 1)) + avg_score) / total_sessions, 2
            )
        else:
            user["average_score"] = round(avg_score, 2)

        # Update best score
        if best > user.get("best_score", 0):
            user["best_score"] = best

        # Add XP
        gained_xp = int(rounds * 10 + avg_score * 5)
        user["xp"] = user.get("xp", 0) + gained_xp

        # Recalculate level
        xp = user["xp"]
        if xp >= 600:
            user["level"] = "Expert"
        elif xp >= 300:
            user["level"] = "Advanced"
        elif xp >= 100:
            user["level"] = "Intermediate"
        else:
            user["level"] = "Beginner"

        # Save first and latest response
        if user_response:
            if not user.get("first_response", {}).get("text"):
                user["first_response"] = {
                    "text": user_response,
                    "score": best,
                    "scenario": scenario
                }
            user["latest_response"] = {
                "text": user_response,
                "score": best,
                "scenario": scenario
            }

        save_users(users)
    except Exception as e:
        print(f"Error updating user stats: {e}")
