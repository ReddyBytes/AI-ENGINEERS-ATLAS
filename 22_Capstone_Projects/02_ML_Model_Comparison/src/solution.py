"""
Project 2 — ML Model Comparison  [SOLUTION]
============================================
Trains 4 classifiers on the Iris dataset, evaluates them
with standard metrics, checks for overfitting, and plots
a confusion matrix for the best model.

Libraries required: pip install scikit-learn matplotlib pandas numpy
Run: python solution.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, ConfusionMatrixDisplay
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB


# ============================================================
# SECTION 1 — LOAD AND SPLIT DATA
# ============================================================

def load_and_split(test_size: float = 0.2, random_state: int = 42):
    """
    Load the Iris dataset and split into train/test sets.

    Returns:
        X_train, X_test, y_train, y_test, class_names
    """
    iris = load_iris()
    X = iris.data    # ← feature matrix: shape (150, 4)
    y = iris.target  # ← labels: 0, 1, or 2 (one per class)
    class_names = iris.target_names

    print(f"Dataset: {len(X)} samples, {X.shape[1]} features, {len(class_names)} classes")

    # stratify=y ensures each class has the same proportion in train and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y   # ← prevents all of one class ending up in one split
    )

    print(f"Train size: {len(X_train)}  |  Test size: {len(X_test)}\n")
    return X_train, X_test, y_train, y_test, class_names


# ============================================================
# SECTION 2 — DEFINE AND TRAIN MODELS
# ============================================================

def get_models() -> dict:
    """
    Return a dictionary of model name -> sklearn model instance.
    Models are initialized but NOT yet trained.
    """
    models = {
        "Logistic Regression": LogisticRegression(max_iter=200, random_state=42),
        # max_iter=200 gives the solver enough iterations to converge on Iris
        "Decision Tree":        DecisionTreeClassifier(random_state=42),
        # random_state controls tie-breaking in splits
        "Random Forest":        RandomForestClassifier(n_estimators=100, random_state=42),
        # n_estimators=100 = 100 trees in the ensemble
        "Naive Bayes":          GaussianNB(),
        # GaussianNB has no random_state — it's fully deterministic
    }
    return models


def train_all_models(models: dict, X_train, y_train) -> None:
    """Train every model in the dict on the training data. Modifies in place."""
    for name, model in models.items():
        model.fit(X_train, y_train)  # ← .fit() learns the parameters from training data
        print(f"Trained: {name}")


# ============================================================
# SECTION 3 — EVALUATE MODELS
# ============================================================

def evaluate_model(model, X_test, y_test) -> dict:
    """
    Evaluate a trained model on the test set.
    Returns a dict with keys: Accuracy, Precision, Recall, F1
    """
    y_pred = model.predict(X_test)  # ← generates hard class labels (0, 1, or 2)

    accuracy  = accuracy_score(y_test, y_pred)
    # ← fraction of all predictions that are correct

    precision = precision_score(y_test, y_pred, average='weighted')
    # ← weighted: averages per-class precision, weighted by class frequency

    recall    = recall_score(y_test, y_pred, average='weighted')
    # ← weighted average of per-class recall (sensitivity)

    f1        = f1_score(y_test, y_pred, average='weighted')
    # ← harmonic mean of precision and recall — penalizes imbalance between them

    return {
        "Accuracy":  accuracy,
        "Precision": precision,
        "Recall":    recall,
        "F1":        f1,
    }


def build_comparison_table(models: dict, X_test, y_test) -> pd.DataFrame:
    """Evaluate all models and return a DataFrame with one row per model."""
    rows = []
    for name, model in models.items():
        metrics = evaluate_model(model, X_test, y_test)
        row = {"Model": name}
        row.update(metrics)
        rows.append(row)
    return pd.DataFrame(rows)


# ============================================================
# SECTION 4 — OVERFITTING CHECK
# ============================================================

def check_overfitting(models: dict, X_train, y_train, X_test, y_test) -> None:
    """
    Print train accuracy, test accuracy, and gap for each model.
    Flag models with gap > 0.05 as potential overfits.
    """
    print("--- Train vs Test Accuracy (Overfitting Check) ---")
    for name, model in models.items():
        train_acc = model.score(X_train, y_train)  # ← .score() returns accuracy directly
        test_acc  = model.score(X_test, y_test)    # ← same method on held-out data

        gap = train_acc - test_acc  # ← large gap = model memorized training data

        flag = " <- possible overfit!" if gap > 0.05 else ""  # ← 5% threshold is a common heuristic

        print(f"{name:25s}  train={train_acc:.4f}  test={test_acc:.4f}  gap={gap:+.4f}{flag}")
    print()


# ============================================================
# SECTION 5 — CONFUSION MATRIX
# ============================================================

def plot_confusion_matrix(model, X_test, y_test,
                           class_names, model_name: str,
                           output_dir: str) -> None:
    """Plot and save the confusion matrix for the given model."""
    os.makedirs(output_dir, exist_ok=True)

    y_pred = model.predict(X_test)  # ← predicted labels for all test samples

    # 3x3 matrix: rows = true class, cols = predicted class
    # diagonal = correct predictions, off-diagonal = errors
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, cmap='Blues', colorbar=False)  # ← Blues colormap: darker = more predictions
    ax.set_title(f'Confusion Matrix — {model_name}')
    plt.tight_layout()

    filepath = os.path.join(output_dir, "confusion_matrix.png")
    plt.savefig(filepath)
    plt.close()
    print(f"Confusion matrix saved to: {filepath}")


# ============================================================
# SECTION 6 — FIND BEST MODEL AND REPORT
# ============================================================

def find_best_model(df_results: pd.DataFrame) -> str:
    """Return the model name with the highest F1 score."""
    best_name = df_results.loc[df_results['F1'].idxmax(), 'Model']
    # ← idxmax() returns the row index where F1 is largest; we then look up its 'Model' value
    return best_name


def print_final_report(df_results: pd.DataFrame, best_model_name: str) -> None:
    """Print the comparison table and a recommendation."""
    print("--- Model Comparison ---")
    formatted = df_results.copy()
    for col in ["Accuracy", "Precision", "Recall", "F1"]:
        formatted[col] = formatted[col].map(lambda x: f"{x:.4f}")
    print(formatted.to_string(index=False))
    print()
    print(f"Recommendation: Use '{best_model_name}'")
    print("Reason: Highest F1 score — balances precision and recall across all 3 classes.")


# ============================================================
# MAIN — Wire everything together
# ============================================================

def main():
    print("=" * 55)
    print("  ML Model Comparison — Iris Dataset")
    print("=" * 55)
    print()

    # Stage 1 — Load data
    X_train, X_test, y_train, y_test, class_names = load_and_split()

    # Stage 2 — Build and train models
    models = get_models()
    train_all_models(models, X_train, y_train)
    print()

    # Stage 3 — Evaluate
    df_results = build_comparison_table(models, X_test, y_test)

    # Stage 4 — Overfitting check
    check_overfitting(models, X_train, y_train, X_test, y_test)

    # Stage 5 — Find best and plot confusion matrix
    best_name = find_best_model(df_results)
    plot_confusion_matrix(
        models[best_name], X_test, y_test,
        class_names, best_name, output_dir="outputs"
    )

    # Stage 6 — Report
    print()
    print_final_report(df_results, best_name)
    print("\nDone!")


if __name__ == "__main__":
    main()
