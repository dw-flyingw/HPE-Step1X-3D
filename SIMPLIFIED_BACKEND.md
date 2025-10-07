# Simplified Backend Implementation

## Problem with Current Backend

The current `backend/app.py` is **750+ lines** with:
- ❌ All custom classes embedded (AttnProcessor2_0, FluxTransformerBlock, etc.)
- ❌ Manual pipeline implementation
- ❌ Fragile and hard to maintain
- ❌ Breaks with dependency updates

## The Simple Solution

Use the **official Step1X-3D pipelines** from the [Hugging Face model](https://huggingface.co/stepfun-ai/Step1X-3D):

### New Simplified Backend: `backend/app_simple.py`

**Only ~180 lines** with:
- ✅ Uses official pipelines from step1x3d_geometry and step1x3d_texture
- ✅ Clean, maintainable code
- ✅ Follows official documentation
- ✅ Easier to update and debug
- ✅ Supports both geometry-only and full textured generation

## API Endpoints

### 1. Health Check
```bash
GET /
```

### 2. Generate Geometry Only (Untextured)
```bash
curl -X POST http://localhost:8000/generate-geometry \
  -F "image=@input.png" \
  -F "guidance_scale=7.5" \
  -F "num_inference_steps=50" \
  -F "seed=2025"
```

### 3. Generate Full Textured Asset
```bash
curl -X POST http://localhost:8000/generate-textured \
  -F "image=@input.png" \
  -F "guidance_scale=7.5" \
  -F "num_inference_steps=50" \
  -F "seed=2025"
```

## Key Differences

| Feature | Old Backend | New Backend |
|---------|-------------|-------------|
| Lines of Code | 750+ | ~180 |
| Custom Classes | Many embedded | None (uses official) |
| Maintainability | Low | High |
| API | Text prompt | Image input (correct) |
| Texture Support | No | Yes |
| Error Prone | Very | Minimal |

## Note: Image Input, Not Text

**Important:** Step1X-3D is an **image-to-3D** model, not text-to-3D:
- ❌ Old API: `/generate-3d` with text prompt (incorrect usage)
- ✅ New API: `/generate-textured` with image file (correct usage)

From the [official documentation](https://huggingface.co/stepfun-ai/Step1X-3D):
```python
# Input is an IMAGE, not text
input_image_path = "examples/test.png"
out = geometry_pipeline(input_image_path, ...)
```

## How to Switch

### 1. Backup Current Implementation
```bash
cd ~/HPE-Step1X-3D
mv backend/app.py backend/app_old.py
```

### 2. Use Simplified Version
```bash
mv backend/app_simple.py backend/app.py
```

### 3. Update Dockerfile CMD (if needed)
The dockerfile already uses `uvicorn app:app` so no changes needed!

### 4. Rebuild
```bash
docker compose down
docker compose build backend
docker compose up -d backend
```

## Advantages of Simplified Backend

1. **Maintainability**: Official pipelines handle all complexity
2. **Updates**: Just update the step1x3d packages, no code changes needed
3. **Features**: Automatically get new features from Step1X-3D updates
4. **Debugging**: Errors are in the library, not your code
5. **Documentation**: Follow official examples exactly
6. **Texture Support**: Full geometry + texture pipeline

## Dependencies

The simplified version requires:
- `step1x3d_geometry` package (from Step1X-3D repo)
- `step1x3d_texture` package (from Step1X-3D repo)

These are automatically available when you clone the Step1X-3D repository into your project.

## Testing

```bash
# Test geometry generation
curl -X POST http://localhost:8000/generate-geometry \
  -F "image=@test_image.png" \
  -o geometry.glb

# Test full textured generation
curl -X POST http://localhost:8000/generate-textured \
  -F "image=@test_image.png" \
  -o textured.glb
```

## Migration Checklist

- [ ] Backup current app.py
- [ ] Copy app_simple.py to app.py
- [ ] Verify Step1X-3D repository is in place
- [ ] Update frontend to use image upload instead of text prompt
- [ ] Test geometry generation
- [ ] Test textured generation
- [ ] Update API documentation

## Conclusion

The simplified backend:
- **4x less code** (750 → 180 lines)
- **Uses official APIs** (more reliable)
- **Easier to maintain** (no custom implementations)
- **Supports textures** (full pipeline)
- **Follows documentation** (best practices)

This is the recommended approach for production use!

