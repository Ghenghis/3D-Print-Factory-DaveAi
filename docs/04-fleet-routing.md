# 04 - Fleet Routing

## Intelligent Printer Selection System

```mermaid
flowchart TB
    subgraph Input["📥 ROUTING DECISION INPUT"]
        STL["📄 STL File"]
        Req["📋 Requirements<br/>Size, Material, Quality"]
    end

    subgraph Evaluation["⚖️ EVALUATION ENGINE"]
        
        subgraph Checks["🔍 PRE-FLIGHT CHECKS"]
            Size["📐 Size Check"]
            Material["🧪 Material Check"]
            Status["🔋 Printer Status"]
        end

        subgraph Scoring["🏆 SCORING MATRIX"]
            Speed["⚡ Speed Score"]
            Quality["✨ Quality Score"]
            Capacity["📊 Capacity Score"]
            Material["🔬 Material Score"]
        end

        subgraph Selection["🎯 FINAL SELECTION"]
            Rank["📊 Rank Printers"]
            Assign["✅ Assign Printer"]
        end
    end

    subgraph Output["📤 OUTPUT"]
        Selected["🖨️ Selected Printer"]
        Config["⚙️ Print Config"]
    end

    Input --> Evaluation
    Checks --> Scoring
    Scoring --> Selection
    Selection --> Output
```

---

## Decision Flowchart

```mermaid
flowchart TD
    START([📦 New Print Job]) --> SIZE{📐 Model Size?}
    
    SIZE -->|Mini <50mm| MINI
    SIZE -->|Small 50-100mm| SMALL
    SIZE -->|Medium 100-200mm| MEDIUM
    SIZE -->|Large 200-300mm| LARGE
    SIZE -->|XL >300mm| XL
    
    MINI --> SPEED_PRIORITY{⚡ Speed?}
    SPEED_PRIORITY -->|Yes| MINI_SPEED["FLSUN V400 ⭐⭐⭐⭐⭐<br/>or Super Racer ⭐⭐⭐⭐"]
    SPEED_PRIORITY -->|No| MINI_QUALITY["FLSUN T1 ⭐⭐⭐⭐<br/>or S1 ⭐⭐⭐⭐"]
    
    SMALL --> QUALITY_PRIORITY{✨ Quality?}
    QUALITY_PRIORITY -->|Yes| SMALL_HIGH["Prusa MK3S ⭐⭐⭐⭐⭐<br/>Best Detail"]
    QUALITY_PRIORITY -->|No| SMALL_FAST["FLSUN T1 ⭐⭐⭐⭐<br/>Balanced"]
    
    MEDIUM --> TYPE{▭ Type?}
    TYPE -->|Detail| MEDIUM_DETAIL["FLSUN S1 ⭐⭐⭐⭐<br/>or CR-6 Max ⭐⭐⭐⭐"]
    TYPE -->|Speed| MEDIUM_SPEED["Super Racer ⭐⭐⭐⭐<br/>High Speed"]
    
    LARGE --> LARGE_CHECK{Large Format?}
    LARGE_CHECK -->|Yes| LARGE_PRINTER["CR-10S ⭐⭐⭐⭐⭐<br/>or X5SA Pro ⭐⭐⭐⭐"]
    LARGE_CHECK -->|No| LARGE_FALLBACK["FLSUN S1 ⭐⭐⭐<br/>Can print up to 300mm"]
    
    XL --> XL_CHECK{Available?}
    XL_CHECK -->|X5SA Ready| XL_BEST["X5SA Pro ⭐⭐⭐⭐⭐<br/>330×330×400mm"]
    XL_CHECK -->|CR-10S Ready| XL_ALT["CR-10S ⭐⭐⭐⭐<br/>300×300×400mm"]
    XL_CHECK -->|Neither| MANUAL_XL["👤 Manual Required<br/>Split model or wait"]
    
    FINAL([✅ Route Complete]) 
    MINI_SPEED --> FINAL
    MINI_QUALITY --> FINAL
    SMALL_HIGH --> FINAL
    SMALL_FAST --> FINAL
    MEDIUM_DETAIL --> FINAL
    MEDIUM_SPEED --> FINAL
    LARGE_PRINTER --> FINAL
    LARGE_FALLBACK --> FINAL
    XL_BEST --> FINAL
    XL_ALT --> FINAL
    MANUAL_XL --> FINAL
```

---

## Material-Based Routing

