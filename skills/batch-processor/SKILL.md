---
name: batch-processor
description: Process multiple 3D print jobs from a queue or watched folder. Use this skill when handling batch print jobs or automating print queue management.
---

# Batch Processor Skill

Handle multiple 3D print jobs automatically from a queue.

## When to Use

- User wants to print multiple models
- Uploaded a folder of STL files
- Automated print queue processing
- Night/weekend batch printing

## Queue Management

### Queue Structure
```python
{
  "jobs": [
    {
      "id": "uuid",
      "input_file": "path/to/model.obj",
      "priority": 1,  # Lower = higher priority
      "status": "pending",
      "created": "timestamp",
      "settings": {
        "printer": "auto",  # or specific printer
        "material": "PLA",
        "quality": "standard"
      }
    }
  ],
  "max_concurrent": 3,  # Max simultaneous prints
  "max_pending": 10     # Max queued jobs
}
```

### Job Status Flow
```
PENDING → QUEUED → PRINTING → COMPLETED
              ↓         ↓
           CANCELLED  FAILED → RETRY/ESCALATE
```

## Watch Folder

Monitor a folder for new files:
```
/input/photos/      → Photos to convert
/input/stl/         → Ready-to-print STL files
/output/            → Generated OBJ/STL files
```

### File Processing
```
New file detected →
1. Validate file type (.obj, .stl, .jpg, .png)
2. Add to queue with default settings
3. Notify user of queue position
4. Process when resources available
```

## Parallelization

### Limits
- Max concurrent 3D generation: 2 (VRAM limited)
- Max concurrent Blender: 2 (CPU limited)
- Max concurrent prints: 11 (full fleet)

### Scheduling Strategy
```
1. Check available printers
2. Check generation queue
3. If generation complete + printer available:
   → Upload to printer
   → Start print
   → Update queue
4. If all printers busy:
   → Continue generating for next batch
5. If all generators busy:
   → Wait for completion
```

## Batch Workflow

### Phase 1: Collect
```
1. Scan input folder
2. Identify file types
3. Group by processing method:
   - Photos → 3D generation needed
   - OBJ → Mesh processing only
   - STL → Direct to print
```

### Phase 2: Generate (Parallel)
```
For photos:
1. Analyze with vision model
2. Queue for ComfyUI generation
3. Process up to 2 at a time
4. Store generated OBJ
```

### Phase 3: Process (Parallel)
```
For all models:
1. Queue for Blender processing
2. Repair mesh
3. Add solidify
4. Export STL
5. Max 2 concurrent
```

### Phase 4: Print
```
When printer available:
1. Route to optimal printer
2. Upload STL
3. Start print
4. Monitor progress
5. Update queue
6. On completion → Next job
```

## Output Format

### Queue Status
```
📋 PRINT QUEUE - 8 jobs

Processing: 2
  [1] Photo: dragon.jpg → Generating (45%)
  [2] STL: phone_case.stl → Processing (20%)

Printing: 3
  [3] FLSUN T1 #1: dragon_v2.stl - 67%
  [4] CR-6 Max: gear_set.stl - 23%
  [5] X5SA Pro: baseplate.stl - 8%

Pending: 3
  [6] mech_part.obj - Waiting for printer
  [7] figurine.stl - Waiting for printer
  [8] prototype.obj - Waiting for printer

Completed today: 12
```

### Batch Progress
```
📊 BATCH PROGRESS

Job 1/8: dragon.jpg
  ✓ Photo analysis complete
  ✓ 3D model generated (Hunyuan3D)
  ✓ Mesh processed (2.5mm walls)
  ✓ Routed to FLSUN T1 #1
  🔵 Printing - 67%

Job 2/8: phone_case.stl
  ✓ Received
  ✓ Processing in Blender
  🔄 Mesh repair

Jobs 3-8: Pending
```

## Configuration

### Default Settings
```yaml
batch:
  max_concurrent_generation: 2
  max_concurrent_blender: 2
  max_concurrent_prints: 3
  auto_retry: 3
  retry_delay_seconds: 60

material_defaults:
  PLA:
    bed_temp: 60
    nozzle_temp: 210
    speed: 60
  PETG:
    bed_temp: 80
    nozzle_temp: 240
    speed: 50
```

### Quality Presets
| Preset | Layer Height | Speed | Use Case |
|--------|-------------|-------|----------|
| Draft | 0.3mm | 80mm/s | Prototypes |
| Standard | 0.2mm | 60mm/s | General |
| Quality | 0.12mm | 40mm/s | Final prints |
| Precision | 0.08mm | 25mm/s | Miniatures |

## Error Handling

### Generation Failures
```
1. Retry with same settings (max 3)
2. Fallback to faster model (TRELLIS)
3. Mark as failed, continue batch
4. Report failures at end
```

### Processing Failures
```
1. Retry mesh repair
2. Try alternate repair method
3. Manual intervention flag
```

### Print Failures
```
1. Cancel failed print
2. Attempt retry on same printer
3. Route to backup printer
4. Mark as failed after 2 attempts
```

## Notification Schedule

| Event | Notify |
|-------|--------|
| Job started | Immediate |
| Progress milestone (25%, 50%, 75%) | Skip (too noisy) |
| Job completed | Immediate |
| Job failed | Immediate |
| Batch completed | Summary |
| All printers busy | Status update |

## Examples

### Simple Batch
```
User: print everything in /models/to_print

→ Scan folder
→ Found 5 STL files
→ All PLA, standard quality
→ Queue and process
→ Start prints as printers available
```

### Photo Batch
```
User: print these 10 photos

→ Analyze all photos
→ Queue for generation (2 at a time)
→ Process meshes as generated
→ Print as printers free
→ Report completion
```

### Priority Override
```
User: I need this prototype ASAP

→ Set priority to 1 (highest)
→ Move to front of queue
→ Use fastest printer (V400)
→ Skip ahead of other jobs
```

## Batch Report

At batch completion:
```
📊 BATCH COMPLETE

Processed: 10 jobs
  ✓ Successful: 8
  ⚠️ Failed: 2 (logged)
  ⏱️ Total time: 6h 45m
  🖨️ Printer usage:
    - FLSUN T1 #1: 3 jobs, 4h
    - CR-6 Max: 2 jobs, 2.5h
    - X5SA Pro: 2 jobs, 3h
    - etc.

Failed jobs:
  - gear_v2.stl: Mesh repair failed
  - bracket.obj: Too large for any printer
```

## Notes

- Use priority queue for job ordering
- Respect max concurrent limits
- Save generated files for future reference
- Log all events for debugging
- Consider overnight/weekend for large batches
