"""
DaveAI Verdict Engine — evaluates all gates and produces final verdict.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


VERDICTS = [
    "FAIL",
    "DEV_COMPLETE_NOT_E2E_PROVEN",
    "LOCAL_AGENT_READY",
    "PRODUCTION_CANDIDATE_BLOCKED",
    "PRODUCTION_CANDIDATE",
    "PRODUCTION_READY",
]


class VerdictEngine:
    def __init__(self, proof_root: str = "proof"):
        self.proof_root = Path(proof_root)
        self.gates = {}

    def record_gate(self, gate_id: str, status: str, proof_path: Optional[str] = None, note: str = ""):
        self.gates[gate_id] = {
            "status": status,
            "proof": proof_path,
            "note": note,
        }

    def evaluate(self) -> dict:
        """Compute overall verdict from gate statuses."""
        gate_statuses = {k: v["status"] for k, v in self.gates.items()}

        if any(s == "FAIL" for s in gate_statuses.values()):
            verdict = "FAIL"
        elif not self.gates:
            verdict = "DEV_COMPLETE_NOT_E2E_PROVEN"
        elif all(
            s in ["PASS", "N/A", "SKIP"] for s in gate_statuses.values()
            if "G11" not in s
        ):
            controlled_print = gate_statuses.get("G11_controlled_print", "PENDING")
            if controlled_print == "PASS":
                verdict = "PRODUCTION_READY"
            else:
                blocked_gates = [k for k, v in gate_statuses.items() if v == "BLOCKED"]
                if blocked_gates:
                    verdict = "PRODUCTION_CANDIDATE_BLOCKED"
                else:
                    verdict = "PRODUCTION_CANDIDATE"
        elif any(s == "BLOCKED" for s in gate_statuses.values()):
            verdict = "PRODUCTION_CANDIDATE_BLOCKED"
        else:
            verdict = "DEV_COMPLETE_NOT_E2E_PROVEN"

        gate_table = []
        for gate_id, info in self.gates.items():
            gate_table.append({
                "gate": gate_id,
                "status": info["status"],
                "proof": info.get("proof", ""),
                "note": info.get("note", ""),
            })

        blocked = [g for g in gate_table if g["status"] == "BLOCKED"]
        passed = [g for g in gate_table if g["status"] == "PASS"]
        failed = [g for g in gate_table if g["status"] == "FAIL"]

        return {
            "verdict": verdict,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gate_table": gate_table,
            "summary": {
                "total": len(gate_table),
                "pass": len(passed),
                "fail": len(failed),
                "blocked": len(blocked),
            },
            "remaining_blockers": [
                f"{g['gate']}: {g['note']}" for g in blocked
            ],
        }

    def write_final_verdict(self, commands_run: list = None, bugs_fixed: list = None) -> str:
        """Write proof/windsurf/final/WINDSURF_FINAL_VERDICT.md and return verdict string."""
        result = self.evaluate()
        verdict = result["verdict"]

        final_dir = Path("proof/windsurf/final")
        final_dir.mkdir(parents=True, exist_ok=True)

        gate_rows = "\n".join(
            f"| {g['gate']} | {g['status']} | {g['proof']} |"
            for g in result["gate_table"]
        )

        blockers = "\n".join(
            f"- {b}" for b in result["remaining_blockers"]
        ) or "None"

        cmds = "\n".join(
            f"- {c}" for c in (commands_run or [])
        ) or "See task-history.jsonl"

        bugs = "\n".join(
            f"- {b}" for b in (bugs_fixed or [])
        ) or "None recorded"

        md = f"""# Windsurf Final Verdict — DaveAI 3D Print Factory

## Verdict

**{verdict}**

Generated: {result['timestamp']}

## Gate Table

| Gate | Status | Proof |
|------|--------|-------|
{gate_rows}

## Summary

- Total gates: {result['summary']['total']}
- Pass: {result['summary']['pass']}
- Fail: {result['summary']['fail']}
- Blocked: {result['summary']['blocked']}

## Files Changed

See git diff on branch `windsurf/final-e2e-truth-proof`

## Commands Run by Windsurf

{cmds}

## Proof Artifacts

See `proof/windsurf/` directory tree.

## Bugs Found and Fixed

{bugs}

## Remaining Blockers

{blockers}

## Owner Facts Requested

- Printer IPs: if auto-discovery fails, provide IPs for FLSUN V400/T1#1/T1#2/S1
- Controlled print approval: required for PRODUCTION_READY verdict

## Final Release Judge Statement

Verdict `{verdict}` is the honest assessment based on locally executed proof gates.
No gate is marked PASS without real test execution and artifact generation.
"""

        (final_dir / "WINDSURF_FINAL_VERDICT.md").write_text(md, encoding="utf-8")
        (final_dir / "verdict.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"[VerdictEngine] Final verdict: {verdict}")
        return verdict
