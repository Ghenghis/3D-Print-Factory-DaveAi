"""
Targeted fix: move encoding="utf-8" from inside json.dumps() to write_text().
Also fix the mangled .get() call in printer_discovery.py.
"""
import re
import pathlib

local_agent = pathlib.Path("local_agent")
files = list(local_agent.glob("*.py"))

# Pattern: write_text(json.dumps(CONTENT, indent=2, encoding="utf-8"))
# Fix to:  write_text(json.dumps(CONTENT, indent=2), encoding="utf-8")
re_bad = re.compile(
    r'\.write_text\((json\.dumps\([^)]+),\s*encoding=["\']utf-8["\']\)\)',
    re.DOTALL
)

# Also fix: .get("moonraker_status", encoding="utf-8") -> .get("moonraker_status", "")
re_bad_get = re.compile(r'\.get\("moonraker_status",\s*encoding=["\']utf-8["\']\)')

fixed = []
for fp in files:
    text = fp.read_text(encoding="utf-8")
    original = text

    text = re_bad.sub(lambda m: '.write_text(' + m.group(1) + '), encoding="utf-8")', text)
    text = re_bad_get.sub('.get("moonraker_status", "")', text)

    if text != original:
        fp.write_text(text, encoding="utf-8")
        fixed.append(fp.name)
        print(f"Fixed: {fp.name}")
    else:
        print(f"Clean: {fp.name}")

print(f"\nDone. Fixed {len(fixed)} files.")
