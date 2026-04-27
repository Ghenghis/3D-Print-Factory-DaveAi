# WINDSURF CONTRACT — DaveAI 3D Print Factory Final Truth/Proof E2E Completion

**Contract version:** V1  
**Use case:** MaxHermes credits are out; Windsurf must finish the remaining local RTX 3090 Ti / LAN printer / ComfyUI / Moonraker truth-proof gates.  
**Project path:** `C:\Users\Admin\Downloads\3d-printer-daveai`  
**Final mission:** Production-candidate or production-ready only after real proof, never fake completion.

---

## 0. Paste this into Windsurf first

```text
You are now the local execution agent for DaveAI 3D Print Factory.

MaxHermes credits are out, so Windsurf must continue from the latest verified state. Do not restart the project. Do not redo completed work except to verify proof artifacts. Do not claim production-ready unless real proof exists.

The current honest MaxHermes verdict is:

DEV_COMPLETE_NOT_E2E_PROVEN

Known gate status:
- G5 Blender E2E: PASS, real Blender output verified
- G6 Fleet Router: PASS, 4 ACTIVE + 8 IDLE model works
- G8 Safety Gate: PASS, safety blocks print without confirmation
- G3 Moonraker: BLOCKED_HARDWARE because cloud sandbox could not reach LAN printers
- G4 ComfyUI: BLOCKED_SERVICE because cloud sandbox had no GPU / no local ComfyUI
- Full dry-run / controlled print: not production-proven yet

Your job is to complete all remaining gates locally on the user's Windows RTX 3090 Ti workstation, where LAN printers and GPU are available.

Do not ask the user to run commands. You run commands in Windsurf terminal. The user only provides:
- printer IPs if discovery fails
- API/model tokens if required
- permission to install dependencies
- printer power-state facts
- real controlled-print approval

Currently active/can-online printers:
1. FLSUN V400
2. FLSUN T1 #1
3. FLSUN T1 #2
4. FLSUN S1

The other 8 printers remain configured but IDLE_NOT_ONLINE:
- FLSUN QQ-S Pro
- FLSUN Super Racer
- Creality CR-10S
- Tronxy D01 Pro Enclosed
- Tronxy X5SA Pro
- Creality CR-6 Max
- Prusa MK3S
- Sovol SV-01

Do not remove any of the 12 printers from config.
Only route real dry-run jobs to ACTIVE_TESTABLE printers.
Do not fail production-candidate because idle printers are offline.
Dry-run must remain default.
No firmware flashing.
No printer.cfg overwrite without backup and confirmation.
No real print without explicit owner approval.
```

---

## 1. Current verified state to continue from

MaxHermes produced a V4 report showing:

```text
Verdict: DEV_COMPLETE_NOT_E2E_PROVEN

G5 Blender E2E: PASS
G6 Fleet Router: PASS
G8 Safety Gate: PASS
G3 Moonraker: BLOCKED_HARDWARE
G4 ComfyUI: BLOCKED_SERVICE
```

Expected changed files from MaxHermes:

```text
config/config.yaml
scripts/klipper/config.yaml
scripts/klipper/fleet_router.py
```

Expected proof files:

```text
proof/blender/blender-e2e-test.json
proof/router/router-validation.json
proof/safety/safety-gate-test.json
proof/moonraker/fleet-scan-4active.json
proof/final/V4_AGENTIC_VERDICT_REPORT.md
```

Windsurf must verify these files exist. If any are missing, rerun the local tests and regenerate proof.

---

## 2. Absolute truth/proof policy

A feature is not done because code exists. A feature is done only when this chain exists:

```text
code exists
+ command executed
+ test passed
+ real dependency used when required
+ proof artifact saved
+ failure mode tested
+ rollback/safety path exists
+ final verdict references the proof path
```

Do not write:

```text
production ready
fully complete
100% done
bug free
memory leak proof
all features working
```

unless every gate in this contract is proven.

Allowed verdicts:

```text
FAIL
DEV_COMPLETE_NOT_E2E_PROVEN
LOCAL_AGENT_READY
PRODUCTION_CANDIDATE_BLOCKED
PRODUCTION_CANDIDATE
PRODUCTION_READY
```

