"""
Project 1 — Data & Probability Explorer
========================================
Uses the Titanic dataset to explore probability distributions,
descriptive statistics, and conditional probabilities.

Libraries required: pip install pandas numpy matplotlib
Run: python starter.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


# ============================================================
# SECTION 1 — LOAD AND INSPECT THE DATA
# ============================================================

def load_data(url: str) -> pd.DataFrame:
    """Load the Titanic CSV from a URL or local path."""
    print("Loading dataset...")
    df = pd.read_csv(url)  # ← pandas reads CSVs directly from a URL
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}\n")
    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Print a quick inspection of the dataset."""
    print("--- First 5 rows ---")
    print(df.head())
    print("\n--- Data types ---")
    print(df.dtypes)
    print("\n--- Missing values ---")
    print(df.isnull().sum())  # ← counts NaN per column — check Age!
    print()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing Age values for this project."""
    # TODO: Use df.dropna(subset=['Age']) to keep only rows with a valid Age value.
    # Store the result in df_clean and return it.
    df_clean = None  # TODO: replace this line
    print(f"After cleaning: {df_clean.shape[0]} rows remain\n")
    return df_clean


# ============================================================
# SECTION 2 — DESCRIPTIVE STATISTICS
# ============================================================

def compute_statistics(df: pd.DataFrame, column: str) -> dict:
    """
    Compute mean, variance, and standard deviation for a numeric column.
    Returns a dict with keys: 'mean', 'variance', 'std'
    """
    values = df[column].values  # ← .values converts a pandas Series to a numpy array

    # TODO: Compute the mean using np.mean()
    mean = None  # TODO: replace this line

    # TODO: Compute the variance using np.var()
    variance = None  # TODO: replace this line

    # TODO: Compute the standard deviation using np.std()
    std = None  # TODO: replace this line

    return {"mean": mean, "variance": variance, "std": std}


def print_statistics(df: pd.DataFrame) -> None:
    """Print descriptive statistics for Age and Fare."""
    print("--- Descriptive Statistics ---")
    for col in ["Age", "Fare"]:
        stats = compute_statistics(df, col)
        print(f"{col:8s}: mean={stats['mean']:.2f}, "
              f"variance={stats['variance']:.2f}, "
              f"std={stats['std']:.2f}")
    print()


# ============================================================
# SECTION 3 — MARGINAL PROBABILITIES
# ============================================================

def marginal_probability(df: pd.DataFrame, column: str, value) -> float:
    """
    Calculate P(column == value) from the dataframe.

    P(A) = count(rows where A is true) / total rows

    Args:
        df:     the dataset
        column: the column name to check
        value:  the value we want the probability of

    Returns:
        float: probability between 0 and 1
    """
    total = len(df)  # ← total number of rows = total outcomes in sample space

    # TODO: Count how many rows have df[column] == value
    # Hint: (df[column] == value).sum() gives you the count
    count = None  # TODO: replace this line

    # TODO: Divide count by total to get the probability
    probability = None  # TODO: replace this line

    return probability


def print_marginal_probabilities(df: pd.DataFrame) -> None:
    """Print marginal probabilities for key events."""
    print("--- Marginal Probabilities ---")

    p_survived = marginal_probability(df, "Survived", 1)
    print(f"P(Survived)            = {p_survived:.4f}")

    # TODO: Call marginal_probability for Sex='female'
    p_female = None  # TODO: replace this line
    print(f"P(Female)              = {p_female:.4f}")

    # TODO: Call marginal_probability for Pclass=1
    p_first = None  # TODO: replace this line
    print(f"P(Pclass=1)            = {p_first:.4f}")
    print()


# ============================================================
# SECTION 4 — CONDITIONAL PROBABILITIES
# ============================================================

def conditional_probability(df: pd.DataFrame,
                             target_col: str,
                             target_val,
                             condition_col: str,
                             condition_val) -> float:
    """
    Calculate P(target_col == target_val | condition_col == condition_val).

    Reads as: "given that condition_col equals condition_val,
               what fraction of those rows have target_col == target_val?"

    Args:
        df:            the full dataset
        target_col:    the column we want the probability of
        target_val:    the value we are checking in target_col
        condition_col: the column we are conditioning on
        condition_val: filter condition_col to this value first

    Returns:
        float: conditional probability between 0 and 1
    """
    # TODO: Step 1 — filter df to only rows where condition_col == condition_val
    # Hint: subset = df[df[condition_col] == condition_val]
    subset = None  # TODO: replace this line

    # TODO: Step 2 — within that subset, calculate P(target_col == target_val)
    # Hint: (subset[target_col] == target_val).sum() / len(subset)
    probability = None  # TODO: replace this line

    return probability


def print_conditional_probabilities(df: pd.DataFrame) -> None:
    """Print conditional survival probabilities by class and sex."""
    print("--- Conditional Probabilities ---")

    for pclass in [1, 2, 3]:
        p = conditional_probability(df, "Survived", 1, "Pclass", pclass)
        print(f"P(Survived | Pclass={pclass}) = {p:.4f}")

    print()

    for sex in ["female", "male"]:
        p = conditional_probability(df, "Survived", 1, "Sex", sex)
        label = "Female" if sex == "female" else "Male  "
        print(f"P(Survived | {label})   = {p:.4f}")
    print()


# ============================================================
# SECTION 5 — VISUALIZATIONS
# ============================================================

def plot_histogram(df: pd.DataFrame, column: str, output_dir: str) -> None:
    """
    Plot a histogram of the given column and save it as a PNG.

    Args:
        df:         the dataset
        column:     column to plot (e.g. 'Age')
        output_dir: folder where the PNG will be saved
    """
    os.makedirs(output_dir, exist_ok=True)  # ← create folder if it does not exist

    plt.figure(figsize=(8, 5))

    # TODO: Use plt.hist() to plot the histogram of df[column]
    # Hint: plt.hist(df[column], bins=30, edgecolor='black', color='steelblue')

    # TODO: Add a title with plt.title(), x-label with plt.xlabel(), y-label with plt.ylabel()

    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    filename = f"{column.lower()}_distribution.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)  # ← saves the figure to disk — no GUI popup
    plt.close()
    print(f"Saved: {filepath}")


def plot_survival_by_class(df: pd.DataFrame, output_dir: str) -> None:
    """Plot a bar chart of survival rate by passenger class and save it."""
    os.makedirs(output_dir, exist_ok=True)

    # TODO: Use df.groupby('Pclass')['Survived'].mean() to get survival rate per class
    # .mean() works here because Survived is 0/1 — mean equals the proportion
    survival_by_class = None  # TODO: replace this line

    plt.figure(figsize=(7, 5))

    # TODO: Call survival_by_class.plot(kind='bar', ...) to create the bar chart
    # TODO: Add title, xlabel ('Passenger Class'), ylabel ('Survival Rate')
    # TODO: Set plt.ylim(0, 1) so the y-axis goes from 0 to 1
    # TODO: Set plt.xticks(rotation=0) so class labels are horizontal

    plt.tight_layout()
    filepath = os.path.join(output_dir, "survival_by_class.png")
    plt.savefig(filepath)
    plt.close()
    print(f"Saved: {filepath}")


# ============================================================
# MAIN — Wire everything together
# ============================================================

def main():
    print("=" * 50)
    print("  Titanic Dataset — Probability Explorer")
    print("=" * 50)
    print()

    url = "https://raw.githubusercontent.com/datasciencedboys/datasets/master/titanic.csv"

    # Load and clean
    df = load_data(url)
    inspect_data(df)
    df = clean_data(df)

    # Statistics
    print_statistics(df)

    # Probabilities
    print_marginal_probabilities(df)
    print_conditional_probabilities(df)

    # Plots
    print("--- Generating plots ---")
    plot_histogram(df, "Age", "outputs")
    plot_histogram(df, "Fare", "outputs")
    plot_survival_by_class(df, "outputs")

    print("\nDone! Check the outputs/ folder for your plots.")


if __name__ == "__main__":
    main()
