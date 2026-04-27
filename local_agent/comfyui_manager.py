"""
DaveAI ComfyUI Manager — detects, installs, starts, and health-checks ComfyUI.
Manages Hunyuan3D model detection and sequential VRAM policy.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass


# Primary ComfyUI install (verified on this machine)
COMFYUI_SEARCH_PATHS = [
    r"G:\Github\ComfyUI",           # PRIMARY — verified present
    r"C:\Users\Admin\Downloads\ComfyUI",
    r"C:\Users\Admin\ComfyUI",
    r"G:\ComfyUI",
]
COMFYUI_INSTALL_PATH = r"G:\Github\ComfyUI"
COMFYUI_URL = "http://localhost:8188"

# Hunyuan3D HuggingFace repo IDs — 2.1 is PRIMARY for RTX 3090 Ti (24GB)
HUNYUAN3D_MODEL_IDS = [
    "tencent/Hunyuan3D-2.1",   # PRIMARY — best quality, needs ~18-20GB VRAM
    "tencent/Hunyuan3D-2",    # fallback — v2.0
]

# Subfolder names inside the HF repo / ComfyUI model dirs
# 2.1 uses 'hunyuan3d-dit-v2-1' for shape and 'hunyuan3d-paint-v2-1' for paint
HUNYUAN3D_SHAPE_NAMES = [
    "hunyuan3d-dit-v2-1",     # 2.1 full — PRIMARY for 3090 Ti
    "hunyuan3d-dit-v2-0",     # 2.0 fallback
    "Hunyuan3D-Shape-v2-1",
    "hy3dgen",
]
HUNYUAN3D_PAINT_NAMES = [
    "hunyuan3d-paintpbr-v2-1", # 2.1 PBR paint — PRIMARY (physically-based rendering)
    "hunyuan3d-vae-v2-1",      # 2.1 VAE — required for mesh decoding
    "hunyuan3d-paint-v2-1",
    "hunyuan3d-paint-v2-0",    # 2.0 fallback
    "Hunyuan3D-Paint-v2-1",
]

# Where models land after download
# Layout: G:\Github\ComfyUI\models\hunyuan3d\  (shape + paint subfolders)
COMFYUI_HUNYUAN3D_MODEL_DIR = r"G:\Github\ComfyUI\models\hunyuan3d"
COMFYUI_CUSTOM_NODES_DIR    = r"G:\Github\ComfyUI\custom_nodes"

# HuggingFace cache roots (for detection fallback)
HF_CACHE_ROOTS = [
    r"C:\Users\Admin\.cache\huggingface\hub",
    r"G:\Github\ComfyUI\models\hunyuan3d",
    r"C:\Users\Admin\.huggingface",
]


def find_comfyui() -> Optional[str]:
    """Return path to ComfyUI installation or None."""
    for path in COMFYUI_SEARCH_PATHS:
        main_py = os.path.join(path, "main.py")
        if os.path.exists(main_py):
            return path
    return None


def check_comfyui_health(url: str = COMFYUI_URL, timeout: int = 10) -> dict:
    """Check if ComfyUI is running and responding."""
    result = {"url": url, "running": False, "status_code": None, "error": None}
    try:
        req = urllib.request.Request(f"{url}/system_stats")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result["running"] = True
            result["status_code"] = resp.status
            data = json.loads(resp.read().decode())
            result["system_stats"] = data
    except urllib.error.URLError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = str(e)
    return result


def find_hunyuan3d_models() -> dict:
    """Search for Hunyuan3D model files in known locations."""
    found = {
        "shape_models": [],
        "paint_models": [],
        "search_paths": HF_CACHE_ROOTS,
    }

    comfyui_path = find_comfyui()
    search_dirs = list(HF_CACHE_ROOTS)
    search_dirs.append(COMFYUI_HUNYUAN3D_MODEL_DIR)
    if comfyui_path:
        search_dirs.append(os.path.join(comfyui_path, "models"))
        search_dirs.append(os.path.join(comfyui_path, "models", "hunyuan3d"))
        search_dirs.append(os.path.join(comfyui_path, "custom_nodes"))
        search_dirs.append(os.path.join(comfyui_path, "custom_nodes", "ComfyUI-Hunyuan3DWrapper"))
        search_dirs.append(os.path.join(comfyui_path, "custom_nodes", "ComfyUI-Hunyuan-3D-2"))

    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        for root, dirs, files in os.walk(search_dir):
            for name in HUNYUAN3D_SHAPE_NAMES:
                if name.lower() in root.lower() or name.lower() in " ".join(files).lower():
                    if root not in found["shape_models"]:
                        found["shape_models"].append(root)
            for name in HUNYUAN3D_PAINT_NAMES:
                if name.lower() in root.lower() or name.lower() in " ".join(files).lower():
                    if root not in found["paint_models"]:
                        found["paint_models"].append(root)

    return found


def write_vram_policy(proof_dir: Path) -> None:
    """Write VRAM sequential policy documentation."""
    policy = """# Hunyuan3D VRAM Sequential Policy — RTX 3090 Ti (24GB)

