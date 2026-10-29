import os
import sys
import random
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')

from gi.repository import Gtk, Adw, Gdk, GLib, Pango
from .storage import StorageManager, PROFILES_DATA
from .sound_player import SoundPlayer
from .notifier import DesktopNotifier, MOTIVATIONAL_QUOTES
from .timer_engine import TimerEngine, MODE_FOCUS, MODE_SHORT_BREAK, MODE_LONG_BREAK, STATE_RUNNING, STATE_PAUSED, STATE_STOPPED
from .circular_ring import CircularProgressRing
from .heatmap_widget import HeatmapWidget
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
        self.set_default_size(560, 720)
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
        self._refresh_streak_page()

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

        # View Stack for Tabs
        self.view_stack = Adw.ViewStack()

        # Left Header: Mini Mode Toggle
        self.mini_mode_btn = Gtk.Button(icon_name="view-restore-symbolic")
        self.mini_mode_btn.set_tooltip_text("Kompakt / Mini Mod (M)")
        self.mini_mode_btn.connect("clicked", lambda b: self._toggle_mini_mode())
        self.header_bar.pack_start(self.mini_mode_btn)

        # Center Header: View Switcher (Sayaç, Zinciri Kırma, Modlar)
        self.view_switcher = Adw.ViewSwitcher(stack=self.view_stack)
        self.view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        self.header_bar.set_title_widget(self.view_switcher)

        # Right Header: Settings Button
        self.settings_btn = Gtk.Button(icon_name="emblem-system-symbolic")
        self.settings_btn.set_tooltip_text("Ayarlar")
        self.settings_btn.connect("clicked", self._open_settings)
        self.header_bar.pack_end(self.settings_btn)

        # Add ViewStack to Root
        self.root_box.append(self.view_stack)

        # 2. Build Tab Pages
        self._build_timer_page()
        self._build_streak_page()
        self._build_profiles_page()

    # =========================================================================
    # TAB 1: SAYAÇ (TIMER)
    # =========================================================================
    def _build_timer_page(self):
        self.timer_page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.timer_page_box.set_margin_top(12)
        self.timer_page_box.set_margin_bottom(16)
        self.timer_page_box.set_margin_start(20)
        self.timer_page_box.set_margin_end(20)
        self.timer_page_box.set_halign(Gtk.Align.CENTER)

        # 1. Mode Switcher Tabs
        self.tabs_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.tabs_container.add_css_class("mode-tab-box")
        self.tabs_container.set_halign(Gtk.Align.CENTER)
        self.timer_page_box.append(self.tabs_container)

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

        # 2. Subject Selector Chips (Ders Seçici FlowBox - No ugly scrollbar)
        self.subject_flowbox = Gtk.FlowBox()
        self.subject_flowbox.add_css_class("subject-flowbox")
        self.subject_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.subject_flowbox.set_max_children_per_line(4)
        self.subject_flowbox.set_min_children_per_line(3)
        self.subject_flowbox.set_column_spacing(8)
        self.subject_flowbox.set_row_spacing(8)
        self.subject_flowbox.set_halign(Gtk.Align.CENTER)
        self.subject_flowbox.set_valign(Gtk.Align.CENTER)
        self.subject_flowbox.set_homogeneous(False)
        self.timer_page_box.append(self.subject_flowbox)

        self._populate_subject_chips()

        # 3. Center Cairo Circular Progress Ring
        self.ring = CircularProgressRing(self.timer, self.storage)
        self.timer_page_box.append(self.ring)

        # 4. Daily Discipline Target Progress (Zorlayıcı / Teşvik Sistemi)
        self.discipline_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.discipline_box.add_css_class("discipline-bar-box")
        self.discipline_box.set_size_request(380, -1)

        self.discipline_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.discipline_title = Gtk.Label(label="🎯 Günlük Hedef: 0 / 8 Seans")
        self.discipline_title.add_css_class("discipline-title")
        self.discipline_header.append(self.discipline_title)

        self.discipline_spacer = Gtk.Box()
        self.discipline_spacer.set_hexpand(True)
        self.discipline_header.append(self.discipline_spacer)

        self.discipline_streak_lbl = Gtk.Label(label="🔥 Zincir: 0 Gün")
        self.discipline_streak_lbl.add_css_class("discipline-sub")
        self.discipline_header.append(self.discipline_streak_lbl)
        self.discipline_box.append(self.discipline_header)

        self.discipline_progress = Gtk.ProgressBar()
        self.discipline_progress.set_fraction(0.0)
        self.discipline_box.append(self.discipline_progress)

        self.timer_page_box.append(self.discipline_box)

        # 5. Primary Action Controls
        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        self.controls_box.set_halign(Gtk.Align.CENTER)
        self.timer_page_box.append(self.controls_box)

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

        # Start / Pause button
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

        # Skip button
        self.skip_btn = Gtk.Button()
        skip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        skip_box.append(Gtk.Image.new_from_icon_name("media-skip-forward-symbolic"))
        skip_box.append(Gtk.Label(label="Sonraki"))
        self.skip_btn.set_child(skip_box)
        self.skip_btn.add_css_class("btn-secondary")
        self.skip_btn.set_tooltip_text("Sonraki aşamaya geç (N)")
        self.skip_btn.connect("clicked", lambda b: self.timer.skip())
        self.controls_box.append(self.skip_btn)

        # 6. Bottom Statistics Metric Cards
        self.stats_cards_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.stats_cards_container.set_halign(Gtk.Align.CENTER)
        self.timer_page_box.append(self.stats_cards_container)

        self.card_sessions, self.lbl_sessions_val, self.lbl_sessions_sub = self._create_metric_card(
            "🍅", "0", "SEANSLAR", "Hedef: 8"
        )
        self.stats_cards_container.append(self.card_sessions)

        self.card_focus_time, self.lbl_focus_val, self.lbl_focus_sub = self._create_metric_card(
            "⏱️", "0 dk", "ODAKLANMA", "Bugün"
        )
        self.stats_cards_container.append(self.card_focus_time)

        self.card_breaks, self.lbl_breaks_val, self.lbl_breaks_sub = self._create_metric_card(
            "☕", "0", "MOLALAR", "Bugün"
        )
        self.stats_cards_container.append(self.card_breaks)

        # Add to view stack
        self.view_stack.add_titled_with_icon(
            self.timer_page_box, "timer", "Sayaç", "alarm-symbolic"
        )

    # =========================================================================
    # TAB 2: ZİNCİRİ KIRMA & İSTATİSTİK (STREAK & ANALYTICS)
    # =========================================================================
    def _build_streak_page(self):
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(16)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        scroller.set_child(content)

        # 1. Streak Hero Card
        hero_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        hero_card.add_css_class("streak-hero-card")

        hero_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        flame_lbl = Gtk.Label(label="🔥")
        flame_lbl.set_markup("<span font='36'>🔥</span>")
        hero_top.append(flame_lbl)

        hero_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.hero_streak_val = Gtk.Label(label="0 GÜNLÜK ZİNCİR")
        self.hero_streak_val.add_css_class("streak-big-val")
        self.hero_streak_val.set_halign(Gtk.Align.START)

        self.hero_streak_sub = Gtk.Label(label="En Uzun Rekor: 0 Gün | Bugün: 0 Seans")
        self.hero_streak_sub.add_css_class("metric-sub")
        self.hero_streak_sub.set_halign(Gtk.Align.START)

        hero_info.append(self.hero_streak_val)
        hero_info.append(self.hero_streak_sub)
        hero_top.append(hero_info)
        hero_card.append(hero_top)

        # Motivational quote box
        quote_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        quote_box.add_css_class("streak-quote-box")
        self.quote_label = Gtk.Label()
        self.quote_label.set_wrap(True)
        self.quote_label.set_text(f"💡 {random.choice(MOTIVATIONAL_QUOTES)}")
        quote_box.append(self.quote_label)
        hero_card.append(quote_box)

        content.append(hero_card)

        # 2. Heatmap Section
        heatmap_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        heatmap_card.add_css_class("metric-card")

        hm_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hm_title = Gtk.Label(label="📅 Son 28 Günün Çalışma Isı Haritası")
        hm_title.add_css_class("discipline-title")
        hm_header.append(hm_title)
        heatmap_card.append(hm_header)

        self.heatmap = HeatmapWidget(self.storage)
        heatmap_card.append(self.heatmap)

        hm_legend = Gtk.Label(label="Daha Az Çalışma ░ ▒ ▓ █ Hedefe Ulaşıldı")
        hm_legend.add_css_class("metric-sub")
        hm_legend.set_halign(Gtk.Align.CENTER)
        heatmap_card.append(hm_legend)

        content.append(heatmap_card)

        # 3. Subject Breakdown Card
        self.breakdown_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.breakdown_card.add_css_class("metric-card")

        bd_title = Gtk.Label(label="📚 Bugünün Ders Dağılımı")
        bd_title.add_css_class("discipline-title")
        bd_title.set_halign(Gtk.Align.START)
        self.breakdown_card.append(bd_title)

        self.breakdown_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.breakdown_card.append(self.breakdown_list_box)

        content.append(self.breakdown_card)

        self.view_stack.add_titled_with_icon(
            scroller, "streak", "Zinciri Kırma", "starred-symbolic"
        )

    # =========================================================================
    # TAB 3: MODLAR & DERSLER (PROFILES & WORKSPACES)
    # =========================================================================
    def _build_profiles_page(self):
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_top(16)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        scroller.set_child(content)

        # Profile selection title
        p_title = Gtk.Label(label="🎓 Çalışma Alanı & Mod Seçimi")
        p_title.add_css_class("discipline-title")
        p_title.set_halign(Gtk.Align.START)
        content.append(p_title)

        # Profiles list
        active_pid = self.storage.config.get("active_profile", "yks")
        for pid, pdata in PROFILES_DATA.items():
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            card.add_css_class("metric-card")

            top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            lbl_name = Gtk.Label(label=pdata["name"])
            lbl_name.add_css_class("discipline-title")
            top_row.append(lbl_name)

            spacer = Gtk.Box()
            spacer.set_hexpand(True)
            top_row.append(spacer)

            select_btn = Gtk.Button(label="Seçildi" if pid == active_pid else "Aktif Yap")
            select_btn.add_css_class("suggested-action" if pid == active_pid else "btn-secondary")
            select_btn.connect("clicked", self._make_profile_selector(pid))
            top_row.append(select_btn)
            card.append(top_row)

            lbl_desc = Gtk.Label(label=pdata["description"])
            lbl_desc.add_css_class("metric-sub")
            lbl_desc.set_halign(Gtk.Align.START)
            card.append(lbl_desc)

            # Subjects chips preview
            chips_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            for s in pdata["subjects"]:
                chip_lbl = Gtk.Label(label=f"{s['icon']} {s['name']}")
                chip_lbl.add_css_class("subject-chip")
                chips_row.append(chip_lbl)
            card.append(chips_row)

            content.append(card)

        # Preset Durations Section
        dur_title = Gtk.Label(label="⏱️ Hızlı Seans Şablonları")
        dur_title.add_css_class("discipline-title")
        dur_title.set_halign(Gtk.Align.START)
        content.append(dur_title)

        dur_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        p25_btn = Gtk.Button(label="🍅 25/5 dk (Klasik)")
        p25_btn.add_css_class("btn-secondary")
        p25_btn.connect("clicked", lambda b: self._apply_duration_preset(25, 5))
        dur_box.append(p25_btn)

        p50_btn = Gtk.Button(label="📚 50/10 dk (YKS Blok / Deneme)")
        p50_btn.add_css_class("btn-secondary")
        p50_btn.connect("clicked", lambda b: self._apply_duration_preset(50, 10))
        dur_box.append(p50_btn)

        p90_btn = Gtk.Button(label="⚡ 90/20 dk (Derin Odak / Flow)")
        p90_btn.add_css_class("btn-secondary")
        p90_btn.connect("clicked", lambda b: self._apply_duration_preset(90, 20))
        dur_box.append(p90_btn)

        content.append(dur_box)

        self.view_stack.add_titled_with_icon(
            scroller, "profiles", "Modlar", "system-users-symbolic"
        )

    def _make_profile_selector(self, profile_id: str):
        def _handler(btn):
            self.storage.set_active_profile(profile_id)
            self._populate_subject_chips()
            self._update_stats_display()
            self.ring.update_subject(self.storage.get_selected_subject())
            self._update_start_button_style()
            if self.timer.state == STATE_STOPPED:
                self.timer.reset()

            # Refresh profiles page view
            self.view_stack.remove(self.view_stack.get_child_by_name("profiles"))
            self._build_profiles_page()
            self.view_stack.set_visible_child_name("timer")
        return _handler

    def _apply_duration_preset(self, focus_m: int, break_m: int):
        self.storage.config["focus_duration"] = focus_m
        self.storage.config["short_break_duration"] = break_m
        self.storage.save_config()
        if self.timer.state == STATE_STOPPED:
            self.timer.reset()
        toast = Adw.Toast.new(f"Süre şablonu güncellendi: {focus_m} dk odak / {break_m} dk mola")
        self.toast_overlay.add_toast(toast)

    # =========================================================================
    # SUBJECT CHIPS & SELECTION
    # =========================================================================
    def _populate_subject_chips(self):
        # Clear existing chips
        while child := self.subject_flowbox.get_first_child():
            self.subject_flowbox.remove(child)

        subjects = self.storage.get_subjects()
        sel_sub = self.storage.get_selected_subject()
        sel_id = sel_sub.get("id", "")

        for s in subjects:
            chip_btn = Gtk.Button(label=f"{s['icon']} {s['name']}")
            chip_btn.add_css_class("subject-chip")
            if s["id"] == sel_id:
                chip_btn.add_css_class("active-subject")

            chip_btn.connect("clicked", self._make_subject_chip_handler(s))
            self.subject_flowbox.append(chip_btn)

    def _make_subject_chip_handler(self, subject: dict):
        def _handler(btn):
            self.storage.set_selected_subject(subject["id"])
            self.ring.update_subject(subject)
            self._populate_subject_chips()
            self._update_start_button_style()
        return _handler

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
        time_text = f"{h}s {m}dk" if h > 0 else f"{m} dk"
        self.lbl_focus_val.set_text(time_text)

        b_today = stats.get("today_breaks", 0)
        self.lbl_breaks_val.set_text(str(b_today))

        # Update discipline progress bar
        fraction = min(1.0, p_today / float(max(1, goal)))
        self.discipline_progress.set_fraction(fraction)

        streak_info = self.storage.calculate_streak()
        streak_days = streak_info.get("current_streak", 0)
        rem = streak_info.get("remaining_to_goal", 0)

        self.discipline_streak_lbl.set_text(f"🔥 Zincir: {streak_days} Gün")
        if rem > 0:
            self.discipline_title.set_text(f"🎯 Günlük Hedef: {p_today}/{goal} Seans • Zincire {rem} Kaldı!")
        else:
            self.discipline_title.set_text(f"🎯 Hedefe Ulaşıldı! Zincir Korundu 🔥 ({p_today}/{goal})")

        # Update ring session cycle dots
        interval = self.storage.config.get("long_break_interval", 4)
        current_step = (self.timer.session_count % interval) + 1
        self.ring.update_cycle_info(current_step, interval)

    def _refresh_streak_page(self):
        streak_info = self.storage.calculate_streak()
        curr = streak_info["current_streak"]
        best = streak_info["best_streak"]
        p_today = streak_info["today_pomodoros"]

        self.hero_streak_val.set_text(f"{curr} GÜNLÜK ZİNCİR")
        self.hero_streak_sub.set_text(f"En Uzun Rekor: {best} Gün | Bugün: {p_today} Seans")

        self.heatmap.refresh()

        # Update breakdown list
        while child := self.breakdown_list_box.get_first_child():
            self.breakdown_list_box.remove(child)

        today_subs = self.storage.stats.get("today_subjects", {})
        subjects_lookup = {s["id"]: s for s in self.storage.get_subjects()}

        if not today_subs:
            empty_lbl = Gtk.Label(label="Bugün henüz tamamlanan ders seansı yok.")
            empty_lbl.add_css_class("metric-sub")
            empty_lbl.set_halign(Gtk.Align.CENTER)
            self.breakdown_list_box.append(empty_lbl)
        else:
            total_sec = max(1, sum(today_subs.values()))
            for sid, sec in today_subs.items():
                sdata = subjects_lookup.get(sid, {"name": sid, "icon": "📚", "color": "#3B82F6"})
                row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                row.add_css_class("subject-row")

                top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                name_lbl = Gtk.Label(label=f"{sdata.get('icon', '📚')} {sdata.get('name', sid)}")
                name_lbl.add_css_class("discipline-title")
                top.append(name_lbl)

                spacer = Gtk.Box()
                spacer.set_hexpand(True)
                top.append(spacer)

                sh = sec // 3600
                sm = (sec % 3600) // 60
                dur_text = f"{sh}s {sm}dk" if sh > 0 else f"{sm} dk"
                time_lbl = Gtk.Label(label=dur_text)
                time_lbl.add_css_class("discipline-sub")
                top.append(time_lbl)
                row.append(top)

                bar = Gtk.ProgressBar()
                bar.set_fraction(sec / float(total_sec))
                row.append(bar)

                self.breakdown_list_box.append(row)

    def _select_mode(self, mode: str):
        if self.timer.state == STATE_RUNNING:
            self.timer.pause()
        self.timer.set_mode(mode)

    def _on_tick(self, time_str: str, progress_ratio: float):
        if self.timer.state == STATE_RUNNING:
            sub = self.storage.get_selected_subject()
            prefix = f"{sub.get('icon', '🍅')} {sub.get('name', 'Odak')}" if self.timer.mode == MODE_FOCUS else "☕ Mola"
            self.set_title(f"({time_str}) {prefix} - Pomodoro Pro")
        else:
            self.set_title("Pomodoro Focus Pro")

    def _on_state_change(self, new_state: str):
        self._update_start_button_style()

    def _on_mode_change(self, new_mode: str):
        self._update_mode_tabs(new_mode)
        self._update_start_button_style()

    def _on_session_complete(self, completed_mode: str):
        self._update_stats_display()
        self._refresh_streak_page()
        if completed_mode == MODE_FOCUS:
            sub = self.storage.get_selected_subject()
            toast = Adw.Toast.new(f"🎉 Harika! {sub['icon']} {sub['name']} seansını tamamladın. Zincir güçleniyor!")
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
        if self.timer.state == STATE_STOPPED:
            self.timer.reset()
        self._update_stats_display()
        self._refresh_streak_page()

    def _toggle_mini_mode(self):
        self.is_mini_mode = not self.is_mini_mode
        self.storage.config["mini_mode"] = self.is_mini_mode
        self.storage.save_config()
        self._apply_mini_mode(self.is_mini_mode)

    def _apply_mini_mode(self, is_mini: bool):
        if is_mini:
            self.view_switcher.set_visible(False)
            self.tabs_container.set_visible(False)
            self.subject_flowbox.set_visible(False)
            self.discipline_box.set_visible(False)
            self.stats_cards_container.set_visible(False)
            self.reset_btn.set_visible(False)
            self.skip_btn.set_visible(False)
            self.ring.set_content_width(200)
            self.ring.set_content_height(200)
            self.set_default_size(280, 310)
            self.mini_mode_btn.set_icon_name("view-fullscreen-symbolic")
            self.mini_mode_btn.set_tooltip_text("Tam Görünüme Dön (M)")
            self.view_stack.set_visible_child_name("timer")
        else:
            self.view_switcher.set_visible(True)
            self.tabs_container.set_visible(True)
            self.subject_flowbox.set_visible(True)
            self.discipline_box.set_visible(True)
            self.stats_cards_container.set_visible(True)
            self.reset_btn.set_visible(True)
            self.skip_btn.set_visible(True)
            self.ring.set_content_width(280)
            self.ring.set_content_height(280)
            self.set_default_size(560, 720)
            self.mini_mode_btn.set_icon_name("view-restore-symbolic")
            self.mini_mode_btn.set_tooltip_text("Kompakt / Mini Mod (M)")
