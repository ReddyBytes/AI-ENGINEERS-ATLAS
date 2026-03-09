# Supervised Learning — Code Example

## Training a Decision Tree on the Iris Dataset

The Iris dataset is the classic "hello world" of machine learning. It has measurements of 150 flowers (features) and the species name for each flower (labels). We will train a model to predict species from measurements.

```python
# ============================================================
# SUPERVISED LEARNING — IRIS CLASSIFICATION
# Goal: Train a model to predict flower species from measurements
# ============================================================

from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ============================================================
# STEP 1: LOAD THE DATA
# The Iris dataset has 150 flowers, each with 4 measurements
# ============================================================

iris = load_iris()

# X = features (the inputs — what the model will look at)
# Each row is one flower, each column is one measurement:
#   column 0: sepal length (cm)
#   column 1: sepal width (cm)
#   column 2: petal length (cm)
#   column 3: petal width (cm)
X = iris.data
print(f"Features shape: {X.shape}")  # (150, 4) = 150 flowers, 4 features each

# y = labels (the correct answers — what we want the model to predict)
# 0 = setosa, 1 = versicolor, 2 = virginica
y = iris.target
print(f"Labels shape: {y.shape}")    # (150,) = one label per flower
print(f"Label values: {set(y)}")     # {0, 1, 2}

# ============================================================
# STEP 2: SPLIT INTO TRAINING SET AND TEST SET
# We hold out 20% of data to evaluate the model later.
# The model will NEVER see test data during training.
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,      # 20% goes to test, 80% to train
    random_state=42     # fixes the random split so results are reproducible
)

print(f"Training examples: {len(X_train)}")  # 120 flowers
print(f"Test examples:     {len(X_test)}")   # 30 flowers

# ============================================================
# STEP 3: CREATE AND TRAIN THE MODEL
# A Decision Tree learns a series of if/else rules from the data.
# "fit" = train = show the model examples and let it learn
# ============================================================

model = DecisionTreeClassifier(
    max_depth=3,    # limit tree depth to avoid memorizing the data
    random_state=42
)

# Training happens here — the model studies X_train and y_train
model.fit(X_train, y_train)

print("Model trained!")

# ============================================================
# STEP 4: MAKE PREDICTIONS ON THE TEST SET
# predict() runs inference — model only sees features, not labels
# It outputs its best guess for the species of each test flower
# ============================================================

y_pred = model.predict(X_test)

print(f"First 10 predictions:    {y_pred[:10]}")
print(f"First 10 actual labels:  {y_test[:10]}")

# ============================================================
# STEP 5: EVALUATE — HOW ACCURATE IS THE MODEL?
# Compare predictions to the real labels we held out
# ============================================================

accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.2%}")  # typically ~95-97% on this dataset

# ============================================================
# BONUS: MAKE A PREDICTION ON A SINGLE NEW FLOWER
# This is what real inference looks like — one example at a time
# ============================================================

# A flower with: sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2
new_flower = [[5.1, 3.5, 1.4, 0.2]]
prediction = model.predict(new_flower)
species_names = iris.target_names  # ['setosa', 'versicolor', 'virginica']
print(f"\nNew flower prediction: {species_names[prediction[0]]}")  # setosa
```

---

## What This Shows

- **X = features, y = labels** — this is the fundamental structure of every supervised learning problem. Features are inputs; labels are correct answers.

- **train_test_split** — splits data so the model trains on one part and is evaluated on a completely separate part. This simulates real-world conditions where the model faces unseen data.

- **model.fit(X_train, y_train)** — this one line does all the learning. The decision tree builds its if/else rules by studying the labeled examples.

- **model.predict(X_test)** — this is inference. The model is now frozen and just applies what it learned. No labels needed here.

- **accuracy_score** — compares predictions to true labels on the test set. ~95% means the model gets 95 out of 100 flowers right on data it never saw during training.

The entire workflow — load data, split, train, predict, evaluate — is the same for virtually every supervised learning project, regardless of the algorithm or dataset size.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [02 Training vs Inference](../02_Training_vs_Inference/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md)
