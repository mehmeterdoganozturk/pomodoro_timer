#!/usr/bin/env bash
set -e

echo "Pomodoro Focus Pro kaldırılıyor..."

rm -rf "${HOME}/.local/share/pomodoro-focus-pro"
rm -f "${HOME}/.local/bin/pomodoro-focus-pro"
rm -f "${HOME}/.local/share/applications/pomodoro-focus-pro.desktop"
rm -f "${HOME}/.local/share/icons/hicolor/256x256/apps/pomodoro-focus-pro.png"
rm -f "${HOME}/.local/share/icons/hicolor/scalable/apps/pomodoro-focus-pro.svg"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true
fi

echo "Kaldırma işlemi tamamlandı."