---

## 3. Safety rules

Permanent defaults:

```text
DRY_RUN_ONLY=true
ALLOW_REAL_PRINT=false
```

Real printing requires:

```text
owner explicit approval
selected printer
known G-code file
SHA256 hash logged
printer status healthy
Moonraker reachable
cancel/emergency stop path verified
proof file written before start
```

Never do these automatically:

```text
flash firmware
overwrite printer.cfg
change MCU config
start real print
publish repos publicly with secrets
commit tokens/secrets
```

If any code attempts these without approval, block it.

---

## 4. Branch and baseline

Windsurf must run this locally:

```powershell
cd C:\Users\Admin\Downloads\3d-printer-daveai
git status
git checkout -b windsurf/final-e2e-truth-proof
```

If branch exists:

```powershell
git checkout windsurf/final-e2e-truth-proof
```

Create proof folders:

```powershell
$folders = @(
  "proof\windsurf",
  "proof\windsurf\baseline",
  "proof\windsurf\env",
  "proof\windsurf\install",
  "proof\windsurf\comfyui",
  "proof\windsurf\moonraker",
  "proof\windsurf\blender",
  "proof\windsurf\router",
  "proof\windsurf\safety",
  "proof\windsurf\e2e",
  "proof\windsurf\memory",
  "proof\windsurf\visual",
  "proof\windsurf\final"
)
foreach ($f in $folders) { New-Item -ItemType Directory -Force -Path $f | Out-Null }
```

Record baseline:

```powershell
git status > proof\windsurf\baseline\git-status-before.txt
tree /F > proof\windsurf\baseline\file-tree-before.txt
python --version > proof\windsurf\env\python-version.txt
```

---

## 5. Phase order

Do not skip phases.

```text
Phase 0 — Verify MaxHermes proof
Phase 1 — Source-of-truth cleanup
Phase 2 — Local agentic runner / no manual commands
Phase 3 — ComfyUI + Hunyuan3D RTX 3090 Ti install/verify
Phase 4 — Moonraker active-printer LAN discovery
Phase 5 — Blender proof regression check
Phase 6 — Router/safety proof regression check
Phase 7 — Full dry-run E2E
Phase 8 — Memory/reliability/cleanup
Phase 9 — Optional GUI/visual E2E if UI exists
Phase 10 — Controlled print gate
Phase 11 — Final verdict and commit
```

---

## 6. Phase 0 — Verify MaxHermes proof

Run:

```powershell
cd C:\Users\Admin\Downloads\3d-printer-daveai

Get-ChildItem proof -Recurse | Out-File proof\windsurf\baseline\existing-proof-files.txt

Test-Path proof\blender\blender-e2e-test.json
Test-Path proof\router\router-validation.json
Test-Path proof\safety\safety-gate-test.json
Test-Path proof\moonraker\fleet-scan-4active.json
Test-Path proof\final\V4_AGENTIC_VERDICT_REPORT.md
```

Create:

```text
proof/windsurf/baseline/MAXHERMES_PROOF_VERIFICATION.md
```

It must state:

- proof files found
- proof files missing
- proof files regenerated by Windsurf

---

## 7. Phase 1 — Source-of-truth cleanup

Classify folders:

| Folder | Role |
|---|---|
| `Mini-Agent/mcp_servers/` | likely current MCP source |
| `scripts/blender/` | Blender processing scripts |
| `scripts/klipper/` | Moonraker/Klipper helpers |
| `config/` | 12-printer fleet source |
| `setup/` | bootstrap/proof runner |
| `proof/` | proof artifacts |
| `skills/` | skill docs or executable skill wrappers |

Create:

```text
docs/SOURCE_OF_TRUTH_MAP.md
proof/windsurf/baseline/source-of-truth-map.md
```

Run a stub scan:

```powershell
Select-String -Path .\**\*.py,.\**\*.md,.\**\*.yaml,.\**\*.json -Pattern "TODO|FIXME|placeholder|stub|NotImplemented|mock|fake|production ready" -CaseSensitive:$false |
  Out-File proof\windsurf\baseline\stub-placeholder-scan.txt
```

