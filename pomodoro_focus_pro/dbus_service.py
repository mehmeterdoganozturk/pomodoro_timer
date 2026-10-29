import json
import os
from gi.repository import Gio, GLib

BUS_NAME = "com.github.erdogan.PomodoroFocusPro"
OBJECT_PATH = "/com/github/erdogan/PomodoroFocusPro"
INTERFACE_NAME = "com.github.erdogan.PomodoroFocusPro"

INTROSPECTION_XML = f"""
<node>
  <interface name="{INTERFACE_NAME}">
    <method name="ShowWindow"/>
    <method name="HideWindow"/>
    <method name="Toggle"/>
    <method name="Reset"/>
    <method name="Skip"/>
    <method name="Quit"/>
    <method name="GetStatus">
      <arg type="s" name="time_str" direction="out"/>
      <arg type="d" name="ratio" direction="out"/>
      <arg type="s" name="state" direction="out"/>
      <arg type="s" name="mode" direction="out"/>
      <arg type="s" name="subject_name" direction="out"/>
      <arg type="s" name="subject_icon" direction="out"/>
      <arg type="b" name="window_visible" direction="out"/>
    </method>
    <signal name="StatusChanged">
      <arg type="s" name="time_str"/>
      <arg type="d" name="ratio"/>
      <arg type="s" name="state"/>
      <arg type="s" name="mode"/>
      <arg type="s" name="subject_name"/>
      <arg type="s" name="subject_icon"/>
      <arg type="b" name="window_visible"/>
    </signal>
  </interface>
</node>
"""

class DBusService:
    def __init__(self, app, window, timer, storage):
        self.app = app
        self.window = window
        self.timer = timer
        self.storage = storage

        self.connection = None
        self.registration_id = 0
        self.owner_id = 0

        self.node_info = Gio.DBusNodeInfo.new_for_xml(INTROSPECTION_XML)
        self.interface_info = self.node_info.interfaces[0]

        self.live_state_file = os.path.expanduser("~/.config/pomodoro-focus-pro/live_state.json")

        # Acquire session bus name
        self.owner_id = Gio.bus_own_name(
            Gio.BusType.SESSION,
            BUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            self._on_bus_acquired,
            self._on_name_acquired,
            self._on_name_lost
        )

        # Connect timer callbacks to emit signals
        self.timer.on_tick_callbacks.append(self._on_tick)
        self.timer.on_state_change_callbacks.append(lambda s: self.broadcast_status())
        self.timer.on_mode_change_callbacks.append(lambda m: self.broadcast_status())

    def _on_bus_acquired(self, connection, name):
        self.connection = connection
        self.registration_id = connection.register_object(
            OBJECT_PATH,
            self.interface_info,
            self._handle_method_call,
            None,
            None
        )

    def _on_name_acquired(self, connection, name):
        self.broadcast_status()

    def _on_name_lost(self, connection, name):
        pass

    def _handle_method_call(self, connection, sender, object_path, interface_name, method_name, parameters, invocation):
        if method_name == "ShowWindow":
            GLib.idle_add(self._do_show_window)
            invocation.return_value(None)

        elif method_name == "HideWindow":
            GLib.idle_add(self._do_hide_window)
            invocation.return_value(None)

        elif method_name == "Toggle":
            GLib.idle_add(self.timer.toggle)
            invocation.return_value(None)

        elif method_name == "Reset":
            GLib.idle_add(self.timer.reset)
            invocation.return_value(None)

        elif method_name == "Skip":
            GLib.idle_add(self.timer.skip)
            invocation.return_value(None)

        elif method_name == "Quit":
            GLib.idle_add(self._do_quit)
            invocation.return_value(None)

        elif method_name == "GetStatus":
            status_tuple = self._get_status_tuple()
            invocation.return_value(GLib.Variant('(sdssssb)', status_tuple))

        else:
            invocation.return_value(None)

    def _do_show_window(self):
        if self.window:
            self.window.set_visible(True)
            self.window.present()
        self.broadcast_status()
        return False

    def _do_hide_window(self):
        if self.window:
            self.window.set_visible(False)
        self.broadcast_status()
        return False

    def _do_quit(self):
        self._write_dead_state()
        if self.app:
            self.app.quit()
        return False

    def _get_status_tuple(self):
        time_str = self.timer.get_formatted_time()
        ratio = self.timer.get_progress_ratio()
        state = self.timer.state
        mode = self.timer.mode
        sub = self.storage.get_selected_subject()
        sub_name = sub.get("name", "Ders Çalışma")
        sub_icon = sub.get("icon", "📐")
        is_visible = self.window.get_visible() if self.window else False

        return (time_str, ratio, state, mode, sub_name, sub_icon, is_visible)

    def _on_tick(self, time_str, ratio):
        self.broadcast_status()

    def broadcast_status(self):
        status_tuple = self._get_status_tuple()
        time_str, ratio, state, mode, sub_name, sub_icon, is_visible = status_tuple

        # 1. Emit D-Bus Signal
        if self.connection and self.registration_id > 0:
            try:
                self.connection.emit_signal(
                    None,
                    OBJECT_PATH,
                    INTERFACE_NAME,
                    "StatusChanged",
                    GLib.Variant('(sdssssb)', status_tuple)
                )
            except Exception:
                pass

        # 2. Write file cache
        try:
            state_data = {
                "time_str": time_str,
                "ratio": ratio,
                "state": state,
                "mode": mode,
                "subject_name": sub_name,
                "subject_icon": sub_icon,
                "window_visible": is_visible,
                "running": True
            }
            with open(self.live_state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, ensure_ascii=False)
        except Exception:
            pass

    def _write_dead_state(self):
        try:
            with open(self.live_state_file, "w", encoding="utf-8") as f:
                json.dump({"running": False}, f)
        except Exception:
            pass
