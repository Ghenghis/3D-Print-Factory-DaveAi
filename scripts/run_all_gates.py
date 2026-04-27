"""Run all local_agent proof gates and print a summary table."""
import sys
sys.path.insert(0, ".")

results = []

def gate(name, fn):
    try:
        r = fn()
        g = r.get("gate", "UNKNOWN")
        detail = r.get("blocker") or r.get("block_reason") or ""
        results.append((name, g, detail))
        print(f"[{g:6}] {name}  {detail}")
        return r
    except Exception as e:
        results.append((name, "ERROR", str(e)))
        print(f"[ERROR ] {name}  {e}")
        return {}


print("=" * 60)
print("DaveAI Local Agent — Full Gate Suite")
print("=" * 60)

from local_agent.safety_policy import SafetyPolicy
gate("Safety Policy", lambda: SafetyPolicy().run_gate_test())

from local_agent.fleet_router import run_router_tests
gate("Fleet Router", run_router_tests)

from local_agent.blender_manager import run_blender_e2e
gate("Blender E2E", run_blender_e2e)

from local_agent.comfyui_manager import run_comfyui_phase
gate("ComfyUI / Hunyuan3D", run_comfyui_phase)

from local_agent.maintenance_manager import get_all
maint = get_all()
maint_on = [v["name"] for v in maint.values() if v["maintenance"]]
results.append(("Maintenance Toggles", "INFO", f"{len(maint_on)} in maintenance: {maint_on}"))
print(f"[INFO  ] Maintenance Toggles  {len(maint_on)} in maintenance: {maint_on}")

from local_agent.proof_collector import build_proof_index
idx = build_proof_index()
missing = idx.get("missing_required", [])
g = "PASS" if not missing else "WARN"
results.append(("Proof Index", g, f"{idx['total_proof_files']} files, {len(missing)} required missing"))
print(f"[{g:6}] Proof Index  {idx['total_proof_files']} files, {len(missing)} required missing")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
passed = sum(1 for _, g, _ in results if g == "PASS")
failed = sum(1 for _, g, _ in results if g in ("FAIL", "ERROR"))
blocked = sum(1 for _, g, _ in results if g == "BLOCKED")
print(f"PASS: {passed}  BLOCKED: {blocked}  FAIL/ERROR: {failed}  TOTAL: {len(results)}")
for name, g, detail in results:
    marker = "OK" if g == "PASS" else ("!!" if g in ("FAIL","ERROR") else "--")
    print(f"  [{marker}] {name:25} {g:8} {detail[:60]}")
print()
