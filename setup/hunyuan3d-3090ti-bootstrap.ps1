#Requires -Version 5.1
<#
.SYNOPSIS
    Install Hunyuan3D 2.1 models for RTX 3090 Ti (24GB VRAM)
.DESCRIPTION
    Downloads shape and paint models using huggingface-cli.
    Requires HuggingFace token if models are gated.
    Applies sequential VRAM policy (shape → save → clear → paint).
.PARAMETER HfToken
    HuggingFace token (optional if models are public)
#>
param(
    [string]$HfToken = ""
)

$ModelId  = "tencent/Hunyuan3D-2"
# Store models inside ComfyUI so the custom node finds them directly
$ModelDir = "G:\Github\ComfyUI\models\hunyuan3d"
$CacheDir = "$env:USERPROFILE\.cache\huggingface\hub"   # fallback only

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Hunyuan3D 2.1 Bootstrap — RTX 3090 Ti" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VRAM mode: sequential (shape only, then clear, then paint)" -ForegroundColor Yellow
Write-Host "GPU target: RTX 3090 Ti 24GB" -ForegroundColor Yellow
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found." -ForegroundColor Red
    exit 1
}

pip install huggingface-hub --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Could not install huggingface-hub" -ForegroundColor Red
    exit 1
}

if ($HfToken) {
    huggingface-cli login --token $HfToken
}

New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null

Write-Host "Downloading Hunyuan3D-2 shape model -> $ModelDir\shape" -ForegroundColor Yellow
huggingface-cli download tencent/Hunyuan3D-2 `
    --include "hunyuan3d-dit-v2-0/**" "hunyuan3d-dit-v2-0-turbo/**" `
    --local-dir "$ModelDir\shape"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Shape model download failed. May need HF token or manual download." -ForegroundColor Yellow
}

Write-Host "Downloading Hunyuan3D-2 paint model -> $ModelDir\paint" -ForegroundColor Yellow
huggingface-cli download tencent/Hunyuan3D-2 `
    --include "hunyuan3d-paint-v2-0/**" `
    --local-dir "$ModelDir\paint"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Paint model download failed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking downloaded files..." -ForegroundColor Yellow
if (Test-Path $ModelDir) {
    $Files = Get-ChildItem -Recurse $ModelDir | Where-Object { -not $_.PSIsContainer }
    $Files | ForEach-Object { Write-Host "  $($_.FullName) ($([math]::Round($_.Length/1MB,1)) MB)" }
    New-Item -ItemType Directory -Force -Path "proof\windsurf\comfyui" | Out-Null
    $Files.FullName | Out-File -Encoding utf8 "proof\windsurf\comfyui\hunyuan3d-model-files.txt"
    Write-Host "Model files saved to proof." -ForegroundColor Green
} else {
    Write-Host "Model directory not found at $ModelDir" -ForegroundColor Red
    "NOT_FOUND: $ModelDir" | Out-File -Encoding utf8 "proof\windsurf\comfyui\hunyuan3d-model-files.txt"
}

Write-Host ""
Write-Host "Bootstrap complete." -ForegroundColor Green
Write-Host "Run verify-hunyuan3d.py to confirm model loading."
