# Probability — Mini Exercise

No code. No formulas to memorize. Just think through these five problems. Try to answer before looking at the answers at the bottom.

---

## Exercise 1 — Guess the Probability

Without calculating anything, which of these events do you think is most likely?

A) Rolling a 6 on a standard die
B) Flipping heads on a fair coin
C) Picking a red card from a standard deck of 52 cards
D) It being a weekday (Monday through Friday) on a randomly chosen day

Rank them from least likely to most likely.

---

## Exercise 2 — The Complement Trick

A bag has 10 marbles: 7 red, 3 blue.

You reach in without looking and grab one marble.

**Question:** What's the probability of NOT getting a red marble?

Hint: Calculate P(red) first, then use the complement rule.

---

## Exercise 3 — The AND Rule

You flip a coin AND roll a die.

**Question 1:** What's the probability of getting heads on the coin?
**Question 2:** What's the probability of rolling a 4 on the die?
**Question 3:** What's the probability of getting heads AND rolling a 4 at the same time?

---

## Exercise 4 — The OR Rule

You draw one card from a standard 52-card deck.

- P(drawing a heart) = 13/52 = 0.25
- P(drawing a king) = 4/52 ≈ 0.077

**Question:** What's the probability of drawing a heart OR a king?

Careful: don't forget the overlap. Is there a card that is both a heart AND a king?

---

## Exercise 5 — Conditional Thinking

You know these facts about your commute:
- 40% of days it rains
- When it rains, your bus is late 60% of the time
- When it does NOT rain, your bus is late only 10% of the time

**Question 1:** On a rainy day, what's the probability the bus is late?
**Question 2:** On a day with no rain, what's the probability the bus is late?
**Question 3:** Which situation makes late buses much more likely?

No calculation needed for Q3 — just compare your answers to Q1 and Q2.

---

---

## Answers

**Exercise 1 — Ranking:**
- A) Rolling a 6: 1/6 ≈ 0.167 (17%)
- B) Flipping heads: 1/2 = 0.5 (50%)
- C) Red card: 26/52 = 0.5 (50%) — same as heads!
- D) Weekday: 5/7 ≈ 0.714 (71%)

Ranking: A < B = C < D

---

**Exercise 2 — Complement:**
P(red) = 7/10 = 0.7
P(NOT red) = 1 - 0.7 = **0.3** (30% chance of getting blue)

---

**Exercise 3 — AND Rule:**
Q1: P(heads) = 0.5
Q2: P(rolling 4) = 1/6 ≈ 0.167
Q3: P(heads AND 4) = 0.5 × 0.167 ≈ **0.083** (about 8%)

The two events are independent — the coin doesn't care what the die does.

---

**Exercise 4 — OR Rule:**
P(heart OR king) = P(heart) + P(king) - P(heart AND king)
= 0.25 + 0.077 - (1/52)
= 0.25 + 0.077 - 0.019
= **0.308** (about 31%)

Yes, there is one card that is both: the King of Hearts. We must subtract it once.

---

**Exercise 5 — Conditional:**
Q1: P(late | rain) = **0.6** (60%) — given by the problem directly
Q2: P(late | no rain) = **0.1** (10%) — given by the problem directly
Q3: Rain makes late buses 6x more likely (60% vs 10%). Rain is strong evidence that the bus will be late.

This is conditional probability thinking. The same question ("will my bus be late?") has a very different answer depending on the conditions.

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

⬅️ **Prev:** [00 Learning Guide](../../00_Learning_Guide/Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Statistics](../02_Statistics/Theory.md)
