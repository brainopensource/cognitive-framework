#!/bin/sh
# tools/wordcount_v4.sh — the authoritative v4 word count (see 00 §4.1).
#
# Rules, in order:
#   1. Strip the leading YAML front-matter block (first --- to next ---).
#   2. Strip fenced code blocks (``` ... ```), including the fences.
#   3. A word is a whitespace-separated token containing >= 1 alphanumeric char.
# Markdown tables, headings, links and blockquotes DO count. Code does not.
#
# Usage: tools/wordcount_v4.sh docs/v4/*.md
# Exit status is always 0; budget enforcement is CI's job (CI-5).

total=0
for f in "$@"; do
  n=$(awk '
    NR==1 && $0=="---" { fm=1; next }
    fm==1 && $0=="---" { fm=0; next }
    fm==1 { next }
    /^[ \t]*```/ { code = !code; next }
    code { next }
    { print }
  ' "$f" | tr -s '[:space:]' '\n' | grep -c '[[:alnum:]]')
  total=$((total + n))
  printf '%7d  %s\n' "$n" "$f"
done
printf '%7d  TOTAL\n' "$total"
