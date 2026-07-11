#!/bin/bash
# Build script for Sony Walkman Repair Tool macOS App
# This creates a one-click .app bundle

echo "🎵 Building Sony Walkman Repair Tool..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create the app bundle structure
APP_NAME="Sony Walkman Repair"
APP_DIR="${APP_NAME}.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

echo "📁 Creating app bundle structure..."
rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy the Python script
echo "📄 Copying Python script..."
cp sony_walkman_repair_gui.py "$RESOURCES_DIR/"

# Copy template files
echo "📦 Copying template files..."
if [ -d "dmg_contents/ManicStage.app/Contents/Resources/templates" ]; then
    cp -r "dmg_contents/ManicStage.app/Contents/Resources/templates" "$RESOURCES_DIR/"
fi

# Create the Info.plist
echo "⚙️  Creating Info.plist..."
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>Sony Walkman Repair</string>
    <key>CFBundleIdentifier</key>
    <string>com.sonywalkman.repair</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>MacOS/SonyWalkmanRepair</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSBackgroundOnly</key>
    <false/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Create the launcher script
echo "🚀 Creating launcher..."
cat > "$MACOS_DIR/SonyWalkmanRepair" << 'LAUNCHER'
#!/bin/bash
# Launcher for Sony Walkman Repair Tool

# Get the Resources directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../Resources" && pwd )"

# Find Python 3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v /usr/bin/python3 &> /dev/null; then
    PYTHON_CMD="/usr/bin/python3"
else
    osascript -e 'display alert "Python 3 Not Found" message "Please install Python 3 from python.org" as critical'
    exit 1
fi

# Run the GUI script
cd "$SCRIPT_DIR"
$PYTHON_CMD "$SCRIPT_DIR/sony_walkman_repair_gui.py"
LAUNCHER

chmod +x "$MACOS_DIR/SonyWalkmanRepair"

# Create an icon (simple placeholder)
echo "🎨 Creating app icon..."
# For now, we'll use a generic document icon
# Users can replace Icon.icns with a custom one if desired

echo ""
echo "✅ Build complete!"
echo ""
echo "📍 Your app is ready: $SCRIPT_DIR/${APP_NAME}.app"
echo ""
echo "To use:"
echo "  1. Connect your Sony NW-S715F via USB"
echo "  2. Double-click '${APP_NAME}.app'"
echo "  3. Click 'Start Repair'"
echo "  4. Wait for completion and safely eject"
echo ""
echo "⚠️  Note: macOS may warn about unidentified developer."
echo "   To fix: Right-click the app → Open → Click Open again"
echo ""
