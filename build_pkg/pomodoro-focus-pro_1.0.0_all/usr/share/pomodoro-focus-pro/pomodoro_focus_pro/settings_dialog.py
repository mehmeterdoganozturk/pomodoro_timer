import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class SettingsDialog(Adw.PreferencesWindow):
    def __init__(self, parent_window, storage_manager, sound_player, timer_engine, on_settings_changed_callback=None):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.set_title("Pomodoro Pro Ayarları")
        self.set_default_size(560, 580)
        self.set_search_enabled(False)

        self.storage = storage_manager
        self.sound = sound_player
        self.timer = timer_engine
        self.on_changed = on_settings_changed_callback

        # =====================================================================
        # SAYFA 1: ZAMANLAYICI & AKIŞ
        # =====================================================================
        page_timer = Adw.PreferencesPage()
        page_timer.set_title("Zamanlayıcı")
        page_timer.set_icon_name("alarm-symbolic")
        self.add(page_timer)

        # 1. Süre Ayarları Grubu
        dur_group = Adw.PreferencesGroup()
        dur_group.set_title("Süre Ayarları")
        dur_group.set_description("Odaklanma ve mola periyotlarının uzunlukları")
        page_timer.add(dur_group)

        # Odak Süresi
        self.focus_spin = Adw.SpinRow.new_with_range(1, 90, 1)
        self.focus_spin.set_title("Odaklanma Süresi (Dakika)")
        self.focus_spin.set_subtitle("Ders çalışma ve derin odaklanma süresi")
        self.focus_spin.set_value(self.storage.config.get("focus_duration", 25))
        self.focus_spin.connect("notify::value", self._on_value_changed)
        dur_group.add(self.focus_spin)

        # Varsayılan Test / Soru Süresi
        self.test_spin = Adw.SpinRow.new_with_range(5, 180, 5)
        self.test_spin.set_title("Varsayılan Test Süresi (Dakika)")
        self.test_spin.set_subtitle("Soru çözme ve deneme sınavı süresi")
        self.test_spin.set_value(self.storage.config.get("test_duration", 20))
        self.test_spin.connect("notify::value", self._on_value_changed)
        dur_group.add(self.test_spin)

        # Kısa Mola
        self.short_spin = Adw.SpinRow.new_with_range(1, 30, 1)
        self.short_spin.set_title("Kısa Mola Süresi (Dakika)")
        self.short_spin.set_subtitle("Her seans sonrası hızlı nefes alma molası")
        self.short_spin.set_value(self.storage.config.get("short_break_duration", 5))
        self.short_spin.connect("notify::value", self._on_value_changed)
        dur_group.add(self.short_spin)

        # Uzun Mola
        self.long_spin = Adw.SpinRow.new_with_range(5, 60, 5)
        self.long_spin.set_title("Uzun Mola Süresi (Dakika)")
        self.long_spin.set_subtitle("Belirli seans döngüsünden sonraki dinlenme")
        self.long_spin.set_value(self.storage.config.get("long_break_duration", 15))
        self.long_spin.connect("notify::value", self._on_value_changed)
        dur_group.add(self.long_spin)

        # Uzun Mola Aralığı
        self.interval_spin = Adw.SpinRow.new_with_range(2, 8, 1)
        self.interval_spin.set_title("Uzun Mola Aralığı")
        self.interval_spin.set_subtitle("Kaç odak seansından sonra uzun mola verilsin?")
        self.interval_spin.set_value(self.storage.config.get("long_break_interval", 4))
        self.interval_spin.connect("notify::value", self._on_value_changed)
        dur_group.add(self.interval_spin)

        # 2. Akış ve Otomasyon Grubu
        auto_group = Adw.PreferencesGroup()
        auto_group.set_title("Akış ve Otomasyon")
        page_timer.add(auto_group)

        # Otomatik Mola Başlat
        self.auto_break_switch = Adw.SwitchRow()
        self.auto_break_switch.set_title("Otomatik Mola Başlat")
        self.auto_break_switch.set_subtitle("Odaklanma bittiğinde molayı beklemeden başlat")
        self.auto_break_switch.set_active(self.storage.config.get("auto_start_breaks", False))
        self.auto_break_switch.connect("notify::active", self._on_value_changed)
        auto_group.add(self.auto_break_switch)

        # Moladan Sonra Otomatik Odaklan
        self.auto_focus_switch = Adw.SwitchRow()
        self.auto_focus_switch.set_title("Moladan Sonra Otomatik Odaklan")
        self.auto_focus_switch.set_subtitle("Mola bittiğinde yeni seansı doğrudan başlat")
        self.auto_focus_switch.set_active(self.storage.config.get("auto_start_pomodoros", False))
        self.auto_focus_switch.connect("notify::active", self._on_value_changed)
        auto_group.add(self.auto_focus_switch)

        # Günlük Hedef
        self.goal_spin = Adw.SpinRow.new_with_range(1, 20, 1)
        self.goal_spin.set_title("Günlük Hedef (Pomodoro)")
        self.goal_spin.set_subtitle("Günde tamamlamayı hedeflediğiniz seans sayısı")
        self.goal_spin.set_value(self.storage.config.get("daily_goal", 8))
        self.goal_spin.connect("notify::value", self._on_value_changed)
        auto_group.add(self.goal_spin)

        # =====================================================================
        # SAYFA 2: BİLDİRİMLER VE VERİ
        # =====================================================================
        page_alerts = Adw.PreferencesPage()
        page_alerts.set_title("Bildirimler ve Veri")
        page_alerts.set_icon_name("preferences-system-notifications-symbolic")
        self.add(page_alerts)

        # 3. Uyarılar ve Sesler Grubu
        alert_group = Adw.PreferencesGroup()
        alert_group.set_title("Uyarılar ve Sesler")
        page_alerts.add(alert_group)

        # Sesli Uyarı
        self.sound_switch = Adw.SwitchRow()
        self.sound_switch.set_title("Sesli Uyarı (Kristal Çan)")
        self.sound_switch.set_subtitle("Süre dolduğunda zarif bir çan sesi çal")
        self.sound_switch.set_active(self.storage.config.get("sound_enabled", True))
        self.sound_switch.connect("notify::active", self._on_value_changed)

        test_sound_btn = Gtk.Button(label="Test Et")
        test_sound_btn.set_valign(Gtk.Align.CENTER)
        test_sound_btn.add_css_class("flat")
        test_sound_btn.connect("clicked", lambda b: self.sound.play_test_sound())
        self.sound_switch.add_suffix(test_sound_btn)
        alert_group.add(self.sound_switch)

        # Masaüstü Bildirimleri
        self.notif_switch = Adw.SwitchRow()
        self.notif_switch.set_title("Masaüstü Bildirimleri")
        self.notif_switch.set_subtitle("Ubuntu sistem bildirim afişi ve motivasyon mesajı göster")
        self.notif_switch.set_active(self.storage.config.get("notifications_enabled", True))
        self.notif_switch.connect("notify::active", self._on_value_changed)
        alert_group.add(self.notif_switch)

        # 4. Veri Yönetimi Grubu
        data_group = Adw.PreferencesGroup()
        data_group.set_title("Veri Yönetimi")
        page_alerts.add(data_group)

        reset_row = Adw.ActionRow()
        reset_row.set_title("Bugünün İstatistiklerini Sıfırla")
        reset_row.set_subtitle("Bugünkü sayaç ve odak sürelerini sıfırlar")
        reset_btn = Gtk.Button(label="Sıfırla")
        reset_btn.set_valign(Gtk.Align.CENTER)
        reset_btn.add_css_class("destructive-action")
        reset_btn.connect("clicked", self._on_reset_today_stats)
        reset_row.add_suffix(reset_btn)
        data_group.add(reset_row)

    def _on_value_changed(self, widget, pspec):
        cfg = self.storage.config
        cfg["focus_duration"] = int(self.focus_spin.get_value())
        cfg["test_duration"] = int(self.test_spin.get_value())
        cfg["short_break_duration"] = int(self.short_spin.get_value())
        cfg["long_break_duration"] = int(self.long_spin.get_value())
        cfg["long_break_interval"] = int(self.interval_spin.get_value())
        cfg["auto_start_breaks"] = bool(self.auto_break_switch.get_active())
        cfg["auto_start_pomodoros"] = bool(self.auto_focus_switch.get_active())
        cfg["daily_goal"] = int(self.goal_spin.get_value())
        cfg["sound_enabled"] = bool(self.sound_switch.get_active())
        cfg["notifications_enabled"] = bool(self.notif_switch.get_active())
        self.storage.save_config()

        if self.on_changed:
            self.on_changed()

    def _on_reset_today_stats(self, btn):
        self.storage.reset_today_stats()
        if self.on_changed:
            self.on_changed()
        self.close()
