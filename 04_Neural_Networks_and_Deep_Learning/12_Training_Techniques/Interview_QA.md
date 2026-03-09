# Training Techniques — Interview Q&A

## Beginner

**Q1: What is an epoch and how many should you train for?**

One epoch is one complete pass through the entire training dataset. After one epoch, the model has seen every training example once. You typically train for multiple epochs — on each pass, the model sees the data in a different order (due to shuffling), encountering different batches. How many epochs? There is no universal answer. Train until the validation loss stops improving — this is why early stopping is so important. Common ranges: 10–50 for small datasets, 100–300 for medium, and training loops for large models are measured in steps (not epochs) and can run for days or weeks.

---

**Q2: What is the difference between batch size and epoch?**

Batch size is how many examples the model sees before making one weight update. Epoch is one full pass through all training data. If you have 10,000 examples and a batch size of 100, each epoch consists of 100 weight updates (one per batch). If you train for 10 epochs, you make 1,000 total weight updates. Larger batch sizes mean fewer updates per epoch. The relationship: `steps per epoch = dataset_size / batch_size`.

---

**Q3: What is transfer learning in simple terms?**

Transfer learning is using knowledge gained from one task to accelerate learning on a different task. In deep learning, this means taking a model already trained on a large dataset (like a neural network trained to recognize 1000 types of objects from millions of images) and adapting it for your specific task (like identifying 5 types of medical scans from 500 images). The pretrained model has already learned useful low-level features — edges, textures, shapes — that are useful for many visual tasks. You add a new final layer for your specific classes and train on your small dataset. You get good results with far less data and compute.

---

## Intermediate

**Q4: What is the "learning rate warmup" strategy and when is it used?**

Learning rate warmup starts training with a very small learning rate (near zero) and linearly increases it to the target value over the first few hundred or thousand steps. Without warmup, large learning rates at the start of training cause erratic weight updates — the model has randomly initialized weights and high-variance gradients, making large steps destructive. Warmup gives the model time to "settle in" before taking big steps. Warmup is particularly important for transformers and large models where the Adam optimizer's second moment estimates (variance of gradients) are unreliable at the start of training because they initialize at zero. Standard transformer training: linear warmup for ~4% of total steps, then cosine decay.

---

**Q5: What is the difference between feature extraction and fine-tuning in transfer learning?**

Feature extraction freezes all pretrained layers and only trains the new head (final layers added for the new task). The pretrained model is used purely as a feature extractor — its internal representations are fixed. This is fast, requires little data, and works when the new task is similar to the pretrained task. Fine-tuning unfreezes some or all of the pretrained layers and trains them along with the new head. The pretrained weights are adjusted for the new task. This is slower, requires more data, but achieves higher accuracy. A common strategy: start with feature extraction, then gradually unfreeze layers from the top (closest to output) downward, using a small learning rate for pretrained layers to avoid "forgetting" what was learned.

---

**Q6: What is mixed precision training and what are its requirements?**

Mixed precision training uses 16-bit (float16) precision for most computations and 32-bit (float32) for weight storage and the optimizer state. The 16-bit computations run 2–8× faster on modern GPU tensor cores (NVIDIA Volta/Turing/Ampere, Google TPU). The requirement: a mechanism called "loss scaling." Float16 has a much smaller dynamic range than float32. Small gradients underflow to zero in float16. Loss scaling multiplies the loss by a large factor (e.g., 1024) before backprop, then scales gradients back down before the weight update — preventing underflow. Modern frameworks (PyTorch `torch.cuda.amp`, TensorFlow) handle this automatically. Requirements: a modern GPU (NVIDIA V100, A100, or newer), and using the framework's automatic mixed precision API.

---

## Advanced

**Q7: What is gradient checkpointing and when would you use it?**

During backpropagation, you need the intermediate activations from the forward pass to compute gradients. Standard training stores ALL activations in memory, which scales linearly with model depth and batch size. For very large models, this can require hundreds of gigabytes of GPU memory. Gradient checkpointing trades memory for compute: instead of storing all activations, it only stores checkpoints at regular intervals (every k layers). During the backward pass, it recomputes the un-stored activations on-the-fly from the nearest checkpoint. This typically increases training time by ~30% (from the recomputation) but reduces memory by a factor proportional to the checkpoint interval — often reducing memory by 4–10×. Used in training very large models (GPT-3, LLaMA) that would otherwise not fit in GPU memory.

---

**Q8: What is curriculum learning and what evidence supports its effectiveness?**

Curriculum learning (Bengio et al., 2009) is the strategy of presenting training examples in a deliberate order — from easy to hard — rather than randomly. The intuition: humans learn better when material is introduced in a structured progression. For machine learning: start with clean, unambiguous examples, then progressively add harder, more ambiguous ones. Evidence of effectiveness: in NLP, training language models on shorter sequences first then longer ones improves convergence speed. In reinforcement learning, curriculum over task difficulty is often essential (random ordering fails on hard tasks). In object detection, sampling hard examples more frequently (hard negative mining) dramatically improves accuracy. The challenge: defining "difficulty" is task-specific and often requires domain knowledge.

---

**Q9: What is the difference between layer normalization and batch normalization, and why does the choice matter?**

Batch normalization (BN) normalizes across the batch dimension for each feature: for a given feature, it computes mean and variance across all samples in the batch, then normalizes. This means BN statistics depend on batch size — it behaves differently with small batches (noisy statistics) and differently at inference (uses running statistics). BN does not work well for RNNs (sequences have different lengths) or for small batch sizes. Layer normalization (LN) normalizes across the feature dimension for each sample independently: for a given sample, it computes mean and variance across all features at one position. LN statistics are independent of batch size, making it suitable for RNNs, transformers, and variable-length sequences. All modern transformer architectures (BERT, GPT) use Layer Norm. CNN architectures typically use Batch Norm because images are same-size, batches are large, and BN has a mild regularization effect from batch statistics noise.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Troubleshooting_Guide.md](./Troubleshooting_Guide.md) | Training troubleshooting guide |

⬅️ **Prev:** [11 GANs](../11_GANs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Text Preprocessing](../../05_NLP_Foundations/01_Text_Preprocessing/Theory.md)
