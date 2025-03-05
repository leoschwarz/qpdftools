#!/bin/bash

# Script to generate Windows app.ico from SVG source
# This script requires ImageMagick to be installed
# Run: sudo apt-get install imagemagick (on Debian/Ubuntu)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SVG_SOURCE="$PROJECT_ROOT/resources/icons/sc-apps-br.eng.silas.qpdftools.svg"
ICO_OUTPUT="$PROJECT_ROOT/resources/windows/app.ico"

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "Error: ImageMagick is not installed. Please install it first:"
    echo "  sudo apt-get install imagemagick"
    exit 1
fi

echo "Generating Windows icon from SVG source..."
convert "$SVG_SOURCE" -define icon:auto-resize=16,32,48,64,128,256 "$ICO_OUTPUT"

# Verify the icon was created
if [ ! -f "$ICO_OUTPUT" ]; then
    echo "Error: Failed to generate app.ico"
    exit 1
fi

echo "Successfully generated app.ico"
echo "File size: $(du -h "$ICO_OUTPUT" | cut -f1)"
echo "Location: $ICO_OUTPUT"

# Remind to commit the file
echo ""
echo "Don't forget to commit the generated icon file:"
echo "  git add $ICO_OUTPUT"
echo "  git commit -m \"Add pre-generated Windows icon\""