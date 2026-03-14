# Guidance and Conditioning — Code Example

## Setup

```bash
pip install diffusers transformers accelerate torch
```

---

## Example 1: CFG Scale Comparison — Same Prompt, Different Guidance

```python
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

prompt = "a majestic eagle soaring over mountain peaks, dramatic lighting, professional wildlife photography"
negative_prompt = "blurry, low quality, cartoon, watermark"

# Generate the same prompt at different CFG scales
cfg_values = [1.0, 3.0, 7.5, 12.0, 20.0]
images = []

for cfg in cfg_values:
    # Use same seed for fair comparison
    generator = torch.Generator("cuda").manual_seed(42)

    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=30,
        guidance_scale=cfg,
        generator=generator,
    ).images[0]

    images.append(image)
    image.save(f"eagle_cfg_{cfg}.png")
    print(f"Saved eagle_cfg_{cfg}.png")

# Create a side-by-side comparison
total_width = sum(img.width for img in images)
comparison = Image.new("RGB", (total_width, images[0].height + 40), (255, 255, 255))

x_offset = 0
for i, (img, cfg) in enumerate(zip(images, cfg_values)):
    comparison.paste(img, (x_offset, 40))
    x_offset += img.width

comparison.save("cfg_comparison.png")
print("Comparison saved to cfg_comparison.png")
print(f"\nExpected observations:")
print("cfg=1.0  : Creative, loosely follows prompt, model's own aesthetic")
print("cfg=3.0  : Some prompt adherence, more variety")
print("cfg=7.5  : Good balance — clear eagle, natural image quality")
print("cfg=12.0 : Very on-prompt, may look over-contrasty")
print("cfg=20.0 : Oversaturated, distorted, prompt over-amplified")
```

---

## Example 2: Negative Prompt Experiments

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

prompt = "a portrait of a person smiling"
generator_base = torch.Generator("cuda").manual_seed(99)

# ── No negative prompt ──
image_no_neg = pipe(
    prompt=prompt,
    num_inference_steps=30,
    guidance_scale=7.5,
    generator=torch.Generator("cuda").manual_seed(99),
).images[0]
image_no_neg.save("portrait_no_negative.png")

# ── With quality negative prompt ──
image_with_neg = pipe(
    prompt=prompt,
    negative_prompt="blurry, low quality, distorted, watermark, bad anatomy, ugly, deformed",
    num_inference_steps=30,
    guidance_scale=7.5,
    generator=torch.Generator("cuda").manual_seed(99),
).images[0]
image_with_neg.save("portrait_with_negative.png")

# ── With anatomy-specific negative prompt ──
image_anatomy = pipe(
    prompt=prompt,
    negative_prompt="extra fingers, missing fingers, deformed hands, crossed eyes, bad face, asymmetric eyes, ugly",
    num_inference_steps=30,
    guidance_scale=7.5,
    generator=torch.Generator("cuda").manual_seed(99),
).images[0]
image_anatomy.save("portrait_anatomy_negative.png")

print("Generated three variants — compare the quality differences")
print("Key insight: negative prompts push the model AWAY from those concepts,")
print("they don't guarantee perfection but meaningfully improve average quality")
```

---

## Example 3: Visualizing What CFG Does Mathematically

```python
import torch
from diffusers import StableDiffusionPipeline, DDIMScheduler
import numpy as np

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Replace scheduler with DDIM for deterministic stepping
pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)

# Demonstrate the CFG formula manually for one step
# (simplified — just to show the concept)

prompt = "a red apple on a white table"
negative_prompt = ""

# Encode the prompts
text_inputs = pipe.tokenizer(
    [prompt, negative_prompt],
    padding="max_length",
    max_length=pipe.tokenizer.model_max_length,
    return_tensors="pt",
).to("cuda")

with torch.no_grad():
    # Get text embeddings for both conditioned and unconditioned
    text_embeddings = pipe.text_encoder(text_inputs.input_ids)[0]

cond_embeddings, uncond_embeddings = text_embeddings.chunk(2)

