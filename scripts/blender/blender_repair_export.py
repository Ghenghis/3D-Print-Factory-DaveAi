"""
DaveAI Blender Repair/Export Script
Run via local_agent.blender_manager or directly:
  blender --background --python scripts/blender/blender_repair_export.py -- input.stl output.stl proof.json
"""
import bpy
import sys
import json
import os

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) < 3:
    print("Usage: blender --background --python blender_repair_export.py -- INPUT OUTPUT PROOF_JSON")
    sys.exit(1)

input_path, output_path, proof_path = args[0], args[1], args[2]

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
    if ext in [".stl"]:
        bpy.ops.import_mesh.stl(filepath=input_path)
    elif ext in [".obj"]:
        bpy.ops.import_scene.obj(filepath=input_path)
    elif ext in [".glb", ".gltf"]:
        bpy.ops.import_scene.gltf(filepath=input_path)
    else:
        bpy.ops.import_mesh.stl(filepath=input_path)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode="OBJECT")
            result["vertex_count"] = len(obj.data.vertices)
            result["face_count"] = len(obj.data.polygons)
            break

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
