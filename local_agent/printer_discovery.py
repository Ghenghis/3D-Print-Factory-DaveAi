"""
DaveAI Auto Network Scanner for 3D Printers
============================================
Discovers 3D printers on all local network interfaces automatically.

Strategy (fastest to slowest):
  1. Detect all local interface subnets via ipconfig
  2. ARP/ping sweep to find live hosts (pre-filter — skips dead IPs fast)
  3. Parallel TCP probe on all 3D printer ports
  4. HTTP fingerprint to identify printer API type:
       - Moonraker  (Klipper)   → port 7125  /server/info
       - OctoPrint              → port 5000  /api/version
       - Duet RRF               → port 80    /rr_status
       - Bambu Lab              → port 2222  (MQTT-based, detected by TCP)
       - Generic HTTP webcam    → port 8080
  5. Auto-match discovered IPs to fleet config by printer model/name
  6. Persist confirmed IPs to config/printer-ip-overrides.yaml
  7. Write full proof artifacts to proof/windsurf/moonraker/

Respects maintenance toggles — maintenance printers are connection-tested only.
"""

import json
import socket
import ipaddress
import subprocess
import platform
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

try:
    from local_agent.maintenance_manager import is_in_maintenance
except ImportError:
    def is_in_maintenance(key): return False


# ---------------------------------------------------------------------------
# Ports to probe on each candidate host
# ---------------------------------------------------------------------------
PRINTER_PORTS = {
    7125: "moonraker",
    5000: "octoprint",
    80:   "http_generic",
    443:  "https_generic",
    8080: "http_alt",
    8888: "http_alt2",
    2222: "bambu_mqtt",
    4751: "duet3",
}

MOONRAKER_PORTS  = [7125]
OCTOPRINT_PORTS  = [5000, 80]
DUET_PORTS       = [80, 443]
BAMBU_PORTS      = [2222]

PROBE_TIMEOUT    = 2        # seconds per TCP connect
HTTP_TIMEOUT     = 4        # seconds per HTTP GET
PING_TIMEOUT_MS  = 300      # ms per ping
MAX_SCAN_WORKERS = 128      # parallel TCP workers during subnet sweep
MAX_PING_WORKERS = 200      # parallel ping workers

SUBNETS_FALLBACK = [
    "192.168.1.0/24",
    "192.168.0.0/24",
    "10.0.0.0/24",
    "172.16.0.0/24",
]

# ---------------------------------------------------------------------------
# Fleet registry
# ---------------------------------------------------------------------------
ACTIVE_PRINTERS = [
    {"name": "FLSUN V400",  "key": "flsun_v400",  "status": "ACTIVE_TESTABLE",   "routing_allowed": True},
    {"name": "FLSUN T1 #1", "key": "flsun_t1_1",  "status": "ACTIVE_TESTABLE",   "routing_allowed": True},
    {"name": "FLSUN T1 #2", "key": "flsun_t1_2",  "status": "ACTIVE_TESTABLE",   "routing_allowed": True},
    {
        "name": "FLSUN S1",
        "key":  "flsun_s1",
        "status": "ONLINE_MAINTENANCE",
        "routing_allowed": False,
        "maintenance_note": "Hotend disassembled — connection test only. Do NOT send jobs, heat, or move commands.",
    },
]

IDLE_PRINTERS = [
    {"name": "FLSUN QQ-S Pro",         "key": "flsun_qq_pro",    "status": "IDLE_NOT_ONLINE"},
    {"name": "FLSUN Super Racer",       "key": "flsun_super_racer","status": "IDLE_NOT_ONLINE"},
    {"name": "Creality CR-10S",         "key": "cr10s",           "status": "IDLE_NOT_ONLINE"},
    {"name": "Tronxy D01 Pro Enclosed", "key": "tronxy_d01",      "status": "IDLE_NOT_ONLINE", "enclosure": True},
    {"name": "Tronxy X5SA Pro",         "key": "tronxy_x5sa",     "status": "IDLE_NOT_ONLINE"},
    {"name": "Creality CR-6 Max",       "key": "cr6_max",         "status": "IDLE_NOT_ONLINE"},
    {"name": "Prusa MK3S",              "key": "prusa_mk3s",      "status": "IDLE_NOT_ONLINE"},
    {"name": "Sovol SV-01",             "key": "sovol_sv01",      "status": "IDLE_NOT_ONLINE"},
]

ALL_PRINTERS = ACTIVE_PRINTERS + IDLE_PRINTERS

