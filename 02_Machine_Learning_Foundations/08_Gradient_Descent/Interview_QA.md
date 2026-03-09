# Gradient Descent — Interview Q&A

## Beginner Level

**Q1: What is gradient descent and what problem does it solve?**

A: Gradient descent is the optimization algorithm used to train machine learning models. The problem it solves: finding the values for a model's parameters (weights) that minimize the loss — the measure of how wrong the model is. Since modern models can have billions of parameters, there is no formula to solve for the optimal weights directly. Gradient descent is a practical iterative approach: repeatedly take small steps in the direction that reduces the loss, until the loss is low enough. It is the engine inside virtually every ML training loop.

**Q2: What is the learning rate and why does its value matter?**

A: The learning rate controls how big each step is when updating the model's weights. If it is too large, the model overshoots the minimum — the loss bounces around or even explodes higher with each update. If it is too small, training takes an extremely long time because each step barely moves the weights. The right learning rate leads to steady, smooth convergence. In practice you start with a reasonable default (1e-3 or 1e-4), watch the loss curve, and adjust. A rising loss usually means the learning rate is too high.

**Q3: What is the difference between batch gradient descent and stochastic gradient descent?**

A: Batch gradient descent computes the gradient using the entire training dataset before making one weight update. It is accurate but very slow when the dataset is large. Stochastic gradient descent (SGD) computes the gradient and updates weights after each individual training example. It is fast but noisy — the loss jumps around because each example gives a different gradient estimate. Mini-batch gradient descent is the practical middle ground used in almost all modern deep learning: process a small batch (32 or 128 examples), compute the gradient, update weights. It gets most of the speed benefits of SGD with much more stable convergence.

---

## Intermediate Level

**Q4: What is the problem of getting stuck in a local minimum and how does mini-batch SGD help?**

A: A local minimum is a point on the loss surface where the gradient is zero but it is not the globally lowest point. Pure gradient descent can get stuck here — from that point, every direction looks uphill so training stops. Mini-batch SGD helps because the noise from using different random batches each step means the gradient estimate varies. This noise can "kick" the optimizer out of shallow local minima and saddle points. In high-dimensional spaces (neural networks with billions of parameters), most "flat" regions are actually saddle points rather than true local minima, and the noise in mini-batch SGD is particularly helpful for escaping them.

**Q5: What are adaptive learning rate optimizers like Adam and why are they preferred?**

A: Basic gradient descent uses the same learning rate for every parameter. Adam (Adaptive Moment Estimation) maintains a separate, adaptive learning rate for each parameter, based on recent gradient history. Parameters with consistently large gradients get a smaller effective learning rate; parameters with small or sparse gradients get a larger effective learning rate. Adam also uses momentum — it accumulates a velocity vector in the direction of consistent gradients, helping it move faster through flat regions and reducing oscillation. In practice Adam converges much faster than plain SGD with a fixed learning rate and requires much less learning rate tuning.

**Q6: What does "vanishing gradient" mean and when does it occur?**

A: Vanishing gradients occur in deep neural networks when gradients become extremely small as they propagate backward through many layers. During backpropagation, gradients are multiplied layer by layer. If each multiplication makes the gradient slightly smaller (which happens with sigmoid activations, for example), after 20 layers the gradient reaching the early layers is effectively zero. Those early layers learn almost nothing. The weights stay close to random initialization. This severely limits how deep a network can be trained effectively. Solutions include using ReLU activations (which do not squash gradients), batch normalization, residual connections (skip connections in ResNets), and gradient clipping.

---

## Advanced Level

**Q7: What is the difference between first-order and second-order optimization methods?**

A: First-order methods (gradient descent, Adam, SGD) use only the gradient — the first derivative of the loss. They tell you which direction is downhill but not how curved the loss surface is. Second-order methods (like Newton's method and L-BFGS) also use the Hessian — the second derivative, which describes curvature. Knowing the curvature lets you take much more accurate steps and potentially converge faster. The problem: computing the Hessian for a model with millions of parameters is computationally infeasible. Quasi-Newton methods approximate the Hessian. In practice, first-order methods like Adam are standard for deep learning due to scale. L-BFGS is useful for smaller problems where the Hessian approximation is tractable.

**Q8: What is learning rate scheduling and what strategies exist?**

A: Learning rate scheduling changes the learning rate over the course of training rather than keeping it fixed. Common strategies: step decay (reduce learning rate by a factor every N epochs), exponential decay (learning rate decreases exponentially each epoch), cosine annealing (learning rate follows a cosine curve from high to near-zero, then resets — can find better minima by periodically letting the optimizer explore), warm-up (start with a very small learning rate for the first few epochs, then ramp up — prevents large early updates on randomly initialized weights), and reduce-on-plateau (reduce learning rate when validation loss stops improving). Scheduling often provides better final performance than any fixed learning rate.

**Q9: How does gradient clipping work and when should you use it?**

A: Gradient clipping caps the magnitude of gradients before applying them to weights. There are two types: value clipping (clip each gradient element to a maximum value) and norm clipping (scale down the entire gradient vector if its L2 norm exceeds a threshold — more common). It is most important when training recurrent neural networks (LSTMs, GRUs) on long sequences, where gradients can explode due to repeated multiplications through many time steps. A typical norm clip value is 1.0. You should use it when you see loss spikes during training, NaN losses, or weights growing to very large magnitudes. For most modern architectures with batch normalization, gradient clipping is less critical but still a good safety net.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [07 Feature Engineering](../07_Feature_Engineering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Loss Functions](../09_Loss_Functions/Theory.md)
