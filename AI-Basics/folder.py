import os

# Base directory for NLP repo
base_dir = "NLP"

# Folder structure as dictionary
folders = {
    "01_Introduction_to_NLP": ["Introduction_to_NLP.md"],
    "02_Text_Preprocessing_and_Feature_Engineering": [
        "Tokenization.md",
        "Stemming_and_Lemmatization.md",
        "Stopwords_and_Cleaning.md",
        "Feature_Representation.md"
    ],
    "03_Classical_NLP_Algorithms": [
        "Naive_Bayes.md",
        "Hidden_Markov_Models.md",
        "Conditional_Random_Fields.md"
    ],
    "04_Deep_Learning_for_NLP": [
        "RNN.md",
        "LSTM.md",
        "GRU.md",
        "Seq2Seq.md",
        "Attention_in_NLP.md"
    ],
    "05_Transformers_in_NLP": [
        "BERT.md",
        "GPT.md",
        "Encoder_Decoder_Transformers.md",
        "FineTuning_Transformers.md"
    ],
    "06_Advanced_NLP_Tasks": [
        "Text_Classification.md",
        "Sentiment_Analysis.md",
        "Named_Entity_Recognition.md",
        "Question_Answering.md",
        "Text_Summarization.md",
        "Machine_Translation.md",
        "Text_Generation.md"
    ],
    "07_Generative_NLP_and_LLM_Applications": [
        "Chatbots_and_Conversational_AI.md",
        "Prompt_Engineering.md",
        "FineTuning_and_RLHF.md",
        "Multimodal_NLP.md"
    ],
    "08_Evaluation_Metrics_in_NLP": [
        "Perplexity_and_BLEU.md",
        "ROUGE_and_METEOR.md",
        "F1_Accuracy_Precision_Recall.md"
    ],
    "09_NLP_in_Production": [
        "Tokenizers_and_Pipelines.md",
        "Deployment_and_Inference.md",
        "Monitoring_and_Ethics.md"
    ]
}

# Create base directory
os.makedirs(base_dir, exist_ok=True)

# Create folders and markdown files
for folder, files in folders.items():
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    for file in files:
        file_path = os.path.join(folder_path, file)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(f"# {file.replace('.md','').replace('_',' ')}\n\n")  # Add title in markdown

# Create README.md in base directory
readme_path = os.path.join(base_dir, "README.md")
if not os.path.exists(readme_path):
    with open(readme_path, "w") as f:
        f.write("# NLP Deep Dive Repository\n\n")
        f.write("This repository contains detailed NLP notes organized by topics and subtopics.\n\n")
        f.write("## Folders:\n")
        for folder in folders.keys():
            f.write(f"- {folder}\n")

print(f"All folders and files have been created under '{base_dir}'")