CONFIG_IPS = {
    # Real IPs verified by auto-scan on 192.168.0.0/24
    "flsun_v400":        "192.168.0.34",   # speeder-pad, Moonraker v0.10.0
    "flsun_t1_1":        "192.168.0.10",   # FLSunT1, Moonraker 1.0.9.8
    "flsun_t1_2":        "192.168.0.11",   # FLSunT1 (second unit), Moonraker 1.0.9.8
    "flsun_s1":          "192.168.0.12",   # FLSunS1, Moonraker 1.0.8.9 — MAINTENANCE
    "flsun_super_racer": "",
    "flsun_qq_pro":      "",
    "cr10s":             "",
    "cr6_max":           "",
    "tronxy_d01":        "",
    "tronxy_x5sa":       "",
    "prusa_mk3s":        "",
    "sovol_sv01":        "",
}

# Keywords used to auto-match a discovered printer to a fleet key.
# Checked against Moonraker hostname, model_name, printer/info fields.
# More specific entries listed first to avoid false matches.
PRINTER_FINGERPRINTS = {
    "flsun_v400":        ["speeder-pad", "speederpad", "v400", "flsun v400"],
    "flsun_t1_1":        ["flsunt1", "flsun t1"],   # matched first free T1 slot
    "flsun_t1_2":        ["flsunt1", "flsun t1"],   # second T1 if t1_1 already matched
    "flsun_s1":          ["fls uns1", "flsuns1", "flsun s1", "s1"],
    "flsun_super_racer": ["super racer", "superracer", "superracer2.0"],
    "flsun_qq_pro":      ["qq-s pro", "qqspro", "qq pro", "flsun qq"],
    "cr10s":             ["cr-10s", "cr10s", "cr-10", "cr10"],
    "cr6_max":           ["cr-6 max", "cr6max", "cr-6", "cr6"],
    "tronxy_d01":        ["d01 pro", "tronxy d01", "d01"],
    "tronxy_x5sa":       ["x5sa pro", "tronxy x5sa", "x5sa"],
    "prusa_mk3s":        ["mk3s", "prusaMK3", "prusa mk3", "mk3"],
    "sovol_sv01":        ["sv01", "sovol sv", "sovol"],
}


# ---------------------------------------------------------------------------
# Step 1 — Interface / subnet detection
# ---------------------------------------------------------------------------