```mermaid
flowchart TB
    subgraph Materials["🧪 MATERIAL REQUIREMENTS"]
        
        PLA["🟢 PLA<br/>50-60°C bed<br/>190-220°C nozzle"]
        
        PETG["🟠 PETG<br/>70-80°C bed<br/>230-250°C nozzle"]
        
        ABS["🔴 ABS<br/>90-110°C bed<br/>230-250°C nozzle<br/>Enclosure Required"]
        
        ASA["🟣 ASA<br/>90-110°C bed<br/>240-260°C nozzle<br/>Enclosure Required"]
        
        TPU["🔵 TPU<br/>50-60°C bed<br/>220-250°C nozzle<br/>Low Speed"]
    end

    subgraph Printer_Selection["🖨️ BEST PRINTER BY MATERIAL"]
        PLA_Printers["✅ All Printers<br/>FLSUN Deltas<br/>Cartesian Any"]
        
        PETG_Printers["✅ Most Printers<br/>Recommended:<br/>S1, CR-6 Max<br/>MK3S"]
        
        ABS_Printers["🔥 Tronxy D01 Pro<br/>Enclosed Chamber<br/>Active Heating"]
        
        ASA_Printers["🔥 Tronxy D01 Pro<br/>Enclosed Chamber<br/>UV Resistant"]
        
        TPU_Printers["🐢 Tronxy D01 Pro<br/>or Sovol SV-01<br/>Slow, Flexible"]
    end

    PLA --> PLA_Printers
    PETG --> PETG_Printers
    ABS --> ABS_Printers
    ASA --> ASA_Printers
    TPU --> TPU_Printers
```

---

## Printer Availability Matrix

```mermaid
flowchart TB
    subgraph Fleet_Status["🟢 PRINTER AVAILABILITY"]
        
        subgraph Deltas["Δ FLSUN Deltas"]
            V400_Status["V400<br/>🟢 Available<br/>⚡ Speed"]
            T1_1_Status["T1 #1<br/>🟢 Available<br/>🎯 Balanced"]
            T1_2_Status["T1 #2<br/>🟢 Available<br/>🎯 Balanced"]
            S1_Status["S1<br/>🟢 Available<br/>📐 Medium"]
            SR_Status["Super Racer<br/>🟢 Available<br/>⚡ Very Fast"]
            QQSP_Status["QQ-S Pro<br/>🟢 Available<br/>📐 Compact"]
        end
        
        subgraph Cartesians["▭ Cartesian"]
            CR10S_Status["CR-10S<br/>🟢 Available<br/>📏 Large"]
            CR6MAX_Status["CR-6 Max<br/>🟢 Available<br/>🏭 Stable"]
            D01_Status["D01 Pro<br/>🟢 Available<br/>🔥 Enclosed"]
            X5SA_Status["X5SA Pro<br/>🟢 Available<br/>📏 XL"]
            MK3S_Status["MK3S<br/>🟢 Available<br/>✨ Precision"]
            SV01_Status["SV-01<br/>🟢 Available<br/>🧪 General"]
        end
    end
```

| Status | Code | Meaning | Can Route? |
|--------|------|---------|-----------|
| 🟢 Available | `available` | Idle, ready | ✅ Yes |
| 🟡 Busy | `printing` | Currently printing | ⚠️ Check ETA |
| 🔴 Error | `error` | Problem detected | ❌ No |
| 🔵 Maintenance | `maintenance` | Needs attention | ❌ No |

---

## Priority Scoring Algorithm

```mermaid
flowchart LR
    subgraph Input["📊 SCORING FACTORS"]
        D[📐 Dimensions]
        M[🧪 Material]
        Q[✨ Quality Req]
        T[⏱️ Time Priority]
        A[🔋 Availability]
    end

    subgraph Weights["⚖️ WEIGHT CONFIGURATION"]
        W_SIZE["Size Match: 30%"]
        W_MAT["Material Match: 20%"]
        W_QUAL["Quality Match: 25%"]
        W_TIME["Speed Match: 15%"]
        W_AVAIL["Availability: 10%"]
    end

    subgraph Calculate["🧮 SCORE CALCULATION"]
        Score["Total Score =<br/>Σ(Factor × Weight)"]
    end

    subgraph Output["🏆 OUTPUT"]
        Rank["Ranked Printer List"]
        Best["🥇 Best Match"]
    end

    Input --> Weights
    Weights --> Calculate
    Calculate --> Output
```

### Scoring Formula

```
Score = (SizeScore × 0.30) + (MaterialScore × 0.20) + (QualityScore × 0.25) + (TimeScore × 0.15) + (AvailScore × 0.10)
```

### Score Ranges

| Score | Meaning | Action |
|-------|---------|--------|
| **90-100** | Perfect match | Assign immediately |
| **70-89** | Good match | Assign if no perfect |
| **50-69** | Acceptable | Fallback option |
| **<50** | Poor match | Manual review needed |

---

## Configuration File (routing-rules.yaml)

