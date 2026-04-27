"""
Verify ComfyUI is running and healthy. Writes proof artifact.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from local_agent.comfyui_manager import run_comfyui_phase
import json

result = run_comfyui_phase()
print(json.dumps(result, indent=2))
sys.exit(0 if result["gate"] == "PASS" else 1)
