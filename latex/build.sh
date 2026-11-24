#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
for target in questions answers; do
  xelatex -interaction=nonstopmode -halt-on-error "$target.tex"
  xelatex -interaction=nonstopmode -halt-on-error "$target.tex"
done
