# ML Workflow — End to End

> How a real machine learning project flows from raw data to production — and back again.

```mermaid
flowchart LR
    A[(Data\nIngestion)] --> B[Data\nAnalysis]
    B --> C[Data\nPreparation]
    C --> D[Model\nTraining]

    subgraph Experiment["Model Training and Experimentation"]
        D --> E[Model Evaluation\nand Validation]
        E -->|needs improvement| D
    end

    E --> F[(Trained\nModel)]
    F --> G[(Model\nRegistry)]
    G --> H[Model\nServing]
    H --> I[Production\nService]
    I --> J[Model Performance\nMonitoring]
    J -->|trigger retraining| A

    style Experiment fill:#f0f9ff,stroke:#0ea5e9
    style A fill:#dbeafe,stroke:#3b82f6
    style F fill:#dcfce7,stroke:#16a34a
    style G fill:#dcfce7,stroke:#16a34a
    style I fill:#fef9c3,stroke:#ca8a04
    style J fill:#fce7f3,stroke:#ec4899
```

## Each Stage Explained

| Stage | What Happens | Key Questions |
|---|---|---|
| **Data Ingestion** | Collect raw data from sources (DBs, APIs, files) | What data do I have? Is it labeled? |
| **Data Analysis** | Explore distributions, find patterns, detect issues | Are there outliers? Class imbalance? Missing values? |
| **Data Preparation** | Clean, transform, normalize, split train/val/test | What features matter? How to encode categoricals? |
| **Model Training** | Fit model on training data, tune hyperparameters | Which algorithm? What regularization? |
| **Model Evaluation** | Measure accuracy, precision, recall, F1 on held-out data | Is the model generalizing? Overfitting? |
| **Model Registry** | Version and store the trained model artifacts | Which version goes to production? |
| **Model Serving** | Deploy model behind an API endpoint | Latency? Batching? A/B testing? |
| **Production Service** | Model serves real users | Cost? SLAs? Monitoring alerts? |
| **Performance Monitoring** | Track live metrics, detect drift | When does the model go stale? |

## The Feedback Loop

The monitoring stage feeds back to the start — when live performance degrades (data drift, concept drift), it triggers a new training run. This is why ML systems are never truly "finished."

---

✅ **What this diagram shows:** Real ML is a loop, not a pipeline. Deployment is the beginning of maintenance, not the end.

---

## 📂 Navigation

⬅️ **Back to:** [02 ML Foundations](./Readme.md)
