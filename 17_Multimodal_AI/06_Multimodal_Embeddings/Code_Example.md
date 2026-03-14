# Multimodal Embeddings — Code Example: Image Search with CLIP

## Build a searchable image library using CLIP embeddings

```python
"""
clip_image_search.py — Search a photo library by typing descriptions
pip install transformers torch pillow sentence-transformers numpy
"""
import os
import json
import numpy as np
from pathlib import Path
from PIL import Image
import torch


# ──────────────────────────────────────────────
# Option A: Using sentence-transformers (simpler)
# ──────────────────────────────────────────────

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

def build_image_index_simple(image_dir: str, index_file: str = "index.json") -> dict:
    """
    Build a CLIP embedding index for all images in a directory.
    Saves to a JSON file for reuse.
    """
    model = SentenceTransformer("clip-ViT-B-32")
    image_dir = Path(image_dir)

    image_paths = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png")) + list(image_dir.glob("*.webp"))

    print(f"Indexing {len(image_paths)} images...")

    index = {}
    for path in image_paths:
        try:
            img = Image.open(path).convert("RGB")
            embedding = model.encode(img)
            index[str(path)] = embedding.tolist()
            print(f"  Indexed: {path.name}")
        except Exception as e:
            print(f"  Skipped {path.name}: {e}")

    with open(index_file, "w") as f:
        json.dump(index, f)

    print(f"Saved index with {len(index)} images to {index_file}")
    return index


def search_images_simple(query: str, index_file: str = "index.json", top_k: int = 5) -> list[dict]:
    """
    Search for images matching a text description.
    Returns list of {path, score} dicts sorted by relevance.
    """
    model = SentenceTransformer("clip-ViT-B-32")

    # Load index
    with open(index_file) as f:
        index = json.load(f)

    if not index:
        return []

    # Encode query
    query_embedding = model.encode(query)

    # Compute similarities
    results = []
    for path, embedding in index.items():
        score = float(cos_sim(
            torch.tensor(query_embedding),
            torch.tensor(embedding)
        ))
        results.append({"path": path, "score": score})

    # Sort by similarity (highest first)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ──────────────────────────────────────────────
# Option B: Using raw transformers (more control)
# ──────────────────────────────────────────────

from transformers import CLIPProcessor, CLIPModel

class CLIPImageSearcher:
    """Full-featured CLIP image search with text and image queries."""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        print(f"Loading CLIP model: {model_name}")
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()

        self.index: dict[str, np.ndarray] = {}  # path → normalized embedding

    def _encode_image(self, image: Image.Image) -> np.ndarray:
        """Encode a PIL image to a normalized L2 unit vector."""
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)  # L2 normalize
        return features.squeeze().numpy()

    def _encode_text(self, text: str) -> np.ndarray:
        """Encode text to a normalized L2 unit vector."""
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        with torch.no_grad():
            features = self.model.get_text_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)
        return features.squeeze().numpy()

    def add_image(self, image_path: str):
        """Add a single image to the index."""
        img = Image.open(image_path).convert("RGB")
        self.index[image_path] = self._encode_image(img)

    def index_directory(self, directory: str):
        """Index all images in a directory."""
        dir_path = Path(directory)
        image_files = (
            list(dir_path.glob("*.jpg")) +
            list(dir_path.glob("*.jpeg")) +
            list(dir_path.glob("*.png")) +
            list(dir_path.glob("*.webp"))
        )
        print(f"Indexing {len(image_files)} images in {directory}...")
        for path in image_files:
            try:
                self.add_image(str(path))
                print(f"  ✓ {path.name}")
            except Exception as e:
                print(f"  ✗ {path.name}: {e}")
        print(f"Index complete: {len(self.index)} images")

    def save_index(self, path: str = "clip_index.npz"):
        """Save index to disk for reuse."""
        paths = list(self.index.keys())
        embeddings = np.stack([self.index[p] for p in paths])
        np.savez(path, paths=paths, embeddings=embeddings)
        print(f"Saved index ({len(paths)} images) to {path}")

    def load_index(self, path: str = "clip_index.npz"):
        """Load a saved index."""
        data = np.load(path, allow_pickle=True)
        for p, e in zip(data["paths"], data["embeddings"]):
            self.index[str(p)] = e
        print(f"Loaded index: {len(self.index)} images")

    def search_by_text(self, query: str, top_k: int = 5) -> list[dict]:
        """Find images matching a text description."""
        query_vec = self._encode_text(query)
        return self._search(query_vec, top_k)

    def search_by_image(self, image_path: str, top_k: int = 5) -> list[dict]:
        """Find images similar to an uploaded image."""
        img = Image.open(image_path).convert("RGB")
        query_vec = self._encode_image(img)
        return self._search(query_vec, top_k, exclude_path=image_path)

    def _search(self, query_vec: np.ndarray, top_k: int, exclude_path: str = None) -> list[dict]:
        if not self.index:
            return []

        paths = list(self.index.keys())
        embeddings = np.stack([self.index[p] for p in paths])

        # Cosine similarity = dot product of unit vectors
        scores = embeddings @ query_vec

        # Sort and return top-k
        sorted_idx = np.argsort(scores)[::-1]
        results = []
        for idx in sorted_idx:
            path = paths[idx]
            if path == exclude_path:
                continue
            results.append({"path": path, "score": float(scores[idx])})
            if len(results) >= top_k:
                break

        return results

    def zero_shot_classify(self, image_path: str, labels: list[str]) -> list[dict]:
        """
        Zero-shot image classification.
        Returns labels sorted by how well they match the image.
        """
        img = Image.open(image_path).convert("RGB")
        image_vec = self._encode_image(img)

        results = []
        for label in labels:
            text_vec = self._encode_text(f"a photo of a {label}")
            score = float(image_vec @ text_vec)
            results.append({"label": label, "score": score})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results


# ──────────────────────────────────────────────
# Demo usage
# ──────────────────────────────────────────────

if __name__ == "__main__":
    searcher = CLIPImageSearcher()

    # Example 1: Index a folder of images
    # searcher.index_directory("my_photos/")
    # searcher.save_index("my_photos_index.npz")

    # Example 2: Load existing index
    # searcher.load_index("my_photos_index.npz")

    # Example 3: Search by text description
    # results = searcher.search_by_text("sunset over water with warm colors", top_k=5)
    # for r in results:
    #     print(f"  {r['score']:.3f} — {r['path']}")

    # Example 4: Search by image (find similar images)
    # results = searcher.search_by_image("my_photo.jpg", top_k=5)

    # Example 5: Zero-shot classification
    # labels = ["cat", "dog", "bird", "car", "person"]
    # classification = searcher.zero_shot_classify("animal.jpg", labels)
    # print(f"Top match: {classification[0]['label']} ({classification[0]['score']:.3f})")

    # Demo with synthetic in-memory test
    print("Demo: Creating test images and computing similarity matrix")

    # Create solid-color test images to demonstrate the concept
    test_data = [
        ("red_image", (255, 0, 0), "a red object"),
        ("blue_image", (0, 0, 255), "a blue sky"),
        ("green_image", (0, 128, 0), "green grass"),
    ]

    for name, color, description in test_data:
        img = Image.new("RGB", (224, 224), color=color)
        img.save(f"/tmp/{name}.jpg")

    searcher2 = CLIPImageSearcher()
    for name, color, desc in test_data:
        searcher2.add_image(f"/tmp/{name}.jpg")

    # Search with different queries
    queries = ["a red object", "blue sky", "green grass"]
    for q in queries:
        results = searcher2.search_by_text(q, top_k=3)
        print(f"\nQuery: '{q}'")
        for r in results:
            print(f"  {r['score']:.3f} — {Path(r['path']).stem}")
```

