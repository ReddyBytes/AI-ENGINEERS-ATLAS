# Named Entity Recognition (NER) in NLP

Imagine reading a news article:  
*"Apple announced its new iPhone in San Francisco on September 12."*  
You immediately recognize **Apple** as a company, **San Francisco** as a location, and **September 12** as a date. Named Entity Recognition (NER) automates this process — it **identifies and classifies entities** in text.

# What is Named Entity Recognition?

NER is a **subtask of information extraction** in NLP. It identifies **predefined categories of entities** in text, such as:

- **Persons:** Names of people (e.g., "Elon Musk")  
- **Organizations:** Companies, institutions (e.g., "Google")  
- **Locations:** Cities, countries (e.g., "Paris")  
- **Dates/Times:** Specific dates, times (e.g., "August 1st")  
- **Miscellaneous:** Money, percentages, product names, etc.

NER can be implemented using **rule-based systems, statistical models, or modern deep learning methods** like LSTMs, GRUs, and transformers.

 

### How NER Works

1. **Text Preprocessing:** Tokenization, lowercasing, and stopword removal.  
2. **Feature Extraction:** Word embeddings (Word2Vec, GloVe) or contextual embeddings (BERT, RoBERTa).  
3. **Modeling:**  
   - **Rule-Based:** Pattern matching with dictionaries and regular expressions.  
   - **Statistical:** Conditional Random Fields (CRF), HMMs.  
   - **Deep Learning:** BiLSTM-CRF, Transformer-based models.  
4. **Prediction:** Classify each token as a named entity or non-entity.  
5. **Post-processing:** Merge multi-token entities, handle overlapping entities.

 

### Why NER is Needed

- Extracts **structured information** from unstructured text.  
- Enables **knowledge graphs, search engines, question answering, and analytics**.  
- Without NER:
  - Text data remains **unstructured**, making it hard to retrieve actionable insights.  
  - Automating business intelligence or document understanding becomes inefficient.

*Example:* In finance, identifying companies, stock symbols, and monetary values from news articles allows automated market analysis.

 

### Applications of NER

- **Information Extraction:** Automatically extract key entities from documents.  
- **Question Answering:** Helps models understand which entities are relevant.  
- **Knowledge Graphs:** Populate entity-relation databases.  
- **Content Recommendation:** Categorize content based on entities.  
- **Healthcare & Bioinformatics:** Extract diseases, genes, and drug names from research papers.  

 

## Interview Q&A

**Q1. What is Named Entity Recognition (NER)?**  
A: NER identifies and classifies **entities in text** into predefined categories like person, location, organization, date, etc.

**Q2. What approaches exist for NER?**  
A: Rule-based, statistical (CRF, HMM), and deep learning approaches (BiLSTM-CRF, transformer-based models).

**Q3. Why is NER important in NLP pipelines?**  
A: It transforms **unstructured text into structured information**, which is essential for search, QA, analytics, and knowledge graphs.

**Q4. Give an example of a deep learning model used for NER.**  
A: BiLSTM-CRF or BERT-based models fine-tuned on NER datasets like CoNLL-2003.

**Q5. Can NER handle multi-word entities?**  
A: Yes, models identify spans of tokens as a single entity, e.g., "San Francisco" as a location.

 

## Key Takeaways

- NER extracts **key entities** from unstructured text.  
- Modern methods rely on **contextual embeddings and deep learning** for higher accuracy.  
- Widely used in **information extraction, QA, knowledge graphs, healthcare, and finance**.  
- Critical for converting raw text into **structured, actionable data**.
