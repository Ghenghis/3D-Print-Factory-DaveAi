"""
DaveAI Proof Collector — indexes and validates all proof artifacts.
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_PROOF_FILES = [
    "proof/windsurf/baseline/MAXHERMES_PROOF_VERIFICATION.md",
    "proof/windsurf/baseline/git-status-before.txt",
    "proof/windsurf/env/python-version.txt",
    "proof/windsurf/blender/blender-version.txt",
    "proof/windsurf/blender/blender-e2e-output.txt",
    "proof/windsurf/blender/output-sha256.txt",
    "proof/windsurf/comfyui/comfyui-location.txt",
    "proof/windsurf/comfyui/comfyui-health.json",
    "proof/windsurf/comfyui/hunyuan3d-model-files.txt",
    "proof/windsurf/comfyui/hunyuan3d-shape-test.json",
    "proof/windsurf/comfyui/vram-policy.md",
    "proof/windsurf/moonraker/printer-scan-results.json",
    "proof/windsurf/moonraker/active-printer-status.json",
    "proof/windsurf/moonraker/idle-printer-status.json",
    "proof/windsurf/router/router-validation.json",
    "proof/windsurf/safety/safety-gate-test.json",
    "proof/windsurf/e2e/full-dryrun-report.md",
    "proof/windsurf/e2e/no-print-started.txt",
    "proof/windsurf/memory/memory-loop.csv",
    "proof/windsurf/final/WINDSURF_FINAL_VERDICT.md",
    "proof/blender/blender-e2e-test.json",
    "proof/router/router-validation.json",
    "proof/safety/safety-gate-test.json",
    "proof/moonraker/fleet-scan-4active.json",
]


def hash_file(path: str) -> str:
    if not os.path.exists(path):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_proof_index() -> dict:
    """Scan all proof files, compute hashes, write index."""
    proof_dir = Path("proof")
    index_dir = Path("proof/windsurf/final")
    index_dir.mkdir(parents=True, exist_ok=True)

    all_files = []
    if proof_dir.exists():
        for p in sorted(proof_dir.rglob("*")):
            if p.is_file():
                all_files.append({
                    "path": str(p),
                    "size_bytes": p.stat().st_size,
                    "sha256": hash_file(str(p)),
                })

    required_check = []
    for req in REQUIRED_PROOF_FILES:
        exists = os.path.exists(req)
        required_check.append({
            "required": req,
            "exists": exists,
            "sha256": hash_file(req) if exists else None,
        })

    missing = [r for r in required_check if not r["exists"]]

    index = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_proof_files": len(all_files),
        "required_files_present": len(required_check) - len(missing),
        "required_files_missing": len(missing),
        "missing_files": [m["required"] for m in missing],
        "all_files": all_files,
        "required_check": required_check,
    }

    (index_dir / "proof-index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"[ProofCollector] {index['total_proof_files']} files, {len(missing)} required missing")
    return index


if __name__ == "__main__":
    result = build_proof_index()
    print(f"Missing: {result['missing_files']}")
