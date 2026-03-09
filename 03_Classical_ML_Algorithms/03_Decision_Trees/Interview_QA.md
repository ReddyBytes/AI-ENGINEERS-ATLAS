# Decision Trees — Interview Q&A

## Beginner Level

**Q1: How does a decision tree make a prediction?**

A: A decision tree traverses a series of if/else rules from the root to a leaf. You start at the root node — the first question (e.g., "Is heart_rate > 100?"). Depending on the answer, you follow the yes or no branch to the next node. This continues until you reach a leaf node, which contains the final prediction — a class label or a numeric value. Every prediction follows one path through the tree. The path taken is determined entirely by the input feature values.

**Q2: What is Gini impurity and how does the tree use it to choose splits?**

A: Gini impurity measures how mixed the classes are in a node. If a node contains only one class, Gini = 0 (perfectly pure). If it contains equal proportions of all classes, Gini is at its maximum (0.5 for binary classification). When choosing a split, the tree evaluates every possible threshold on every feature. It picks the split that reduces the weighted average Gini impurity across the resulting child nodes the most. This "information gain" from the split tells the tree how much more organized the data becomes after asking that question. The goal is to ask the most clarifying question first.

**Q3: What is overfitting in a decision tree and how do you prevent it?**

A: Without constraints, a decision tree will grow until it creates a separate leaf for every training example. It achieves 100% training accuracy by memorizing every data point — but then fails on any new data because it learned noise and specific examples rather than generalizable patterns. The main prevention is max_depth — limiting how many levels of questions the tree can ask. Other constraints include min_samples_leaf (require at least N examples in every leaf) and min_samples_split (require at least N examples before splitting a node). These constraints force the tree to find patterns that hold for groups of examples, not just individual ones.

---

## Intermediate Level

**Q4: What is the difference between Gini impurity and entropy as splitting criteria?**

A: Both measure how mixed a node is, and both lead to very similar trees in practice. Gini impurity (used by sklearn by default) is computationally slightly faster because it avoids logarithm calculations. Entropy (from information theory) measures the average information content: -Σ p×log₂(p). Entropy is slightly more sensitive to class imbalance — it penalizes impure nodes a bit more heavily. In practice, the difference in tree quality between the two is minimal. Most practitioners use Gini unless they have a specific reason to prefer entropy. The bigger impact on tree quality comes from hyperparameter tuning (max_depth, min_samples_leaf) than from the choice of criterion.

**Q5: How does feature importance work in decision trees?**

A: Feature importance is calculated as the total impurity reduction that each feature is responsible for across all splits in the tree, weighted by the number of samples at each node. A feature used near the root on a large portion of the data gets a higher importance score. Feature importances sum to 1. High importance means the tree found that feature very useful for making pure splits. Feature importance from decision trees is computationally cheap and gives useful signal about which features drive predictions. However, it can be misleading with correlated features — if two features carry the same information, their importance is split arbitrarily between them.

**Q6: What is pruning in decision trees and when is it useful?**

A: Pruning is the process of removing sections of a tree that provide little predictive power. Pre-pruning (early stopping) stops the tree from growing when splits do not meet a threshold of improvement — controlled by parameters like min_impurity_decrease in sklearn. Post-pruning (cost-complexity pruning) grows the full tree first, then removes nodes that add little benefit while penalizing tree size — controlled by the ccp_alpha parameter in sklearn. Post-pruning can sometimes produce better-generalized trees than pre-pruning because it can "see" the full tree before deciding what to remove. In practice, most people use max_depth and min_samples_leaf for simplicity.

---

## Advanced Level

**Q7: Why do decision trees struggle with certain types of patterns?**

A: Decision trees make axis-aligned splits — each split divides the feature space with a horizontal or vertical line. This makes them inefficient at representing diagonal decision boundaries. For example, if two classes are separated by the line "x₁ + x₂ > 5", a decision tree needs many splits to approximate this diagonal line. Each split divides parallel to one axis. More splits mean deeper trees and higher overfitting risk. In contrast, logistic regression captures that diagonal in a single linear equation. Decision trees are also poor at extrapolation — they cannot predict values outside the range seen in training data because predictions are always averages of training examples in leaf nodes.

**Q8: How is a decision tree for regression different from one for classification?**

A: The structure and splitting process are the same, but the splitting criterion and leaf output differ. For regression, the tree minimizes variance rather than Gini/entropy. It finds the split that minimizes the weighted sum of variance in the child nodes. The leaf output is the mean of all training examples that reach that leaf. The prediction for a new example is whatever mean value is stored in its leaf. A key consequence: regression trees cannot extrapolate beyond the training data range. If all training houses cost between $100k and $500k, the tree will never predict $600k — its predictions are always averages of seen values.

**Q9: What are CART, ID3, and C4.5, and how do they differ?**

A: These are different algorithms for building decision trees. ID3 (Iterative Dichotomiser 3) uses information gain with entropy as the criterion, but only works on categorical features and cannot handle continuous values directly. C4.5 (successor to ID3) adds support for continuous features through threshold-based splits, handles missing values, and uses gain ratio (normalizes information gain to account for features with many unique values). CART (Classification and Regression Trees) builds binary trees (each split always creates exactly two children), handles both categorical and continuous features, supports both classification (Gini) and regression (variance), and is the algorithm used in sklearn. CART is the standard in practice. The differences matter mainly for academic contexts or when working with legacy systems.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Logistic Regression](../02_Logistic_Regression/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Random Forests](../04_Random_Forests/Theory.md)
