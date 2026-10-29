import os
import random
import subprocess
import threading

MOTIVATIONAL_QUOTES = [
    "Hedefine giden yol her gün çözdüğün bir soruyla açılır. Zinciri kırma!",
    "Başarı, her gün tekrarlanan küçük disiplinlerin toplamıdır.",
    "Bugün ertelediğin konu yarın sınavda karşına çıkabilir. Asla pes etme!",
    "Rakiplerin yorulup bıraktığında senin attığın her adım seni zirveye taşır.",
    "Zor sorular zihni güçlendirir; derin odaklanma ustalığı getirir.",
    "Günde 1 saat fazla çalışan bir öğrenci, yılda 365 saat öne geçer!",
    "Büyük hayaller büyük emekler ister. Harika gidiyorsun!",
    "Mola bittiğinde masaya daha güçlü dön. Kazananlar istikrarlı olanlardır."
]

class DesktopNotifier:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")

    def notify_focus_finished(self, subject_name: str, subject_icon: str, break_minutes: int, is_long_break: bool = False):
        if not self.storage.config.get("notifications_enabled", True):
            return

        streak_info = self.storage.calculate_streak()
        rem = streak_info.get("remaining_to_goal", 0)

        if rem > 0:
            sub_status = f"Bugünkü hedefe ve zincire {rem} seans kaldı!"
        else:
            sub_status = f"Tebrikler! Bugünün hedefine ulaşıldı, zincir korundu! 🔥 ({streak_info['current_streak']} Gün)"

        break_type = "uzun mola" if is_long_break else "kısa mola"
        quote = random.choice(MOTIVATIONAL_QUOTES)

        title = f"🎉 {subject_icon} {subject_name} Tamamlandı!"
        message = f"Harika bir seans bitirdin! Şimdi {break_minutes} dk {break_type}.\n\n💡 {quote}\n📌 {sub_status}"

        self._send_notification(title, message, urgency="normal")

    def notify_break_finished(self):
        if not self.storage.config.get("notifications_enabled", True):
            return

        title = "☕ Mola Sona Erdi!"
        message = "Dinlendin ve tazelendin! Yeni bir odaklanma seansına başlamak için hazır mısın? Masaya dönme vakti!"
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
