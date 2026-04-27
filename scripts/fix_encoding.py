"""Fix all local_agent .py files: add encoding='utf-8' to write_text, fix utcnow deprecation."""
import re
import pathlib

local_agent = pathlib.Path("local_agent")
files = list(local_agent.glob("*.py"))

def fix_write_text(m):
    args = m.group(1)
    if "encoding" in args:
        return m.group(0)
    return ".write_text(" + args + ', encoding="utf-8")'

for fp in files:
    text = fp.read_text(encoding="utf-8")
    original = text

    # Fix .write_text() calls — add encoding="utf-8" if missing
    text = re.sub(r'\.write_text\(([^)]+)\)', fix_write_text, text)

    # Fix datetime.utcnow() -> datetime.now(timezone.utc)
    text = text.replace("datetime.utcnow()", "datetime.now(timezone.utc)")

    # Ensure timezone is imported alongside datetime
    if "timezone.utc" in text:
        text = re.sub(
            r"from datetime import datetime(?!\s*,\s*timezone)",
            "from datetime import datetime, timezone",
            text,
        )

    if text != original:
        fp.write_text(text, encoding="utf-8")
        print(f"Fixed: {fp.name}")
    else:
        print(f"Clean: {fp.name}")

print("Done.")
