# GANs — Interview Q&A

## Beginner

**Q1: What is a GAN and what are its two components?**

<details>
<summary>💡 Show Answer</summary>

A GAN (Generative Adversarial Network) is a framework for training a neural network to generate realistic synthetic data. It consists of two competing networks. The **Generator** takes random noise as input and produces synthetic data (e.g., a fake image). The **Discriminator** takes any image — either real (from training data) or fake (from the generator) — and outputs a probability of it being real. The two networks are trained adversarially: the generator tries to fool the discriminator, and the discriminator tries not to be fooled. This competition drives both networks to improve.

</details>

---

**Q2: What is the training process for a GAN?**

<details>
<summary>💡 Show Answer</summary>

GAN training alternates between two steps. First, train the discriminator: sample real images from training data, generate fakes from the generator, and update the discriminator to correctly label real images as real (output near 1) and fake images as fake (output near 0). Second, train the generator: generate fakes, pass them through the discriminator (whose weights are now frozen), and update the generator to produce fakes that the discriminator labels as real. This alternation continues for thousands of iterations. Both networks improve through the competition.

</details>

---

**Q3: What is mode collapse and why is it a problem?**

<details>
<summary>💡 Show Answer</summary>

Mode collapse is when the generator learns to produce only a small subset of possible outputs — even though the real data has much more variety. For example, trained on a dataset of all digits (0–9), a GAN might collapse to only generating the digit "8" because those fakes successfully fool the discriminator. The discriminator then adapts to detect "8" fakes, and the generator might switch to only generating "3"s. The generator keeps collapsing to narrow modes rather than covering the full diversity of the data. This is a major practical problem: the generated data is high quality but not diverse, limiting usefulness for augmentation or generative tasks.

</details>

---

## Intermediate

**Q4: Why is GAN training notoriously unstable, and what causes it?**

<details>
<summary>💡 Show Answer</summary>

GAN training involves a minimax game between two networks, and the optimization landscape is non-stationary — as one network improves, the other's loss landscape changes. This leads to several instabilities. If the discriminator becomes too strong, it always outputs near 0 for generated images. The gradient `log(1 - D(G(z)))` saturates near zero — the generator gets almost no gradient and stops learning. Conversely, if the generator becomes too strong, the discriminator gets fooled consistently and D's loss saturates. Getting both networks to improve in sync is extremely sensitive to learning rates, architecture choices, and initialization.

</details>

---

**Q5: What is the Wasserstein GAN (WGAN) and how does it improve stability?**

<details>
<summary>💡 Show Answer</summary>

Vanilla GAN uses binary cross-entropy, which measures how well D classifies real vs fake. When D becomes very confident (D(real) → 1, D(fake) → 0), the gradients for G vanish — the loss saturates. Wasserstein GAN (WGAN) replaces the discriminator with a "critic" that estimates the Wasserstein distance (Earth Mover's distance) between real and generated distributions. The critic outputs raw scores (not probabilities), and the loss is simply the difference in critic scores: `E[D(real)] - E[D(fake)]`. This has the crucial property that gradients for G are almost always non-zero, even when D is much better than G. WGAN training is significantly more stable and the loss curve is more meaningful (lower = better in a consistent way).

</details>

---

**Q6: What is a conditional GAN (cGAN) and how does conditioning work?**

<details>
<summary>💡 Show Answer</summary>

A conditional GAN adds an additional input — a condition — to both the generator and discriminator. For class-conditional generation, the condition is a class label. The generator receives noise z AND a class label, and is trained to generate images of that specific class. The discriminator receives an image AND a class label, and must determine if the image genuinely belongs to that class (not just if it looks real). The generator learns to produce diverse, class-specific outputs. Example: given label "cat" → generate a cat; given "dog" → generate a dog. Conditioning can also be an image (CycleGAN — translate styles), text (text-to-image), or other modalities.

</details>

---

## Advanced

**Q7: What is the Nash equilibrium of a GAN and is it actually achieved in practice?**

<details>
<summary>💡 Show Answer</summary>

The Nash equilibrium of the GAN game is the point where: (1) the generator perfectly learns the real data distribution — G(z) is indistinguishable from real data, and (2) the discriminator can do no better than random guessing — D(x) = 0.5 for all inputs. At this point, neither network can improve unilaterally — changing G makes D better again, and vice versa. In practice, this equilibrium is extremely difficult to reach. The optimization alternates gradients rather than finding a true equilibrium, and the loss landscapes are non-convex. Models like StyleGAN come impressively close for human faces, but perfect Nash equilibria are theoretical ideals. Most practical GAN applications aim for "good enough" quality rather than true equilibrium.

</details>

---

**Q8: How do GANs compare to Variational Autoencoders (VAEs) and Diffusion Models for generation?**

<details>
<summary>💡 Show Answer</summary>

All three are generative models, but with different tradeoffs. VAEs optimize a variational lower bound on the data likelihood — they are more stable to train, provide interpretable latent spaces, but generate slightly blurrier images because the reconstruction loss directly compares pixels. GANs use adversarial training — they produce sharper, more photorealistic images but are harder to train (mode collapse, instability) and the latent space is less interpretable. Diffusion Models (DALL-E 2, Stable Diffusion) learn to reverse a gradual noising process — they produce the highest quality and most diverse images, have excellent mode coverage, and are easy to condition on text. Diffusion models have now surpassed GANs for most image generation tasks, but GANs remain faster at inference time (no iterative denoising needed).

</details>

---

**Q9: What is the training objective of StyleGAN and how does it achieve photorealistic face generation?**

<details>
<summary>💡 Show Answer</summary>

StyleGAN (Karras et al., 2018, NVIDIA) uses a progressive training strategy — starting from 4×4 resolution and gradually adding layers to reach 1024×1024. The key architectural innovation is the style-based generator: instead of feeding the latent vector z directly into the generator, z is first mapped by an 8-layer MLP to an intermediate latent space W (which has more disentangled properties). This W vector is then injected at each layer through "adaptive instance normalization" (AdaIN), controlling the style of features at each level of detail (coarse styles = pose/shape, fine styles = texture/color). This separation allows independent control of coarse and fine styles — enabling operations like "mixing the pose of person A with the texture of person B." StyleGAN2 and StyleGAN3 added further improvements (removing characteristic droplet artifacts, equivariant generator). The result is faces indistinguishable from real human photos.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | GAN architecture deep dive |

⬅️ **Prev:** [10 RNNs](../10_RNNs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [12 Training Techniques](../12_Training_Techniques/Theory.md)
