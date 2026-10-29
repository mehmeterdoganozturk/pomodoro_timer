#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/share/pomodoro-focus-pro"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR_PNG="${HOME}/.local/share/icons/hicolor/256x256/apps"
ICON_DIR_SVG="${HOME}/.local/share/icons/hicolor/scalable/apps"

echo "=========================================================="
echo " Kurulum Başlatılıyor: Pomodoro Focus Pro (Kullanıcı Alanı)"
echo "=========================================================="

# Create directories
mkdir -p "${TARGET_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${DESKTOP_DIR}"
mkdir -p "${ICON_DIR_PNG}"
mkdir -p "${ICON_DIR_SVG}"

# Copy application files
cp -r "${REPO_DIR}/main.py" "${TARGET_DIR}/"
cp -r "${REPO_DIR}/pomodoro_focus_pro" "${TARGET_DIR}/"

# Create launcher script in ~/.local/bin
cat << EOF > "${BIN_DIR}/pomodoro-focus-pro"
#!/usr/bin/env bash
exec /usr/bin/python3 "${TARGET_DIR}/main.py" "\$@"
EOF
chmod +x "${BIN_DIR}/pomodoro-focus-pro"

# Copy icons
cp "${REPO_DIR}/pomodoro_focus_pro/assets/icon.png" "${ICON_DIR_PNG}/pomodoro-focus-pro.png"
cp "${REPO_DIR}/pomodoro_focus_pro/assets/icon.svg" "${ICON_DIR_SVG}/pomodoro-focus-pro.svg"

# Install .desktop file
cat << EOF > "${DESKTOP_DIR}/pomodoro-focus-pro.desktop"
[Desktop Entry]
Name=Pomodoro Focus Pro
GenericName=Pomodoro Zamanlayıcı
Comment=Ubuntu GNOME için Modern Pomodoro ve Ders Çalışma Sayacı
Exec=${BIN_DIR}/pomodoro-focus-pro %U
Icon=pomodoro-focus-pro
Terminal=false
Type=Application
Categories=Utility;Clock;
Keywords=pomodoro;timer;focus;study;saat;zamanlayici;ders;calisma;
StartupNotify=true
StartupWMClass=com.github.erdogan.PomodoroFocusPro
EOF
chmod +x "${DESKTOP_DIR}/pomodoro-focus-pro.desktop"

# Update desktop & icon caches if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo "=========================================================="
echo " TEBRİKLER! Pomodoro Focus Pro Başarıyla Kuruldu!"
echo ""
echo " Çalıştırmak için:"
echo "   1. Uygulama menüsünden 'Pomodoro Focus Pro' aratıp açabilirsiniz."
echo "   2. Veya terminalden: pomodoro-focus-pro"
echo "=========================================================="
