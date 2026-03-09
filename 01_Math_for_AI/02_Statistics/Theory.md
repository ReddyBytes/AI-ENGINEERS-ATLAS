# Statistics — Theory

Ms. Chen just finished grading 30 exams. She spreads them on her desk. One score is 98. One is 42. Most are somewhere in the middle. She thinks: "What's the typical score? Are these scores spread out or bunched together? Are there more high scores or low scores?" She needs to summarize 30 numbers into a few key facts.

👉 This is why we need **Statistics** — to turn a pile of raw numbers into useful, understandable insights.

---

## From Raw Data to Insight

Imagine these 7 exam scores: **55, 60, 70, 72, 75, 88, 95**

Seven numbers. Hard to see anything. Statistics gives us tools to summarize them.

---

## Mean — The "Average"

Add them all up and divide by how many there are.

```
Mean = (55 + 60 + 70 + 72 + 75 + 88 + 95) / 7
     = 515 / 7
     ≈ 73.6
```

The mean is the "center of gravity" of the data. Pull it too far either way and something outlier-ish happened.

**Problem with the mean:** One extreme value destroys it. If one student scored 5 instead of 55, the mean drops a lot. A single outlier can make the mean misleading.

---

## Median — The Middle Value

Sort the numbers. Find the one in the middle.

Sorted: 55, 60, 70, **72**, 75, 88, 95

The median is **72**. Three numbers below it, three above it.

The median doesn't care about extreme values. A billionaire moving into a neighborhood raises the mean income hugely — but barely moves the median. That's why median income is often more useful than mean income.

---

## Mode — The Most Common Value

The mode is the value that appears most often.

In scores: 55, 60, 70, 72, 75, 88, 95 — each appears once, so there's no mode here.

New example: 70, 72, 72, 75, 75, 75, 88

The mode is **75** — it appears 3 times.

Useful when you want to know "what's the most popular result?"

---

## Variance — How Spread Out Is the Data?

The mean tells you where the center is. Variance tells you how far the data points scatter from that center.

Step 1: Find the mean (say it's 73.6).
Step 2: For each score, find the distance from the mean.
Step 3: Square those distances (so negatives don't cancel out).
Step 4: Average the squared distances.

```
Variance = average of (each value - mean)²
```

High variance = scores are all over the place.
Low variance = scores are tightly clustered.

---

## Standard Deviation — Variance in Plain Units

Variance uses squared units, which is awkward. Take the square root and you get standard deviation (SD).

```
Standard Deviation = √Variance
```

If the mean score is 73.6 and the SD is 12, that means most scores are roughly within 12 points of 73.6 — so between about 62 and 86.

**SD is the most useful measure of spread.** It's in the same units as your data.

---

## The Normal Distribution

When you have a lot of data that clusters naturally around an average, it often forms a bell curve — also called the normal distribution.

- Most values cluster near the mean
- Fewer values are further away
- The curve is symmetric

```
              |
         *    |    *
       *      |      *
     *        |        *
   *          |          *
  *           |           *
 _____________|_____________
      -2SD  -1SD  mean  +1SD  +2SD
```

In a normal distribution:
- ~68% of data falls within 1 SD of the mean
- ~95% falls within 2 SDs
- ~99.7% falls within 3 SDs

This is called the **68-95-99.7 rule**. An AI model trained on normally distributed data behaves very predictably.

---

## Visualizing the Pipeline

```mermaid
flowchart LR
    A[Raw Data\n55 60 70 72 75 88 95] --> B[Central Tendency\nMean / Median / Mode]
    A --> C[Spread\nVariance / Std Dev]
    B --> D[Where is the center?]
    C --> E[How scattered is it?]
    D --> F[Summary Statistics\nInsights about the data]
    E --> F
    F --> G[Detect patterns\nand anomalies]
```

---

## Why AI Cares

Statistics is the foundation of every ML algorithm.

- **Feature scaling:** subtract the mean, divide by SD — called normalization
- **Model evaluation:** accuracy, precision, recall are all statistical measures
- **Detecting outliers:** data points more than 3 SDs from the mean are suspicious
- **Comparing models:** is model A actually better, or just got lucky on this dataset?

Every time a data scientist says "this model performs at 94%," that's a statistical statement. Every time they say "results are statistically significant," that's statistics.

---

✅ **What you just learned:** Statistics gives you tools — mean, median, mode, variance, and standard deviation — to summarize and understand large collections of numbers.

🔨 **Build this now:** Take any 5 numbers (your 5 most recent grades, temperatures, or prices). Calculate the mean by hand. Then calculate the median. Are they different? What does that difference tell you?

➡️ **Next step:** Linear Algebra — `01_Math_for_AI/03_Linear_Algebra/Theory.md`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Mini_Exercise.md](./Mini_Exercise.md) | Practice exercises |

⬅️ **Prev:** [01 Probability](../01_Probability/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Linear Algebra](../03_Linear_Algebra/Theory.md)
