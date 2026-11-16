# HW4 — submission

**AI assistance:** <!-- what you used, and for what. "None" is an answer too. -->

---

## Part A — Plan on paper (Easy)

> Commit this whole part before any `.py` file exists.

### A1 — The steps

| # | Step | What goes in (types) | What comes out (types) | When it goes wrong | Tool, loop, or model? |
|---|---|---|---|---|---|
| 1 | | | | | |

**How the steps connect:**

<!-- which step feeds which: a list, an ASCII diagram, or an image committed to the repo -->

**What I am assuming:**

<!-- census year, archived profiles, corrections, units, where rounding happens, ... -->

### A2 — The two tools

#### `lookup`

```json
```

| Case | What the tool returns |
|---|---|
| success | |
| | |

**Worst thing it could do with strange or dangerous input:**

#### `calculate`

```json
```

| Case | What the tool returns |
|---|---|
| success | |
| | |

**Worst thing it could do with strange or dangerous input:**

### A3 — Q-09 by hand

```json
```

**My arithmetic:**

### A4 — Why I split it this way

<!-- one other way to split the task, and why you did not choose it -->

---

## Part B — Build it and run it (Medium)

### What I changed from Part A while coding

<!-- what changed in your plan, and why. "None" is an answer too. -->

### B2 — Tests

```text
<!-- pytest output -->
```

### B3 — The loop

- Round limit, and why:
- Where the logs are:
- Real Q-09 conversation compared with my A3 version, what is different:

### B4 — Three strategies

**What I kept the same:**

<!-- model, temperature, k, prompts, answer format, anything else -->

**My rule for a correct answer** (written before the first full run):

| Run | Strategy | Correct /20 | Unanswered | Input tokens | Output tokens | Median seconds per question | Total seconds | Cost ($) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 direct | | | | | | | |
| 1 | S2 think and vote (k = ) | | | | | | | |
| 1 | S3 tools | | | | | | | |
| 2 | S1 direct | | | | | | | |
| 2 | S2 think and vote (k = ) | | | | | | | |
| 2 | S3 tools | | | | | | | |

**Per question (run 1):**

| Question | S1 | S2 | S3 |
|---|:---:|:---:|:---:|
| Q-01 | | | |
| Q-02 | | | |
| Q-03 | | | |
| Q-04 | | | |
| Q-05 | | | |
| Q-06 | | | |
| Q-07 | | | |
| Q-08 | | | |
| Q-09 | | | |
| Q-10 | | | |
| Q-11 | | | |
| Q-12 | | | |
| Q-13 | | | |
| Q-14 | | | |
| Q-15 | | | |
| Q-16 | | | |
| Q-17 | | | |
| Q-18 | | | |
| Q-19 | | | |
| Q-20 | | | |

---

## Part C — Explain and choose (Hard)

### C1 — Does the tool description matter?

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|---|---:|---:|---|---|
| | | | | |

### C2 — Three mistakes explained

### C3 — Which strategy I would use, and what would change it

### C4 — How sure I can be

### Final questions

1. The model has only requested a tool call. Python has not executed it yet. My loop checks the arguments, runs the tool and returns the result.

2. Arguments arrive as a JSON string from the model. I use json.loads() to convert them into a dictionary. Without validation, the function can receive incorrect inputs.

3. My two serialized tool definitions used approximately 200 tokens, measured with tiktoken and o200k_base. The API may count some internal formatting differently.

4. S2 used an average of 219600 input and 13124.5 output tokens per run. S1 used 43600 input and 353.5 output tokens. S2 used about 5.3 times as many total tokens because it generated five answers. The exact dollar cost depends on the verified model tariff.

5. Q-01 required the most rounds in my S3 logs: 4. I inspected the saved log to understand which lookups, calculations or retries caused the extra rounds.

6. With 100000 documents, I would use a database or search index instead of scanning all text. I would keep source IDs and apply corrections before returning data.

7. My calculator uses ast instead of eval or exec. It allows only arithmetic operations and rejects dangerous Python expressions. However, the model can still give incorrect numbers or units.

8. Tools helped with numerical questions that required several facts and calculations. S3 achieved 77.5% average accuracy, while S1 achieved 22.5%. Tools did not fully prevent unit errors, as shown by Q-08.