print(f"Text embedding shape: {cond_embeddings.shape}")  # [1, 77, 768]
print(f"Each of 77 tokens has a 768-dimensional embedding vector")
print(f"\nThe CFG formula at each denoising step:")
print(f"ε_guided = ε_uncond + w × (ε_text - ε_uncond)")
print(f"\nWith w=7.5:")
print(f"ε_guided = ε_uncond + 7.5 × (ε_text - ε_uncond)")
print(f"        = -6.5 × ε_uncond + 7.5 × ε_text")
print(f"\nThis is extrapolation: we go 7.5x in the direction of the text,")
print(f"using unconditioned as the baseline 'zero point'")
```

---

## Example 4: Prompt Weighting (Emphasis via Attention)

Some libraries support explicit weighting of prompt tokens using parentheses or brackets:

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Standard prompt
image1 = pipe(
    prompt="a cat sitting on a red sofa",
    num_inference_steps=30,
    guidance_scale=7.5,
    generator=torch.Generator("cuda").manual_seed(7),
).images[0]
image1.save("cat_normal.png")

# Note: Token weighting syntax varies by library.
# In AUTOMATIC1111 / ComfyUI:
#   (word:1.5) = 50% more weight on that word
#   [word] = 90% weight (reduce emphasis)
#
# In HuggingFace diffusers, you can use the 'compel' library:
# pip install compel
from compel import Compel
compel = Compel(tokenizer=pipe.tokenizer, text_encoder=pipe.text_encoder)

# Emphasize "red sofa" with 1.5x weight
prompt_embeds = compel('a cat sitting on a (red sofa)1.5')

image2 = pipe(
    prompt_embeds=prompt_embeds,
    num_inference_steps=30,
    guidance_scale=7.5,
    generator=torch.Generator("cuda").manual_seed(7),
).images[0]
image2.save("cat_red_sofa_emphasized.png")
print("Compare: cat_normal.png vs cat_red_sofa_emphasized.png")
print("The sofa should be more visually prominent in the second image")
```

---

## Example 5: Dynamic CFG with Progress Callback

```python
import torch
from diffusers import StableDiffusionPipeline, DDIMScheduler

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")
pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)

# Some practitioners use high CFG early (for structure) and lower CFG late (for quality)
# This can be approximated with a callback that modifies parameters mid-generation

step_log = []

def log_callback(step, timestep, latents):
    step_log.append({"step": step, "timestep": int(timestep)})

image = pipe(
    prompt="a lighthouse on rocky cliffs during a storm, dramatic waves, cinematic",
    negative_prompt="calm, sunny, flat, low quality",
    num_inference_steps=30,
    guidance_scale=7.5,
    callback=log_callback,
    callback_steps=1,
).images[0]

image.save("lighthouse.png")

print(f"\nDenoising timeline (first 5 steps):")
for entry in step_log[:5]:
    print(f"  Step {entry['step']:2d}: timestep = {entry['timestep']}")
print(f"  ...")
print(f"  Final step {step_log[-1]['step']}: timestep = {step_log[-1]['timestep']}")
```

---

## CFG Scale Visual Summary

```
Guidance Scale Effect on "a majestic eagle":

CFG=1.0  ████░░░░░░░░░░░░░░░░  Mostly unconditioned; creative, generic
CFG=3.0  ████████░░░░░░░░░░░░  Some structure; loosely eagle-like
CFG=7.5  ████████████████░░░░  Clear eagle, good composition (sweet spot)
CFG=12.0 ██████████████████░░  Very on-prompt; slightly over-rendered
CFG=20.0 ████████████████████  Over-amplified; saturated, distorted artifacts

Quality:
CFG=1.0  ▓▓▓▓▓▓░░░░  Some good images, some random
CFG=7.5  ▓▓▓▓▓▓▓▓░░  Most images are good
CFG=12.0 ▓▓▓▓▓▓░░░░  Prompt-correct but quality can drop
CFG=20.0 ▓▓░░░░░░░░  Usually degraded
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | CFG guide + negative prompt tips |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Stable Diffusion](../03_Stable_Diffusion/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Modern Diffusion Models](../05_Modern_Diffusion_Models/Theory.md)
