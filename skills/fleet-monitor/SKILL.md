---
name: fleet-monitor
description: Monitor the status of all printers in the fleet, track print progress, and alert on errors. Use this skill when checking fleet status or monitoring active prints.
---

# Fleet Monitor Skill

Real-time monitoring of all 11 printers in the fleet.

## When to Use

- User asks "what's the fleet status?"
- After starting a print, track progress
- Periodic health check
- Alert user on errors or completion

## Fleet Overview

### Delta Printers (5)

| Printer | Host | Status Endpoint |
|---------|------|-----------------|
| FLSUN V400 | 192.168.1.101 | mainsail-v400.local |
| FLSUN T1 #1 | 192.168.1.102 | mainsail-t1-1.local |
| FLSUN T1 #2 | 192.168.1.103 | mainsail-t1-2.local |
| FLSUN S1 | 192.168.1.104 | mainsail-s1.local |
| FLSUN Super Racer | 192.168.1.105 | mainsail-super.local |

### Cartesian Printers (6)

| Printer | Host | Status Endpoint |
|---------|------|-----------------|
| Creality CR-10S | 192.168.1.107 | mainsail-cr10s.local |
| Creality CR-6 Max | 192.168.1.108 | mainsail-cr6.local |
| Tronxy D01 Pro | 192.168.1.109 | mainsail-d01.local |
| Tronxy X5SA Pro | 192.168.1.110 | mainsail-x5sa.local |
| Prusa MK3S | 192.168.1.111 | mainsail-mk3s.local |
| Sovol SV-01 | 192.168.1.112 | mainsail-sv01.local |

## Status Types

| Status | Meaning | Action |
|--------|---------|--------|
| `idle` | Ready for print | None needed |
| `printing` | Active print job | Monitor progress |
| `paused` | Print paused | Offer resume |
| `error` | Problem detected | Investigate |
| `offline` | Cannot connect | Check connection |
| `heating` | Warming up bed/nozzle | Normal |
| `homing` | Homing axes | Normal |

## Query Commands

### Get Fleet Status
```
moonraker_get_fleet_status()
→ Returns status of all printers
```

### Get Single Printer
```
moonraker_get_printer_status(printer="flsun_v400")
→ Returns detailed printer state
```

### Get Print Progress
```
moonraker_get_print_stats(printer="flsun_v400")
→ Returns: job name, progress %, elapsed time, ETA
```

### Get Temperatures
```
moonraker_get_temps(printer="flsun_v400")
→ Returns: bed temp, nozzle temp, target temps
```

## Output Format

### Fleet Overview
```
🖨️ FLEET STATUS - 11 Printers

🟢 IDLE (7)
  • FLSUN V400
  • FLSUN T1 #1
  • FLSUN S1
  • CR-10S
  • Tronxy D01 Pro
  • Prusa MK3S
  • Sovol SV-01

🔵 PRINTING (4)
  • FLSUN T1 #2: Dragon figurine - 67% - ETA 1h 23m
  • FLSUN Super Racer: Prototype v2 - 23% - ETA 2h 45m
  • CR-6 Max: Phone case - 89% - ETA 12m
  • X5SA Pro: Large base - 8% - ETA 8h 15m

⚠️ ERROR (0)
  None

🔴 OFFLINE (0)
  None
```

### Single Printer Detail
```
🖨️ FLSUN T1 #2

Status: 🔵 PRINTING
Job: Dragon figurine_v3.stl
Progress: 67%
Layer: 156 / 234
Elapsed: 1h 12m
ETA: 1h 23m

Temperatures:
  Bed: 60°C / 60°C ✓
  Nozzle: 210°C / 210°C ✓

Position: X:145 Y:120 Z:45
```

## Alert Conditions

Monitor for these conditions and alert user:

| Condition | Severity | Action |
|-----------|----------|--------|
| Temp deviation > 5°C | Warning | Log, continue |
| Print 100% complete | Info | Notify user |
| Print paused | Warning | Ask user to resume |
| Print failed | Error | Route to backup |
| Printer offline | Error | Alert user |
| Power loss | Critical | Emergency stop |

## Progress Tracking

### Update Intervals
- Active print: Every 5 minutes
- Heating: Every 30 seconds
- Idle: On request only

### ETA Calculation
```
remaining_time = (elapsed_time / progress) - elapsed_time
```

### Layer Tracking
```
current_layer = total_layers * (progress / 100)
```

## Print Job Events

### Event Types
1. **Started** - "Print started on [printer]"
2. **Progress** - "[progress]% complete - ETA [time]"
3. **Paused** - "Print paused on [printer]"
4. **Resumed** - "Print resumed on [printer]"
5. **Completed** - "Print COMPLETE: [filename]"
6. **Failed** - "Print FAILED on [printer]: [reason]"
7. **Cancelled** - "Print cancelled on [printer]"

## Batch Monitoring

When multiple prints active:

```
📊 ACTIVE PRINTS: 4

1. 🔵 FLSUN T1 #2
   Dragon figurine - 67% [████████████░░░░] 1h 23m
   Temp: Bed 60°C ✓ Nozzle 210°C ✓

2. 🔵 FLSUN Super Racer  
   Prototype v2 - 23% [████░░░░░░░░░░░░░] 2h 45m
   Temp: Bed 60°C ✓ Nozzle 205°C ✓

3. 🟡 CR-6 Max
   Phone case - 89% [█████████████████░] 12m
   Temp: Bed 65°C ✓ Nozzle 220°C ✓

4. 🔵 X5SA Pro
   Large base - 8% [██░░░░░░░░░░░░░░░░] 8h 15m
   Temp: Bed 100°C ✓ Nozzle 250°C ✓

⏰ Next completion: CR-6 Max in ~12 minutes
```

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| Thermal runaway | Temp sensor issue | Check wiring |
| Filament runout | Out of filament | Reload filament |
| Bed adhesion fail | First layer issue | Cancel, relevel |
| Motor stall | Physical obstruction | Clear, restart |
| Communication error | Network issue | Reconnect |

### Alert Template
```
⚠️ ALERT: [Printer Name]

Issue: [Error type]
Details: [Error message from Moonraker]
Time: [Timestamp]

Action: [Recommended next step]
```

## Examples

### Quick Status Check
```
User: fleet status

→ Query all printers
→ Display summary
→ Highlight any issues
```

### Monitor Active Print
```
User: check on my dragon print

→ Get progress from FLSUN T1 #2
→ Display current status
→ Report ETA
```

### Error Alert
```
Printer: CR-6 Max reports "Thermal Runaway"
→ Alert user immediately
→ Suggest checking thermistor
→ Offer to cancel and retry
```

## Notes

- Cache fleet status for 30 seconds to avoid flooding Moonraker
- Always verify printer is actually printing before reporting progress
- For very long prints (>4 hours), offer to notify on completion
- Log all events for troubleshooting
