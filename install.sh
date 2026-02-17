#!/bin/bash
# TriadDev Installation Script
set -e

echo "🜁 Installing TriadDev..."

SKILL_DIR="${HOME}/.openclaw/skills/triadev"
mkdir -p "$SKILL_DIR"

# Copy files
cp -r lib bin templates tests examples "$SKILL_DIR/" 2>/dev/null || true
cp SKILL.md README.md requirements.txt install.sh "$SKILL_DIR/"

# Add to PATH
if ! grep -q "triadev/bin" "${HOME}/.bashrc" 2>/dev/null; then
    echo 'export PATH="${HOME}/.openclaw/skills/triadev/bin:${PATH}"' >> "${HOME}/.bashrc"
    echo "✅ Added to PATH (restart terminal or source ~/.bashrc)"
fi

echo "✅ TriadDev installed to $SKILL_DIR"
echo "Usage: triadev --help"
