# ControlNet and Adapters — Code Example

## Setup

```bash
pip install diffusers transformers accelerate torch controlnet-aux
```

`controlnet-aux` provides the preprocessing tools (pose detectors, edge detectors, depth estimators).

---

## Example 1: OpenPose ControlNet — Generate from a Pose

```python
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from controlnet_aux import OpenposeDetector
from PIL import Image

# ── Step 1: Load ControlNet model ──
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-openpose",
    torch_dtype=torch.float16,
)

# ── Step 2: Load Stable Diffusion + ControlNet pipeline ──
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16,
).to("cuda")

# Use faster scheduler
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_attention_slicing()

# ── Step 3: Extract pose from reference image ──
detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")

reference_image = Image.open("reference_person.jpg")  # Any photo with a person
reference_image = reference_image.resize((512, 512))

# Detect the 18-keypoint skeleton
pose_image = detector(reference_image)
pose_image.save("detected_pose.png")  # Visualize the skeleton
print("Pose skeleton saved to detected_pose.png")

# ── Step 4: Generate a new person in the detected pose ──
image = pipe(
    prompt="a superhero in a dramatic stance, vibrant comic book style, bright colors",
    negative_prompt="blurry, low quality, realistic, photograph",
    image=pose_image,                          # The pose skeleton as control
    num_inference_steps=20,
    guidance_scale=7.5,
    controlnet_conditioning_scale=1.0,         # How strictly to follow the pose
    generator=torch.Generator("cuda").manual_seed(42),
).images[0]

image.save("superhero_in_pose.png")
print("Generated image saved to superhero_in_pose.png")
```

---

## Example 2: Canny Edge ControlNet — Generate from Shape

```python
import torch
import cv2
import numpy as np
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from PIL import Image

# Load Canny ControlNet
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny",
    torch_dtype=torch.float16,
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16,
).to("cuda")
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)

# ── Extract Canny edges from a reference image ──
reference = Image.open("building_photo.jpg").resize((512, 512))
reference_np = np.array(reference)

# Canny edge detection (low_threshold, high_threshold)
edges = cv2.Canny(reference_np, threshold1=100, threshold2=200)

# Convert to 3-channel PIL image
edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
canny_image = Image.fromarray(edges_rgb)
canny_image.save("detected_edges.png")

# ── Generate a new building keeping the same shape ──
image = pipe(
    prompt="a futuristic skyscraper with glass and steel, cyberpunk cityscape, neon lights",
    negative_prompt="blurry, old, rundown, cartoon",
    image=canny_image,
    num_inference_steps=20,
    guidance_scale=7.5,
    controlnet_conditioning_scale=0.9,   # Slightly relaxed for more creative freedom
).images[0]

image.save("futuristic_building.png")
```

---

## Example 3: Depth ControlNet — Preserve 3D Layout

```python
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from controlnet_aux import MidasDetector
from PIL import Image

# Load Depth ControlNet
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-depth",
    torch_dtype=torch.float16,
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16,
).to("cuda")
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)

# ── Extract depth map ──
depth_detector = MidasDetector.from_pretrained("lllyasviel/Annotators")

reference = Image.open("interior_photo.jpg").resize((512, 512))
depth_map = depth_detector(reference)
depth_map.save("depth_map.png")

# ── Generate new interior keeping same 3D layout ──
image = pipe(
    prompt="a Japanese zen interior, minimalist, bamboo furniture, natural light, tatami mats",
    negative_prompt="cluttered, western, modern, industrial",
    image=depth_map,
    num_inference_steps=20,
    guidance_scale=7.5,
    controlnet_conditioning_scale=1.0,
).images[0]

image.save("zen_interior.png")
```

---

## Example 4: Loading and Using a LoRA

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# ── Load a LoRA from a local file ──
# Download a LoRA from Civitai or train your own
# Example: a "studio ghibli style" LoRA
pipe.load_lora_weights(
    "./loras/",
    weight_name="studio_ghibli_style.safetensors",
)

# Generate with LoRA active
image = pipe(
    prompt="a young woman walking through a meadow with wildflowers, warm afternoon light",
    negative_prompt="photorealistic, dark, scary",
    num_inference_steps=30,
    guidance_scale=7.0,
    cross_attention_kwargs={"scale": 0.8},  # LoRA scale: 0.0 (off) to 1.0+ (full)
).images[0]
image.save("ghibli_style.png")

