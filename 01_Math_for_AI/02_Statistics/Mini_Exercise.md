# Statistics — Mini Exercise

Five short exercises. No code. Work through these by hand (or on paper). Answers are at the bottom.

---

## Exercise 1 — Calculate the Mean

A student recorded the time (in minutes) it took them to solve 5 math problems:

**4, 7, 3, 9, 2**

What is the mean solving time?

---

## Exercise 2 — Mean vs. Median

A small company has 6 employees with these annual salaries (in thousands):

**30, 32, 35, 38, 40, 120**

1. What is the mean salary?
2. What is the median salary?
3. Which number better represents a "typical" employee's pay? Why?

---

## Exercise 3 — Calculate Variance and Standard Deviation

Take this small dataset of 5 quiz scores:

**10, 12, 10, 14, 14**

Step 1: Calculate the mean.
Step 2: Find each score's distance from the mean.
Step 3: Square each distance.
Step 4: Average the squared distances (this is the variance).
Step 5: Take the square root (this is the standard deviation).

---

## Exercise 4 — Comparing Spread

Two students each took 4 tests. Here are their scores:

**Student A:** 70, 72, 68, 70
**Student B:** 55, 85, 60, 90

Both students have the same mean score. Calculate the mean for each to confirm. Then, just by looking at the numbers, which student has higher variance? Which is more consistent?

---

## Exercise 5 — Spotting the Outlier

Here are 6 daily step counts:

**8200, 7800, 8100, 8400, 7900, 400**

1. Calculate the mean.
2. Calculate the median.
3. Which value is the outlier?
4. Is the mean or median more representative of a "typical" day?

---

---

## Answers

**Exercise 1 — Mean:**
Sum = 4 + 7 + 3 + 9 + 2 = 25
Mean = 25 / 5 = **5 minutes**

---

**Exercise 2 — Mean vs. Median:**
Sum = 30 + 32 + 35 + 38 + 40 + 120 = 295
Mean = 295 / 6 = **$49,167**

Sorted: 30, 32, 35, 38, 40, 120
Median = average of 3rd and 4th values = (35 + 38) / 2 = **$36,500**

The **median** better represents a typical employee. The $120k salary is an outlier (likely a manager or founder) that pulls the mean way up. No one actually earns near $49k — most earn around $33k-$38k. The median tells the true story.

---

**Exercise 3 — Variance and SD:**
Mean = (10 + 12 + 10 + 14 + 14) / 5 = 60 / 5 = **12**

Distances from mean: -2, 0, -2, +2, +2
Squared distances: 4, 0, 4, 4, 4

Variance = (4 + 0 + 4 + 4 + 4) / 5 = 16 / 5 = **3.2**

Standard Deviation = √3.2 ≈ **1.79**

Meaning: most scores are within about 1.79 points of the mean of 12.

---

**Exercise 4 — Comparing Spread:**
Student A mean: (70 + 72 + 68 + 70) / 4 = 280 / 4 = **70**
Student B mean: (55 + 85 + 60 + 90) / 4 = 290 / 4 = **72.5**

(They're close but not quite the same — that's okay, the point is the spread comparison.)

Student A's scores: 68, 70, 70, 72 — all within 2 points of 70. **Very low variance. Consistent.**
Student B's scores: 55, 60, 85, 90 — swinging wildly. **Very high variance. Inconsistent.**

Same ballpark average, completely different reliability.

---

**Exercise 5 — Outlier:**
Sum = 8200 + 7800 + 8100 + 8400 + 7900 + 400 = 40,800
Mean = 40,800 / 6 = **6,800 steps**

Sorted: 400, 7800, 7900, 8100, 8200, 8400
Median = average of 3rd and 4th = (7900 + 8100) / 2 = **8,000 steps**

The outlier is **400 steps** (probably a rest day or a data recording error).

The **median** (8,000) is more representative of a typical day. The mean (6,800) is dragged down by that one unusual day.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| 📄 **Mini_Exercise.md** | ← you are here |

⬅️ **Prev:** [01 Probability](../01_Probability/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Linear Algebra](../03_Linear_Algebra/Theory.md)