```yaml
# Printer Routing Rules Configuration
# Location: /config/routing-rules.yaml

printers:
  flsun_v400:
    type: delta
    kinematics: delta
    build_volume: [300, 300]  # mm
    max_speed: 300  # mm/s
    qualities: [low, medium]
    materials: [pla, petg]
    enclosure: false
    priority: 10
    tags: [speed, miniature, prototype]

  flsun_t1:
    type: delta
    kinematics: delta
    build_volume: [300, 400]
    max_speed: 250
    qualities: [medium, high]
    materials: [pla, petg]
    enclosure: false
    priority: 9
    tags: [balanced, general]

  flsun_t1_2:
    type: delta
    kinematics: delta
    build_volume: [300, 400]
    max_speed: 250
    qualities: [medium, high]
    materials: [pla, petg]
    enclosure: false
    priority: 9
    tags: [balanced, general]

  flsun_s1:
    type: delta
    kinematics: delta
    build_volume: [300, 400]
    max_speed: 250
    qualities: [medium, high]
    materials: [pla, petg, abs]
    enclosure: false
    priority: 8
    tags: [medium, versatile]

  flsun_super_racer:
    type: delta
    kinematics: delta
    build_volume: [300, 400]
    max_speed: 300
    qualities: [low, medium]
    materials: [pla, petg]
    enclosure: false
    priority: 10
    tags: [speed, prototype]

  flsun_qqsp:
    type: delta
    kinematics: delta
    build_volume: [255, 300]
    max_speed: 250
    qualities: [medium]
    materials: [pla, petg]
    enclosure: false
    priority: 7
    tags: [compact, delta]

  creality_cr10s:
    type: cartesian
    kinematics: xyz
    build_volume: [300, 300, 400]
    max_speed: 100
    qualities: [high]
    materials: [pla, petg, abs]
    enclosure: false
    priority: 8
    tags: [large, flat]

  creality_cr6max:
    type: cartesian
    kinematics: xyz
    build_volume: [300, 300, 400]
    max_speed: 100
    qualities: [high]
    materials: [pla, petg, abs]
    enclosure: false
    priority: 8
    tags: [large, stable]

  tronxy_d01:
    type: cartesian
    kinematics: xyz
    build_volume: [220, 220, 250]
    max_speed: 80
    qualities: [high]
    materials: [pla, petg, abs, asa, tpu]
    enclosure: true
    priority: 9
    tags: [engineering, enclosed]

  tronxy_x5sa:
    type: cartesian
    kinematics: xyz
    build_volume: [330, 330, 400]
    max_speed: 80
    qualities: [high]
    materials: [pla, petg, abs]
    enclosure: false
    priority: 8
    tags: [xl, large]

  prusa_mk3s:
    type: cartesian
    kinematics: xyz
    build_volume: [250, 210, 210]
    max_speed: 100
    qualities: [maximum]
    materials: [pla, petg, abs]
    enclosure: false
    priority: 10
    tags: [precision, detail, quality]

  sovol_sv01:
    type: cartesian
    kinematics: xyz
    build_volume: [280, 280, 320]
    max_speed: 80
    qualities: [medium, high]
    materials: [pla, petg, abs, tpu]
    enclosure: false
    priority: 6
    tags: [general, testing]

# Routing Rules
rules:
  # Size-based routing
  size_thresholds:
    miniature: 50   # mm
    small: 100
    medium: 200
    large: 300
    xl: 330

  # Material requirements
  material_requirements:
    abs:
      requires_enclosure: true
      preferred_printers: [tronxy_d01]
    asa:
      requires_enclosure: true
      preferred_printers: [tronxy_d01]
    tpu:
      requires_flexible: true
      preferred_printers: [tronxy_d01, sovol_sv01]
    pla:
      preferred_printers: [all]

  # Quality mapping
  quality_presets:
    maximum:
      preferred_printers: [prusa_mk3s]
      layer_height: 0.05
    high:
      preferred_printers: [prusa_mk3s, flsun_s1, cr6max]
      layer_height: 0.12
    medium:
      preferred_printers: [fllsun_t1, flsun_s1]
      layer_height: 0.20
    low:
      preferred_printers: [fllsun_v400, super_racer]
      layer_height: 0.28
```

---

## Router API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/route` | POST | Get best printer for STL |
| `/api/fleet-status` | GET | All printer statuses |
| `/api/queue` | GET | Current job queue |
| `/api/assign/{job_id}` | POST | Assign job to printer |
| `/api/rules` | GET/PUT | Routing rules config |

---

## Example Routing Request

```json
{
  "model": {
    "file": "/output/model.stl",
    "dimensions": {
      "x": 150,
      "y": 200,
      "z": 80
    },
    "volume_cm3": 2400
  },
  "requirements": {
    "material": "pla",
    "quality": "high",
    "time_priority": "normal",
    "enclosure_required": false
  }
}
```

## Example Routing Response

```json
{
  "recommended": {
    "printer": "fllsun_s1",
    "score": 94,
    "estimated_time": "45 minutes",
    "config": {
      "layer_height": 0.12,
      "nozzle_temp": 210,
      "bed_temp": 60
    }
  },
  "alternatives": [
    {
      "printer": "fllsun_t1_1",
      "score": 88,
      "estimated_time": "42 minutes"
    },
    {
      "printer": "creality_cr6max",
      "score": 82,
      "estimated_time": "65 minutes"
    }
  ]
}
```
