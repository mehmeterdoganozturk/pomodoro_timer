import json
import os
import uuid
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

DEFAULT_PROFILES = {
    "yks": {
        "id": "yks",
        "name": "🎓 YKS / Sınav Hazırlık",
        "description": "Matematik, Geometri, Fizik, Kimya, Paragraf ve Deneme",
        "default_focus": 25,
        "default_short_break": 5,
        "default_long_break": 15,
        "default_daily_goal": 8,
        "subjects": [
            {"id": "mat", "name": "Matematik", "icon": "📐", "color": "#3B82F6", "badge": "AYT/TYT", "visible": True},
            {"id": "geo", "name": "Geometri", "icon": "📏", "color": "#06B6D4", "badge": "AYT/TYT", "visible": True},
            {"id": "fiz", "name": "Fizik", "icon": "🔬", "color": "#F59E0B", "badge": "AYT/TYT", "visible": True},
            {"id": "kim", "name": "Kimya", "icon": "🧪", "color": "#10B981", "badge": "AYT/TYT", "visible": True},
            {"id": "turk", "name": "TYT Paragraf / Türkçe", "icon": "📖", "color": "#EC4899", "badge": "TYT", "visible": True},
            {"id": "biy", "name": "Biyoloji", "icon": "🧬", "color": "#84CC16", "badge": "AYT/TYT", "visible": True},
            {"id": "deneme", "name": "Deneme Sınavı", "icon": "📝", "color": "#8B5CF6", "badge": "Genel", "visible": True},
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
            {"id": "code", "name": "Kodlama / Proje", "icon": "💻", "color": "#6366F1", "badge": "Dev", "visible": True},
            {"id": "algo", "name": "Algoritma & Problem", "icon": "⚡", "color": "#F59E0B", "badge": "LeetCode", "visible": True},
            {"id": "arch", "name": "Sistem Mimarisi", "icon": "🏗️", "color": "#06B6D4", "badge": "Design", "visible": True},
            {"id": "debug", "name": "Bugfix & Debugging", "icon": "🐛", "color": "#EF4444", "badge": "Fix", "visible": True},
            {"id": "docs", "name": "Teknik Dokümantasyon", "icon": "📚", "color": "#10B981", "badge": "Docs", "visible": True},
            {"id": "infra", "name": "DevOps & Sunucu", "icon": "⚙️", "color": "#8B5CF6", "badge": "Infra", "visible": True},
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
            {"id": "strat", "name": "Strateji & Planlama", "icon": "🎯", "color": "#3B82F6", "badge": "Plan", "visible": True},
            {"id": "meet", "name": "Toplantı & İletişim", "icon": "👥", "color": "#8B5CF6", "badge": "Team", "visible": True},
            {"id": "report", "name": "Raporlama & Analiz", "icon": "📊", "color": "#10B981", "badge": "Data", "visible": True},
            {"id": "tasks", "name": "Operasyon & Görevler", "icon": "📋", "color": "#F59E0B", "badge": "Ops", "visible": True},
            {"id": "emails", "name": "E-Posta & İletişim", "icon": "✉️", "color": "#EC4899", "badge": "Mail", "visible": True},
        ]
    }
}