---

## Minimal Cross-Modal Similarity Demo

```python
"""
Quick demo: prove that text and image embeddings are aligned
"""
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from PIL import Image
import torch

model = SentenceTransformer("clip-ViT-B-32")

# Create two test images
red_img = Image.new("RGB", (224, 224), color=(255, 50, 50))
blue_img = Image.new("RGB", (224, 224), color=(50, 50, 255))

# Encode images and texts
img_red = model.encode(red_img)
img_blue = model.encode(blue_img)
txt_red = model.encode("a red object")
txt_blue = model.encode("a blue object")

# Print similarity matrix
print("Cross-modal similarity matrix:")
print(f"             'red text'  'blue text'")
print(f"red image:   {cos_sim(img_red, txt_red).item():.3f}      {cos_sim(img_red, txt_blue).item():.3f}")
print(f"blue image:  {cos_sim(img_blue, txt_red).item():.3f}      {cos_sim(img_blue, txt_blue).item():.3f}")

# Expected output:
#              'red text'  'blue text'
# red image:   0.28        0.21
# blue image:  0.19        0.27
# Diagonal entries should be higher — correct modality pairs match
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [05 — Audio and Speech AI](../05_Audio_and_Speech_AI/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 — Multimodal Agents](../07_Multimodal_Agents/Theory.md)
