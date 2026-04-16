#!/usr/bin/env bash

# Use the venv's python directly (avoids CRLF issues in activate scripts on Windows).
PY=""

if [ -f "venv/Scripts/python.exe" ]; then
  PY="venv/Scripts/python.exe"
elif [ -f ".venv/Scripts/python.exe" ]; then
  PY=".venv/Scripts/python.exe"
elif [ -f "venv/bin/python" ]; then
  PY="venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  echo "ERROR: Could not find virtualenv python (venv/ or .venv/)."
  exit 1
fi

# Run the test suite; pytest's exit code becomes this script's exit code (0/1)
"$PY" -m pytest