# ── Compare with LoRA off ──
image_no_lora = pipe(
    prompt="a young woman walking through a meadow with wildflowers, warm afternoon light",
    negative_prompt="photorealistic, dark, scary",
    num_inference_steps=30,
    guidance_scale=7.0,
    cross_attention_kwargs={"scale": 0.0},  # scale=0 means LoRA has no effect
).images[0]
image_no_lora.save("default_style.png")
```

---

## Example 5: Stacking Multiple LoRAs

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Load two LoRAs with different names
pipe.load_lora_weights("./loras/", weight_name="watercolor_style.safetensors", adapter_name="watercolor")
pipe.load_lora_weights("./loras/", weight_name="detailed_portrait.safetensors", adapter_name="portrait")

# Activate both with individual weights
pipe.set_adapters(
    ["watercolor", "portrait"],
    adapter_weights=[0.6, 0.8],   # Sum ≤ 1.5 to avoid artifacts
)

image = pipe(
    prompt="a portrait of a woman, soft light, detailed",
    num_inference_steps=30,
    guidance_scale=7.5,
).images[0]
image.save("stacked_lora.png")

print("Combined watercolor style (0.6) + portrait detail (0.8)")
print("Tip: if artifacts appear, reduce individual weights")
```

---

## Example 6: IP-Adapter — Style Transfer from Reference Image

```python
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

# Load IP-Adapter
pipe.load_ip_adapter(
    "h94/IP-Adapter",
    subfolder="models",
    weight_name="ip-adapter_sd15.bin",
)
pipe.set_ip_adapter_scale(0.6)  # How much to follow reference image style (0.0-1.0)

# Load reference style image
style_reference = Image.open("reference_painting.jpg").resize((512, 512))

# Generate using reference image style + text prompt for content
image = pipe(
    prompt="a cat sitting on a windowsill",     # Content from text
    ip_adapter_image=style_reference,            # Style from reference image
    negative_prompt="blurry, low quality",
    num_inference_steps=30,
    guidance_scale=7.5,
).images[0]

image.save("cat_in_reference_style.png")
print("Content: text prompt (cat on windowsill)")
print("Style: reference image aesthetic")
```

---

## Example 7: ControlNet + SDXL

```python
import torch
from diffusers import (
    StableDiffusionXLControlNetPipeline,
    ControlNetModel,
    AutoencoderKL,
)
from controlnet_aux import OpenposeDetector
from PIL import Image

# ── Load SDXL-compatible ControlNet ──
controlnet = ControlNetModel.from_pretrained(
    "thibaud/controlnet-openpose-sdxl-1.0",   # SDXL-specific ControlNet
    torch_dtype=torch.float16,
)

vae = AutoencoderKL.from_pretrained(
    "madebyollin/sdxl-vae-fp16-fix",           # Numerically stable VAE for SDXL
    torch_dtype=torch.float16,
)

pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    controlnet=controlnet,
    vae=vae,
    torch_dtype=torch.float16,
).to("cuda")
pipe.enable_attention_slicing()

# Detect pose from reference
detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
reference = Image.open("dancer.jpg").resize((1024, 1024))
pose = detector(reference, detect_resolution=1024, image_resolution=1024)

# Generate at SDXL native resolution (1024×1024)
image = pipe(
    prompt="a ballet dancer in a white tutu on stage, professional photography, dramatic lighting",
    negative_prompt="blurry, low quality, amateur",
    image=pose,
    num_inference_steps=30,
    guidance_scale=7.5,
    controlnet_conditioning_scale=1.0,
    height=1024,
    width=1024,
).images[0]

image.save("ballet_dancer_sdxl.png")
print("Note: use SDXL-specific ControlNets with SDXL — SD 1.5 ControlNets are incompatible!")
```

---

## ControlNet vs LoRA vs IP-Adapter Summary

| | ControlNet | LoRA | IP-Adapter |
|--|------------|------|-----------|
| Controls | Structure (pose/depth/edges) | Style/subject/concept | Image style/content |
| Input | Structural map | None (baked into weights) | Reference image |
| Size | ~1.5GB model file | 3-50MB weights | ~100MB adapter |
| Training needed? | Pre-trained options available | Must train or download | Pre-trained available |
| Modifies base model? | No | No (additive) | No (additive) |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Modern Diffusion Models](../05_Modern_Diffusion_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Diffusion vs GANs](../07_Diffusion_vs_GANs/Theory.md)
