#!/usr/bin/env bash
set -e

# Base directory
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_NAME="pomodoro-focus-pro"
VERSION="1.0.0"
ARCH="all"
BUILD_ROOT="${REPO_DIR}/build_pkg/${PKG_NAME}_${VERSION}_${ARCH}"

echo "======================================================"
echo " Building Debian (.deb) Package: ${PKG_NAME}_${VERSION}"
echo "======================================================"

# Clean previous build
rm -rf "${REPO_DIR}/build_pkg"
mkdir -p "${BUILD_ROOT}/DEBIAN"
mkdir -p "${BUILD_ROOT}/usr/bin"
mkdir -p "${BUILD_ROOT}/usr/share/applications"
mkdir -p "${BUILD_ROOT}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${BUILD_ROOT}/usr/share/pomodoro-focus-pro"

# 1. Control File
cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/control"
Package: pomodoro-focus-pro
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Maintainer: Erdoğan <erdogan@local>
Depends: python3, python3-gi, python3-cairo, gir1.2-gtk-4.0, gir1.2-adw-1, libnotify-bin
Description: Modern Pomodoro Timer for Ubuntu GNOME Wayland
 Pomodoro Focus Pro is a sleek, modern productivity and study timer
 designed specifically for Ubuntu 26.04 Wayland and GNOME desktop.
 Features circular progress animations, session stats, sound alerts,
 and desktop notifications.
EOF

# 2. Post-installation Hook
cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/postinst"
#!/bin/sh
set -e
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications || true
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "${BUILD_ROOT}/DEBIAN/postinst"

# 3. Bin Launcher
cat << 'EOF' > "${BUILD_ROOT}/usr/bin/pomodoro-focus-pro"
#!/bin/sh
exec /usr/bin/python3 /usr/share/pomodoro-focus-pro/main.py "$@"
EOF
chmod 755 "${BUILD_ROOT}/usr/bin/pomodoro-focus-pro"

# 4. Copy Codebase to /usr/share/pomodoro-focus-pro/
cp "${REPO_DIR}/main.py" "${BUILD_ROOT}/usr/share/pomodoro-focus-pro/"
cp -r "${REPO_DIR}/pomodoro_focus_pro" "${BUILD_ROOT}/usr/share/pomodoro-focus-pro/"

# 5. Desktop File
cp "${REPO_DIR}/pomodoro-focus-pro.desktop" "${BUILD_ROOT}/usr/share/applications/"

# 6. Icons
cp "${REPO_DIR}/pomodoro_focus_pro/assets/icon.png" "${BUILD_ROOT}/usr/share/icons/hicolor/256x256/apps/pomodoro-focus-pro.png"
cp "${REPO_DIR}/pomodoro_focus_pro/assets/icon.svg" "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps/pomodoro-focus-pro.svg"

# Set permissions: directories 755, files 644, executables 755
find "${BUILD_ROOT}/usr/share" -type d -exec chmod 755 {} +
find "${BUILD_ROOT}/usr/share" -type f -exec chmod 644 {} +
chmod 755 "${BUILD_ROOT}/usr/share/pomodoro-focus-pro/main.py"
chmod 755 "${BUILD_ROOT}/DEBIAN/postinst"
chmod 755 "${BUILD_ROOT}/usr/bin/pomodoro-focus-pro"

# 7. Build package with dpkg-deb
DEB_OUTPUT="${REPO_DIR}/${PKG_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "${BUILD_ROOT}" "${DEB_OUTPUT}"

echo "======================================================"
echo " SUCCESS! Package generated at:"
echo " ${DEB_OUTPUT}"
echo " Install with: sudo apt install ${DEB_OUTPUT}"
echo "======================================================"
