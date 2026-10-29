import json
import os
from datetime import date
from typing import Dict, Any

DEFAULT_CONFIG = {
    "focus_duration": 25,         # minutes
    "short_break_duration": 5,    # minutes
    "long_break_duration": 15,    # minutes
    "long_break_interval": 4,     # Every 4 pomodoros
    "auto_start_breaks": False,
    "auto_start_pomodoros": False,
    "sound_enabled": True,
    "notifications_enabled": True,
    "current_task": "Ders Çalışma",
    "daily_goal": 8,              # Pomodoro target
    "mini_mode": False,
}

class StorageManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/pomodoro-focus-pro")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.stats_file = os.path.join(self.config_dir, "stats.json")
        
        self.config = self._load_config()
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

    def _load_stats(self) -> Dict[str, Any]:
        today_str = date.today().isoformat()
        default_stats = {
            "date": today_str,
            "today_pomodoros": 0,
            "today_breaks": 0,
            "today_focus_seconds": 0,
            "streak_days": 1,
            "lifetime_pomodoros": 0,
            "lifetime_focus_seconds": 0
        }
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Check if today is a new day
                    if data.get("date") != today_str:
                        # Rollover today's counts, preserve lifetime
                        lifetime_p = data.get("lifetime_pomodoros", 0) + data.get("today_pomodoros", 0)
                        lifetime_s = data.get("lifetime_focus_seconds", 0) + data.get("today_focus_seconds", 0)
                        data["date"] = today_str
                        data["today_pomodoros"] = 0
                        data["today_breaks"] = 0
                        data["today_focus_seconds"] = 0
                        data["lifetime_pomodoros"] = lifetime_p
                        data["lifetime_focus_seconds"] = lifetime_s
                    return data
            except Exception:
                pass
        return default_stats

    def save_stats(self):
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def record_completed_pomodoro(self, seconds: int):
        self._check_date_rollover()
        self.stats["today_pomodoros"] += 1
        self.stats["today_focus_seconds"] += seconds
        self.stats["lifetime_pomodoros"] = self.stats.get("lifetime_pomodoros", 0) + 1
        self.stats["lifetime_focus_seconds"] = self.stats.get("lifetime_focus_seconds", 0) + seconds
        self.save_stats()

    def record_completed_break(self):
        self._check_date_rollover()
        self.stats["today_breaks"] += 1
        self.save_stats()

    def reset_today_stats(self):
        self.stats["today_pomodoros"] = 0
        self.stats["today_breaks"] = 0
        self.stats["today_focus_seconds"] = 0
        self.save_stats()

    def _check_date_rollover(self):
        today_str = date.today().isoformat()
        if self.stats.get("date") != today_str:
            self.stats["date"] = today_str
            self.stats["today_pomodoros"] = 0
            self.stats["today_breaks"] = 0
            self.stats["today_focus_seconds"] = 0