Classify findings as:

```text
production blocker
documentation note
historical note
test fixture
safe ignore
```

---

## 8. Phase 2 — Local agentic runner

The user does not want manual command chains. Windsurf must create or finish a local runner:

```text
local_agent/
├─ runner.py
├─ command_executor.py
├─ task_queue.py
├─ proof_collector.py
├─ printer_discovery.py
├─ comfyui_manager.py
├─ model_manager.py
├─ blender_manager.py
├─ e2e_runner.py
├─ verdict_engine.py
├─ safety_policy.py
└─ local_agent_config.yaml
```

Windows launchers:

```text
local_agent/windows/DaveAI-Local-Agent-Launcher.bat
local_agent/windows/DaveAI-Local-Agent-Launcher.ps1
setup/start-local-agentic-runner.ps1
```

Required local runner tasks:

```text
ENV_CHECK
INSTALL_DEPS
DETECT_BLENDER
RUN_BLENDER_E2E
DETECT_COMFYUI
INSTALL_COMFYUI
START_COMFYUI
INSTALL_HUNYUAN3D
RUN_COMFYUI_HEALTH
RUN_HUNYUAN3D_SHAPE_TEST
SCAN_PRINTERS
TEST_ACTIVE_MOONRAKER
VALIDATE_ROUTER
VALIDATE_SAFETY_GATE
RUN_FULL_DRYRUN
RUN_MEMORY_RELIABILITY
GENERATE_FINAL_VERDICT
```

Optional local API, bound only to localhost:

```text
http://127.0.0.1:8799
```

Endpoints:

```text
GET  /health
GET  /capabilities
POST /tasks/run
GET  /tasks/{id}
GET  /proof/index
POST /owner/fact
POST /owner/approve-controlled-print
POST /shutdown
```

Proof:

```text
proof/windsurf/local-agent/local-agent-startup.log
proof/windsurf/local-agent/local-agent-capabilities.json
proof/windsurf/local-agent/task-history.jsonl
```

---

## 9. Phase 3 — ComfyUI + Hunyuan3D setup on RTX 3090 Ti

Windsurf runs install/check itself.

Check these ComfyUI locations:

```text
C:\Users\Admin\Downloads\ComfyUI
C:\Users\Admin\ComfyUI
G:\ComfyUI
G:\Github\ComfyUI
```

If missing, install to:

```text
C:\Users\Admin\Downloads\ComfyUI
```

Target model stack:

```text
Primary: Hunyuan3D 2.1
Shape: Hunyuan3D-Shape-v2-1
Paint: Hunyuan3D-Paint-v2-1
GPU: RTX 3090 Ti 24GB
VRAM mode: sequential
```

Sequential VRAM policy:

```text
1. run shape generation
2. save mesh
3. clear model/cache/GPU memory
4. run texture/paint only if selected
5. clear memory again
6. send geometry to Blender repair
```

Create/update:

```text
setup/comfyui-bootstrap.ps1
setup/hunyuan3d-3090ti-bootstrap.ps1
setup/verify-comfyui.py
setup/verify-hunyuan3d.py
```

Proof:

```text
proof/windsurf/comfyui/comfyui-location.txt
proof/windsurf/comfyui/comfyui-health.json
proof/windsurf/comfyui/hunyuan3d-model-files.txt
proof/windsurf/comfyui/hunyuan3d-model-hashes.txt
proof/windsurf/comfyui/hunyuan3d-shape-test.json
proof/windsurf/comfyui/vram-policy.md
```

If token is needed, ask for token or permission to use the existing local token file. Do not ask the user to run login commands.

---

## 10. Phase 4 — Moonraker active-printer discovery

Active/can-online:

```text
FLSUN V400
FLSUN T1 #1
FLSUN T1 #2
FLSUN S1
```

The other 8 are `IDLE_NOT_ONLINE`.

Create configs:

```text
config/active-printers.yaml
config/idle-printers.yaml
config/printer-ip-overrides.yaml
```

Allowed statuses:

