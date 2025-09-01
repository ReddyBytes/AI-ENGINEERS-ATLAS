# Recurrent Neural Networks (RNNs) in NLP

Imagine you are trying to **predict the next word** in the sentence:  
*"The cat sat on the"*  
To predict the next word, you need to **remember the previous words**. A simple feedforward network cannot handle sequences naturally. This is why we need **Recurrent Neural Networks (RNNs)** — to model **sequential dependencies** in text.

# What is an RNN?

A Recurrent Neural Network (RNN) is a type of neural network designed for **sequential data**. Unlike feedforward networks, RNNs have **loops in their architecture** that allow information to persist across time steps.

### How RNNs Work in NLP

1. **Input Sequence:** Words are converted into embeddings.  
   - Example: ["The", "cat", "sat", "on", "the"] → embeddings vectors.  
2. **Hidden State:** At each time step, the network takes the current input and previous hidden state to produce a new hidden state:  
   \[
   h_t = \text{tanh}(W_x x_t + W_h h_{t-1} + b)
   \]  
3. **Output:** Hidden states can be used to predict the next word, classify text, or generate sequences.  
4. **Training:** Uses **Backpropagation Through Time (BPTT)** to update weights.  

 

### Types of RNNs in NLP

1. **Vanilla RNNs:**  
   - Standard RNN with one hidden layer.  
   - Struggles with **long-term dependencies** due to vanishing gradients.

2. **LSTM (Long Short-Term Memory):**  
   - Introduces **gates (input, forget, output)** and a **cell state** to handle long-range dependencies.  
   - Widely used for NLP tasks with longer sequences.

3. **GRU (Gated Recurrent Unit):**  
   - Simplified LSTM with **update and reset gates**.  
   - Fewer parameters, faster training, still handles long-term dependencies.

 

## Why do we need RNNs in NLP?

- Text is inherently **sequential**; words depend on previous context.  
- Feedforward networks cannot retain past information.  
- RNNs allow models to **remember previous words** and capture patterns across sequences.  
- Without RNNs, tasks like language modeling, translation, and text generation would fail to account for **contextual dependencies**.

*Example:* For the sentence “I went to the bank to deposit money,” predicting “deposit” requires remembering that “bank” refers to a financial institution, not a riverbank.

 

## Applications of RNNs in NLP

- **Language Modeling:** Predict next word in a sentence.  
- **Machine Translation:** Map input sequences to output sequences.  
- **Text Summarization:** Generate concise summaries of long documents.  
- **Speech Recognition:** Convert audio to text using sequential modeling.  
- **Sentiment Analysis:** Classify text based on contextual cues across sentences.

 

## Interview Q&A

**Q1. What is an RNN and why is it used in NLP?**  
A: RNN is a neural network for sequential data. In NLP, it captures **dependencies between words** across sequences.

**Q2. What is the vanishing gradient problem in RNNs?**  
A: During backpropagation, gradients may shrink exponentially, preventing the network from learning **long-term dependencies**.

**Q3. How do LSTMs and GRUs solve the vanishing gradient problem?**  
A: By using **gates and memory states** to control information flow, enabling retention of long-term context.

**Q4. Give an example of an NLP task solved by RNNs.**  
A: Machine translation: predicting the next word in the target language based on the entire source sentence.

**Q5. Why not use feedforward networks for sequence tasks?**  
A: Feedforward networks cannot naturally retain **previous information**; they treat each input independently.

 

## Key Takeaways

- RNNs are **sequence-aware neural networks** ideal for text.  
- They maintain **hidden states** to remember previous inputs.  
- Vanilla RNNs struggle with long sequences, leading to **LSTM and GRU variants**.  
- Core to NLP tasks like **language modeling, translation, summarization, and speech recognition**.  
- Modern NLP often combines RNNs with **attention mechanisms** for improved context handling.
