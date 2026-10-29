import os
import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')

from gi.repository import Gtk, Adw, Gdk, GLib, Pango
from .storage import StorageManager
from .sound_player import SoundPlayer
from .notifier import DesktopNotifier
from .timer_engine import TimerEngine, MODE_FOCUS, MODE_SHORT_BREAK, MODE_LONG_BREAK, STATE_RUNNING, STATE_PAUSED, STATE_STOPPED
from .circular_ring import CircularProgressRing
from .settings_dialog import SettingsDialog

APP_ID = "com.github.erdogan.PomodoroFocusPro"

class PomodoroApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = PomodoroMainWindow(self)
        self.window.present()

class PomodoroMainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.storage = StorageManager()
        self.sound = SoundPlayer(self.storage)
        self.notifier = DesktopNotifier(self.storage)
        self.timer = TimerEngine(self.storage, self.sound, self.notifier)

        self.is_mini_mode = self.storage.config.get("mini_mode", False)

        # Force dark mode
        style_mgr = Adw.StyleManager.get_default()
        style_mgr.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

        self.set_title("Pomodoro Focus Pro")
        self.set_default_size(520, 680)
        self.add_css_class("pomodoro-window")

        # Load Custom CSS
        self._load_css()

        # Connect Timer Engine callbacks
        self.timer.on_tick_callbacks.append(self._on_tick)
        self.timer.on_state_change_callbacks.append(self._on_state_change)
        self.timer.on_mode_change_callbacks.append(self._on_mode_change)
        self.timer.on_complete_callbacks.append(self._on_session_complete)

        # Build UI
        self._build_ui()
        self._setup_shortcuts()

        # Initial view sync
        self._update_mode_tabs(self.timer.mode)
        self._update_start_button_style()
        self._update_stats_display()

        # Apply mini mode state if saved
        if self.is_mini_mode:
            self._apply_mini_mode(True)

    def _load_css(self):
        css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pomodoro.css")
        if os.path.exists(css_file):
            provider = Gtk.CssProvider()
            provider.load_from_path(css_file)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _setup_shortcuts(self):
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_ctrl)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_space:
            self.timer.toggle()
            return True
        elif keyval in (Gdk.KEY_r, Gdk.KEY_R):
            self.timer.reset()
            return True
        elif keyval in (Gdk.KEY_s, Gdk.KEY_S, Gdk.KEY_n, Gdk.KEY_N):
            self.timer.skip()
            return True
        elif keyval in (Gdk.KEY_m, Gdk.KEY_M):
            self._toggle_mini_mode()
            return True
        return False

    def _build_ui(self):
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        # Main Root Box
        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.toast_overlay.set_child(self.root_box)

        # 1. Header Bar
        self.header_bar = Adw.HeaderBar()
        self.header_bar.add_css_class("pomodoro-header")
        self.root_box.append(self.header_bar)

        # Header Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_box.set_halign(Gtk.Align.CENTER)
        icon_img = Gtk.Image.new_from_icon_name("alarm-symbolic")
        title_lbl = Gtk.Label(label="Pomodoro Focus Pro")
        title_lbl.add_css_class("title-pill")
        title_box.append(icon_img)
        title_box.append(title_lbl)
        self.header_bar.set_title_widget(title_box)

        # Left Header: Mini Mode Toggle
        self.mini_mode_btn = Gtk.Button(icon_name="view-restore-symbolic")
        self.mini_mode_btn.set_tooltip_text("Kompakt / Mini Mod (M)")
        self.mini_mode_btn.connect("clicked", lambda b: self._toggle_mini_mode())
        self.header_bar.pack_start(self.mini_mode_btn)

        # Right Header: Settings Button
        self.settings_btn = Gtk.Button(icon_name="emblem-system-symbolic")
        self.settings_btn.set_tooltip_text("Ayarlar")
        self.settings_btn.connect("clicked", self._open_settings)
        self.header_bar.pack_end(self.settings_btn)

        # 2. Main Content Scroller / Box
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.content_box.set_margin_top(14)
        self.content_box.set_margin_bottom(20)
        self.content_box.set_margin_start(24)
        self.content_box.set_margin_end(24)
        self.content_box.set_halign(Gtk.Align.CENTER)
        self.root_box.append(self.content_box)

        # --- Top Mode Switcher Tabs ---
        self.tabs_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.tabs_container.add_css_class("mode-tab-box")
        self.tabs_container.set_halign(Gtk.Align.CENTER)
        self.content_box.append(self.tabs_container)

        self.tab_focus = Gtk.Button(label="🍅 Pomodoro")
        self.tab_focus.add_css_class("mode-tab")
        self.tab_focus.connect("clicked", lambda b: self._select_mode(MODE_FOCUS))
        self.tabs_container.append(self.tab_focus)

        self.tab_short = Gtk.Button(label="☕ Kısa Mola")
        self.tab_short.add_css_class("mode-tab")
        self.tab_short.connect("clicked", lambda b: self._select_mode(MODE_SHORT_BREAK))
        self.tabs_container.append(self.tab_short)

        self.tab_long = Gtk.Button(label="🌴 Uzun Mola")
        self.tab_long.add_css_class("mode-tab")
        self.tab_long.connect("clicked", lambda b: self._select_mode(MODE_LONG_BREAK))
        self.tabs_container.append(self.tab_long)

        # --- Center Cairo Circular Progress Ring ---
        self.ring = CircularProgressRing(self.timer)
        self.content_box.append(self.ring)

        # --- Current Study / Task Pill ---
        self.task_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.task_box.set_halign(Gtk.Align.CENTER)
        self.content_box.append(self.task_box)

        current_task_text = self.storage.config.get("current_task", "Ders Çalışma")
        self.task_btn = Gtk.Button(label=f"🎯 {current_task_text}")
        self.task_btn.add_css_class("task-pill")
        self.task_btn.set_tooltip_text("Çalışma konusunu değiştirmek için tıklayın")
        self.task_btn.connect("clicked", self._edit_task_name)
        self.task_box.append(self.task_btn)

        # --- Primary Action Controls ---
        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        self.controls_box.set_halign(Gtk.Align.CENTER)
        self.content_box.append(self.controls_box)

        # Reset button
        self.reset_btn = Gtk.Button()
        reset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        reset_box.append(Gtk.Image.new_from_icon_name("edit-undo-symbolic"))
        reset_box.append(Gtk.Label(label="Sıfırla"))
        self.reset_btn.set_child(reset_box)
        self.reset_btn.add_css_class("btn-secondary")
        self.reset_btn.set_tooltip_text("Sayacı başa al (R)")
        self.reset_btn.connect("clicked", lambda b: self.timer.reset())
        self.controls_box.append(self.reset_btn)

        # Main Start / Pause button
        self.start_btn = Gtk.Button()
        self.start_btn_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.start_btn_icon = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
        self.start_btn_label = Gtk.Label(label="Başlat")
        self.start_btn_content.append(self.start_btn_icon)
        self.start_btn_content.append(self.start_btn_label)
        self.start_btn.set_child(self.start_btn_content)
        self.start_btn.set_tooltip_text("Başlat / Duraklat (Boşluk Tuşu)")
        self.start_btn.connect("clicked", lambda b: self.timer.toggle())
        self.controls_box.append(self.start_btn)

        # Skip / Next button
        self.skip_btn = Gtk.Button()
        skip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        skip_box.append(Gtk.Image.new_from_icon_name("media-skip-forward-symbolic"))
        skip_box.append(Gtk.Label(label="Sonraki"))
        self.skip_btn.set_child(skip_box)
        self.skip_btn.add_css_class("btn-secondary")
        self.skip_btn.set_tooltip_text("Sonraki aşamaya geç (N)")
        self.skip_btn.connect("clicked", lambda b: self.timer.skip())
        self.controls_box.append(self.skip_btn)

        # --- Bottom Statistics Metric Cards (from reference image) ---
        self.stats_cards_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.stats_cards_container.set_halign(Gtk.Align.CENTER)
        self.stats_cards_container.set_margin_top(8)
        self.content_box.append(self.stats_cards_container)

        # Card 1: Seanslar
        self.card_sessions, self.lbl_sessions_val, self.lbl_sessions_sub = self._create_metric_card(
            "🍅", "0", "SEANSLAR", "Hedef: 8"
        )
        self.stats_cards_container.append(self.card_sessions)

        # Card 2: Odak Süresi
        self.card_focus_time, self.lbl_focus_val, self.lbl_focus_sub = self._create_metric_card(
            "⏱️", "0 dk", "ODAKLANMA", "Bugün"
        )
        self.stats_cards_container.append(self.card_focus_time)

        # Card 3: Molalar
        self.card_breaks, self.lbl_breaks_val, self.lbl_breaks_sub = self._create_metric_card(
            "☕", "0", "MOLALAR", "Bugün"
        )
        self.stats_cards_container.append(self.card_breaks)

    def _create_metric_card(self, icon_str: str, val_str: str, label_str: str, sub_str: str):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card.add_css_class("metric-card")
        card.set_halign(Gtk.Align.CENTER)

        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        icon_lbl = Gtk.Label(label=icon_str)
        lbl_label = Gtk.Label(label=label_str)
        lbl_label.add_css_class("metric-label")
        top_row.append(icon_lbl)
        top_row.append(lbl_label)
        card.append(top_row)

        lbl_val = Gtk.Label(label=val_str)
        lbl_val.add_css_class("metric-value")
        lbl_val.set_halign(Gtk.Align.START)
        card.append(lbl_val)

        lbl_sub = Gtk.Label(label=sub_str)
        lbl_sub.add_css_class("metric-sub")
        lbl_sub.set_halign(Gtk.Align.START)
        card.append(lbl_sub)

        return card, lbl_val, lbl_sub

    def _update_mode_tabs(self, mode: str):
        # Remove active classes
        for btn in (self.tab_focus, self.tab_short, self.tab_long):
            btn.remove_css_class("active-focus")
            btn.remove_css_class("active-short-break")
            btn.remove_css_class("active-long-break")

        if mode == MODE_FOCUS:
            self.tab_focus.add_css_class("active-focus")
        elif mode == MODE_SHORT_BREAK:
            self.tab_short.add_css_class("active-short-break")
        elif mode == MODE_LONG_BREAK:
            self.tab_long.add_css_class("active-long-break")

    def _update_start_button_style(self):
        # Remove any mode classes from start button
        self.start_btn.remove_css_class("btn-primary-focus")
        self.start_btn.remove_css_class("btn-primary-short-break")
        self.start_btn.remove_css_class("btn-primary-long-break")

        if self.timer.mode == MODE_FOCUS:
            self.start_btn.add_css_class("btn-primary-focus")
        elif self.timer.mode == MODE_SHORT_BREAK:
            self.start_btn.add_css_class("btn-primary-short-break")
        elif self.timer.mode == MODE_LONG_BREAK:
            self.start_btn.add_css_class("btn-primary-long-break")

        if self.timer.state == STATE_RUNNING:
            self.start_btn_icon.set_from_icon_name("media-playback-pause-symbolic")
            self.start_btn_label.set_text("Duraklat")
        else:
            self.start_btn_icon.set_from_icon_name("media-playback-start-symbolic")
            self.start_btn_label.set_text("Başlat")

    def _update_stats_display(self):
        stats = self.storage.stats
        p_today = stats.get("today_pomodoros", 0)
        goal = self.storage.config.get("daily_goal", 8)
        self.lbl_sessions_val.set_text(str(p_today))
        self.lbl_sessions_sub.set_text(f"Hedef: {goal}")

        sec_today = stats.get("today_focus_seconds", 0)
        h = sec_today // 3600
        m = (sec_today % 3600) // 60
        if h > 0:
            time_text = f"{h}s {m}dk"
        else:
            time_text = f"{m} dk"
        self.lbl_focus_val.set_text(time_text)

        b_today = stats.get("today_breaks", 0)
        self.lbl_breaks_val.set_text(str(b_today))

        # Update ring session cycle dots
        interval = self.storage.config.get("long_break_interval", 4)
        current_step = (self.timer.session_count % interval) + 1
        self.ring.update_cycle_info(current_step, interval)

    def _select_mode(self, mode: str):
        if self.timer.state == STATE_RUNNING:
            self.timer.pause()
        self.timer.set_mode(mode)

    def _on_tick(self, time_str: str, progress_ratio: float):
        # Update window title with time if running
        if self.timer.state == STATE_RUNNING:
            mode_tr = "🍅 Odak" if self.timer.mode == MODE_FOCUS else "☕ Mola"
            self.set_title(f"({time_str}) {mode_tr} - Pomodoro Pro")
        else:
            self.set_title("Pomodoro Focus Pro")

    def _on_state_change(self, new_state: str):
        self._update_start_button_style()

    def _on_mode_change(self, new_mode: str):
        self._update_mode_tabs(new_mode)
        self._update_start_button_style()

    def _on_session_complete(self, completed_mode: str):
        self._update_stats_display()
        if completed_mode == MODE_FOCUS:
            toast = Adw.Toast.new("🎉 Harika! Odaklanma seansını tamamladın. Dinlenme vakti!")
        else:
            toast = Adw.Toast.new("☕ Mola bitti! Yeni seansa hazırsın.")
        toast.set_timeout(5)
        self.toast_overlay.add_toast(toast)

    def _open_settings(self, btn):
        dialog = SettingsDialog(
            self,
            self.storage,
            self.sound,
            self.timer,
            on_settings_changed_callback=self._on_settings_updated
        )
        dialog.present()

    def _on_settings_updated(self):
        # Reload duration for current mode if stopped
        if self.timer.state == STATE_STOPPED:
            self.timer.reset()
        self._update_stats_display()

    def _edit_task_name(self, btn):
        # Inline quick prompt to change task topic
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Çalışma Konusu",
            body="Hangi ders veya görev üzerinde çalışıyorsun?"
        )
        entry = Gtk.Entry()
        entry.set_text(self.storage.config.get("current_task", "Ders Çalışma"))
        entry.set_margin_start(16)
        entry.set_margin_end(16)
        dialog.set_extra_child(entry)

        dialog.add_response("cancel", "İptal")
        dialog.add_response("save", "Kaydet")
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        def _on_response(d, response_id):
            if response_id == "save":
                new_task = entry.get_text().strip() or "Ders Çalışma"
                self.storage.config["current_task"] = new_task
                self.storage.save_config()
                self.task_btn.set_label(f"🎯 {new_task}")
            d.close()

        dialog.connect("response", _on_response)
        dialog.present()

    def _toggle_mini_mode(self):
        self.is_mini_mode = not self.is_mini_mode
        self.storage.config["mini_mode"] = self.is_mini_mode
        self.storage.save_config()
        self._apply_mini_mode(self.is_mini_mode)

    def _apply_mini_mode(self, is_mini: bool):
        if is_mini:
            # Hide tabs, task pill, stats cards, secondary buttons
            self.tabs_container.set_visible(False)
            self.task_box.set_visible(False)
            self.stats_cards_container.set_visible(False)
            self.reset_btn.set_visible(False)
            self.skip_btn.set_visible(False)
            self.header_bar.set_show_title_buttons(True)
            self.ring.set_content_width(200)
            self.ring.set_content_height(200)
            self.set_default_size(280, 310)
            self.mini_mode_btn.set_icon_name("view-fullscreen-symbolic")
            self.mini_mode_btn.set_tooltip_text("Tam Görünüme Dön (M)")
        else:
            self.tabs_container.set_visible(True)
            self.task_box.set_visible(True)
            self.stats_cards_container.set_visible(True)
            self.reset_btn.set_visible(True)
            self.skip_btn.set_visible(True)
            self.ring.set_content_width(280)
            self.ring.set_content_height(280)
            self.set_default_size(520, 680)
            self.mini_mode_btn.set_icon_name("view-restore-symbolic")
            self.mini_mode_btn.set_tooltip_text("Kompakt / Mini Mod (M)")
