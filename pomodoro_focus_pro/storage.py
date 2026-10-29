import json
import os
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

PROFILES_DATA = {
    "yks": {
        "id": "yks",
        "name": "🎓 YKS / Sınav Hazırlık",
        "description": "Matematik, Fizik, Kimya, Geometri, Paragraf ve Deneme",
        "default_focus": 25,
        "default_short_break": 5,
        "default_long_break": 15,
        "default_daily_goal": 8,
        "subjects": [
            {"id": "mat", "name": "Matematik", "icon": "📐", "color": "#3B82F6", "badge": "AYT/TYT"},
            {"id": "geo", "name": "Geometri", "icon": "📏", "color": "#06B6D4", "badge": "AYT/TYT"},
            {"id": "fiz", "name": "Fizik", "icon": "🔬", "color": "#F59E0B", "badge": "AYT/TYT"},
            {"id": "kim", "name": "Kimya", "icon": "🧪", "color": "#10B981", "badge": "AYT/TYT"},
            {"id": "turk", "name": "TYT Paragraf / Türkçe", "icon": "📖", "color": "#EC4899", "badge": "TYT"},
            {"id": "biy", "name": "Biyoloji", "icon": "🧬", "color": "#84CC16", "badge": "AYT/TYT"},
            {"id": "deneme", "name": "Deneme Sınavı", "icon": "📝", "color": "#8B5CF6", "badge": "Genel"},
        ]
    },
    "engineering": {
        "id": "engineering",
        "name": "💻 Mühendislik & IT",
        "description": "Kodlama, Algoritma, Sistem Mimarisi ve Debugging",
        "default_focus": 50,
        "default_short_break": 10,
        "default_long_break": 20,
        "default_daily_goal": 6,
        "subjects": [
            {"id": "code", "name": "Kodlama / Proje", "icon": "💻", "color": "#6366F1", "badge": "Dev"},
            {"id": "algo", "name": "Algoritma & Problem", "icon": "⚡", "color": "#F59E0B", "badge": "LeetCode"},
            {"id": "arch", "name": "Sistem Mimarisi", "icon": "🏗️", "color": "#06B6D4", "badge": "Design"},
            {"id": "debug", "name": "Bugfix & Debugging", "icon": "🐛", "color": "#EF4444", "badge": "Fix"},
            {"id": "docs", "name": "Teknik Dokümantasyon", "icon": "📚", "color": "#10B981", "badge": "Docs"},
            {"id": "infra", "name": "DevOps & Sunucu", "icon": "⚙️", "color": "#8B5CF6", "badge": "Infra"},
        ]
    },
    "business": {
        "id": "business",
        "name": "💼 İş & Yönetim",
        "description": "Strateji, Toplantı, Raporlama ve Operasyon",
        "default_focus": 30,
        "default_short_break": 5,
        "default_long_break": 15,
        "default_daily_goal": 6,
        "subjects": [
            {"id": "strat", "name": "Strateji & Planlama", "icon": "🎯", "color": "#3B82F6", "badge": "Plan"},
            {"id": "meet", "name": "Toplantı & İletişim", "icon": "👥", "color": "#8B5CF6", "badge": "Team"},
            {"id": "report", "name": "Raporlama & Analiz", "icon": "📊", "color": "#10B981", "badge": "Data"},
            {"id": "tasks", "name": "Operasyon & Görevler", "icon": "📋", "color": "#F59E0B", "badge": "Ops"},
            {"id": "emails", "name": "E-Posta & İletişim", "icon": "✉️", "color": "#EC4899", "badge": "Mail"},
        ]
    }
}

DEFAULT_CONFIG = {
    "active_profile": "yks",
    "selected_subject_id": "mat",
    "focus_duration": 25,
    "short_break_duration": 5,
    "long_break_duration": 15,
    "long_break_interval": 4,
    "auto_start_breaks": False,
    "auto_start_pomodoros": False,
    "sound_enabled": True,
    "notifications_enabled": True,
    "daily_goal": 8,
    "mini_mode": False,
    "profiles_custom": {}
}

class StorageManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/pomodoro-focus-pro")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.stats_file = os.path.join(self.config_dir, "stats.json")
        self.history_file = os.path.join(self.config_dir, "history.json")

        self.config = self._load_config()
        self.history = self._load_history()
        self.stats = self._load_stats()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cfg = DEFAULT_CONFIG.copy()
                    cfg.update(data)
                    return cfg
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _load_history(self) -> Dict[str, Any]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def _load_stats(self) -> Dict[str, Any]:
        today_str = date.today().isoformat()
        if today_str not in self.history:
            self.history[today_str] = {
                "pomodoros": 0,
                "breaks": 0,
                "focus_seconds": 0,
                "subjects": {},
                "goal_achieved": False
            }
            self.save_history()

        day_data = self.history[today_str]
        return {
            "date": today_str,
            "today_pomodoros": day_data.get("pomodoros", 0),
            "today_breaks": day_data.get("breaks", 0),
            "today_focus_seconds": day_data.get("focus_seconds", 0),
            "today_subjects": day_data.get("subjects", {}),
        }

    def save_stats(self):
        today_str = date.today().isoformat()
        goal = self.config.get("daily_goal", 8)
        achieved = self.stats["today_pomodoros"] >= goal

        self.history[today_str] = {
            "pomodoros": self.stats["today_pomodoros"],
            "breaks": self.stats["today_breaks"],
            "focus_seconds": self.stats["today_focus_seconds"],
            "subjects": self.stats.get("today_subjects", {}),
            "goal_achieved": achieved
        }
        self.save_history()

    # --- Profile & Subject Management ---
    def get_active_profile(self) -> Dict[str, Any]:
        pid = self.config.get("active_profile", "yks")
        custom = self.config.get("profiles_custom", {}).get(pid)
        if custom:
            return custom
        return PROFILES_DATA.get(pid, PROFILES_DATA["yks"])

    def set_active_profile(self, profile_id: str):
        if profile_id in PROFILES_DATA:
            self.config["active_profile"] = profile_id
            prof = PROFILES_DATA[profile_id]
            self.config["focus_duration"] = prof["default_focus"]
            self.config["short_break_duration"] = prof["default_short_break"]
            self.config["long_break_duration"] = prof["default_long_break"]
            self.config["daily_goal"] = prof["default_daily_goal"]
            if prof["subjects"]:
                self.config["selected_subject_id"] = prof["subjects"][0]["id"]
            self.save_config()

    def get_subjects(self) -> List[Dict[str, Any]]:
        prof = self.get_active_profile()
        return prof.get("subjects", [])

    def get_selected_subject(self) -> Dict[str, Any]:
        sub_id = self.config.get("selected_subject_id", "mat")
        subjects = self.get_subjects()
        for s in subjects:
            if s["id"] == sub_id:
                return s
        if subjects:
            return subjects[0]
        return {"id": "genel", "name": "Genel Çalışma", "icon": "🎯", "color": "#3B82F6", "badge": "Genel"}

    def set_selected_subject(self, subject_id: str):
        self.config["selected_subject_id"] = subject_id
        self.save_config()

    # --- Record Progress ---
    def record_completed_pomodoro(self, seconds: int, subject_id: str):
        self._check_date_rollover()
        self.stats["today_pomodoros"] += 1
        self.stats["today_focus_seconds"] += seconds

        sub_map = self.stats.setdefault("today_subjects", {})
        sub_map[subject_id] = sub_map.get(subject_id, 0) + seconds

        self.save_stats()

    def record_completed_break(self):
        self._check_date_rollover()
        self.stats["today_breaks"] += 1
        self.save_stats()

    def _check_date_rollover(self):
        today_str = date.today().isoformat()
        if self.stats.get("date") != today_str:
            self.stats = self._load_stats()

    # --- Streak & Heatmap Calculations ---
    def calculate_streak(self) -> Dict[str, Any]:
        """
        Calculates consecutive study days (Zinciri Kırma).
        Returns current streak, best streak, and whether today's goal was met.
        """
        today = date.today()
        current_streak = 0
        best_streak = 0
        temp_streak = 0

        # Sort all historical dates
        sorted_dates = sorted(
            [datetime.strptime(d, "%Y-%m-%d").date() for d in self.history.keys()]
        )

        # Calculate best streak historically
        if sorted_dates:
            prev = None
            for d in sorted_dates:
                entry = self.history.get(d.isoformat(), {})
                # Consider active if user completed >= 1 pomodoro
                if entry.get("pomodoros", 0) > 0:
                    if prev and (d - prev).days == 1:
                        temp_streak += 1
                    else:
                        temp_streak = 1
                    prev = d
                    if temp_streak > best_streak:
                        best_streak = temp_streak
                else:
                    prev = None
                    temp_streak = 0

        # Calculate current active streak backwards from today
        check_day = today
        # Check if today has study
        today_pomo = self.stats.get("today_pomodoros", 0)
        if today_pomo > 0:
            current_streak += 1
            check_day = today - timedelta(days=1)
        else:
            # If today not yet, check yesterday to preserve streak
            check_day = today - timedelta(days=1)

        while True:
            day_str = check_day.isoformat()
            if day_str in self.history and self.history[day_str].get("pomodoros", 0) > 0:
                current_streak += 1
                check_day -= timedelta(days=1)
            else:
                break

        if current_streak > best_streak:
            best_streak = current_streak

        goal = self.config.get("daily_goal", 8)
        goal_met = today_pomo >= goal

        return {
            "current_streak": current_streak,
            "best_streak": max(best_streak, current_streak),
            "today_pomodoros": today_pomo,
            "goal": goal,
            "goal_met": goal_met,
            "remaining_to_goal": max(0, goal - today_pomo)
        }

    def get_past_days_data(self) -> List[Dict[str, Any]]:
        """
        Returns list of day entries for 4 full weeks (Mon-Sun) for heatmap drawing.
        """
        results = []
        today = date.today()
        goal = self.config.get("daily_goal", 8)

        # Align to 4 full weeks ending on Sunday of current week
        days_to_sunday = 6 - today.weekday()
        end_date = today + timedelta(days=days_to_sunday)
        start_date = end_date - timedelta(days=27)

        day_names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

        for i in range(28):
            d = start_date + timedelta(days=i)
            d_str = d.isoformat()
            is_today = (d == today)
            is_future = (d > today)

            if is_today:
                pomo = self.stats.get("today_pomodoros", 0)
                sec = self.stats.get("today_focus_seconds", 0)
            elif is_future:
                pomo = 0
                sec = 0
            else:
                entry = self.history.get(d_str, {})
                pomo = entry.get("pomodoros", 0)
                sec = entry.get("focus_seconds", 0)

            if is_future:
                level = -1
            elif pomo == 0:
                level = 0
            elif pomo < goal * 0.4:
                level = 1
            elif pomo < goal * 0.8:
                level = 2
            elif pomo < goal:
                level = 3
            else:
                level = 4

            results.append({
                "date": d_str,
                "day_name": day_names[d.weekday()],
                "day_num": d.day,
                "pomodoros": pomo,
                "focus_seconds": sec,
                "level": level,
                "is_today": is_today,
                "is_future": is_future
            })
        return results

    def reset_today_stats(self):
        today_str = date.today().isoformat()
        self.stats["today_pomodoros"] = 0
        self.stats["today_breaks"] = 0
        self.stats["today_focus_seconds"] = 0
        self.stats["today_subjects"] = {}
        if today_str in self.history:
            self.history[today_str] = {
                "pomodoros": 0,
                "breaks": 0,
                "focus_seconds": 0,
                "subjects": {},
                "goal_achieved": False
            }
            self.save_history()
        self.save_stats()
