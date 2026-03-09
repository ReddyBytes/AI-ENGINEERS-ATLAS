# GANs — Cheatsheet

**One-liner:** A GAN is a framework where a Generator creates synthetic data and a Discriminator distinguishes real from fake — trained adversarially until generated data is indistinguishable from real data.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Generator (G) | Network that creates fake data from random noise |
| Discriminator (D) | Network that classifies input as real or fake |
| Latent vector (z) | Random noise input to the generator — the seed of creativity |
| Latent space | The space of all possible noise inputs — "directions" correspond to different outputs |
| Adversarial training | G and D trained against each other, each improving because of the other |
| Nash equilibrium | Theoretical ideal: G generates perfectly real data, D guesses randomly |
| Mode collapse | Generator gets stuck producing only one type of output |
| Real distribution p_data | The distribution of real training data |
| Generated distribution p_g | The distribution of data the generator produces |
| Wasserstein distance | A better measure of distribution distance than cross-entropy |

---

## GAN Loss Functions

```
Standard GAN (Goodfellow et al., 2014):
  D loss = -[log(D(x_real)) + log(1 - D(G(z)))]    ← maximize detection
  G loss = -log(D(G(z)))                             ← maximize fooling

WGAN (Wasserstein GAN):
  D loss = -[D(x_real) - D(G(z))]    ← D is called "critic" here
  G loss = -D(G(z))
  Constraint: D must be 1-Lipschitz (enforced by weight clipping or gradient penalty)
```

WGAN gives more stable training and meaningful loss curves.

---

## Training Loop (One Iteration)

```
For each training step:

  1. Sample real images x from training data
  2. Sample noise z from N(0, 1)
  3. Generate fakes: x_fake = G(z)

  4. Train Discriminator:
       D_loss = loss(D(x_real), label=1) + loss(D(x_fake), label=0)
       Update D weights (G weights frozen)

  5. Train Generator:
       G_loss = loss(D(x_fake), label=1)  ← G wants D to say "real"
       Update G weights (D weights frozen)
```

---

## GAN Variants

| Model | Key Idea | Best For |
|-------|---------|----------|
| Vanilla GAN | Original formulation | Understanding, simple data |
| DCGAN | Conv/deconv layers in G and D | Image generation |
| cGAN | Conditioning on a label | Class-conditional generation |
| CycleGAN | Unpaired image-to-image translation | Photo → painting, season transfer |
| WGAN | Wasserstein loss, training stability | Most image tasks |
| StyleGAN | Style-based generator, progressive growing | Ultra-high-resolution face generation |
| BigGAN | Large-scale class-conditional | High-quality ImageNet images |

---

## When to Use / Not Use

| Use GANs when... | Consider alternatives when... |
|------------------|-------------------------------|
| You need photorealistic generated images | You need stable training (VAEs are easier) |
| Data augmentation for rare classes | You need interpretable latent space (use VAE) |
| Image-to-image translation | Text generation (use language models) |
| Super-resolution | You need mode coverage (Diffusion models are better) |

---

## Golden Rules

1. Train D and G in alternating steps — never train one to convergence before updating the other.
2. If D is too strong early on, G gets zero gradient (D(G(z)) ≈ 0, log(0) gradient saturates). Balance them.
3. Mode collapse is the most common training failure — monitor diversity of generated samples.
4. WGAN is almost always more stable than vanilla GAN — use it by default.
5. Learning rate for D is often set slightly lower than G to prevent D from dominating.
6. Check both G loss and D loss. If D_loss → 0: D is dominating. If G_loss → 0: G is winning (mode collapse risk).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | GAN architecture deep dive |

⬅️ **Prev:** [10 RNNs](../10_RNNs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [12 Training Techniques](../12_Training_Techniques/Theory.md)
