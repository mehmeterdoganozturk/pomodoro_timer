#!/usr/bin/env python3
#
# Copyright (c) 2026 Mehmet Erdoğan Öztürk <mehmeterdoganozturk@gmail.com>
# Licensed under the MIT License. See LICENSE in the project root for details.
#
import sys
import os

# Add directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pomodoro_focus_pro.app import PomodoroApp

def main():
    app = PomodoroApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
