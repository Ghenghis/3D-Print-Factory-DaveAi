"""
DaveAI Blender Manager — finds Blender, runs repair/export, writes proof.
"""

import json
import os
import hashlib
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


BLENDER_SEARCH_PATHS = [
    r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender\blender.exe",
    "blender",
]

BLENDER_REPAIR_SCRIPT = '''
import bpy
import sys
import json
import os

args = sys.argv[sys.argv.index("--") + 1:]
input_path = args[0]
output_path = args[1]
proof_path = args[2]

result = {
    "input": input_path,
    "output": output_path,
    "success": False,
    "error": None,
    "vertex_count": 0,
    "face_count": 0,
    "output_size_bytes": 0,
}

try:
    bpy.ops.wm.read_factory_settings(use_empty=True)

    ext = os.path.splitext(input_path)[1].lower()
    if ext in [".stl", ".STL"]:
        bpy.ops.import_mesh.stl(filepath=input_path)
    elif ext in [".obj"]:
        bpy.ops.import_scene.obj(filepath=input_path)
    elif ext in [".glb", ".gltf"]:
        bpy.ops.import_scene.gltf(filepath=input_path)
    else:
        bpy.ops.import_mesh.stl(filepath=input_path)

    obj = None
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            obj = o
            break

    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")

        mesh = obj.data
        result["vertex_count"] = len(mesh.vertices)
        result["face_count"] = len(mesh.polygons)

    out_ext = os.path.splitext(output_path)[1].lower()
    if out_ext == ".stl":
        bpy.ops.export_mesh.stl(filepath=output_path)
    elif out_ext in [".glb", ".gltf"]:
        bpy.ops.export_scene.gltf(filepath=output_path, export_format="GLB")
    else:
        bpy.ops.export_mesh.stl(filepath=output_path)

    if os.path.exists(output_path):
        result["success"] = True
        result["output_size_bytes"] = os.path.getsize(output_path)

except Exception as e:
    result["error"] = str(e)

with open(proof_path, "w") as f:
    json.dump(result, f, indent=2)

sys.exit(0 if result["success"] else 1)
'''


def find_blender() -> str:
    """Return path to Blender executable or raise."""
    for path in BLENDER_SEARCH_PATHS:
        if path == "blender":
            try:
                r = subprocess.run(
                    ["blender", "--version"], capture_output=True, timeout=10
                )
                if r.returncode == 0:
                    return "blender"
            except Exception:
                continue
        elif os.path.exists(path):
            return path
    raise FileNotFoundError("Blender not found in any expected location.")


def get_blender_version(blender_exe: str) -> str:
    try:
        r = subprocess.run(
            [blender_exe, "--version"], capture_output=True, text=True, timeout=15
        )
        return r.stdout.split("\n")[0].strip()
    except Exception as e:
        return f"ERROR: {e}"


