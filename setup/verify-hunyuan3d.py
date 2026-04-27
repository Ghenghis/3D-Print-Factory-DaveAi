"""
Verify Hunyuan3D model files are present and accessible.
"""
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from local_agent.comfyui_manager import find_hunyuan3d_models, write_vram_policy

models = find_hunyuan3d_models()
print("Shape models found:", models["shape_models"])
print("Paint models found:", models["paint_models"])

proof_dir = Path("proof/windsurf/comfyui")
proof_dir.mkdir(parents=True, exist_ok=True)
write_vram_policy(proof_dir)

result = {
    "shape_models": models["shape_models"],
    "paint_models": models["paint_models"],
    "shape_found": len(models["shape_models"]) > 0,
    "paint_found": len(models["paint_models"]) > 0,
}

(proof_dir / "hunyuan3d-verify.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

if not result["shape_found"]:
    print("\nWARNING: No Hunyuan3D shape models found.")
    print("Run: setup/hunyuan3d-3090ti-bootstrap.ps1")
    sys.exit(1)
sys.exit(0)
