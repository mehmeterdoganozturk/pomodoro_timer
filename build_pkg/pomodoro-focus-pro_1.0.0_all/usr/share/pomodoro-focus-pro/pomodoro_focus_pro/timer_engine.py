import time
from gi.repository import GLib

MODE_FOCUS = "focus"
MODE_SHORT_BREAK = "short_break"
MODE_LONG_BREAK = "long_break"

STATE_STOPPED = "stopped"
STATE_RUNNING = "running"
STATE_PAUSED = "paused"

class TimerEngine:
    def __init__(self, storage_manager, sound_player, notifier):
        self.storage = storage_manager
        self.sound = sound_player
        self.notifier = notifier

        self.mode = MODE_FOCUS
        self.state = STATE_STOPPED

        self.session_count = 0
        self.total_duration_seconds = self._get_mode_duration_seconds(self.mode)
        self.remaining_seconds = float(self.total_duration_seconds)
        self.last_tick_time = None

        self._glib_source_id = None
        self.on_tick_callbacks = []
        self.on_state_change_callbacks = []
        self.on_mode_change_callbacks = []
        self.on_complete_callbacks = []

    def _get_mode_duration_seconds(self, mode: str) -> int:
        cfg = self.storage.config
        if mode == MODE_FOCUS:
            return cfg.get("focus_duration", 25) * 60
        elif mode == MODE_SHORT_BREAK:
            return cfg.get("short_break_duration", 5) * 60
        elif mode == MODE_LONG_BREAK:
            return cfg.get("long_break_duration", 15) * 60
        return 25 * 60

    def get_progress_ratio(self) -> float:
        if self.total_duration_seconds <= 0:
            return 0.0
        elapsed = self.total_duration_seconds - self.remaining_seconds
        ratio = elapsed / float(self.total_duration_seconds)
        return max(0.0, min(1.0, ratio))

    def get_formatted_time(self) -> str:
        secs = int(max(0, round(self.remaining_seconds)))
        m = secs // 60
        s = secs % 60
        return f"{m:02d}:{s:02d}"

    def set_mode(self, new_mode: str, auto_start: bool = False):
        if self._glib_source_id:
            GLib.source_remove(self._glib_source_id)
            self._glib_source_id = None

        self.mode = new_mode
        self.state = STATE_STOPPED
        self.total_duration_seconds = self._get_mode_duration_seconds(new_mode)
        self.remaining_seconds = float(self.total_duration_seconds)
        self.last_tick_time = None

        self._notify_mode_change()
        self._notify_tick()

        if auto_start:
            self.start()

    def start(self):
        if self.state == STATE_RUNNING:
            return

        self.state = STATE_RUNNING
        self.last_tick_time = time.monotonic()

        if not self._glib_source_id:
            self._glib_source_id = GLib.timeout_add(200, self._on_timer_tick)

        self._notify_state_change()

    def pause(self):
        if self.state != STATE_RUNNING:
            return

        self.state = STATE_PAUSED
        if self._glib_source_id:
            GLib.source_remove(self._glib_source_id)
            self._glib_source_id = None

        self._notify_state_change()

    def toggle(self):
        if self.state == STATE_RUNNING:
            self.pause()
        else:
            self.start()

    def reset(self):
        if self._glib_source_id:
            GLib.source_remove(self._glib_source_id)
            self._glib_source_id = None

        self.state = STATE_STOPPED
        self.total_duration_seconds = self._get_mode_duration_seconds(self.mode)
        self.remaining_seconds = float(self.total_duration_seconds)
        self.last_tick_time = None

        self._notify_state_change()
        self._notify_tick()

    def skip(self):
        self._advance_to_next_mode(completed=False)

    def _on_timer_tick(self) -> bool:
        if self.state != STATE_RUNNING:
            self._glib_source_id = None
            return False

        now = time.monotonic()
        delta = now - self.last_tick_time
        self.last_tick_time = now

        self.remaining_seconds -= delta

        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0.0
            self._notify_tick()
            self._handle_completed()
            self._glib_source_id = None
            return False

        self._notify_tick()
        return True

    def _handle_completed(self):
        self.state = STATE_STOPPED
        current_mode = self.mode

        if current_mode == MODE_FOCUS:
            self.session_count += 1
            focus_sec = self.total_duration_seconds

            subject = self.storage.get_selected_subject()
            sub_id = subject.get("id", "genel")
            sub_name = subject.get("name", "Ders Çalışma")
            sub_icon = subject.get("icon", "🎯")

            self.storage.record_completed_pomodoro(focus_sec, sub_id)
            self.sound.play_focus_complete()

            interval = self.storage.config.get("long_break_interval", 4)
            is_long = (self.session_count % interval == 0)
            break_mins = self.storage.config.get("long_break_duration" if is_long else "short_break_duration", 15 if is_long else 5)
            self.notifier.notify_focus_finished(sub_name, sub_icon, break_mins, is_long_break=is_long)

            next_mode = MODE_LONG_BREAK if is_long else MODE_SHORT_BREAK
            auto_start = self.storage.config.get("auto_start_breaks", False)
            self._advance_to_next_mode(completed=True, next_mode=next_mode, auto_start=auto_start)

        else:
            self.storage.record_completed_break()
            self.sound.play_break_complete()
            self.notifier.notify_break_finished()

            auto_start = self.storage.config.get("auto_start_pomodoros", False)
            self._advance_to_next_mode(completed=True, next_mode=MODE_FOCUS, auto_start=auto_start)

        for cb in self.on_complete_callbacks:
            try:
                cb(current_mode)
            except Exception as e:
                print(f"Error in on_complete callback: {e}")

    def _advance_to_next_mode(self, completed: bool = False, next_mode: str = None, auto_start: bool = False):
        if not next_mode:
            if self.mode == MODE_FOCUS:
                interval = self.storage.config.get("long_break_interval", 4)
                is_long = (self.session_count > 0 and self.session_count % interval == 0)
                next_mode = MODE_LONG_BREAK if is_long else MODE_SHORT_BREAK
            else:
                next_mode = MODE_FOCUS

        self.set_mode(next_mode, auto_start=auto_start)

    def _notify_tick(self):
        ratio = self.get_progress_ratio()
        time_str = self.get_formatted_time()
        for cb in self.on_tick_callbacks:
            try:
                cb(time_str, ratio)
            except Exception as e:
                print(f"Error in on_tick callback: {e}")

    def _notify_state_change(self):
        for cb in self.on_state_change_callbacks:
            try:
                cb(self.state)
            except Exception as e:
                print(f"Error in on_state_change callback: {e}")

    def _notify_mode_change(self):
        for cb in self.on_mode_change_callbacks:
            try:
                cb(self.mode)
            except Exception as e:
                print(f"Error in on_mode_change callback: {e}")
