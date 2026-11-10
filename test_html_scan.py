import re
from pathlib import Path

print("Scanning for markdown code-block triggers...")
triggers = []
for path in Path("dashboard").glob("**/*.py"):
    content = path.read_text(encoding="utf-8")
    for m in re.finditer(r'st\.markdown\(\s*f?([\"\']{3})(.*?)\1', content, re.DOTALL):
        snippet = m.group(2)
        lines = snippet.split("\n")
        for i in range(len(lines) - 1):
            if lines[i].strip() == "" and (lines[i+1].startswith("    ") or lines[i+1].startswith("\t")):
                if any(c in lines[i+1] for c in ["<", "div", "tr", "td", "span", "table", "p"]):
                    triggers.append((path.name, i+2, lines[i+1].strip()))

for t in triggers:
    print(f"{t[0]}:{t[1]} -> {t[2][:60]}")

print(f"Total potential triggers: {len(triggers)}")

