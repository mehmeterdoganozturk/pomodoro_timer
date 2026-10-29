import os
import shutil
import subprocess
import threading

class DesktopNotifier:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")

    def notify_focus_finished(self, break_minutes: int, is_long_break: bool = False):
        if not self.storage.config.get("notifications_enabled", True):
            return

        break_type = "uzun bir" if is_long_break else "kısa bir"
        title = "🎉 Pomodoro Tamamlandı!"
        message = f"Harika bir odaklanma seansı bitirdin! Şimdi {break_minutes} dakikalık {break_type} mola zamanı."
        self._send_notification(title, message, urgency="normal")

    def notify_break_finished(self):
        if not self.storage.config.get("notifications_enabled", True):
            return

        title = "☕ Mola Sona Erdi!"
        message = "Dinlendin ve tazelendin! Yeni bir odaklanma seansına başlamak için hazır mısın?"
        self._send_notification(title, message, urgency="normal")

    def _send_notification(self, title: str, message: str, urgency: str = "normal"):
        def _worker():
            try:
                cmd = [
                    "notify-send",
                    "--app-name=Pomodoro Focus Pro",
                    f"--urgency={urgency}",
                    "--hint=int:transient:1"
                ]
                if os.path.exists(self.icon_path):
                    cmd.append(f"--icon={self.icon_path}")
                else:
                    cmd.append("--icon=alarm-symbolic")

                cmd.extend([title, message])
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Notification error: {e}")

        threading.Thread(target=_worker, daemon=True).start()