def hash_file(path: str) -> str:
    if not os.path.exists(path):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def run_blender_repair(
    input_path: str,
    output_path: str,
    blender_exe: str = None,
    timeout: int = 120,
) -> dict:
    """Run Blender headless repair on a mesh file."""
    if blender_exe is None:
        blender_exe = find_blender()

    proof_dir = Path("proof/windsurf/blender")
    proof_dir.mkdir(parents=True, exist_ok=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as tf:
        tf.write(BLENDER_REPAIR_SCRIPT)
        script_path = tf.name

    repair_proof_path = str(proof_dir / "blender-repair-result.json")

    cmd = [
        blender_exe,
        "--background",
        "--python", script_path,
        "--",
        input_path,
        output_path,
        repair_proof_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Blender timeout", "returncode": -1}
    finally:
        try:
            os.unlink(script_path)
        except Exception:
            pass

    with open(proof_dir / "blender-e2e-output.txt", "w") as f:
        f.write(f"CMD: {' '.join(cmd)}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}\n")

    repair_result = {}
    if os.path.exists(repair_proof_path):
        with open(repair_proof_path) as f:
            repair_result = json.load(f)

    output_sha256 = hash_file(output_path)

    full_result = {
        "blender_exe": blender_exe,
        "returncode": returncode,
        "input": input_path,
        "output": output_path,
        "output_sha256": output_sha256,
        "output_size_bytes": repair_result.get("output_size_bytes", 0),
        "vertex_count": repair_result.get("vertex_count", 0),
        "face_count": repair_result.get("face_count", 0),
        "success": repair_result.get("success", False),
        "error": repair_result.get("error"),
    }

    with open(proof_dir / "output-sha256.txt", "w") as f:
        f.write(f"{output_sha256}  {output_path}\n")

    return full_result


def run_blender_e2e(loop_count: int = 1) -> dict:
    """Full Blender E2E test — creates synthetic mesh, repairs, exports, verifies."""
    proof_dir = Path("proof/windsurf/blender")
    proof_dir.mkdir(parents=True, exist_ok=True)
    top_proof = Path("proof/blender")
    top_proof.mkdir(parents=True, exist_ok=True)
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)

    blender_exe = find_blender()
    version = get_blender_version(blender_exe)

    (proof_dir / "blender-version.txt").write_text(version, encoding="utf-8")
    print(f"[Blender] Found: {blender_exe} — {version}")

    SYNTHETIC_STL = (
        b"solid test_cube\n"
        b"  facet normal 0 0 -1\n"
        b"    outer loop\n"
        b"      vertex 0 0 0\n"
        b"      vertex 1 0 0\n"
        b"      vertex 1 1 0\n"
        b"    endloop\n"
        b"  endfacet\n"
        b"  facet normal 0 0 -1\n"
        b"    outer loop\n"
        b"      vertex 0 0 0\n"
        b"      vertex 1 1 0\n"
        b"      vertex 0 1 0\n"
        b"    endloop\n"
        b"  endfacet\n"
        b"  facet normal 0 0 1\n"
        b"    outer loop\n"
        b"      vertex 0 0 1\n"
        b"      vertex 1 1 1\n"
        b"      vertex 1 0 1\n"
        b"    endloop\n"
        b"  endfacet\n"
        b"  facet normal 0 0 1\n"
        b"    outer loop\n"
        b"      vertex 0 0 1\n"
        b"      vertex 0 1 1\n"
        b"      vertex 1 1 1\n"
        b"    endloop\n"
        b"  endfacet\n"
        b"endsolid test_cube\n"
    )

    input_path = str(output_dir / "test_input.stl")
    Path(input_path).write_bytes(SYNTHETIC_STL)

    results = []
    for i in range(loop_count):
        output_path = str(output_dir / f"test_repaired_{i}.stl")
        r = run_blender_repair(input_path, output_path, blender_exe)
        r["loop_index"] = i
        results.append(r)
        status = "PASS" if r["success"] else "FAIL"
        print(f"  Loop {i+1}/{loop_count}: {status}")

    files_info = []
    for p in output_dir.glob("*.stl"):
        files_info.append({"file": str(p), "size_bytes": p.stat().st_size})

    (proof_dir / "output-files.txt").write_text(
        "\n".join(f"{f['file']} ({f['size_bytes']} bytes)" for f in files_info),
        encoding="utf-8"
    )

    overall = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "blender_exe": blender_exe,
        "blender_version": version,
        "loop_count": loop_count,
        "results": results,
        "all_passed": all(r["success"] for r in results),
        "output_files": files_info,
        "gate": "PASS" if all(r["success"] for r in results) else "FAIL",
    }

    (proof_dir / "blender-e2e-output.json").write_text(json.dumps(overall, indent=2), encoding="utf-8")
    (top_proof / "blender-e2e-test.json").write_text(json.dumps(overall, indent=2), encoding="utf-8")

    print(f"[Blender E2E] Gate: {overall['gate']}")
    return overall


if __name__ == "__main__":
    result = run_blender_e2e(loop_count=1)
    print(json.dumps(result, indent=2))
