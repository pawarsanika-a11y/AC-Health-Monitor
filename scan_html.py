"""
Scan all dashboard Python files for st.markdown() blocks
that have blank lines before indented HTML (Streamlit code-block trigger).
"""
import re
from pathlib import Path

ROOT = Path(r"c:\Users\lenovo\OneDrive\Desktop\projects\AI-AC-Health-Monitor\AC-Health-Monitor\dashboard")

files = list(ROOT.rglob("*.py"))
findings = []

for f in files:
    text = f.read_text(encoding="utf-8")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        # Find st.markdown( calls
        if "st.markdown(" in line and ('"""' in line or "'''" in line):
            # Look ahead for blank line followed by 4+ space indented HTML tag
            for j in range(i+1, min(i+40, len(lines))):
                if lines[j].strip() == "":  # blank line
                    # Check next non-blank line
                    for k in range(j+1, min(j+5, len(lines))):
                        nl = lines[k]
                        if nl.strip() == "":
                            continue
                        # Check if it starts with 4+ spaces and has an HTML tag
                        leading = len(nl) - len(nl.lstrip())
                        stripped = nl.strip()
                        if leading >= 4 and (stripped.startswith("<") or stripped.startswith("<!--")):
                            findings.append({
                                "file": str(f.relative_to(ROOT.parent)),
                                "markdown_line": i + 1,
                                "blank_line": j + 1,
                                "trigger_line": k + 1,
                                "trigger_content": nl.rstrip()[:80],
                            })
                        break
                    break

if findings:
    print(f"Found {len(findings)} potential raw-HTML triggers:\n")
    for fi in findings:
        print(f"  {fi['file']}:{fi['markdown_line']}  (blank@{fi['blank_line']}, tag@{fi['trigger_line']})")
        print(f"    -> {fi['trigger_content']}")
        print()
else:
    print("No raw-HTML triggers found!")

