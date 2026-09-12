#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/.build"
OUTPUT_DIR="$ROOT_DIR/dist-packages"
VERSION="2.1.0"
ARCH="$(dpkg --print-architecture 2>/dev/null || echo amd64)"

rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

python3 -m venv "$BUILD_DIR/venv"
"$BUILD_DIR/venv/bin/python" -m pip install --upgrade pip
"$BUILD_DIR/venv/bin/pip" install pyinstaller python-xlib six pymsgbox pytweening \
  pyscreeze pyperclip pillow
"$BUILD_DIR/venv/bin/pip" install --no-deps pyautogui pynput

if ! python3 -c 'import tkinter' >/dev/null 2>&1; then
  printf 'Falta Tkinter. Instala python3-tk y vuelve a ejecutar este script.\n' >&2
  exit 1
fi

"$BUILD_DIR/venv/bin/pyinstaller" --noconfirm --clean --windowed \
  --distpath "$BUILD_DIR/dist" --workpath "$BUILD_DIR/build" \
  --specpath "$BUILD_DIR" --name AutoPiano "$ROOT_DIR/autopiano.py"

APP_DIR="$BUILD_DIR/AppDir"
mkdir -p "$APP_DIR/usr/bin" "$APP_DIR/usr/share/icons/hicolor/scalable/apps"
cp -a "$BUILD_DIR/dist/AutoPiano/." "$APP_DIR/usr/bin/"
cp "$ROOT_DIR/packaging/autopiano.desktop" "$APP_DIR/AutoPiano.desktop"
cp "$ROOT_DIR/packaging/autopiano.svg" "$APP_DIR/usr/share/icons/hicolor/scalable/apps/autopiano.svg"
cp "$ROOT_DIR/packaging/autopiano.svg" "$APP_DIR/autopiano.svg"

DEB_ROOT="$BUILD_DIR/deb-root"
mkdir -p "$DEB_ROOT/DEBIAN" "$DEB_ROOT/usr/lib/autopiano" \
  "$DEB_ROOT/usr/share/applications" "$DEB_ROOT/usr/share/icons/hicolor/scalable/apps" \
  "$DEB_ROOT/usr/bin"
cp "$ROOT_DIR/autopiano.py" "$DEB_ROOT/usr/lib/autopiano/"
cp "$ROOT_DIR/requirements.txt" "$DEB_ROOT/usr/lib/autopiano/"
cp "$ROOT_DIR/packaging/autopiano.desktop" "$DEB_ROOT/usr/share/applications/"
sed -i 's/^Exec=AutoPiano$/Exec=autopiano/' "$DEB_ROOT/usr/share/applications/autopiano.desktop"
cp "$ROOT_DIR/packaging/autopiano.svg" "$DEB_ROOT/usr/share/icons/hicolor/scalable/apps/autopiano.svg"
cat > "$DEB_ROOT/usr/bin/autopiano" <<'EOF'
#!/bin/sh
exec python3 /usr/lib/autopiano/autopiano.py "$@"
EOF
chmod 755 "$DEB_ROOT/usr/bin/autopiano"
sed -e "s/@VERSION@/$VERSION/" -e "s/@ARCH@/$ARCH/" \
  "$ROOT_DIR/packaging/control.in" > "$DEB_ROOT/DEBIAN/control"
dpkg-deb --build --root-owner-group "$DEB_ROOT" "$OUTPUT_DIR/autopiano_${VERSION}_${ARCH}.deb"

APPIMAGETOOL="$BUILD_DIR/appimagetool"
if ! command -v appimagetool >/dev/null 2>&1; then
  curl -L --fail --silent --show-error \
    -o "$APPIMAGETOOL" \
    "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
  chmod 755 "$APPIMAGETOOL"
else
  APPIMAGETOOL="$(command -v appimagetool)"
fi
ARCH=x86_64 "$APPIMAGETOOL" "$APP_DIR" \
  "$OUTPUT_DIR/AutoPiano-${VERSION}-x86_64.AppImage"

printf 'Paquetes creados en: %s\n' "$OUTPUT_DIR"