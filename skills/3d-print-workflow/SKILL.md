---
name: 3d-print-workflow
description: Execute complete 3D print pipeline from photo to physical print. Use this skill when user wants to print an object - it handles the entire workflow from image analysis to final print.
---

# 3D Print Workflow Skill

Execute the complete 3D printing pipeline: photo → AI analysis → 3D generation → mesh processing → printer routing → physical print.

## When to Use

- User says "print this", "make this 3D", "print an object"
- User uploads a photo and wants it printed
- User wants to convert an image to a physical object

## Workflow Steps

### Step 1: Photo Analysis
```
Use MiniMax vision to analyze the photo:
- Identify the main object
- Estimate complexity (simple/medium/complex)
- Estimate dimensions
- Flag any issues (blurry, occluded, poor lighting)
```

### Step 2: 3D Generation
```
Choose model based on priority:
- Quality priority: Hunyuan3D-2.1
- Speed priority: TRELLIS.2

Generate via ComfyUI MCP:
- comfyui_queue_prompt with workflow JSON
- Wait for completion
- Get output OBJ/GLB file
```

### Step 3: Mesh Processing
```
Process mesh via Blender MCP:
1. Import OBJ
2. Check for issues (non-manifold, holes)
3. Repair mesh
4. Add solidify modifier (default 2.5mm)
5. Export as STL

Use: blender_full_pipeline or individual tools
```

### Step 4: Printer Routing
```
Select optimal printer:
1. Check model dimensions
2. Match to build volume
3. Consider material requirements
4. Check printer availability
5. Apply routing rules

See printer-router skill for detailed logic.
```

### Step 5: Print Job
```
Execute via Moonraker MCP:
1. Upload STL to printer
2. Configure print settings (temps, speed)
3. Start print
4. Monitor progress
```

## Output Format

Report each step to user:
```
📷 Photo received
✓ Object identified: [type]
📐 Estimated dimensions: [W]x[H]x[D]mm

🎨 Generating 3D model...
✓ Model generated: hunyuan3d_output.obj

🔧 Processing mesh...
✓ Mesh repaired
✓ Wall thickness added: 2.5mm
✓ Exported: output.stl

🗺️ Routing to printer...
✓ Selected: FLSUN T1 #1
   Reason: Balanced size (85x120x60mm), available

🖨️ Starting print...
✓ Print started at 14:32
📊 Progress: 0%

[Monitor and update user]
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| Generation fails | Retry 3x, switch to alternate model |
| Mesh has issues | Retry repair, suggest manual fix |
| Printer busy | Route to next best printer |
| Print fails | Cancel, route to backup printer |

## Configuration

Default settings (can be overridden):
- Wall thickness: 2.5mm
- Layer height: 0.2mm
- Print speed: 60mm/s (balanced)
- Material: PLA (unless specified)

## Quality Levels

| Level | Model | Resolution | Time | Quality |
|-------|-------|------------|------|---------|
| Prototype | TRELLIS.2 | 256³ | 30-60s | Medium |
| Standard | TRELLIS.2 | 384³ | 1-3min | High |
| Production | Hunyuan3D-2.1 | 512³ | 3-6min | Highest |

## Examples

### Basic Print
```
User: Print this toy figure
Photo: toy.jpg

→ Analyze photo
→ Generate 3D with Hunyuan3D (quality)
→ Process mesh
→ Route to FLSUN T1 (balanced size)
→ Start print
```

### Quick Prototype
```
User: I need a quick prototype of this part
Photo: part.jpg

→ Analyze photo
→ Generate 3D with TRELLIS (fast)
→ Process mesh
→ Route to FLSUN V400 (speed priority)
→ Start print
```

### Large Print
```
User: Print this sculpture, make it 150mm tall
Photo: sculpture.jpg

→ Analyze photo, scale to 150mm height
→ Generate 3D
→ Process mesh
→ Route to CR-10S (large format)
→ Start print
```

## Notes

- Always confirm estimated print time with user for long prints
- For very large prints (>4 hours), offer to notify when complete
- If printer becomes unavailable mid-print, offer to resume on another
- Save generated OBJ files for future reference