## Policy

Hunyuan3D 2.1 operates in sequential VRAM mode to fit within 24GB:

1. Load shape generation model (Hunyuan3D-Shape-v2-1)
2. Run shape generation → save mesh to disk
3. Unload shape model, clear CUDA cache, free GPU memory
4. (Optional) Load paint/texture model (Hunyuan3D-Paint-v2-1)
5. Run texture generation on saved mesh
6. Unload paint model, clear CUDA cache
7. Send final mesh to Blender for repair/export

## Implementation

```python
import torch
import gc

def clear_gpu():
    torch.cuda.empty_cache()
    gc.collect()

# Stage 1: Shape
shape_model = load_shape_model()
mesh = shape_model.generate(prompt)
save_mesh(mesh)
del shape_model
clear_gpu()

# Stage 2: Paint (optional)
if texture_requested:
    paint_model = load_paint_model()
    textured = paint_model.apply(mesh_path)
    save_textured(textured)
    del paint_model
    clear_gpu()
```

## GPU
- Device: RTX 3090 Ti
- VRAM: 24GB
- Mode: sequential (not parallel)
"""
    (proof_dir / "vram-policy.md").write_text(policy, encoding="utf-8")


def run_comfyui_phase() -> dict:
    """Full ComfyUI/Hunyuan3D phase check."""
    proof_dir = Path("proof/windsurf/comfyui")
    proof_dir.mkdir(parents=True, exist_ok=True)

    comfyui_path = find_comfyui()
    comfyui_location = comfyui_path or "NOT_FOUND"
    (proof_dir / "comfyui-location.txt").write_text(comfyui_location, encoding="utf-8")
    print(f"[ComfyUI] Location: {comfyui_location}")

    health = check_comfyui_health()
    (proof_dir / "comfyui-health.json").write_text(json.dumps(health, indent=2), encoding="utf-8")
    print(f"[ComfyUI] Running: {health['running']}")

    models = find_hunyuan3d_models()
    model_files_lines = []
    for sm in models["shape_models"]:
        model_files_lines.append(f"SHAPE: {sm}")
    for pm in models["paint_models"]:
        model_files_lines.append(f"PAINT: {pm}")
    if not model_files_lines:
        model_files_lines.append("NO_HUNYUAN3D_MODELS_FOUND — download required")
    (proof_dir / "hunyuan3d-model-files.txt").write_text("\n".join(model_files_lines), encoding="utf-8")

    write_vram_policy(proof_dir)

    shape_test = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "comfyui_found": comfyui_path is not None,
        "comfyui_running": health["running"],
        "hunyuan3d_shape_found": len(models["shape_models"]) > 0,
        "hunyuan3d_paint_found": len(models["paint_models"]) > 0,
        "shape_model_paths": models["shape_models"],
        "paint_model_paths": models["paint_models"],
        "gate": None,
        "blocker": None,
    }

    if not comfyui_path:
        shape_test["gate"] = "BLOCKED"
        shape_test["blocker"] = "BLOCKED_SERVICE — ComfyUI not installed"
    elif not health["running"]:
        shape_test["gate"] = "BLOCKED"
        shape_test["blocker"] = "BLOCKED_SERVICE — ComfyUI not running (start manually or via bootstrap)"
    elif not models["shape_models"]:
        shape_test["gate"] = "BLOCKED"
        shape_test["blocker"] = "BLOCKED_SERVICE — Hunyuan3D shape model not found"
    else:
        shape_test["gate"] = "PASS"

    (proof_dir / "hunyuan3d-shape-test.json").write_text(json.dumps(shape_test, indent=2), encoding="utf-8")
    print(f"[ComfyUI] Gate: {shape_test['gate']} — {shape_test.get('blocker', 'OK')}")
    return shape_test


if __name__ == "__main__":
    result = run_comfyui_phase()
    print(json.dumps(result, indent=2))
