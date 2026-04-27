#Requires -Version 5.1
<#
.SYNOPSIS
    Bootstrap ComfyUI for DaveAI on Windows RTX 3090 Ti
.DESCRIPTION
    Checks for existing ComfyUI install, clones if missing, verifies Python env.
    Does NOT start ComfyUI automatically — use verify-comfyui.py to check.
#>

$InstallPath = "C:\Users\Admin\Downloads\ComfyUI"
$SearchPaths = @(
    "C:\Users\Admin\Downloads\ComfyUI",
    "C:\Users\Admin\ComfyUI",
    "G:\ComfyUI",
    "G:\Github\ComfyUI"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ComfyUI Bootstrap — DaveAI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$Found = $null
foreach ($path in $SearchPaths) {
    if (Test-Path "$path\main.py") {
        $Found = $path
        break
    }
}

if ($Found) {
    Write-Host "ComfyUI found at: $Found" -ForegroundColor Green
    "FOUND: $Found" | Out-File -Encoding utf8 "proof\windsurf\comfyui\comfyui-location.txt"
} else {
    Write-Host "ComfyUI not found. Installing to: $InstallPath" -ForegroundColor Yellow

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: git not found. Install git first." -ForegroundColor Red
        exit 1
    }

    git clone https://github.com/comfyanonymous/ComfyUI.git $InstallPath

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Clone failed." -ForegroundColor Red
        exit 1
    }

    $Found = $InstallPath
    Write-Host "ComfyUI installed at: $Found" -ForegroundColor Green
    "INSTALLED: $Found" | Out-File -Encoding utf8 "proof\windsurf\comfyui\comfyui-location.txt"
}

Write-Host ""
Write-Host "Installing ComfyUI requirements..." -ForegroundColor Yellow

if (Test-Path "$Found\requirements.txt") {
    pip install -r "$Found\requirements.txt" --quiet
    Write-Host "Requirements installed." -ForegroundColor Green
} else {
    Write-Host "WARNING: requirements.txt not found in $Found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "ComfyUI bootstrap complete." -ForegroundColor Green
Write-Host "Start ComfyUI manually: python $Found\main.py --listen 127.0.0.1"
Write-Host "Then run: python setup\verify-comfyui.py"