```text
ACTIVE_TESTABLE
ONLINE_NO_MOONRAKER
POWERED_OFF
IDLE_NOT_ONLINE
UNCONFIGURED
BLOCKED
```

Windsurf must scan:

```text
current gateway subnet
192.168.0.0/24
192.168.1.0/24
10.0.0.0/24
user-provided IPs/subnet
```

Ports:

```text
7125
80
443
8080
```

Moonraker endpoints:

```text
/server/info
/printer/info
/printer/objects/query?webhooks
```

If discovery fails, ask for facts:

```text
Please provide any known IPs:
FLSUN V400 =
FLSUN T1 #1 =
FLSUN T1 #2 =
FLSUN S1 =
```

Proof:

```text
proof/windsurf/moonraker/printer-scan-results.json
proof/windsurf/moonraker/active-printer-status.json
proof/windsurf/moonraker/idle-printer-status.json
proof/windsurf/moonraker/moonraker-api-proof.json
```

---

## 11. Phase 5 — Blender regression proof

MaxHermes passed Blender E2E, but Windsurf must rerun locally.

Required proof:

```text
exact Blender version
commands run
input mesh paths
output STL/3MF paths
output file sizes
SHA256 hashes
repair/export logs
process cleanup result
memory notes
```

Run one of:

```powershell
python e2e_final_test.py
python local_agent\runner.py --task RUN_BLENDER_E2E
```

Proof:

```text
proof/windsurf/blender/blender-version.txt
proof/windsurf/blender/blender-e2e-output.txt
proof/windsurf/blender/output-files.txt
proof/windsurf/blender/output-sha256.txt
proof/windsurf/blender/process-cleanup.txt
```

---

## 12. Phase 6 — Router and safety proof

Router must preserve:

```text
4 ACTIVE_TESTABLE
8 IDLE_NOT_ONLINE
12 total fleet
```

Required router tests:

```text
small PLA routes to active printer
large impossible 450mm+ rejected
ABS/ASA prefers enclosed printer when online, or marks unavailable if idle
inactive/idle printers are not used for real dry-run
offline printer is skipped
```

Because the Tronxy D01 Pro Enclosed is currently idle, ABS/ASA real routing should either:

```text
BLOCKED_NO_ACTIVE_ENCLOSED_PRINTER
```

or route only as a future recommendation, not as active real job.

Safety tests:

```text
can_start_print() false before approval
confirm_print() required
emergency stop path exists
dry-run default true
real print flag false
```

Proof:

```text
proof/windsurf/router/router-validation.json
proof/windsurf/safety/safety-gate-test.json
```

---

## 13. Phase 7 — Full dry-run E2E

Goal:

```text
input prompt or image
→ ComfyUI/Hunyuan3D shape output
→ Blender repair/export
→ route to active printer subset
→ Moonraker dry-run upload or upload simulation if user denies printer upload
→ proof report
```

Do not start print.

Required output:

```text
proof/windsurf/e2e/full-dryrun-report.md
proof/windsurf/e2e/artifact-chain.json
proof/windsurf/e2e/generated-model-hash.txt
proof/windsurf/e2e/repaired-model-hash.txt
proof/windsurf/e2e/router-decision.json
proof/windsurf/e2e/moonraker-dryrun-result.json
proof/windsurf/e2e/no-print-started.txt
```

If ComfyUI is blocked, create:

```text
proof/windsurf/e2e/COMFYUI_BLOCKER.md
```

If Moonraker is blocked, create:

```text
proof/windsurf/e2e/MOONRAKER_BLOCKER.md
```

---

## 14. Phase 8 — Memory, cleanup, reliability

Minimum:

```text
Blender loop x10
Moonraker status loop x25 if printers reachable
ComfyUI health loop x10 if reachable
full dry-run loop x3 if all services available
```

Proof:

```text
proof/windsurf/memory/memory-loop.csv
proof/windsurf/memory/process-cleanup.txt
proof/windsurf/reliability/failure-injection-report.md
```

Failure cases:

```text
ComfyUI stopped
printer offline
invalid mesh
impossible build volume
network timeout
bad IP
cancel dry-run
```

---

## 15. Phase 9 — GUI / visual E2E if UI exists

