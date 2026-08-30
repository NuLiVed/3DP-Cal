#!/usr/bin/env bash
set -euo pipefail

APP_ID="3dp-cost-calculator"
APP_NAME="3DP Cost Calculator"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_EXE="${REPO_ROOT}/dist/${APP_ID}"
INSTALL_DIR="${HOME}/.local/share/${APP_ID}"
INSTALL_EXE="${INSTALL_DIR}/${APP_ID}"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"
ICON_PATH="${ICON_DIR}/${APP_ID}.png"
DESKTOP_DIR="${HOME}/.local/share/applications"
DESKTOP_FILE="${DESKTOP_DIR}/${APP_ID}.desktop"

if [[ ! -f "${SOURCE_EXE}" ]]; then
  echo "Missing ${SOURCE_EXE}. Build it first with PyInstaller." >&2
  exit 1
fi

mkdir -p "${INSTALL_DIR}" "${ICON_DIR}" "${DESKTOP_DIR}"
cp "${SOURCE_EXE}" "${INSTALL_EXE}"
chmod +x "${INSTALL_EXE}"
cp "${REPO_ROOT}/Assets/Logo.png" "${ICON_PATH}"

cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Comment=Calculate 3D print pricing and export receipts
Exec=${INSTALL_EXE}
Icon=${ICON_PATH}
Terminal=false
Categories=Utility;Office;
StartupNotify=true
EOF

chmod 644 "${DESKTOP_FILE}"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache "${HOME}/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

echo "Installed ${APP_NAME}. It should now appear in your application launcher."
