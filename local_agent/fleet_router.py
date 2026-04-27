"""
DaveAI Fleet Router — routes print jobs to correct printer based on material,
size, and active/idle status. Writes proof artifacts.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from local_agent.maintenance_manager import is_in_maintenance, get_all as get_maintenance_all
except ImportError:
    def is_in_maintenance(key): return False
    def get_maintenance_all(): return {}


ACTIVE_PRINTERS = [
    {
        "name": "FLSUN V400",
        "key": "flsun_v400",
        "status": "ACTIVE_TESTABLE",
        "type": "delta",
        "enclosure": False,
        "build_volume_mm": {"x": 300, "y": 300, "z": 410},
        "materials": ["PLA", "PETG", "TPU"],
        "best_for": ["miniatures", "speed"],
    },
    {
        "name": "FLSUN T1 #1",
        "key": "flsun_t1_1",
        "status": "ACTIVE_TESTABLE",
        "type": "delta",
        "enclosure": False,
        "build_volume_mm": {"x": 300, "y": 300, "z": 330},
        "materials": ["PLA", "PETG", "TPU"],
        "best_for": ["balanced", "prototypes"],
    },
    {
        "name": "FLSUN T1 #2",
        "key": "flsun_t1_2",
        "status": "ACTIVE_TESTABLE",
        "type": "delta",
        "enclosure": False,
        "build_volume_mm": {"x": 300, "y": 300, "z": 330},
        "materials": ["PLA", "PETG", "TPU"],
        "best_for": ["balanced", "prototypes"],
    },
    {
        "name": "FLSUN S1",
        "key": "flsun_s1",
        "status": "ONLINE_MAINTENANCE",
        "routing_allowed": False,
        "maintenance_note": "Hotend disassembled — connection test only. No jobs, no heat, no movement.",
        "type": "delta",
        "enclosure": False,
        "build_volume_mm": {"x": 320, "y": 320, "z": 430},
        "materials": ["PLA", "PETG", "TPU", "ABS"],
        "best_for": ["general"],
    },
]

IDLE_PRINTERS = [
    {
        "name": "FLSUN QQ-S Pro",
        "key": "flsun_qq_pro",
        "status": "IDLE_NOT_ONLINE",
        "type": "delta",
        "enclosure": False,
        "build_volume_mm": {"x": 255, "y": 255, "z": 360},
        "materials": ["PLA", "PETG"],
        "best_for": ["compact"],
    },
    {
        "name": "FLSUN Super Racer",
        "key": "flsun_super_racer",
        "status": "IDLE_NOT_ONLINE",
        "type": "delta",
        "enclosure": False,
        "build_volume_mm": {"x": 260, "y": 260, "z": 330},
        "materials": ["PLA", "PETG", "TPU"],
        "best_for": ["speed"],
    },
    {
        "name": "Creality CR-10S",
        "key": "cr10s",
        "status": "IDLE_NOT_ONLINE",
        "type": "cartesian",
        "enclosure": False,
        "build_volume_mm": {"x": 300, "y": 300, "z": 400},
        "materials": ["PLA", "PETG", "ABS"],
        "best_for": ["large"],
    },
    {
        "name": "Tronxy D01 Pro Enclosed",
        "key": "tronxy_d01",
        "status": "IDLE_NOT_ONLINE",
        "type": "cartesian",
        "enclosure": True,
        "build_volume_mm": {"x": 220, "y": 220, "z": 220},
        "materials": ["PLA", "ABS", "ASA", "PC", "Nylon"],
        "best_for": ["abs", "engineering"],
    },
    {
        "name": "Tronxy X5SA Pro",
        "key": "tronxy_x5sa",
        "status": "IDLE_NOT_ONLINE",
        "type": "cartesian",
        "enclosure": False,
        "build_volume_mm": {"x": 330, "y": 330, "z": 400},
        "materials": ["PLA", "PETG", "TPU"],
        "best_for": ["xl"],
    },
    {
        "name": "Creality CR-6 Max",
        "key": "cr6_max",
        "status": "IDLE_NOT_ONLINE",
        "type": "cartesian",
        "enclosure": False,
        "build_volume_mm": {"x": 400, "y": 400, "z": 400},
        "materials": ["PLA", "PETG", "TPU"],
        "best_for": ["large", "detailed"],
    },
    {
        "name": "Prusa MK3S",
        "key": "prusa_mk3s",
        "status": "IDLE_NOT_ONLINE",
        "type": "cartesian",
        "enclosure": False,
        "build_volume_mm": {"x": 250, "y": 210, "z": 210},
        "materials": ["PLA", "PETG", "ABS", "TPU"],
        "best_for": ["precision", "quality"],
    },
    {
        "name": "Sovol SV-01",
        "key": "sovol_sv01",
        "status": "IDLE_NOT_ONLINE",
        "type": "cartesian",
        "enclosure": False,
        "build_volume_mm": {"x": 280, "y": 240, "z": 300},
        "materials": ["PLA", "PETG", "TPU"],
        "best_for": ["testing", "general"],
    },
]

ALL_PRINTERS = ACTIVE_PRINTERS + IDLE_PRINTERS


def fits_in_volume(size_mm: dict, printer: dict) -> bool:
    vol = printer["build_volume_mm"]
    return (
        size_mm.get("x", 0) <= vol["x"]
        and size_mm.get("y", 0) <= vol["y"]
        and size_mm.get("z", 0) <= vol["z"]
    )


def route_job(
    material: str = "PLA",
    size_mm: Optional[dict] = None,
    dry_run: bool = True,
    ip_overrides: dict = None,
) -> dict:
    """
    Route a print job to the best available active printer.

    Returns routing decision with reason.
    """
    if size_mm is None:
        size_mm = {"x": 50, "y": 50, "z": 50}

    material_upper = material.upper()
    needs_enclosure = material_upper in ["ABS", "ASA", "PC", "NYLON"]

    decision = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job": {"material": material, "size_mm": size_mm, "dry_run": dry_run},
        "selected_printer": None,
        "reason": "",
        "skipped_printers": [],
        "blocked": False,
        "block_reason": None,
        "fleet_summary": {
            "total": len(ALL_PRINTERS),
            "active": len(ACTIVE_PRINTERS),
            "idle": len(IDLE_PRINTERS),
        },
    }

    max_dim = max(size_mm.values())
    if max_dim > 450:
        decision["blocked"] = True
        decision["block_reason"] = f"Impossible build volume: {max_dim}mm exceeds all printers"
        decision["selected_printer"] = None
        return decision

    if needs_enclosure:
        enclosed_active = [
            p for p in ACTIVE_PRINTERS
            if p.get("enclosure") and material_upper in [m.upper() for m in p["materials"]]
            and fits_in_volume(size_mm, p)
        ]
        if not enclosed_active:
            decision["blocked"] = True
            decision["block_reason"] = "BLOCKED_NO_ACTIVE_ENCLOSED_PRINTER"
            decision["reason"] = (
                f"{material} requires enclosed printer. "
                "Tronxy D01 Pro Enclosed is IDLE_NOT_ONLINE. "
                "Will be routed when printer comes online."
            )
            for p in IDLE_PRINTERS:
                if p.get("enclosure"):
                    decision["skipped_printers"].append({
                        "name": p["name"],
                        "reason": "IDLE_NOT_ONLINE",
                    })
            return decision

    candidates = []
    for p in ACTIVE_PRINTERS:
        # Check live maintenance toggle (reads config/printer-maintenance.yaml at runtime)
        live_maintenance = is_in_maintenance(p["key"])
        if live_maintenance or p.get("status") == "ONLINE_MAINTENANCE" or not p.get("routing_allowed", True):
            maint_note = p.get("maintenance_note", "maintenance mode — connection test only")
            decision["skipped_printers"].append({
                "name": p["name"],
                "reason": f"ONLINE_MAINTENANCE — {maint_note}",
            })
            continue
        if material_upper not in [m.upper() for m in p["materials"]]:
            decision["skipped_printers"].append({"name": p["name"], "reason": f"Does not support {material}"})
            continue
        if not fits_in_volume(size_mm, p):
            decision["skipped_printers"].append({"name": p["name"], "reason": "Build volume too small"})
            continue
        if needs_enclosure and not p.get("enclosure"):
            decision["skipped_printers"].append({"name": p["name"], "reason": "No enclosure"})
            continue
        candidates.append(p)

    for p in IDLE_PRINTERS:
        decision["skipped_printers"].append({"name": p["name"], "reason": "IDLE_NOT_ONLINE — not used for real jobs"})

    if not candidates:
        decision["blocked"] = True
        decision["block_reason"] = "No active printer can handle this job"
        return decision

    selected = candidates[0]
    decision["selected_printer"] = {
        "name": selected["name"],
        "key": selected["key"],
        "status": selected["status"],
        "build_volume_mm": selected["build_volume_mm"],
    }
    decision["reason"] = f"Selected {selected['name']} — ACTIVE_TESTABLE, supports {material}, fits {size_mm}"

    if ip_overrides and selected["key"] in ip_overrides:
        decision["selected_printer"]["ip"] = ip_overrides[selected["key"]]
    return decision


def run_router_tests() -> dict:
    """Run all required router test scenarios and write proof."""
    proof_dir = Path("proof/windsurf/router")
    proof_dir.mkdir(parents=True, exist_ok=True)
    top_proof = Path("proof/router")
    top_proof.mkdir(parents=True, exist_ok=True)

    tests = []

    t1 = route_job(material="PLA", size_mm={"x": 50, "y": 50, "z": 50})
    t1["test"] = "small_pla_routes_to_active"
    t1["expected"] = "selected_printer is not None and not blocked"
    t1["pass"] = t1["selected_printer"] is not None and not t1["blocked"]
    tests.append(t1)

    t2 = route_job(material="PLA", size_mm={"x": 500, "y": 500, "z": 500})
    t2["test"] = "large_impossible_rejected"
    t2["expected"] = "blocked=True (>450mm)"
    t2["pass"] = t2["blocked"] is True
    tests.append(t2)

    t3 = route_job(material="ABS", size_mm={"x": 100, "y": 100, "z": 100})
    t3["test"] = "abs_requires_enclosure_blocked"
    t3["expected"] = "blocked=True — BLOCKED_NO_ACTIVE_ENCLOSED_PRINTER"
    t3["pass"] = t3["blocked"] is True and "ENCLOSED" in str(t3.get("block_reason", ""))
    tests.append(t3)

    t4 = route_job(material="ASA", size_mm={"x": 80, "y": 80, "z": 80})
    t4["test"] = "asa_requires_enclosure_blocked"
    t4["expected"] = "blocked=True — BLOCKED_NO_ACTIVE_ENCLOSED_PRINTER"
    t4["pass"] = t4["blocked"] is True
    tests.append(t4)

    t5 = route_job(material="PLA", size_mm={"x": 50, "y": 50, "z": 50})
    idle_used = any(
        p["name"] in [s["name"] for s in t5.get("skipped_printers", [])]
        and "IDLE_NOT_ONLINE" in s.get("reason", "")
        for p in IDLE_PRINTERS
        for s in t5.get("skipped_printers", [])
        if s["name"] == p["name"]
    )
    t5["test"] = "idle_printers_not_used"
    t5["expected"] = "all idle printers in skipped list"
    idle_skipped_names = {s["name"] for s in t5.get("skipped_printers", [])}
    idle_names = {p["name"] for p in IDLE_PRINTERS}
    t5["pass"] = idle_names.issubset(idle_skipped_names)
    tests.append(t5)

    t6 = route_job(material="PLA", size_mm={"x": 50, "y": 50, "z": 50})
    s1_skipped = any(
        s["name"] == "FLSUN S1" and "ONLINE_MAINTENANCE" in s.get("reason", "")
        for s in t6.get("skipped_printers", [])
    )
    s1_not_selected = t6.get("selected_printer", {}) is None or (
        t6.get("selected_printer") and t6["selected_printer"].get("key") != "flsun_s1"
    )
    t6["test"] = "s1_maintenance_never_selected"
    t6["expected"] = "FLSUN S1 in skipped list with ONLINE_MAINTENANCE reason, not selected"
    t6["pass"] = s1_skipped and s1_not_selected
    tests.append(t6)

    all_passed = all(t["pass"] for t in tests)
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test_count": len(tests),
        "passed": sum(1 for t in tests if t["pass"]),
        "failed": sum(1 for t in tests if not t["pass"]),
        "tests": tests,
        "fleet_config": {
            "total": 12,
            "active_testable": 3,
            "online_maintenance": 1,
            "idle": 8,
            "maintenance_printers": ["FLSUN S1 — hotend disassembled, connection test only"],
        },
        "gate": "PASS" if all_passed else "FAIL",
    }

    (proof_dir / "router-validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (top_proof / "router-validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"[Router] Gate: {result['gate']} ({result['passed']}/{result['test_count']} passed)")
    return result


if __name__ == "__main__":
    result = run_router_tests()
    print(json.dumps(result, indent=2))
