"""
Fix the over-applied encoding fix:
  json.dumps(..., encoding="utf-8")  -> json.dumps(...)
  .get("moonraker_status", encoding="utf-8")  -> .get("moonraker_status")
Then correctly add encoding="utf-8" ONLY to Path.write_text() calls.
"""
import re
import pathlib

local_agent = pathlib.Path("local_agent")
files = list(local_agent.glob("*.py"))

# Step 1: Remove encoding from json.dumps() — it does not accept encoding kwarg
re_json_dumps_enc = re.compile(r'(json\.dumps\([^)]+),\s*encoding=["\']utf-8["\'](\))')
# Step 2: Remove encoding from dict.get() calls
re_get_enc = re.compile(r'(\.get\([^)]+),\s*encoding=["\']utf-8["\'](\))')
# Step 3: Add encoding="utf-8" to .write_text(expr) where missing
#   Match: .write_text(ANYTHING) — only add if encoding not already present
re_write_text = re.compile(r'\.write_text\(([^)]+)\)')

def fix_write_text(m):
    args = m.group(1)
    if 'encoding' in args:
        return m.group(0)
    return '.write_text(' + args + ', encoding="utf-8")'

fixed_files = []
for fp in files:
    text = fp.read_text(encoding="utf-8")
    original = text

    # Remove bad encoding kwarg from json.dumps
    text = re_json_dumps_enc.sub(lambda m: m.group(1) + m.group(2), text)
    # Remove bad encoding kwarg from .get()
    text = re_get_enc.sub(lambda m: m.group(1) + m.group(2), text)
    # Re-apply correctly: add encoding only to .write_text()
    text = re_write_text.sub(fix_write_text, text)

    if text != original:
        fp.write_text(text, encoding="utf-8")
        fixed_files.append(fp.name)
        print(f"Fixed: {fp.name}")
    else:
        print(f"Clean: {fp.name}")

print(f"\nDone. Fixed {len(fixed_files)} files.")
