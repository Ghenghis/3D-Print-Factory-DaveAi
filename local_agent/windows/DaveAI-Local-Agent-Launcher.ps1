#Requires -Version 5.1
<#
.SYNOPSIS
    DaveAI 3D Print Factory — Local Agent Launcher
.DESCRIPTION
    Launches the full local agent runner. Runs all E2E proof gates automatically.
    Optional: supply printer IP overrides if discovery fails.
.PARAMETER IpOverrides
    Hashtable of printer key to IP. Example: @{flsun_v400="192.168.1.50"}
.PARAMETER ApiMode
    Start HTTP API on 127.0.0.1:8799 alongside the gate runner
.PARAMETER Task
    Run a single task instead of all gates
#>
param(
    [hashtable]$IpOverrides = @{},
    [switch]$ApiMode,
    [string]$Task = ""
)

$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  DaveAI 3D Print Factory — Local Agent" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $Root" -ForegroundColor Gray
Write-Host "Branch:  windsurf/final-e2e-truth-proof" -ForegroundColor Gray
Write-Host ""

$Args = @()
if ($Task) {
    $Args += "--task", $Task
}
if ($ApiMode) {
    $Args += "--api"
}
foreach ($key in $IpOverrides.Keys) {
    $Args += "--ip-override", $key, $IpOverrides[$key]
}

Write-Host "Running: python -m local_agent.runner $Args" -ForegroundColor Yellow
Write-Host ""

python -m local_agent.runner @Args
$Exit = $LASTEXITCODE

Write-Host ""
if ($Exit -eq 0) {
    Write-Host "Agent finished successfully." -ForegroundColor Green
} else {
    Write-Host "Agent exited with code $Exit" -ForegroundColor Red
}

Write-Host ""
Write-Host "Final verdict: proof\windsurf\final\WINDSURF_FINAL_VERDICT.md" -ForegroundColor Cyan
Write-Host "Proof index:   proof\windsurf\final\proof-index.json" -ForegroundColor Cyan
