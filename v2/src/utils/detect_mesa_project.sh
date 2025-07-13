#!/bin/bash

echo "🔍 Scanning Python project for MESA usage..."

# Step 1: Detect files that import mesa
mesa_files=$(grep -rl "import mesa" . --include="*.py")

if [[ -z "$mesa_files" ]]; then
    echo "❌ No usage of MESA detected in this project."
else
    echo "✅ MESA usage detected in the following files:"
    echo "$mesa_files"
    echo ""
fi

# Step 2: Show full folder and file structure (like tree)
echo "📁 Project folder structure:"
find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'
echo ""

# Step 3: List all Python imports
echo "📦 Python imports by file:"
find . -type f -name "*.py" | while read file; do
    echo "---- $file ----"
    grep -E "^\s*(import|from) " "$file" || echo "(no imports)"
    echo ""
done
