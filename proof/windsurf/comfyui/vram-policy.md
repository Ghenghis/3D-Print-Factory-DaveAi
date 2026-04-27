# Hunyuan3D VRAM Sequential Policy — RTX 3090 Ti (24GB)

## Policy

Hunyuan3D 2.1 operates in sequential VRAM mode to fit within 24GB:

1. Load shape generation model (Hunyuan3D-Shape-v2-1)
2. Run shape generation → save mesh to disk
3. Unload shape model, clear CUDA cache, free GPU memory
4. (Optional) Load paint/texture model (Hunyuan3D-Paint-v2-1)
5. Run texture generation on saved mesh
6. Unload paint model, clear CUDA cache
7. Send final mesh to Blender for repair/export

## Implementation

```python
import torch
import gc

def clear_gpu():
    torch.cuda.empty_cache()
    gc.collect()

# Stage 1: Shape
shape_model = load_shape_model()
mesh = shape_model.generate(prompt)
save_mesh(mesh)
del shape_model
clear_gpu()

# Stage 2: Paint (optional)
if texture_requested:
    paint_model = load_paint_model()
    textured = paint_model.apply(mesh_path)
    save_textured(textured)
    del paint_model
    clear_gpu()
```

## GPU
- Device: RTX 3090 Ti
- VRAM: 24GB
- Mode: sequential (not parallel)
