"""
AI Knowledge Base — Repo Scaffold Script
Run from repo root: python scaffold.py

Creates all folders and stubs for the complete AI learning repo.
Skips files that already exist (safe to re-run).
"""

import os

# ── helpers ─────────────────────────────────────────────────────────────────

def make(path, content=""):
    """Create a file only if it doesn't already exist."""
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def title(filename):
    """Convert 'Theory.md' → '# Theory' as stub heading."""
    return "# " + filename.replace(".md", "").replace("_", " ") + "\n\n"

def stub(base, filename):
    make(os.path.join(base, filename), title(filename))

def section(base, files):
    """Create a folder with a set of files."""
    os.makedirs(base, exist_ok=True)
    for f in files:
        stub(base, f)


# ── file sets ────────────────────────────────────────────────────────────────
# Every topic folder gets these 4 core files
STANDARD = [
    "Theory.md",        # Storytelling + deep-dive explanation + inline Mermaid diagrams
    "Cheatsheet.md",    # Quick-reference card
    "Interview_QA.md",  # 10+ interview Q&As (beginner → advanced)
]

def std(*extra):
    """Standard set + any extras for this specific topic."""
    return STANDARD + list(extra)


# ── structure ────────────────────────────────────────────────────────────────

STRUCTURE = {

    # ── 00 ──────────────────────────────────────────────────────────────────
    "00_Learning_Guide": {
        "_root_files": ["Readme.md", "How_to_Use_This_Repo.md", "Learning_Path.md",
                        "Progress_Tracker.md"]
    },

    # ── 01 ──────────────────────────────────────────────────────────────────
    "01_Math_for_AI": {
        "_root_files": ["Readme.md"],
        "01_Probability":              std("Intuition_First.md", "Mini_Exercise.md"),
        "02_Statistics":               std("Intuition_First.md", "Mini_Exercise.md"),
        "03_Linear_Algebra":           std("Intuition_First.md", "Vectors_and_Matrices.md"),
        "04_Calculus_and_Optimization":std("Intuition_First.md", "Gradient_Intuition.md"),
        "05_Information_Theory":       std("Intuition_First.md"),
    },

    # ── 02 ──────────────────────────────────────────────────────────────────
    "02_Machine_Learning_Foundations": {
        "_root_files": ["Readme.md"],
        "01_What_is_ML":                  std(),
        "02_Training_vs_Inference":        std(),
        "03_Supervised_Learning":          std("Code_Example.md"),
        "04_Unsupervised_Learning":        std("Code_Example.md"),
        "05_Model_Evaluation":             std("Metrics_Deep_Dive.md"),
        "06_Overfitting_and_Regularization": std(),
        "07_Feature_Engineering":          std("Code_Example.md"),
        "08_Gradient_Descent":             std(),
        "09_Loss_Functions":               std(),
        "10_Bias_vs_Variance":             std(),
    },

    # ── 03 ──────────────────────────────────────────────────────────────────
    "03_Classical_ML_Algorithms": {
        "_root_files": ["Readme.md", "Algorithm_Comparison.md"],
        "01_Linear_Regression":           std("Math_Intuition.md", "Code_Example.md"),
        "02_Logistic_Regression":         std("Math_Intuition.md", "Code_Example.md"),
        "03_Decision_Trees":              std("Code_Example.md"),
        "04_Random_Forests":              std("Code_Example.md"),
        "05_SVM":                         std("Math_Intuition.md"),
        "06_K_Means_Clustering":          std("Code_Example.md"),
        "07_PCA_Dimensionality_Reduction":std("Math_Intuition.md", "Code_Example.md"),
        "08_Naive_Bayes":                 std("Code_Example.md"),
    },

    # ── 04 ──────────────────────────────────────────────────────────────────
    "04_Neural_Networks_and_Deep_Learning": {
        "_root_files": ["Readme.md"],
        "01_Perceptron":              std(),
        "02_MLPs":                    std("Code_Example.md"),
        "03_Activation_Functions":    std("Comparison.md"),
        "04_Loss_Functions":          std("Comparison.md"),
        "05_Forward_Propagation":     std("Math_Walkthrough.md"),
        "06_Backpropagation":         std("Math_Walkthrough.md"),
        "07_Optimizers":              std("Comparison.md"),
        "08_Regularization":          std(),
        "09_CNNs":                    std("Architecture_Deep_Dive.md", "Code_Example.md"),
        "10_RNNs":                    std("Architecture_Deep_Dive.md", "Code_Example.md"),
        "11_GANs":                    std("Architecture_Deep_Dive.md"),
        "12_Training_Techniques":     std("Troubleshooting_Guide.md"),
    },

    # ── 05 ──────────────────────────────────────────────────────────────────
    "05_NLP_Foundations": {
        "_root_files": ["Readme.md"],
        "01_Text_Preprocessing":         std("Code_Example.md"),
        "02_Tokenization":               std("Code_Example.md"),
        "03_Bag_of_Words_and_TF_IDF":    std("Code_Example.md"),
        "04_Word_Embeddings":            std("Code_Example.md"),
        "05_Semantic_Similarity":        std("Code_Example.md"),
        "06_Hidden_Markov_Models":       std("Math_Intuition.md"),
        "07_Conditional_Random_Fields":  std(),
    },

    # ── 06 ──────────────────────────────────────────────────────────────────
    "06_Transformers": {
        "_root_files": ["Readme.md"],
        "01_Sequence_Models_Before_Transformers": std("Timeline.md"),
        "02_Attention_Mechanism":         std("Math_Walkthrough.md"),
        "03_Self_Attention":              std("Math_Walkthrough.md"),
        "04_Multi_Head_Attention":        std(),
        "05_Positional_Encoding":         std("Math_Intuition.md"),
        "06_Transformer_Architecture":    std("Architecture_Deep_Dive.md", "Component_Breakdown.md"),
        "07_Encoder_Decoder_Models":      std("Comparison.md"),
        "08_BERT":                        std("Code_Example.md"),
        "09_GPT":                         std("Code_Example.md"),
        "10_Vision_Transformers":         std(),
    },

    # ── 07 ──────────────────────────────────────────────────────────────────
    "07_Large_Language_Models": {
        "_root_files": ["Readme.md"],
        "01_LLM_Fundamentals":                std("Timeline.md"),
        "02_How_LLMs_Generate_Text":          std(),
        "03_Pretraining":                     std("Architecture_Deep_Dive.md"),
        "04_Fine_Tuning":                     std("Code_Example.md", "When_to_Use.md"),
        "05_Instruction_Tuning":              std(),
        "06_RLHF":                            std("Architecture_Deep_Dive.md"),
        "07_Context_Windows_and_Tokens":      std(),
        "08_Hallucination_and_Alignment":     std("Mitigation_Strategies.md"),
        "09_Using_LLM_APIs":                  std("Code_Cookbook.md", "Cost_Guide.md"),
    },

    # ── 08 ──────────────────────────────────────────────────────────────────
    "08_LLM_Applications": {
        "_root_files": ["Readme.md"],
        "01_Prompt_Engineering":    std("Prompt_Patterns.md", "Code_Example.md", "Common_Mistakes.md"),
        "02_Tool_Calling":          std("Code_Example.md", "Architecture_Deep_Dive.md"),
        "03_Structured_Outputs":    std("Code_Example.md"),
        "04_Embeddings":            std("Code_Example.md"),
        "05_Vector_Databases":      std("Comparison.md", "Code_Example.md"),
        "06_Semantic_Search":       std("Code_Example.md"),
        "07_Memory_Systems":        std("Comparison.md"),
        "08_Streaming_Responses":   std("Code_Example.md"),
    },

    # ── 09 ──────────────────────────────────────────────────────────────────
    "09_RAG_Systems": {
        "_root_files": ["Readme.md", "Full_Pipeline_Overview.md"],
        "01_RAG_Fundamentals":             std("When_to_Use_RAG.md"),
        "02_Document_Ingestion":           std("Code_Example.md", "Supported_Formats.md"),
        "03_Chunking_Strategies":          std("Comparison.md", "Code_Example.md"),
        "04_Embedding_and_Indexing":       std("Code_Example.md"),
        "05_Retrieval_Pipeline":           std("Code_Example.md"),
        "06_Context_Assembly":             std("Code_Example.md"),
        "07_Advanced_RAG_Techniques":      std("Hybrid_Search.md", "Reranking.md", "Query_Transformation.md"),
        "08_RAG_Evaluation":               std("Metrics_Guide.md", "Code_Example.md"),
        "09_Build_a_RAG_App":              ["Project_Guide.md", "Architecture_Blueprint.md",
                                           "Step_by_Step.md", "Troubleshooting.md"],
    },

    # ── 10 ──────────────────────────────────────────────────────────────────
    "10_AI_Agents": {
        "_root_files": ["Readme.md", "Agent_vs_Chain_vs_RAG.md"],
        "01_Agent_Fundamentals":      std("Mental_Model.md"),
        "02_ReAct_Pattern":           std("Code_Example.md"),
        "03_Tool_Use":                std("Code_Example.md", "Building_Custom_Tools.md"),
        "04_Agent_Memory":            std("Comparison.md", "Code_Example.md"),
        "05_Planning_and_Reasoning":  std("Architecture_Deep_Dive.md"),
        "06_Reflection_and_Self_Correction": std("Code_Example.md"),
        "07_Multi_Agent_Systems":     std("Architecture_Deep_Dive.md", "Code_Example.md"),
        "08_Agent_Frameworks":        std("Comparison.md", "LangChain_Guide.md",
                                         "CrewAI_Guide.md", "AutoGen_Guide.md"),
        "09_Build_an_Agent":          ["Project_Guide.md", "Architecture_Blueprint.md",
                                       "Step_by_Step.md", "Troubleshooting.md"],
    },

    # ── 11 ──────────────────────────────────────────────────────────────────
    "11_MCP_Model_Context_Protocol": {
        "_root_files": ["Readme.md"],
        "01_MCP_Fundamentals":          std("MCP_vs_REST_API.md"),
        "02_MCP_Architecture":          std("Architecture_Deep_Dive.md", "Component_Breakdown.md"),
        "03_Hosts_Clients_Servers":     std(),
        "04_Tools_Resources_Prompts":   std("Code_Example.md"),
        "05_Transport_Layer":           std(),
        "06_Building_an_MCP_Server":    std("Server_Implementation.md", "Code_Example.md",
                                           "Step_by_Step.md"),
        "07_Security_and_Permissions":  std("Best_Practices.md"),
        "08_MCP_Ecosystem":             std("Known_Servers.md", "Integration_Guide.md"),
        "09_Connect_MCP_to_Agents":     std("Code_Example.md"),
    },

    # ── 12 ──────────────────────────────────────────────────────────────────
    "12_Production_AI": {
        "_root_files": ["Readme.md", "Production_Checklist.md"],
        "01_Model_Serving":          std("Architecture_Deep_Dive.md"),
        "02_Latency_Optimization":   std("Optimization_Techniques.md"),
        "03_Cost_Optimization":      std("Cost_Calculator_Guide.md"),
        "04_Caching_Strategies":     std("Code_Example.md"),
        "05_Observability":          std("Tools_Guide.md", "Code_Example.md"),
        "06_Evaluation_Pipelines":   std("Code_Example.md", "Metrics_Guide.md"),
        "07_Safety_and_Guardrails":  std("Implementation_Guide.md"),
        "08_Fine_Tuning_in_Production": std("When_to_Fine_Tune.md", "Code_Example.md"),
        "09_Scaling_AI_Apps":        std("Architecture_Deep_Dive.md"),
    },

    # ── 13 ──────────────────────────────────────────────────────────────────
    "13_AI_System_Design": {
        "_root_files": ["Readme.md", "System_Design_Framework.md"],
        "01_Customer_Support_Agent": ["Architecture_Blueprint.md", "Component_Breakdown.md",
                                      "Data_Flow_Diagram.md", "Tech_Stack.md",
                                      "Build_Guide.md", "Interview_QA.md"],
        "02_RAG_Document_Search_System": ["Architecture_Blueprint.md", "Component_Breakdown.md",
                                          "Data_Flow_Diagram.md", "Tech_Stack.md",
                                          "Build_Guide.md", "Interview_QA.md"],
        "03_AI_Coding_Assistant":   ["Architecture_Blueprint.md", "Component_Breakdown.md",
                                     "Data_Flow_Diagram.md", "Tech_Stack.md",
                                     "Build_Guide.md", "Interview_QA.md"],
        "04_AI_Research_Assistant": ["Architecture_Blueprint.md", "Component_Breakdown.md",
                                     "Data_Flow_Diagram.md", "Tech_Stack.md",
                                     "Build_Guide.md", "Interview_QA.md"],
        "05_Multi_Agent_Workflow":  ["Architecture_Blueprint.md", "Component_Breakdown.md",
                                     "Data_Flow_Diagram.md", "Tech_Stack.md",
                                     "Build_Guide.md", "Interview_QA.md"],
    },

    # ── 14 ──────────────────────────────────────────────────────────────────
    "14_Hugging_Face_Ecosystem": {
        "_root_files": ["Readme.md"],
        "01_Hub_and_Model_Cards":       std("Code_Example.md"),
        "02_Transformers_Library":      std("Code_Example.md", "Pipeline_Guide.md"),
        "03_Datasets_Library":          std("Code_Example.md"),
        "04_PEFT_and_LoRA":             std("Code_Example.md", "When_to_Use.md"),
        "05_Trainer_API":               std("Code_Example.md"),
        "06_Inference_Optimization":    std("Code_Example.md", "Comparison.md"),
        "07_Spaces_and_Gradio":         std("Code_Example.md"),
    },

    # ── 15 ──────────────────────────────────────────────────────────────────
    "15_LangGraph": {
        "_root_files": ["Readme.md", "LangGraph_vs_LangChain.md"],
        "01_LangGraph_Fundamentals":    std("Mental_Model.md"),
        "02_Nodes_and_Edges":           std("Code_Example.md"),
        "03_State_Management":          std("Code_Example.md"),
        "04_Cycles_and_Loops":          std("Code_Example.md"),
        "05_Human_in_the_Loop":         std("Code_Example.md"),
        "06_Multi_Agent_with_LangGraph":std("Architecture_Deep_Dive.md", "Code_Example.md"),
        "07_Streaming_and_Checkpointing":std("Code_Example.md"),
        "08_Build_with_LangGraph":      ["Project_Guide.md", "Architecture_Blueprint.md",
                                         "Step_by_Step.md", "Troubleshooting.md"],
    },

    # ── 16 ──────────────────────────────────────────────────────────────────
    "16_Diffusion_Models": {
        "_root_files": ["Readme.md"],
        "01_Diffusion_Fundamentals":    std("Intuition_First.md"),
        "02_How_Diffusion_Works":       std("Math_Intuition.md", "Architecture_Deep_Dive.md"),
        "03_Stable_Diffusion":          std("Architecture_Deep_Dive.md", "Code_Example.md"),
        "04_Guidance_and_Conditioning": std("Code_Example.md"),
        "05_Modern_Diffusion_Models":   std("Comparison.md"),
        "06_ControlNet_and_Adapters":   std("Code_Example.md"),
        "07_Diffusion_vs_GANs":         ["Comparison.md", "Theory.md", "Cheatsheet.md"],
    },

    # ── 17 ──────────────────────────────────────────────────────────────────
    "17_Multimodal_AI": {
        "_root_files": ["Readme.md"],
        "01_Multimodal_Fundamentals":   std(),
        "02_Vision_Language_Models":    std("Architecture_Deep_Dive.md"),
        "03_Image_Understanding":       std("Code_Example.md"),
        "04_Using_Vision_APIs":         std("Code_Example.md", "Code_Cookbook.md"),
        "05_Audio_and_Speech_AI":       std("Code_Example.md"),
        "06_Multimodal_Embeddings":     std("Code_Example.md"),
        "07_Multimodal_Agents":         std("Architecture_Deep_Dive.md", "Code_Example.md"),
    },

    # ── 18 ──────────────────────────────────────────────────────────────────
    "18_AI_Evaluation": {
        "_root_files": ["Readme.md", "Evaluation_Checklist.md"],
        "01_Evaluation_Fundamentals":   std(),
        "02_Benchmarks":                std("Benchmark_Comparison.md"),
        "03_LLM_as_Judge":              std("Code_Example.md", "Prompt_Templates.md"),
        "04_RAG_Evaluation":            std("Code_Example.md", "Metrics_Guide.md"),
        "05_Agent_Evaluation":          std("Code_Example.md"),
        "06_Red_Teaming":               std("Common_Attack_Patterns.md"),
        "07_Eval_Frameworks":           std("Comparison.md", "Code_Example.md"),
        "08_Build_an_Eval_Pipeline":    ["Project_Guide.md", "Step_by_Step.md",
                                         "Code_Example.md", "Metrics_Guide.md"],
    },

    # ── 19 ──────────────────────────────────────────────────────────────────
    "19_Reinforcement_Learning": {
        "_root_files": ["Readme.md"],
        "01_RL_Fundamentals":           std("Intuition_First.md"),
        "02_Markov_Decision_Processes": std("Math_Intuition.md"),
        "03_Q_Learning":                std("Math_Intuition.md", "Code_Example.md"),
        "04_Deep_Q_Networks":           std("Architecture_Deep_Dive.md", "Code_Example.md"),
        "05_Policy_Gradients":          std("Math_Intuition.md", "Code_Example.md"),
        "06_PPO":                       std("Math_Intuition.md", "Code_Example.md"),
        "07_RL_in_Practice":            std("Code_Example.md", "Frameworks_Guide.md"),
        "08_RL_for_LLMs":               std("Connection_to_RLHF.md"),
    },
}


# ── runner ───────────────────────────────────────────────────────────────────

def build():
    created_folders = 0
    created_files = 0

    for section_name, contents in STRUCTURE.items():
        section_path = section_name

        # root-level files for this section
        root_files = contents.get("_root_files", ["Readme.md"])
        os.makedirs(section_path, exist_ok=True)
        for f in root_files:
            path = os.path.join(section_path, f)
            if not os.path.exists(path):
                make(path, title(f))
                created_files += 1

        # subfolders
        for key, files in contents.items():
            if key.startswith("_"):
                continue
            folder_path = os.path.join(section_path, key)
            os.makedirs(folder_path, exist_ok=True)
            created_folders += 1
            for f in files:
                path = os.path.join(folder_path, f)
                if not os.path.exists(path):
                    make(path, title(f))
                    created_files += 1

    print(f"\n✅  Scaffold complete.")
    print(f"   Sections  : {len(STRUCTURE)}")
    print(f"   Folders   : {created_folders}")
    print(f"   Files     : {created_files}")
    print("\nRun again safely — existing files are never overwritten.\n")


if __name__ == "__main__":
    build()
