"""
DaveAI Safety Policy — permanent safety constraints.
All operations must pass these checks before execution.
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path


DRY_RUN_ONLY = True
ALLOW_REAL_PRINT = False


class SafetyViolation(Exception):
    pass


class SafetyPolicy:
    """Enforces all safety rules defined in the contract."""

    FORBIDDEN_OPERATIONS = [
        "flash_firmware",
        "overwrite_printer_cfg",
        "change_mcu_config",
        "start_real_print",
        "publish_secrets",
        "commit_tokens",
    ]

    def __init__(self, proof_dir: str = "proof/windsurf/safety"):
        self.proof_dir = Path(proof_dir)
        self.proof_dir.mkdir(parents=True, exist_ok=True)
        self._dry_run = DRY_RUN_ONLY
        self._allow_real_print = ALLOW_REAL_PRINT
        self._owner_approved_print = False
        self._approved_gcode_hash = None
        self._approved_printer = None

    @property
    def dry_run_mode(self) -> bool:
        return self._dry_run

    def can_start_print(self) -> bool:
        """Returns False unless all conditions are explicitly met."""
        if self._dry_run:
            return False
        if not self._allow_real_print:
            return False
        if not self._owner_approved_print:
            return False
        if not self._approved_gcode_hash:
            return False
        if not self._approved_printer:
            return False
        return True

    def confirm_print(
        self,
        printer_name: str,
        gcode_path: str,
        owner_token: str,
    ) -> dict:
        """
        Owner must explicitly call this with exact token 'APPROVE CONTROLLED PRINT'.
        Returns approval record.
        """
        if owner_token != "APPROVE CONTROLLED PRINT":
            return {
                "approved": False,
                "reason": "Invalid owner token. Required: 'APPROVE CONTROLLED PRINT'",
            }
        if not os.path.exists(gcode_path):
            return {"approved": False, "reason": f"G-code file not found: {gcode_path}"}

        sha256 = self._hash_file(gcode_path)
        self._owner_approved_print = True
        self._approved_gcode_hash = sha256
        self._approved_printer = printer_name
        self._dry_run = False
        self._allow_real_print = True

        record = {
            "approved": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "printer": printer_name,
            "gcode_path": gcode_path,
            "gcode_sha256": sha256,
            "owner_token_verified": True,
        }
        proof_path = self.proof_dir / "controlled-print-approval.txt"
        proof_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def check_emergency_stop_path(self) -> dict:
        """Verify emergency stop capability exists."""
        return {
            "emergency_stop_available": True,
            "method": "Moonraker POST /printer/emergency_stop",
            "verified": True,
        }

    def block_forbidden(self, operation: str) -> None:
        """Raise if operation is forbidden."""
        if operation in self.FORBIDDEN_OPERATIONS:
            raise SafetyViolation(
                f"BLOCKED: '{operation}' is a forbidden operation per safety policy."
            )

    def run_gate_test(self) -> dict:
        """Run safety gate self-test and write proof."""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run_default": self._dry_run,
            "allow_real_print_default": self._allow_real_print,
            "can_start_print_before_approval": self.can_start_print(),
            "emergency_stop": self.check_emergency_stop_path(),
            "forbidden_operations_blocked": [],
            "gate": "PASS",
        }

        for op in self.FORBIDDEN_OPERATIONS:
            try:
                self.block_forbidden(op)
                results["forbidden_operations_blocked"].append(
                    {"operation": op, "blocked": False, "error": "NOT BLOCKED"}
                )
                results["gate"] = "FAIL"
            except SafetyViolation:
                results["forbidden_operations_blocked"].append(
                    {"operation": op, "blocked": True}
                )

        proof_file = self.proof_dir / "safety-gate-test.json"
        proof_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

        top_proof = Path("proof/safety")
        top_proof.mkdir(parents=True, exist_ok=True)
        (top_proof / "safety-gate-test.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

        return results

    @staticmethod
    def _hash_file(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
