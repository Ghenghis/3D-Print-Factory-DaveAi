# =============================================================================
# DaveAI — Hunyuan3D-2 Bootstrap for 3D Printing
# Installs ONLY the 3D model generation components needed for the print pipeline.
# ComfyUI location: G:\Github\ComfyUI
# Models location:  G:\Github\ComfyUI\models\hunyuan3d\
# Custom node:      G:\Github\ComfyUI\custom_nodes\ComfyUI-Hunyuan3D-2\
# =============================================================================

$ErrorActionPreference = "Stop"

$COMFYUI_DIR     = "G:\Github\ComfyUI"
$CUSTOM_NODES    = "$COMFYUI_DIR\custom_nodes"
$HUNYUAN_NODE    = "$CUSTOM_NODES\ComfyUI-Hunyuan3DWrapper"
$MODEL_BASE      = "$COMFYUI_DIR\models\hunyuan3d"
$SHAPE_DIR       = "$MODEL_BASE\shape"
$PAINT_DIR       = "$MODEL_BASE\paint"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  DaveAI Hunyuan3D-2  Bootstrap (3D Print Pipeline)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- Check prerequisites ---
if (-not (Test-Path "$COMFYUI_DIR\main.py")) {
    Write-Host "[ERROR] ComfyUI not found at $COMFYUI_DIR" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] ComfyUI found at $COMFYUI_DIR" -ForegroundColor Green

$pythonExe = (Get-Command python -ErrorAction SilentlyContinue)?.Source
if (-not $pythonExe) { $pythonExe = "python" }
Write-Host "[OK] Python: $pythonExe"

# Check huggingface_hub
& $pythonExe -c "import huggingface_hub" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Installing huggingface_hub..." -ForegroundColor Yellow
    & $pythonExe -m pip install -q huggingface_hub
}
Write-Host "[OK] huggingface_hub available" -ForegroundColor Green

# --- Step 1: Clone ComfyUI-Hunyuan3D-2 custom node ---
Write-Host ""
Write-Host "[Step 1] Installing ComfyUI-Hunyuan3D-2 custom node..." -ForegroundColor Yellow

if (Test-Path $HUNYUAN_NODE) {
    Write-Host "  Already exists — pulling latest..." -ForegroundColor Gray
    Push-Location $HUNYUAN_NODE
    git pull --quiet
    Pop-Location
} else {
    git clone https://github.com/kijai/ComfyUI-Hunyuan3DWrapper.git $HUNYUAN_NODE
}
Write-Host "[OK] Custom node ready: $HUNYUAN_NODE" -ForegroundColor Green

# --- Step 2: Install custom node requirements ---
Write-Host ""
Write-Host "[Step 2] Installing custom node Python requirements..." -ForegroundColor Yellow

$reqFile = "$HUNYUAN_NODE\requirements.txt"
if (Test-Path $reqFile) {
    & $pythonExe -m pip install -q -r $reqFile
    Write-Host "[OK] Requirements installed" -ForegroundColor Green
} else {
    Write-Host "  No requirements.txt found — skipping" -ForegroundColor Gray
}

# --- Step 3: Download Hunyuan3D-2.1 shape model (BEST QUALITY for RTX 3090 Ti 24GB) ---
Write-Host ""
Write-Host "[Step 3] Downloading Hunyuan3D-2.1 shape model (full quality)..." -ForegroundColor Yellow
Write-Host "  Destination: $SHAPE_DIR" -ForegroundColor Gray
Write-Host "  Source: tencent/Hunyuan3D-2.1  (subfolder: hunyuan3d-dit-v2-1)" -ForegroundColor Gray
Write-Host "  Size: ~10-14GB | RTX 3090 Ti uses ~18-20GB VRAM during inference" -ForegroundColor Gray
Write-Host "  This is the BEST quality model for watertight 3D print meshes." -ForegroundColor Gray

New-Item -ItemType Directory -Force -Path $SHAPE_DIR | Out-Null

& $pythonExe -c @"
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='tencent/Hunyuan3D-2.1',
    allow_patterns=['hunyuan3d-dit-v2-1/**'],
    local_dir=r'$SHAPE_DIR',
    local_dir_use_symlinks=False,
)
print('Shape model 2.1 downloaded.')
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Shape model 2.1 ready: $SHAPE_DIR" -ForegroundColor Green
} else {
    Write-Host "[WARN] Download may have partially failed. Retrying with v2.0 fallback..." -ForegroundColor Yellow
    & $pythonExe -c @"
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='tencent/Hunyuan3D-2',
    allow_patterns=['hunyuan3d-dit-v2-0/**'],
    local_dir=r'$SHAPE_DIR',
    local_dir_use_symlinks=False,
)
print('Shape model 2.0 fallback downloaded.')
"@
}

# --- Step 4: Download Hunyuan3D-2.1 paint/texture model ---
Write-Host ""
Write-Host "[Step 4] Downloading Hunyuan3D-2.1 paint/texture model..." -ForegroundColor Yellow
Write-Host "  Destination: $PAINT_DIR" -ForegroundColor Gray
Write-Host "  Source: tencent/Hunyuan3D-2.1  (subfolder: hunyuan3d-paint-v2-1)" -ForegroundColor Gray
Write-Host "  Size: ~6-8GB | Adds texture/color to printed models." -ForegroundColor Gray
Write-Host "  Skip with Ctrl+C if you only need geometry for FDM printing." -ForegroundColor Gray

New-Item -ItemType Directory -Force -Path $PAINT_DIR | Out-Null

& $pythonExe -c @"
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='tencent/Hunyuan3D-2.1',
    allow_patterns=['hunyuan3d-paint-v2-1/**'],
    local_dir=r'$PAINT_DIR',
    local_dir_use_symlinks=False,
)
print('Paint model 2.1 downloaded.')
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Paint model 2.1 ready: $PAINT_DIR" -ForegroundColor Green
} else {
    Write-Host "[WARN] Paint model download may have partially failed — check $PAINT_DIR" -ForegroundColor Yellow
}

# --- Step 5: Verify ---
Write-Host ""
Write-Host "[Step 5] Verifying installation..." -ForegroundColor Yellow

& $pythonExe -c @"
import sys, os
sys.path.insert(0, r'c:\Users\Admin\Downloads\3d-printer-daveai')
from local_agent.comfyui_manager import find_comfyui, find_hunyuan3d_models
print('ComfyUI:', find_comfyui())
m = find_hunyuan3d_models()
print('Shape models:', m['shape_models'] or ['NOT FOUND'])
print('Paint models:', m['paint_models'] or ['NOT FOUND'])
"@

# --- Summary ---
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Bootstrap Complete" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Model layout:" -ForegroundColor White
Write-Host "  Shape (geometry):  $SHAPE_DIR\hunyuan3d-dit-v2-0\" -ForegroundColor Gray
Write-Host "  Paint (texture):   $PAINT_DIR\hunyuan3d-paint-v2-0\" -ForegroundColor Gray
Write-Host "  Custom node:       $HUNYUAN_NODE\  (kijai/ComfyUI-Hunyuan3DWrapper)" -ForegroundColor Gray
Write-Host ""
Write-Host "To start ComfyUI:" -ForegroundColor White
Write-Host "  cd G:\Github\ComfyUI" -ForegroundColor Gray
Write-Host "  python main.py --listen" -ForegroundColor Gray
Write-Host ""
Write-Host "Then run the gate check:" -ForegroundColor White
Write-Host "  cd C:\Users\Admin\Downloads\3d-printer-daveai" -ForegroundColor Gray
Write-Host "  python scripts\run_all_gates.py" -ForegroundColor Gray
Write-Host ""
