"""
DaveAI Maintenance Manager
Reads/writes config/printer-maintenance.yaml at runtime.
No restart required — toggled per printer key.
"""

import json
from pathlib import Path
from typing import Optional

MAINTENANCE_FILE = Path("config/printer-maintenance.yaml")

ALL_PRINTER_KEYS = [
    "flsun_v400",
    "flsun_t1_1",
    "flsun_t1_2",
    "flsun_s1",
    "flsun_qq_pro",
    "flsun_super_racer",
    "cr10s",
    "tronxy_d01",
    "tronxy_x5sa",
    "cr6_max",
    "prusa_mk3s",
    "sovol_sv01",
]

PRINTER_NAMES = {
    "flsun_v400": "FLSUN V400",
    "flsun_t1_1": "FLSUN T1 #1",
    "flsun_t1_2": "FLSUN T1 #2",
    "flsun_s1": "FLSUN S1",
    "flsun_qq_pro": "FLSUN QQ-S Pro",
    "flsun_super_racer": "FLSUN Super Racer",
    "cr10s": "Creality CR-10S",
    "tronxy_d01": "Tronxy D01 Pro Enclosed",
    "tronxy_x5sa": "Tronxy X5SA Pro",
    "cr6_max": "Creality CR-6 Max",
    "prusa_mk3s": "Prusa MK3S",
    "sovol_sv01": "Sovol SV-01",
}


def _load_raw() -> dict:
    """Load YAML without requiring PyYAML — simple line parser for this config."""
    if not MAINTENANCE_FILE.exists():
        return {}

    raw = MAINTENANCE_FILE.read_text(encoding="utf-8")

    # Try PyYAML first
    try:
        import yaml
        return yaml.safe_load(raw) or {}
    except ImportError:
        pass

    # Fallback: minimal parser for this specific file structure
    result = {"maintenance": {}}
    current_key = None
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        if stripped == "maintenance:":
            continue
        # Printer key line (2-space indent + key + colon)
        if line.startswith("  ") and not line.startswith("    ") and stripped.endswith(":"):
            current_key = stripped[:-1]
            result["maintenance"][current_key] = {"enabled": False, "reason": ""}
        # Field line (4-space indent)
        elif line.startswith("    ") and current_key:
            if "enabled:" in stripped:
                val = stripped.split("enabled:")[-1].strip().lower()
                result["maintenance"][current_key]["enabled"] = val == "true"
            elif "reason:" in stripped:
                val = stripped.split("reason:")[-1].strip().strip('"')
                result["maintenance"][current_key]["reason"] = val
    return result


def _save(data: dict) -> None:
    """Write back to YAML — preserves header comment, rebuilds body."""
    header = (
        "# DaveAI Printer Maintenance Toggles\n"
        "# Set maintenance: true to put a printer into ONLINE_MAINTENANCE mode.\n"
        "# The agent reads this file at runtime — no restart required.\n"
        "# When maintenance: true, the printer is connection-tested only.\n"
        "# No jobs, no heat, no movement commands will be sent.\n\n"
        "maintenance:\n"
    )
    body = ""
    maintenance = data.get("maintenance", {})
    for key in ALL_PRINTER_KEYS:
        entry = maintenance.get(key, {"enabled": False, "reason": ""})
        enabled = str(entry.get("enabled", False)).lower()
        reason = entry.get("reason", "")
        body += f"  {key}:\n"
        body += f"    enabled: {enabled}\n"
        body += f"    reason: \"{reason}\"\n\n"
    MAINTENANCE_FILE.write_text(header + body, encoding="utf-8")


def get_all() -> dict:
    """Return full maintenance state for all printers."""
    data = _load_raw()
    maintenance = data.get("maintenance", {})
    result = {}
    for key in ALL_PRINTER_KEYS:
        entry = maintenance.get(key, {"enabled": False, "reason": ""})
        result[key] = {
            "name": PRINTER_NAMES.get(key, key),
            "key": key,
            "maintenance": entry.get("enabled", False),
            "reason": entry.get("reason", ""),
        }
    return result


def is_in_maintenance(printer_key: str) -> bool:
    """Returns True if printer is currently in maintenance mode."""
    data = _load_raw()
    entry = data.get("maintenance", {}).get(printer_key, {})
    return bool(entry.get("enabled", False))


def set_maintenance(printer_key: str, enabled: bool, reason: str = "") -> dict:
    """
    Toggle maintenance mode for a printer.
    Returns updated state dict.
    """
    if printer_key not in ALL_PRINTER_KEYS:
        return {"error": f"Unknown printer key: {printer_key}"}

    data = _load_raw()
    if "maintenance" not in data:
        data["maintenance"] = {}
    if printer_key not in data["maintenance"]:
        data["maintenance"][printer_key] = {}

    data["maintenance"][printer_key]["enabled"] = enabled
    data["maintenance"][printer_key]["reason"] = reason
    _save(data)

    action = "MAINTENANCE ON" if enabled else "MAINTENANCE OFF"
    name = PRINTER_NAMES.get(printer_key, printer_key)
    print(f"[Maintenance] {name} ({printer_key}): {action} — {reason or 'no reason given'}")

    return {
        "printer": name,
        "key": printer_key,
        "maintenance": enabled,
        "reason": reason,
        "action": action,
    }


def print_status_table() -> None:
    """Print a human-readable maintenance status table."""
    all_state = get_all()
    print("\n=== Printer Maintenance Status ===")
    print(f"{'Printer':<30} {'Key':<20} {'Maintenance':<12} Reason")
    print("-" * 80)
    for key, info in all_state.items():
        flag = "*** ON ***" if info["maintenance"] else "off"
        print(f"{info['name']:<30} {key:<20} {flag:<12} {info['reason']}")
    print()


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if not args or args[0] == "status":
        print_status_table()

    elif args[0] == "on" and len(args) >= 2:
        key = args[1]
        reason = " ".join(args[2:]) if len(args) > 2 else ""
        result = set_maintenance(key, True, reason)
        print(json.dumps(result, indent=2))

    elif args[0] == "off" and len(args) >= 2:
        key = args[1]
        result = set_maintenance(key, False, "")
        print(json.dumps(result, indent=2))

    else:
        print("Usage:")
        print("  python -m local_agent.maintenance_manager status")
        print("  python -m local_agent.maintenance_manager on <printer_key> [reason]")
        print("  python -m local_agent.maintenance_manager off <printer_key>")
        print()
        print("Printer keys:", ", ".join(ALL_PRINTER_KEYS))
