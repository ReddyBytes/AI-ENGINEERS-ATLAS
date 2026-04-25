"""
Project 1 — Data & Probability Explorer  [SOLUTION]
=====================================================
Uses the Titanic dataset to explore probability distributions,
descriptive statistics, and conditional probabilities.

Libraries required: pip install pandas numpy matplotlib
Run: python solution.py
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
    df_clean = df.dropna(subset=['Age'])  # ← keep only rows where Age is not NaN
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

    mean     = np.mean(values)   # ← sum of all values divided by count
    variance = np.var(values)    # ← average squared deviation from the mean
    std      = np.std(values)    # ← square root of variance — same units as the data

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

    count = (df[column] == value).sum()  # ← boolean mask sums to count of True values

    probability = count / total  # ← fraction of outcomes where the event occurred

    return probability


def print_marginal_probabilities(df: pd.DataFrame) -> None:
    """Print marginal probabilities for key events."""
    print("--- Marginal Probabilities ---")

    p_survived = marginal_probability(df, "Survived", 1)
    print(f"P(Survived)            = {p_survived:.4f}")

    p_female = marginal_probability(df, "Sex", "female")  # ← proportion of women on board
    print(f"P(Female)              = {p_female:.4f}")

    p_first = marginal_probability(df, "Pclass", 1)  # ← proportion in first class
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
    # Step 1 — restrict the sample space to rows matching the condition
    subset = df[df[condition_col] == condition_val]  # ← filter to the conditioning event

    # Step 2 — within that subset, what fraction has the target value?
    probability = (subset[target_col] == target_val).sum() / len(subset)  # ← P(A|B) = P(A∩B)/P(B)

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

    plt.hist(df[column], bins=30, edgecolor='black', color='steelblue')  # ← 30 bins covers the range well

    plt.title(f"Distribution of {column}")  # ← descriptive title
    plt.xlabel(column)                       # ← x-axis label matches the column name
    plt.ylabel("Count")                      # ← y-axis is frequency count

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

    # .mean() on a 0/1 column gives the proportion of 1s — i.e., survival rate
    survival_by_class = df.groupby('Pclass')['Survived'].mean()  # ← Series: index=Pclass, value=rate

    plt.figure(figsize=(7, 5))

    survival_by_class.plot(
        kind='bar',
        color='steelblue',
        edgecolor='black'
    )  # ← pandas .plot() delegates to matplotlib

    plt.title("Survival Rate by Passenger Class")
    plt.xlabel("Passenger Class")
    plt.ylabel("Survival Rate")
    plt.ylim(0, 1)       # ← fix y-axis so proportions are comparable across plots
    plt.xticks(rotation=0)  # ← horizontal tick labels are easier to read

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
