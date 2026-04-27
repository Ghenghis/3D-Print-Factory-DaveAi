#Requires -Version 5.1
<#
.SYNOPSIS
    Start the DaveAI local agentic runner from project root.
.DESCRIPTION
    Verifies Python, creates proof dirs, then launches the full gate runner.
    Optionally accepts printer IP overrides.
.PARAMETER IpOverrides
    Hashtable of printer IPs to override config defaults.
    Example: @{flsun_v400="192.168.1.50"; flsun_s1="192.168.1.55"}
#>
param(
    [hashtable]$IpOverrides = @{}
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  DaveAI 3D Print Factory — Agentic Runner" -ForegroundColor Cyan
Write-Host "  Branch: windsurf/final-e2e-truth-proof" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found. Install Python 3.10+." -ForegroundColor Red
    exit 1
}
Write-Host "Python: $(python --version)" -ForegroundColor Green

$Folders = @(
    "proof\windsurf", "proof\windsurf\baseline", "proof\windsurf\env",
    "proof\windsurf\comfyui", "proof\windsurf\moonraker", "proof\windsurf\blender",
    "proof\windsurf\router", "proof\windsurf\safety", "proof\windsurf\e2e",
    "proof\windsurf\memory", "proof\windsurf\reliability", "proof\windsurf\visual",
    "proof\windsurf\final", "proof\windsurf\local-agent", "proof\windsurf\hardware",
    "proof\blender", "proof\router", "proof\safety", "proof\moonraker", "proof\final",
    "output\blender", "output\comfyui", "input\stl"
)
foreach ($f in $Folders) {
    New-Item -ItemType Directory -Force -Path $f | Out-Null
}
Write-Host "Proof directories ready." -ForegroundColor Green

$ExtraArgs = @()
foreach ($key in $IpOverrides.Keys) {
    $ExtraArgs += "--ip-override", $key, $IpOverrides[$key]
    Write-Host "IP override: $key = $($IpOverrides[$key])" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Launching local agent..." -ForegroundColor Yellow
Write-Host ""

python -m local_agent.runner @ExtraArgs

$Exit = $LASTEXITCODE
Write-Host ""
if ($Exit -eq 0) {
    Write-Host "SUCCESS" -ForegroundColor Green
} else {
    Write-Host "Completed with exit $Exit — check verdict for blockers" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Results:" -ForegroundColor Cyan
Write-Host "  Verdict: proof\windsurf\final\WINDSURF_FINAL_VERDICT.md"
Write-Host "  Index:   proof\windsurf\final\proof-index.json"
Write-Host "  Log:     proof\windsurf\local-agent\local-agent-startup.log"