def get_local_interfaces() -> list:
    """
    Returns list of local subnets detected from all active interfaces.
    Windows: parses ipconfig. Falls back to hardcoded list.
    """
    subnets = []
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["ipconfig"], capture_output=True, text=True, timeout=10
            )
            ip = None
            mask = None
            for line in result.stdout.splitlines():
                line = line.strip()
                # IPv4 address
                m = re.search(r"IPv4 Address.*?:\s*([\d.]+)", line)
                if m:
                    ip = m.group(1)
                # Subnet mask
                m = re.search(r"Subnet Mask.*?:\s*([\d.]+)", line)
                if m:
                    mask = m.group(1)
                if ip and mask:
                    try:
                        net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
                        subnet = str(net)
                        if subnet not in subnets and not net.is_loopback:
                            subnets.append(subnet)
                    except Exception:
                        pass
                    ip = None
                    mask = None
        else:
            result = subprocess.run(
                ["ip", "addr"], capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                m = re.search(r"inet ([\d.]+/\d+)", line)
                if m:
                    try:
                        net = ipaddress.IPv4Network(m.group(1), strict=False)
                        if not net.is_loopback:
                            subnets.append(str(net))
                    except Exception:
                        pass
    except Exception:
        pass

    # Always include fallbacks if not already present
    for fb in SUBNETS_FALLBACK:
        if fb not in subnets:
            subnets.append(fb)

    return subnets


# ---------------------------------------------------------------------------
# Step 2 — Ping sweep (fast host pre-filter)
# ---------------------------------------------------------------------------

def ping_host(ip: str) -> bool:
    """Returns True if host responds to ping."""
    try:
        if platform.system() == "Windows":
            cmd = ["ping", "-n", "1", "-w", str(PING_TIMEOUT_MS), ip]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", ip]
        r = subprocess.run(cmd, capture_output=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False


def ping_sweep(subnet: str) -> list:
    """Ping all hosts in subnet, return list of live IPs."""
    try:
        net = ipaddress.ip_network(subnet, strict=False)
        hosts = [str(h) for h in net.hosts()]
    except ValueError:
        return []

    live = []
    with ThreadPoolExecutor(max_workers=MAX_PING_WORKERS) as ex:
        futures = {ex.submit(ping_host, ip): ip for ip in hosts}
        for future in as_completed(futures):
            ip = futures[future]
            if future.result():
                live.append(ip)
    return live


# ---------------------------------------------------------------------------
# Step 3 — TCP port probe
# ---------------------------------------------------------------------------

def tcp_probe(host: str, port: int) -> bool:
    """Returns True if TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=PROBE_TIMEOUT):
            return True
    except Exception:
        return False


def probe_all_ports(host: str) -> dict:
    """Check all printer ports on a host, return open ports dict."""
    open_ports = {}
    with ThreadPoolExecutor(max_workers=len(PRINTER_PORTS)) as ex:
        futures = {ex.submit(tcp_probe, host, port): (port, label)
                   for port, label in PRINTER_PORTS.items()}
        for future in as_completed(futures):
            port, label = futures[future]
            if future.result():
                open_ports[port] = label
    return open_ports


# ---------------------------------------------------------------------------
# Step 4 — HTTP fingerprinting
# ---------------------------------------------------------------------------

def http_get(url: str) -> Optional[dict]:
    """GET JSON from URL, return parsed dict or None."""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "DaveAI-Scanner/1.0"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read().decode(errors="replace")
            try:
                return json.loads(raw)
            except Exception:
                return {"_raw": raw[:200]}
    except Exception:
        return None


def fingerprint_printer(host: str, open_ports: dict) -> dict:
    """
    Try each known printer API to identify type and model.
    Returns fingerprint dict with api_type, model_name, firmware_version, raw_info.
    """
    fp = {
        "api_type": "UNKNOWN",
        "model_name": None,
        "firmware_version": None,
        "hostname": None,
        "raw_info": None,
        "confidence": "low",
    }

    # --- Moonraker (Klipper) ---
    if 7125 in open_ports:
        data = http_get(f"http://{host}:7125/server/info")
        if data and "klippy_state" in str(data):
            fp["api_type"] = "moonraker"
            fp["confidence"] = "high"
            fp["raw_info"] = data
            # Try printer info for model
            pinfo = http_get(f"http://{host}:7125/printer/info")
            if pinfo:
                result = pinfo.get("result", pinfo)
                fp["model_name"] = result.get("machine_name") or result.get("hostname")
                fp["firmware_version"] = result.get("software_version")
                fp["hostname"] = result.get("hostname")
            return fp
        elif data:
            fp["api_type"] = "moonraker_likely"
            fp["confidence"] = "medium"
            fp["raw_info"] = data

    # --- OctoPrint ---
    for port in OCTOPRINT_PORTS:
        if port in open_ports:
            data = http_get(f"http://{host}:{port}/api/version")
            if data and "server" in data:
                fp["api_type"] = "octoprint"
                fp["confidence"] = "high"
                fp["firmware_version"] = data.get("server")
                fp["raw_info"] = data
                pdata = http_get(f"http://{host}:{port}/api/printer")
                if pdata:
                    fp["model_name"] = pdata.get("state", {}).get("text")
                return fp

    # --- Duet RRF ---
    if 80 in open_ports:
        data = http_get(f"http://{host}/rr_status?type=1")
        if data and "coords" in str(data):
            fp["api_type"] = "duet_rrf"
            fp["confidence"] = "high"
            fp["raw_info"] = data
            return fp
        # Duet v3 SBC
        data = http_get(f"http://{host}/machine/status")
        if data and "boards" in str(data):
            fp["api_type"] = "duet3_sbc"
            fp["confidence"] = "high"
            fp["raw_info"] = data
            return fp

    # --- Bambu Lab (MQTT on 2222 — only TCP detectable) ---
    if 2222 in open_ports:
        fp["api_type"] = "bambu_mqtt"
        fp["confidence"] = "medium"
        fp["model_name"] = "Bambu Lab printer (MQTT)"
        return fp

    # --- Generic HTTP fallback ---
    for port in [80, 8080, 8888]:
        if port in open_ports:
            data = http_get(f"http://{host}:{port}/")
            if data:
                fp["api_type"] = "http_unknown"
                fp["raw_info"] = data
                fp["confidence"] = "low"
                break

    return fp


# ---------------------------------------------------------------------------
# Step 5 — Auto-match discovered printer to fleet config
# ---------------------------------------------------------------------------

def match_to_fleet(fp: dict, ip: str, already_matched: set) -> Optional[str]:
    """
    Try to match a discovered printer fingerprint to a fleet printer key.
    Returns matched key or None.
    Priority: exact IP match → name keyword match.
    """
    # Exact IP match against config
    for key, config_ip in CONFIG_IPS.items():
        if config_ip == ip and key not in already_matched:
            return key

    # Keyword match against model_name or hostname
    search_text = " ".join(filter(None, [
        str(fp.get("model_name") or ""),
        str(fp.get("hostname") or ""),
    ])).lower()

    if search_text.strip():
        for key, keywords in PRINTER_FINGERPRINTS.items():
            if key in already_matched:
                continue
            for kw in keywords:
                if kw in search_text:
                    return key

    return None


# ---------------------------------------------------------------------------
# Step 6 — Persist discovered IPs
# ---------------------------------------------------------------------------

def save_ip_overrides(discovered: dict) -> None:
    """
    Write confirmed IPs to config/printer-ip-overrides.yaml.
    Only writes keys where a match was found.
    """
    override_file = Path("config/printer-ip-overrides.yaml")
    header = (
        "# DaveAI Printer IP Overrides\n"
        "# Auto-updated by network scanner.\n"
        "# These override the defaults in active-printers.yaml / idle-printers.yaml.\n\n"
        "ip_overrides:\n"
    )
    body = ""
    for key, ip in sorted(discovered.items()):
        body += f"  {key}: \"{ip}\"\n"
    if not body:
        body = "  # No printers auto-discovered yet\n"
    override_file.write_text(header + body, encoding="utf-8")


# ---------------------------------------------------------------------------
# Step 7 — Main scan entry points
# ---------------------------------------------------------------------------

def probe_moonraker(host: str, port: int = 7125) -> dict:
    """Backward-compatible single-host probe (used by e2e_runner)."""
    result = {"host": host, "port": port, "reachable": False, "moonraker": False, "info": None}
    if not tcp_probe(host, port):
        return result
    result["reachable"] = True
    data = http_get(f"http://{host}:{port}/server/info")
    if data and "klippy_state" in str(data):
        result["moonraker"] = True
        result["info"] = data
    elif data:
        result["moonraker"] = True  # responsive = moonraker
        result["info"] = data
    return result


def scan_subnet(subnet: str, max_workers: int = MAX_SCAN_WORKERS) -> list:
    """Scan subnet for any 3D printer. Returns list of found printer dicts."""
    print(f"  [Scan] {subnet} — ping sweep...")
    live_hosts = ping_sweep(subnet)
    print(f"  [Scan] {subnet} — {len(live_hosts)} live hosts, probing ports...")

    found = []

    def full_probe(ip):
        open_ports = probe_all_ports(ip)
        if not open_ports:
            return None
        # Only fingerprint if printer-likely ports are open
        printer_port_hit = any(
            p in open_ports for p in [7125, 5000, 2222, 4751]
        ) or (80 in open_ports or 8080 in open_ports)
        if not printer_port_hit:
            return None
        fp = fingerprint_printer(ip, open_ports)
        if fp["api_type"] == "UNKNOWN":
            return None
        return {
            "ip": ip,
            "open_ports": open_ports,
            "fingerprint": fp,
        }

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(full_probe, ip): ip for ip in live_hosts}
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)

    return found


def get_local_gateway() -> Optional[str]:
    """Return primary gateway subnet string."""
    subnets = get_local_interfaces()
    return subnets[0] if subnets else None


def auto_scan_network(extra_subnets: list = None) -> dict:
    """
    Full automatic network scan.
    Detects all interfaces, sweeps subnets, fingerprints printers,
    auto-matches to fleet, persists IPs.
    Returns complete scan report.
    """
    t_start = time.time()
    print("\n[AutoScan] Detecting local network interfaces...")
    subnets = get_local_interfaces()
    if extra_subnets:
        for s in extra_subnets:
            if s not in subnets:
                subnets.append(s)
    print(f"[AutoScan] Subnets to scan: {subnets}")

    all_discovered = []
    for subnet in subnets:
        found = scan_subnet(subnet)
        all_discovered.extend(found)
        print(f"  [AutoScan] {subnet}: {len(found)} printer(s) found")

    # De-duplicate by IP
    seen_ips = set()
    unique = []
    for d in all_discovered:
        if d["ip"] not in seen_ips:
            seen_ips.add(d["ip"])
            unique.append(d)

    print(f"\n[AutoScan] Total unique printers found: {len(unique)}")

    # Auto-match to fleet
    matched = {}
    unmatched = []
    already_matched = set()
    for d in unique:
        key = match_to_fleet(d["fingerprint"], d["ip"], already_matched)
        if key:
            already_matched.add(key)
            matched[key] = {
                "ip": d["ip"],
                "fleet_key": key,
                "fleet_name": next((p["name"] for p in ALL_PRINTERS if p["key"] == key), key),
                "api_type": d["fingerprint"]["api_type"],
                "model_name": d["fingerprint"]["model_name"],
                "firmware_version": d["fingerprint"]["firmware_version"],
                "open_ports": list(d["open_ports"].keys()),
                "confidence": d["fingerprint"]["confidence"],
            }
            print(f"  MATCHED: {d['ip']} -> {key} ({d['fingerprint']['api_type']})")
        else:
            unmatched.append({
                "ip": d["ip"],
                "api_type": d["fingerprint"]["api_type"],
                "model_name": d["fingerprint"]["model_name"],
                "open_ports": list(d["open_ports"].keys()),
                "note": "Unknown printer - not in fleet config",
            })
            print(f"  UNMATCHED: {d['ip']} ({d['fingerprint']['api_type']})")

    # Persist discovered IPs
    discovered_ips = {k: v["ip"] for k, v in matched.items()}
    save_ip_overrides(discovered_ips)

    elapsed = round(time.time() - t_start, 1)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "subnets_scanned": subnets,
        "live_hosts_found": len(seen_ips),
        "printers_found": len(unique),
        "matched_to_fleet": matched,
        "unmatched_printers": unmatched,
        "ip_overrides_saved": discovered_ips,
    }
    return report


def discover_printers(ip_overrides: dict = None) -> dict:
    """
    Main discovery function called by runner/e2e_runner.
    1. Probes fleet config IPs directly
    2. Runs full auto network scan
    3. Applies any manual IP overrides
    4. Writes all proof artifacts
    """
    proof_dir = Path("proof/windsurf/moonraker")
    proof_dir.mkdir(parents=True, exist_ok=True)
    top_proof = Path("proof/moonraker")
    top_proof.mkdir(parents=True, exist_ok=True)

    # Load any previously auto-discovered IPs from override file
    override_file = Path("config/printer-ip-overrides.yaml")
    auto_ips = {}
    if override_file.exists():
        raw = override_file.read_text(encoding="utf-8")
        for line in raw.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and ":" in line and "ip_overrides" not in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    k = parts[0].strip()
                    v = parts[1].strip().strip('"').strip("'")
                    if k and v:
                        auto_ips[k] = v

    effective_ips = dict(CONFIG_IPS)
    effective_ips.update(auto_ips)
    if ip_overrides:
        effective_ips.update(ip_overrides)

    # --- Phase A: Direct config IP probe ---
    active_results = []
    print("\n[PrinterDiscovery] Phase A: Probing fleet by configured IPs...")
    for printer in ACTIVE_PRINTERS:
        key = printer["key"]
        ip = effective_ips.get(key, "")
        probe = {
            "printer": printer["name"],
            "key": key,
            "configured_ip": ip,
            "source": "config",
        }
        if ip:
            r = probe_moonraker(ip)
            probe.update(r)
            live_maintenance = is_in_maintenance(key)
            static_maintenance = printer.get("status") == "ONLINE_MAINTENANCE"
            if live_maintenance or static_maintenance:
                probe["moonraker_status"] = "ONLINE_MAINTENANCE_CONNECTION_TEST"
                probe["routing_allowed"] = False
                probe["maintenance_note"] = printer.get(
                    "maintenance_note", "see config/printer-maintenance.yaml"
                )
                probe["live_maintenance_toggle"] = live_maintenance
            else:
                probe["moonraker_status"] = (
                    "ONLINE_MOONRAKER" if r.get("moonraker")
                    else ("ONLINE_NO_MOONRAKER" if r.get("reachable") else "OFFLINE")
                )
                probe["routing_allowed"] = r.get("moonraker", False)
        else:
            probe["moonraker_status"] = "NO_IP_CONFIGURED"
            probe["routing_allowed"] = False
        active_results.append(probe)
        print(f"  {printer['name']:25} @ {ip or 'NO_IP':15} → {probe['moonraker_status']}")

    idle_results = []
    for printer in IDLE_PRINTERS:
        key = printer["key"]
        ip = effective_ips.get(key, "")
        idle_results.append({
            "printer": printer["name"],
            "key": key,
            "configured_ip": ip,
            "status": "IDLE_NOT_ONLINE",
            "note": "Not probed — idle fleet member",
        })

    # --- Phase B: Full auto network scan ---
    print("\n[PrinterDiscovery] Phase B: Auto network scan...")
    scan_report = auto_scan_network()
    (proof_dir / "auto-scan-report.json").write_text(json.dumps(scan_report, indent=2), encoding="utf-8")

    # Apply any newly discovered IPs to active results (update source)
    for key, match in scan_report["matched_to_fleet"].items():
        for ar in active_results:
            if ar["key"] == key and ar.get("moonraker_status") in ("OFFLINE", "NO_IP_CONFIGURED"):
                ar["discovered_ip"] = match["ip"]
                ar["discovery_source"] = "auto_scan"
                ar["api_type"] = match["api_type"]
                # Re-probe with discovered IP
                r2 = probe_moonraker(match["ip"])
                ar["moonraker_status"] = (
                    "ONLINE_MOONRAKER" if r2.get("moonraker")
                    else ("ONLINE_NO_MOONRAKER" if r2.get("reachable") else "OFFLINE_AFTER_SCAN")
                )
                ar["routing_allowed"] = r2.get("moonraker", False)
            print(f"  [AutoScan resolved] {ar['printer']} -> {match['ip']} ({ar['moonraker_status']})")

    # --- Proof artifacts ---
    fleet_scan = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_fleet": 12,
        "active_count": len(ACTIVE_PRINTERS),
        "idle_count": len(IDLE_PRINTERS),
        "active_printers": active_results,
        "idle_printers": idle_results,
        "auto_scan": scan_report,
        "subnets_scanned": scan_report["subnets_scanned"],
        "ip_overrides_applied": list(ip_overrides.keys()) if ip_overrides else [],
        "auto_discovered_ips": scan_report["ip_overrides_saved"],
        "unmatched_devices": scan_report["unmatched_printers"],
    }

    (proof_dir / "printer-scan-results.json").write_text(json.dumps(fleet_scan, indent=2), encoding="utf-8")
    (proof_dir / "active-printer-status.json").write_text(json.dumps(active_results, indent=2), encoding="utf-8")
    (proof_dir / "idle-printer-status.json").write_text(json.dumps(idle_results, indent=2), encoding="utf-8")
    (proof_dir / "moonraker-api-proof.json").write_text(
        json.dumps([p for p in active_results if p.get("moonraker_status", "") == "ONLINE_MOONRAKER"], indent=2)
    )
    (top_proof / "fleet-scan-4active.json").write_text(json.dumps(fleet_scan, indent=2), encoding="utf-8")

    online = [p for p in active_results if p.get("moonraker_status") == "ONLINE_MOONRAKER"]
    maintenance = [p for p in active_results if "MAINTENANCE" in p.get("moonraker_status", "")]
    print(f"\n[PrinterDiscovery] Done — {len(online)} ONLINE_MOONRAKER | "
          f"{len(maintenance)} MAINTENANCE | "
          f"{scan_report['printers_found']} total discovered on LAN")
    print(f"[PrinterDiscovery] Proof written to {proof_dir}/")
    return fleet_scan


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="DaveAI Auto Network Scanner")
    parser.add_argument("--scan-only", action="store_true",
                        help="Run auto-scan only, no fleet probe")
    parser.add_argument("--subnet", action="append", metavar="CIDR",
                        help="Extra subnet to scan (repeatable)")
    parser.add_argument("--no-ping", action="store_true",
                        help="Skip ping pre-filter (slower but catches firewalled hosts)")
    args = parser.parse_args()

    if args.scan_only:
        report = auto_scan_network(extra_subnets=args.subnet)
        print(json.dumps(report, indent=2, default=str))
    else:
        result = discover_printers()
        online_active = [
            p for p in result["active_printers"]
            if p.get("moonraker_status") == "ONLINE_MOONRAKER"
        ]
        maintenance_active = [
            p for p in result["active_printers"]
            if "MAINTENANCE" in p.get("moonraker_status", "")
        ]
        print(f"\n=== Fleet Summary ===")
        print(f"Online (Moonraker):  {len(online_active)}")
        print(f"Maintenance mode:    {len(maintenance_active)}")
        print(f"Idle (not online):   {len(IDLE_PRINTERS)}")
        print(f"Total fleet:         12")
        print(f"\nAuto-discovered IPs saved to: config/printer-ip-overrides.yaml")