If there is a dashboard, local agent UI, or web panel:

```powershell
npx playwright install chromium
npx playwright test tests\visual --reporter=list
```

If Playwright is not set up, create minimal tests:

```text
dashboard loads
12 printers listed
4 active + 8 idle displayed
ComfyUI status shown
Blender status shown
Moonraker status shown
proof report link works
no dead buttons
no blank panels
no console errors
```

Proof:

```text
proof/windsurf/visual/playwright-output.txt
proof/windsurf/visual/screenshots/
proof/windsurf/visual/console-errors.txt
```

---

## 16. Phase 10 — Controlled print gate

Only after `PRODUCTION_CANDIDATE`.

Required prompt:

```text
Production-candidate gates passed. To move to PRODUCTION_READY, approve one controlled small test print.

Please confirm:
1. Which printer?
2. Confirm printer is physically safe and watched.
3. Confirm selected G-code hash.
4. Type: APPROVE CONTROLLED PRINT
```

If not approved:

```text
PRODUCTION_CANDIDATE_BLOCKED_BY_OWNER_PRINT_APPROVAL
```

Proof if approved:

```text
proof/windsurf/hardware/controlled-print-approval.txt
proof/windsurf/hardware/controlled-print-gcode-hash.txt
proof/windsurf/hardware/controlled-print-moonraker-log.json
proof/windsurf/hardware/controlled-print-result.md
```

---

## 17. Phase 11 — Final verdict

Create:

```text
proof/windsurf/final/WINDSURF_FINAL_VERDICT.md
```

Template:

```markdown
# Windsurf Final Verdict — DaveAI 3D Print Factory

## Verdict

FAIL / DEV_COMPLETE_NOT_E2E_PROVEN / PRODUCTION_CANDIDATE_BLOCKED / PRODUCTION_CANDIDATE / PRODUCTION_READY

## Gate table

| Gate | Status | Proof |
|---|---|---|
| G0 source truth | | |
| G1 stubs removed | | |
| G2 12-printer config | | |
| G3 active Moonraker subset | | |
| G4 ComfyUI/Hunyuan3D | | |
| G5 Blender E2E | | |
| G6 router | | |
| G7 safety | | |
| G8 full dry-run | | |
| G9 memory/reliability | | |
| G10 visual/UI if applicable | | |
| G11 controlled print | | |
| G12 proof archive | | |

## Files changed

## Commands run by Windsurf

## Proof artifacts

## Bugs found and fixed

## Remaining blockers

## Owner facts requested

## Final release judge statement
```

---

## 18. Git commit requirements

Do not commit secrets.

Before commit:

```powershell
git status
git diff --stat
Select-String -Path .\**\* -Pattern "sk-|ghp_|hf_|password|PRIVATE KEY|AZURE|MINIMAX" -CaseSensitive:$false
```

If secrets are found in repo-tracked files, stop and move them to `.env.example` or private local config.

Commit in logical chunks:

```text
commit 1: proof baseline and source truth
commit 2: local agentic runner / setup improvements
commit 3: ComfyUI/Hunyuan3D bootstrap
commit 4: Moonraker printer discovery
commit 5: E2E proof runner
commit 6: docs/final verdict
```

---

## 19. Windsurf completion standard

The final answer must be one of:

```text
PRODUCTION_CANDIDATE — with proof
PRODUCTION_READY — with controlled print proof
PRODUCTION_CANDIDATE_BLOCKED — exact missing IP/token/service/approval listed
DEV_COMPLETE_NOT_E2E_PROVEN — if real services remain unavailable
FAIL — if implementation broke
```

Anything else is incomplete.

---

## 20. Short command for Windsurf

```text
Continue DaveAI 3D Print Factory from MaxHermes V4/V5 state. Verify existing proof, preserve 12-printer config with 4 active and 8 idle, run all remaining local RTX 3090 Ti / LAN printer / ComfyUI / Hunyuan3D / Moonraker / dry-run / memory / visual proof gates. Do not ask the user to run commands. Ask only for IPs, tokens, power-state facts, or controlled-print approval. Do not claim production-ready until real proof exists.
```
