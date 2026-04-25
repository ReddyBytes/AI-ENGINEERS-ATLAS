# 🏗️ Project 1 — Architecture

## System Overview

This project is a data analysis pipeline — a linear flow from raw data to insights. There is no model training here. The purpose is to understand the data that models will eventually learn from.

---

## System Diagram

```mermaid
flowchart TD
    A[CSV File / URL\nTitanic Dataset] --> B[Load & Inspect\npandas read_csv]
    B --> C[Clean Data\nDrop missing Age rows]
    C --> D1[Descriptive Statistics\nnp.mean / np.var / np.std]
    C --> D2[Marginal Probabilities\nP-A = count-A / total]
    C --> D3[Conditional Probabilities\nP-A given B = filter then count]
    D1 --> E[Print Statistics Report]
    D2 --> E
    D3 --> E
    C --> F[Visualizations\nmatplotlib histograms + bar charts]
    F --> G[outputs/ folder\nPNG files saved to disk]
    E --> H[Terminal Output\nFormatted probability report]
```

---

## Data Flow

```mermaid
flowchart LR
    subgraph Input
        A[titanic.csv\n891 rows × 12 cols]
    end

    subgraph Processing
        B[Load DataFrame]
        C[Drop NaN rows\n714 rows remain]
        D[Extract column arrays\ne.g. Age as numpy array]
    end

    subgraph Analysis
        E[Statistics\nmean, var, std]
        F[Probabilities\nP-A and P-A given B]
    end

    subgraph Output
        G[Terminal Report]
        H[Histogram PNGs]
    end

    A --> B --> C --> D --> E --> G
    D --> F --> G
    C --> H
```

---

## Component Table

| Component | File / Library | Role | Inputs | Outputs |
|---|---|---|---|---|
| Data Loader | `pandas.read_csv()` | Fetch and parse CSV data | URL or file path | DataFrame (891 × 12) |
| Data Cleaner | `df.dropna()` | Remove rows with missing values | Raw DataFrame | Clean DataFrame (714 rows) |
| Statistics Engine | `numpy` (mean/var/std) | Compute distribution summaries | Numeric column array | 3 float values |
| Probability Calculator | Custom Python functions | Compute P(A) and P(A\|B) | DataFrame + column names | Float 0–1 |
| Visualizer | `matplotlib` | Plot distributions as images | DataFrame columns | PNG files in outputs/ |
| Report Printer | Python `print()` | Display results in terminal | Computed values | Formatted text |

---

## Key Data Structures

```mermaid
classDiagram
    class DataFrame {
        +891 rows
        +12 columns
        +Survived int
        +Pclass int
        +Sex string
        +Age float
        +Fare float
    }

    class StatisticsResult {
        +mean float
        +variance float
        +std float
    }

    class ProbabilityResult {
        +p_survived float
        +p_female float
        +p_first_class float
        +p_survived_given_class dict
        +p_survived_given_sex dict
    }

    DataFrame --> StatisticsResult : compute_statistics()
    DataFrame --> ProbabilityResult : marginal_probability()\nconditional_probability()
```

---

## Concepts Map

```mermaid
flowchart TD
    T1[Topic 5 — Probability] --> C1[marginal_probability function\nP-A = count / total]
    T1 --> C2[conditional_probability function\nP-A given B = filter + proportion]
    T2[Topic 6 — Statistics] --> C3[compute_statistics function\nmean, variance, std dev]
    T3[Topic 7 — Linear Algebra] --> C4[DataFrame shape understanding\nfeature vectors, matrix rows]
    C1 --> R[Final Report + Plots]
    C2 --> R
    C3 --> R
    C4 --> R
```

---

## Tech Stack

| Tool | Version | Why This Tool |
|---|---|---|
| `pandas` | 1.5+ | Load CSV, filter rows, groupby operations |
| `numpy` | 1.23+ | Compute statistics, array math |
| `matplotlib` | 3.6+ | Plot histograms and bar charts |

---

## Folder Structure

```
01_Data_and_Probability_Explorer/
├── src/
│   └── starter.py            ← Main Python script
├── outputs/
│   ├── age_distribution.png
│   ├── fare_distribution.png
│   └── survival_by_class.png
├── 01_MISSION.md
├── 02_ARCHITECTURE.md
├── 03_GUIDE.md
└── 04_RECAP.md
```

---

## Why This Architecture?

This project uses a functional, single-file architecture by design. Each concept gets its own function:

- `compute_statistics()` — isolates the statistics concept
- `marginal_probability()` — isolates P(A)
- `conditional_probability()` — isolates P(A|B)

This makes it easy to test each piece independently and swap in different datasets. As you move to more complex projects, these functions will be replaced by classes and modules — but the same logic applies.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Context and objectives |
| 📄 **02_ARCHITECTURE.md** | You are here |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [📄 src/starter.py](./src/starter.py) | Starter code with TODOs |
| [📄 04_RECAP.md](./04_RECAP.md) | Concepts recap and next steps |

➡️ **Next Project:** [02 — ML Model Comparison](../02_ML_Model_Comparison/01_MISSION.md)