PROFILES_DATA = DEFAULT_PROFILES

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
    "profiles": DEFAULT_PROFILES
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
                    # Ensure profiles exists
                    if "profiles" not in cfg or not cfg["profiles"]:
                        cfg["profiles"] = DEFAULT_PROFILES.copy()
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

    # --- Profile Management ---
    def get_profiles(self) -> Dict[str, Any]:
        return self.config.get("profiles", DEFAULT_PROFILES)

    def get_active_profile(self) -> Dict[str, Any]:
        pid = self.config.get("active_profile", "yks")
        profiles = self.get_profiles()
        if pid in profiles:
            return profiles[pid]
        return profiles.get("yks", DEFAULT_PROFILES["yks"])

    def set_active_profile(self, profile_id: str):
        profiles = self.get_profiles()
        if profile_id in profiles:
            self.config["active_profile"] = profile_id
            prof = profiles[profile_id]
            self.config["focus_duration"] = prof.get("default_focus", 25)
            self.config["short_break_duration"] = prof.get("default_short_break", 5)
            self.config["long_break_duration"] = prof.get("default_long_break", 15)
            self.config["daily_goal"] = prof.get("default_daily_goal", 8)

            # Select first visible subject
            visible_subs = [s for s in prof.get("subjects", []) if s.get("visible", True)]
            if visible_subs:
                self.config["selected_subject_id"] = visible_subs[0]["id"]
            elif prof.get("subjects"):
                self.config["selected_subject_id"] = prof["subjects"][0]["id"]

            self.save_config()

    def create_profile(self, name: str, description: str, default_focus: int = 25, default_break: int = 5, default_goal: int = 8) -> str:
        pid = "prof_" + uuid.uuid4().hex[:6]
        new_prof = {
            "id": pid,
            "name": name,
            "description": description,
            "default_focus": default_focus,
            "default_short_break": default_break,
            "default_long_break": 15,
            "default_daily_goal": default_goal,
            "subjects": [
                {"id": f"{pid}_sub1", "name": "Genel Çalışma", "icon": "🎯", "color": "#3B82F6", "badge": "Ana", "visible": True}
            ]
        }
        self.config.setdefault("profiles", {})[pid] = new_prof
        self.set_active_profile(pid)
        return pid

    def delete_profile(self, profile_id: str) -> bool:
        profiles = self.get_profiles()
        if profile_id in profiles and len(profiles) > 1:
            del profiles[profile_id]
            # If deleted profile was active, switch to first remaining
            if self.config.get("active_profile") == profile_id:
                new_pid = next(iter(profiles.keys()))
                self.set_active_profile(new_pid)
            else:
                self.save_config()
            return True
        return False

    # --- Subject Management (CRUD + Visibility) ---
    def get_subjects(self, only_visible: bool = False) -> List[Dict[str, Any]]:
        prof = self.get_active_profile()
        subs = prof.get("subjects", [])
        if only_visible:
            return [s for s in subs if s.get("visible", True)]
        return subs

    def get_selected_subject(self) -> Dict[str, Any]:
        sub_id = self.config.get("selected_subject_id", "")
        subjects = self.get_subjects(only_visible=False)
        for s in subjects:
            if s["id"] == sub_id:
                return s
        # Fallback to first visible or first
        visible = [s for s in subjects if s.get("visible", True)]
        if visible:
            return visible[0]
        if subjects:
            return subjects[0]
        return {"id": "genel", "name": "Ders Çalışma", "icon": "🎯", "color": "#3B82F6", "badge": "Genel", "visible": True}

    def set_selected_subject(self, subject_id: str):
        self.config["selected_subject_id"] = subject_id
        self.save_config()

    def add_subject(self, name: str, icon: str, color: str, badge: str = "", visible: bool = True) -> Dict[str, Any]:
        prof = self.get_active_profile()
        sub_id = "sub_" + uuid.uuid4().hex[:6]
        new_sub = {
            "id": sub_id,
            "name": name.strip(),
            "icon": icon.strip() or "📚",
            "color": color or "#3B82F6",
            "badge": badge.strip(),
            "visible": visible
        }
        prof.setdefault("subjects", []).append(new_sub)
        self.save_config()
        return new_sub

    def update_subject(self, subject_id: str, name: str, icon: str, color: str, badge: str = "", visible: bool = True):
        prof = self.get_active_profile()
        for s in prof.get("subjects", []):
            if s["id"] == subject_id:
                s["name"] = name.strip()
                s["icon"] = icon.strip() or "📚"
                s["color"] = color or "#3B82F6"
                s["badge"] = badge.strip()
                s["visible"] = visible
                break
        self.save_config()

    def delete_subject(self, subject_id: str) -> bool:
        prof = self.get_active_profile()
        subs = prof.get("subjects", [])
        if len(subs) <= 1:
            return False  # Don't delete last subject

        prof["subjects"] = [s for s in subs if s["id"] != subject_id]
        if self.config.get("selected_subject_id") == subject_id:
            rem = [s for s in prof["subjects"] if s.get("visible", True)]
            if rem:
                self.config["selected_subject_id"] = rem[0]["id"]
            else:
                self.config["selected_subject_id"] = prof["subjects"][0]["id"]

        self.save_config()
        return True

    def toggle_subject_visibility(self, subject_id: str, visible: bool):
        prof = self.get_active_profile()
        for s in prof.get("subjects", []):
            if s["id"] == subject_id:
                s["visible"] = visible
                break
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
        today = date.today()
        current_streak = 0
        best_streak = 0
        temp_streak = 0

        sorted_dates = sorted(
            [datetime.strptime(d, "%Y-%m-%d").date() for d in self.history.keys()]
        )

        if sorted_dates:
            prev = None
            for d in sorted_dates:
                entry = self.history.get(d.isoformat(), {})
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

        check_day = today
        today_pomo = self.stats.get("today_pomodoros", 0)
        if today_pomo > 0:
            current_streak += 1
            check_day = today - timedelta(days=1)
        else:
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
        results = []
        today = date.today()
        goal = self.config.get("daily_goal", 8)

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
