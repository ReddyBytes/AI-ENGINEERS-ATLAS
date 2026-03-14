# Project 1 — Architecture Blueprint

## System Overview

This project is a **data analysis pipeline** — a linear flow from raw data to insights. There's no model training here. The purpose is to understand the data that models will eventually learn from.

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
| Data Cleaner | `df.dropna()` | Remove rows with missing values | Raw DataFrame | Clean DataFrame |
| Statistics Engine | `numpy` (mean/var/std) | Compute distribution summaries | Numeric column array | 3 float values |
| Probability Calculator | Custom Python functions | Compute P(A) and P(A\|B) | DataFrame + column names | Float 0–1 |
| Visualizer | `matplotlib` | Plot distributions as images | DataFrame columns | PNG files |
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

This diagram shows how the code components map to the theory topics they implement:

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

## Folder Structure

```
01_Data_and_Probability_Explorer/
├── explorer.py               ← Your main Python script
├── outputs/
│   ├── age_distribution.png
│   ├── fare_distribution.png
│   └── survival_by_class.png
├── Project_Guide.md
├── Step_by_Step.md
├── Starter_Code.md
└── Architecture_Blueprint.md
```

---

## Why This Architecture?

This project uses a **functional, single-file** architecture by design. Each concept gets its own function:

- `compute_statistics()` — isolates the statistics concept
- `marginal_probability()` — isolates P(A)
- `conditional_probability()` — isolates P(A|B)

This makes it easy to test each piece independently and swap in different datasets. As you move to more complex projects, these functions will be replaced by classes and modules — but the same logic applies.

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| **Architecture_Blueprint.md** | You are here |
