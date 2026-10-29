import os
import shutil
import subprocess
import threading

class SoundPlayer:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.focus_sound = os.path.join(self.assets_dir, "focus_complete.wav")
        self.break_sound = os.path.join(self.assets_dir, "break_complete.wav")

        # Find best available player command
        self.player_cmd = None
        for cmd in ["pw-play", "paplay", "canberra-gtk-play", "aplay"]:
            if shutil.which(cmd):
                self.player_cmd = cmd
                break

    def play_focus_complete(self):
        if not self.storage.config.get("sound_enabled", True):
            return
        self._play_file_async(self.focus_sound)

    def play_break_complete(self):
        if not self.storage.config.get("sound_enabled", True):
            return
        self._play_file_async(self.break_sound)

    def play_test_sound(self):
        self._play_file_async(self.focus_sound)

    def _play_file_async(self, sound_path):
        if not os.path.exists(sound_path) or not self.player_cmd:
            return

        def _worker():
            try:
                if self.player_cmd == "canberra-gtk-play":
                    subprocess.run(["canberra-gtk-play", "-f", sound_path],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run([self.player_cmd, sound_path],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Sound play error: {e}")

        threading.Thread(target=_worker, daemon=True).start()
