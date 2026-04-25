"""
Project 2 — ML Model Comparison
=================================
Trains 4 classifiers on the Iris dataset, evaluates them
with standard metrics, checks for overfitting, and plots
a confusion matrix for the best model.

Libraries required: pip install scikit-learn matplotlib pandas numpy
Run: python starter.py
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

    # TODO: Split the data using train_test_split()
    # Use the test_size and random_state parameters passed to this function.
    # Set stratify=y to keep class proportions equal in both train and test sets.
    # Hint: X_train, X_test, y_train, y_test = train_test_split(X, y, ...)
    X_train, X_test, y_train, y_test = None, None, None, None  # TODO: replace

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
    # TODO: Fill in the four models below.
    # LogisticRegression(max_iter=200, random_state=42)
    # DecisionTreeClassifier(random_state=42)
    # RandomForestClassifier(n_estimators=100, random_state=42)
    # GaussianNB()
    models = {
        "Logistic Regression": None,  # TODO: LogisticRegression(...)
        "Decision Tree":        None,  # TODO: DecisionTreeClassifier(...)
        "Random Forest":        None,  # TODO: RandomForestClassifier(...)
        "Naive Bayes":          None,  # TODO: GaussianNB()
    }
    return models


def train_all_models(models: dict, X_train, y_train) -> None:
    """Train every model in the dict on the training data. Modifies in place."""
    for name, model in models.items():
        # TODO: Call model.fit(X_train, y_train) to train the model
        # TODO: Print f"Trained: {name}"
        pass  # TODO: replace


# ============================================================
# SECTION 3 — EVALUATE MODELS
# ============================================================

def evaluate_model(model, X_test, y_test) -> dict:
    """
    Evaluate a trained model on the test set.
    Returns a dict with keys: Accuracy, Precision, Recall, F1
    """
    # TODO: Call model.predict(X_test) to get predictions
    y_pred = None  # TODO: replace

    # TODO: Compute all 4 metrics using the sklearn functions imported above.
    # For precision_score, recall_score, f1_score: use average='weighted'
    # (required for multi-class classification)
    accuracy  = None  # TODO: accuracy_score(y_test, y_pred)
    precision = None  # TODO: precision_score(y_test, y_pred, average='weighted')
    recall    = None  # TODO: recall_score(...)
    f1        = None  # TODO: f1_score(...)

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
        # TODO: model.score(X_train, y_train) returns train accuracy
        train_acc = None  # TODO: replace

        # TODO: model.score(X_test, y_test) returns test accuracy
        test_acc = None  # TODO: replace

        gap = train_acc - test_acc  # ← large gap = model memorized training data

        # TODO: Build a flag string: " <- possible overfit!" if gap > 0.05 else ""
        flag = None  # TODO: replace

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

    # TODO: Call model.predict(X_test) to get predictions
    y_pred = None  # TODO: replace

    # TODO: Use confusion_matrix(y_test, y_pred) to compute the CM
    # A 3x3 matrix for 3 Iris classes: rows=actual, cols=predicted
    cm = None  # TODO: replace

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
    # TODO: Find the row in df_results where F1 is maximum
    # Hint: df_results.loc[df_results['F1'].idxmax(), 'Model']
    best_name = None  # TODO: replace
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
