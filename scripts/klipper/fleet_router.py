"""
DaveAI Fleet Router — Klipper/Moonraker integration helper.
Thin wrapper around local_agent.fleet_router for script-level use.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from local_agent.fleet_router import route_job, run_router_tests

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", default="PLA")
    parser.add_argument("--size-x", type=float, default=50)
    parser.add_argument("--size-y", type=float, default=50)
    parser.add_argument("--size-z", type=float, default=50)
    parser.add_argument("--test", action="store_true", help="Run all router tests")
    args = parser.parse_args()

    if args.test:
        result = run_router_tests()
    else:
        result = route_job(
            material=args.material,
            size_mm={"x": args.size_x, "y": args.size_y, "z": args.size_z},
        )

    print(json.dumps(result, indent=2))
