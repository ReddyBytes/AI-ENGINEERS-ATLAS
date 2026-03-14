# Stable Diffusion — Code Example

## Setup

```bash
pip install diffusers transformers accelerate torch
```

You'll need at least 4GB of VRAM for SD 1.5 in float16. A CPU-only run is possible but slow (~5 minutes per image).

---

## Example 1: Basic Text-to-Image

```python
import torch
from diffusers import StableDiffusionPipeline

# Load the pipeline — this downloads ~4GB of weights on first run
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,   # Use float16 for GPU memory efficiency
)
pipe = pipe.to("cuda")  # Move to GPU; use "mps" for Apple Silicon, "cpu" for no GPU

# Generate an image
image = pipe(
    prompt="a golden retriever puppy sitting on a sunny beach, professional photography, bokeh",
    num_inference_steps=30,    # 20-50 is the practical range; 30 is a good default
    guidance_scale=7.5,        # CFG scale; 7-8 is the sweet spot
    height=512,                # Must be divisible by 8
    width=512,
).images[0]

image.save("golden_retriever.png")
print("Image saved to golden_retriever.png")
```

---

## Example 2: With Negative Prompt

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

image = pipe(
    prompt="portrait of a woman, oil painting, renaissance style, dramatic lighting",
    negative_prompt="blurry, low quality, distorted, watermark, text, ugly, bad anatomy, extra limbs",
    num_inference_steps=30,
    guidance_scale=7.5,
).images[0]

image.save("portrait.png")
```

**Why negative prompts work:** The CFG formula subtracts the unconditional prediction and adds the conditioned one. When you provide a negative prompt instead of an empty string for the unconditional run, the model actively pushes away from those concepts. See folder 04 for the full CFG explanation.

---

## Example 3: Reproducible Generation with a Seed

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Fix the seed for reproducibility
generator = torch.Generator("cuda").manual_seed(42)

image = pipe(
    prompt="a cozy cabin in a snowy forest, warm light from windows, evening, cinematic",
    negative_prompt="blurry, low quality",
    num_inference_steps=30,
    guidance_scale=7.5,
    generator=generator,  # Same seed = same image every time
).images[0]

image.save("cabin_seed42.png")

# Run again with the same seed — you'll get the exact same image
generator = torch.Generator("cuda").manual_seed(42)
image2 = pipe(
    prompt="a cozy cabin in a snowy forest, warm light from windows, evening, cinematic",
    negative_prompt="blurry, low quality",
    num_inference_steps=30,
    guidance_scale=7.5,
    generator=generator,
).images[0]

image2.save("cabin_seed42_duplicate.png")
# cabin_seed42.png and cabin_seed42_duplicate.png are identical
```

---

## Example 4: Batch Generation

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Enable memory efficient attention for larger batches
pipe.enable_attention_slicing()

# Generate 4 images at once
images = pipe(
    prompt="a futuristic city skyline at night, neon lights, cyberpunk",
    negative_prompt="blurry, low quality",
    num_inference_steps=30,
    guidance_scale=7.5,
    num_images_per_prompt=4,  # Generate 4 variations
).images

for i, img in enumerate(images):
    img.save(f"city_{i}.png")
    print(f"Saved city_{i}.png")
```

---

## Example 5: img2img — Transform an Existing Image

```python
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Load and resize your input image
init_image = Image.open("your_photo.jpg").convert("RGB")
init_image = init_image.resize((512, 512))

image = pipe(
    prompt="oil painting in the style of Van Gogh, swirling brush strokes, vibrant colors",
    image=init_image,
    strength=0.75,        # 0.0 = no change, 1.0 = completely regenerated
                          # 0.5-0.8 is the practical range for style transfer
    guidance_scale=7.5,
    num_inference_steps=30,
).images[0]

image.save("transformed.png")
```

---

## Example 6: Inspect the Full Pipeline Components

```python
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")

# See all components
print(type(pipe.vae))         # AutoencoderKL
print(type(pipe.text_encoder)) # CLIPTextModel
print(type(pipe.tokenizer))    # CLIPTokenizer
print(type(pipe.unet))         # UNet2DConditionModel
print(type(pipe.scheduler))    # PNDMScheduler (default) or DDIMScheduler

# Count parameters
def count_params(model):
    return sum(p.numel() for p in model.parameters()) / 1e6

print(f"VAE: {count_params(pipe.vae):.1f}M parameters")
print(f"CLIP text encoder: {count_params(pipe.text_encoder):.1f}M parameters")
print(f"U-Net: {count_params(pipe.unet):.1f}M parameters")
# Output:
# VAE: 83.7M parameters
# CLIP text encoder: 123.1M parameters
# U-Net: 859.5M parameters
```

---

## Example 7: Switch to DDIM Scheduler for Speed

```python
import torch
from diffusers import StableDiffusionPipeline, DDIMScheduler

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Replace the default scheduler with DDIM
pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)

# DDIM can achieve good quality in just 20 steps
image = pipe(
    prompt="a majestic lion in golden hour light, wildlife photography",
    negative_prompt="blurry, low quality, cartoon",
    num_inference_steps=20,   # DDIM quality in 20 steps vs PNDM's 50
    guidance_scale=7.5,
).images[0]

image.save("lion_ddim.png")
```

---

## Memory Optimization Tips

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Tip 1: Attention slicing — trade speed for memory
pipe.enable_attention_slicing()

# Tip 2: VAE slicing — reduces memory for batch generation
pipe.enable_vae_slicing()

# Tip 3: Model CPU offload — very low VRAM (<4GB), moves components to CPU when not in use
# pipe.enable_model_cpu_offload()  # Slower but works on 2-3GB VRAM

# Tip 4: xFormers — faster attention if installed
# pip install xformers
# pipe.enable_xformers_memory_efficient_attention()

image = pipe(
    prompt="a serene Japanese garden with cherry blossoms",
    num_inference_steps=30,
    guidance_scale=7.5,
).images[0]
image.save("garden.png")
```

---

## Expected Output Quality Guide

| Inference Steps | Guidance Scale | Expected Result |
|----------------|---------------|-----------------|
| 10 | 7.5 | Fast, rough, usable for previews |
| 20 | 7.5 | Good quality, practical for most uses |
| 30 | 7.5 | High quality — recommended default |
| 50 | 7.5 | Excellent — diminishing returns beyond this |
| 30 | 1.0 | Creative / dream-like; ignores prompt |
| 30 | 15+ | Over-saturated, harsh; avoids this |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full SD architecture diagram |

⬅️ **Prev:** [How Diffusion Works](../02_How_Diffusion_Works/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Guidance and Conditioning](../04_Guidance_and_Conditioning/Theory.md)
