---
name: printer-router
description: Select the optimal 3D printer from the fleet based on model dimensions, material requirements, and availability. Use this skill when routing a print job to a printer.
---

# Printer Router Skill

Intelligently select the best printer for a given print job.

## When to Use

- After mesh is processed and ready for printing
- Need to decide which printer to use
- Multiple printers available, need to choose best
- Printer becomes unavailable mid-job

## Input Parameters

| Parameter | Source | Description |
|-----------|--------|-------------|
| dimensions | Mesh analysis | W x H x D in mm |
| material | User request | PLA, PETG, ABS, TPU |
| priority | User request | speed, quality, balanced |
| complexity | AI analysis | simple, medium, complex |

## Fleet Reference

### Delta Printers (FLSUN) - Speed Optimized

| Printer | Build Volume | Max Speed | Best For |
|---------|-------------|-----------|----------|
| FLSUN V400 | 300x300mm | 300mm/s | Miniatures, prototypes |
| FLSUN T1 x2 | 300x400mm | 250mm/s | Balanced prints |
| FLSUN S1 | 300x400mm | 250mm/s | General purpose |
| FLSUN Super Racer | 300x400mm | 300mm/s | Speed priority |
| FLSUN QQ-S Pro | 255x300mm | 250mm/s | Compact prints |

### Cartesian Printers - Precision & Size

| Printer | Build Volume | Features | Best For |
|---------|-------------|----------|----------|
| Creality CR-10S | 300x300x400mm | Open | Large format |
| Creality CR-6 Max | 300x300x400mm | Open, Stable | Large, detailed |
| Tronxy D01 Pro | 220x220x250mm | **Enclosed**, Heated | ABS, ASA, Engineering |
| Tronxy X5SA Pro | 330x330x400mm | Open | XL prints |
| Prusa MK3S | 250x210x210mm | High precision | Precision, Quality |
| Sovol SV-01 | 280x280x320mm | Open | Testing, General |

## Decision Matrix

### By Size

| Model Size | Delta/FLSUN | Cartesian | Special |
|------------|-------------|----------|---------|
| Miniature (<50mm) | V400, T1 | - | Turbo mode |
| Small (50-100mm) | T1, S1 | MK3S | Standard |
| Medium (100-200mm) | S1, Super Racer | CR-6 Max | Standard |
| Large (200-300mm) | - | CR-10S, X5SA | Large mode |
| XL (>300mm) | - | X5SA Pro | XL mode |

### By Material

| Material | Required Printer | Reason |
|----------|-----------------|--------|
| PLA | Any | Standard settings |
| PETG | Any | Slight higher temps |
| ABS | Tronxy D01 (enclosed) | Needs heated chamber |
| ASA | Tronxy D01 (enclosed) | UV resistant, needs enclosure |
| TPU | FLSUN V400, T1 | Flexible, needs slow print |

### By Priority

| Priority | Best Printer | Alternative |
|----------|-------------|-------------|
| Speed | FLSUN V400 | Super Racer, T1 |
| Quality | Prusa MK3S | CR-6 Max |
| Balanced | FLSUN T1, S1 | CR-6 Max |
| Size | X5SA Pro, CR-10S | CR-6 Max |

## Routing Algorithm

```
1. FILTER by build volume
   - Exclude printers where model doesn't fit

2. FILTER by material
   - ABS/ASA requires Tronxy D01 (enclosed)

3. FILTER by availability
   - Exclude printers with active prints

4. SCORE remaining printers
   - Size match: +40 points
   - Priority match: +30 points
   - Material compatibility: +20 points
   - Recent use (rotation): +10 points

5. SELECT highest score
   - If tie, prefer printer with fewer jobs today
```

## Size Check Formula

```
Fits in printer if:
  width <= printer.max_width
  depth <= printer.max_depth
  height <= printer.max_height

For deltas (circular bed):
  effective_width = min(width, depth)
  effective_depth = min(width, depth)
  must fit within radius = min(max_width, max_depth) / 2
```

## Output Format

```
🗺️ Printer Selection

Model: 85 x 120 x 60mm
Priority: Balanced
Material: PLA

Filtered Options:
  ✓ FLSUN T1 #1 - Score: 85
  ✓ FLSUN T1 #2 - Score: 85
  ✓ FLSUN S1 - Score: 80
  ✗ FLSUN V400 - Too small (300mm < 120mm height)
  ✗ CR-10S - Lower quality score

Selected: FLSUN T1 #1
Reason: Best balance of size fit and speed priority
```

## Availability Check

Query Moonraker for printer status:

```python
get_printer_status(printer)
# Returns: idle, printing, error, unavailable

get_print_stats(printer)
# Returns: current job, progress %, estimated time
```

## Fallback Routing

If primary printer fails:

1. Same category printer
2. Next best scored printer
3. Any available printer (relax constraints)

## Examples

### Miniature Speed Print
```
Input:
  dimensions: 40 x 40 x 40mm
  priority: speed
  material: PLA

Output:
  Selected: FLSUN V400
  Reason: Small size fits V400, ultra-fast speed
```

### Large ABS Engineering Part
```
Input:
  dimensions: 150 x 80 x 200mm
  priority: quality
  material: ABS

Output:
  Selected: Tronxy D01 Pro
  Reason: ABS requires enclosed printer, quality priority
```

### XL Print
```
Input:
  dimensions: 280 x 280 x 350mm
  priority: balanced
  material: PETG

Output:
  Selected: Tronxy X5SA Pro
  Reason: Only printer with height > 350mm
```

## Notes

- Always verify build volume before selecting
- For delta printers, circular build area limits rectangular prints
- Tronxy D01 is the ONLY option for ABS/ASA (enclosed)
- FLSUN V400 is fastest but smallest delta
- Prusa MK3S has best quality but smallest build volume
