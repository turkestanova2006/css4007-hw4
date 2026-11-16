# HW4 — submission

**AI assistance:** I used ChatGPT to help organize the written plan, draft Python/Jupyter code, debug function calling, and explain my experiment results. I ran the notebook, inspected the tests and logs, and checked the calculations.

---

## Part A — Plan on paper (Easy)

> Commit this whole part before any `.py` file exists.

### A1 — The steps

| # | Step | What goes in (types) | What comes out (types) | When it goes wrong | Tool, loop, or model? |
|---|---|---|---|---|---|
| 1 | Read question | question (str) | district names, requested measure (str) | Ask for clarification or return UNANSWERED | model |
| 2 | Select needed fields | question (str) | district/field pairs (dict) | Use supported field names | model |
| 3 | Find facts | district, field (str) | value, unit, source (dict) | Return error/suggestion on unknown field or district | lookup tool + Python loop |
| 4 | Check corrections | fact/source (dict) | corrected current fact (dict) | Avoid archived profiles; use NR-16 | lookup tool |
| 5 | Prepare arithmetic | numeric values (float) | expression (str) | Check conversion and missing numbers | model |
| 6 | Calculate and compare | expression (str) | numeric result (float) | Reject unsafe math and division by zero | calculate tool + Python loop |
| 7 | Format answer | selected district, difference | `ANSWER: name \| number` (str) | Use UNANSWERED if unresolved | model |

**How the steps connect:**

Question → model decides fields → `lookup` → check values and corrections → model prepares formula → `calculate` → model compares values → final answer. The Python loop executes each requested tool call and returns its result to the model.

**What I am assuming:**

- Use the current 2025 district data; archived 2019 profiles are not used for current comparisons.
- Brightwater area is corrected to **921.4 km²** by NR-16.
- Convert units consistently, including megalitres to cubic metres and tenge to million tenge when required.
- Use the 2025 household water tariff when a question asks for water payments.
- Do calculations at full precision and round only the final answer to the requested decimals.
- If a required fact is missing, return an error rather than guess.

### A2 — The two tools

#### `lookup`

```json
{
  "type": "function",
  "function": {
    "name": "lookup",
    "description": "Find current Nine Rivers district facts, use corrections and return value, unit, and source ID. Allowed fields: population_2025, population_2020, area_km2, budget_2025, water_2025, water_tariff_2025, schools, pupils, roads_km, founded_year.",
    "parameters": {
      "type": "object",
      "properties": {
        "district": {
          "type": "string"
        },
        "field": {
          "type": "string"
        }
      },
      "required": [
        "district",
        "field"
      ],
      "additionalProperties": false
    }
  }
}
```

| Case | What the tool returns |
|---|---|
| success | `{"value": 44675, "unit": "residents", "source": "NR-05"}` (example) |
| wrong district | Error and possible close matches |
| wrong field | Error: unknown field |
| archived profile | Uses current profile instead of archived text |
| corrected area | NR-16 value for Brightwater |
| empty / invalid input | Error; do not execute input as code |

**Worst thing it could do with strange or dangerous input:** It could select a wrong or old fact, confuse similar district names, or accept a misleading field. I validate inputs, restrict supported field names, use local documents and preserve the document source.

#### `calculate`

```json
{
  "type": "function",
  "function": {
    "name": "calculate",
    "description": "Safely evaluate simple arithmetic expressions without running arbitrary Python.",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string"
        }
      },
      "required": [
        "expression"
      ],
      "additionalProperties": false
    }
  }
}
```

| Case | What the tool returns |
|---|---|
| success | `{"result": 48.48599956587801}` for `44675 / 921.4` |
| division by zero | Error |
| invalid or empty expression | Error |
| function call / attribute / exponent expression | Rejects unsupported syntax |
| very large expression | Error |

**Worst thing it could do with strange or dangerous input:** It could execute code or use excessive resources if arbitrary expressions were accepted. My implementation uses `ast` instead of `eval`/`exec`, permits only basic arithmetic, and limits expression size and magnitude.

### A3 — Q-09 by hand

The question asks which of Brightwater and Millbrook has higher 2025 population density and by how many residents per km². This is my **planned** conversation (not a copied live API trace).

```json
[
  {
    "role": "user",
    "content": "Q-09: Which district has higher 2025 population density, Brightwater or Millbrook, and by how many residents per square kilometre?"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "name": "lookup",
        "arguments": {
          "district": "Brightwater",
          "field": "population_2025"
        }
      },
      {
        "name": "lookup",
        "arguments": {
          "district": "Brightwater",
          "field": "area_km2"
        }
      },
      {
        "name": "lookup",
        "arguments": {
          "district": "Millbrook",
          "field": "population_2025"
        }
      },
      {
        "name": "lookup",
        "arguments": {
          "district": "Millbrook",
          "field": "area_km2"
        }
      }
    ]
  },
  {
    "role": "tool",
    "name": "lookup",
    "results": [
      {
        "district": "Brightwater",
        "field": "population_2025",
        "value": 44675,
        "source": "NR-05"
      },
      {
        "district": "Brightwater",
        "field": "area_km2",
        "value": 921.4,
        "source": "NR-16"
      },
      {
        "district": "Millbrook",
        "field": "population_2025",
        "value": 37203,
        "source": "NR-11"
      },
      {
        "district": "Millbrook",
        "field": "area_km2",
        "value": 758.6,
        "source": "NR-11"
      }
    ]
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "name": "calculate",
        "arguments": {
          "expression": "44675/921.4"
        }
      },
      {
        "name": "calculate",
        "arguments": {
          "expression": "37203/758.6"
        }
      },
      {
        "name": "calculate",
        "arguments": {
          "expression": "37203/758.6-44675/921.4"
        }
      }
    ]
  },
  {
    "role": "tool",
    "name": "calculate",
    "results": [
      48.48599956587801,
      49.041655681518584,
      0.5556561156405735
    ]
  },
  {
    "role": "assistant",
    "content": "ANSWER: Millbrook | 0.6"
  }
]
```

**My arithmetic:**

- Brightwater: 44,675 ÷ 921.4 = **48.4860** residents/km² (NR-05, NR-16).
- Millbrook: 37,203 ÷ 758.6 = **49.0417** residents/km² (NR-11).
- Difference: 49.0417 − 48.4860 = **0.5557 ≈ 0.6** residents/km².
- **Final:** `ANSWER: Millbrook | 0.6`

### A4 — Why I split it this way

I separated fact lookup from arithmetic because the two tasks can fail in different ways. An alternative was one large tool that both searches documents and calculates, but it would be harder to test, debug and reuse. With two tools I can inspect whether a mistake came from a source value or a formula.

---

## Part B — Build it and run it (Medium)

### What I changed from Part A while coding

I implemented `lookup` using regular expressions over local JSONL profiles and a separate correction rule for Brightwater. I implemented `calculate` with safe `ast` operators and limits. During the first live Q-09 test, the agent used natural phrases such as `2025 population` instead of the exact `population_2025` field. I improved the tool description to list supported fields and tell the model to calculate density from population and area. I also added `reasoning_effort="none"` after the Chat Completions API rejected function tools with its default reasoning setting, and tightened the final answer format.

### B2 — Tests

```text
platform win32 -- Python 3.12.4, pytest-9.2.0
collected 17 items
test_lookup.py: 7 passed
test_calculate.py: 10 passed
============================= 17 passed in 0.04s =============================
```

Test output was also written to `outputs/pytest_results.txt`. The tests cover current and corrected values, an archived profile, similar names, water conversion, arithmetic, zero division, unsafe expressions and large values.

### B3 — The loop

- **Round limit, and why:** 12 model rounds, to let multi-step questions finish while preventing an endless tool-call loop.
- **Where the logs are:** `outputs/b3/` for direct agent runs, and `outputs/b4/run_1/S3/` and `outputs/b4/run_2/S3/` for the two experiment runs. Each log stores the question, answer, token counts, tool calls, rounds and elapsed time.
- **Real Q-09 conversation compared with my A3 version, what is different:** The working agent finished in **4 rounds with 7 tool calls**: four lookups and three calculations. The earlier test initially used invalid field names, so I added explicit supported names. The final live answer was `ANSWER: Millbrook | 0.6`, agreeing with my paper arithmetic. The live assistant split the operations across model rounds rather than following my planned compact JSON steps exactly.

### B4 — Three strategies

**What I kept the same:**

- All runs used the same 20 questions and model `gpt-5.6-luna` with `reasoning_effort="none"`.
- S1 and S2 received the same 17-document corpus and used the same final answer format; S2 added a step-by-step instruction and voted across **k = 5** samples per question.
- S2 requested temperature 0.7 where supported; the code retried without a custom temperature if the model rejected that setting. S1 used the default temperature.
- S3 received tool descriptions and used `lookup` and `calculate` instead of putting the full corpus in the prompt.
- The ground truth was used to evaluate answers after generation, not included in model prompts.

**My rule for a correct answer** (written before the first full run):

Extract the `ANSWER: name | number` pattern. The name must match the expected name case-insensitively, and the absolute numeric difference must be at most `10^(-decimals)` according to `questions.json`. Invalid or unanswered outputs are incorrect. This was implemented in `is_correct`.

**Cost estimate assumption:** $0.20 per 1M input tokens and $1.20 per 1M output tokens, with no cached-token discount. These were the rates used for the estimate, **not billing-verified pricing for `gpt-5.6-luna`**. Replace the rates if actual account pricing differs.

| Run | Strategy | Correct /20 | Unanswered | Input tokens | Output tokens | Median seconds per question | Total seconds | Cost ($) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 direct | 5 | 0 | 43,600 | 398 | 1.18 | 24.58 | 0.009198 |
| 1 | S2 think and vote (k = 5) | 15 | 0 | 219,600 | 13,041 | 9.36 | 188.16 | 0.059569 |
| 1 | S3 tools | 15 | 0 | 35,729 | 3,399 | 4.46 | 91.19 | 0.011225 |
| 2 | S1 direct | 4 | 0 | 43,600 | 309 | 1.19 | 23.78 | 0.009091 |
| 2 | S2 think and vote (k = 5) | 15 | 0 | 219,600 | 13,208 | 9.66 | 196.69 | 0.059770 |
| 2 | S3 tools | 16 | 0 | 38,971 | 3,608 | 4.46 | 95.10 | 0.012124 |

**Per question (run 1):**

| Question | S1 | S2 | S3 |
|---|:---:|:---:|:---:|
| Q-01 | ✗ | ✓ | ✓ |
| Q-02 | ✗ | ✓ | ✓ |
| Q-03 | ✗ | ✓ | ✓ |
| Q-04 | ✓ | ✓ | ✓ |
| Q-05 | ✗ | ✗ | ✓ |
| Q-06 | ✓ | ✓ | ✓ |
| Q-07 | ✗ | ✓ | ✓ |
| Q-08 | ✗ | ✓ | ✗ |
| Q-09 | ✓ | ✓ | ✓ |
| Q-10 | ✓ | ✓ | ✓ |
| Q-11 | ✗ | ✓ | ✗ |
| Q-12 | ✗ | ✓ | ✓ |
| Q-13 | ✗ | ✓ | ✗ |
| Q-14 | ✗ | ✓ | ✓ |
| Q-15 | ✗ | ✗ | ✓ |
| Q-16 | ✓ | ✓ | ✓ |
| Q-17 | ✗ | ✗ | ✗ |
| Q-18 | ✗ | ✗ | ✓ |
| Q-19 | ✗ | ✓ | ✗ |
| Q-20 | ✗ | ✗ | ✓ |


---

## Part C — Explain and choose (Hard)

### C1 — Does the tool description matter?

I compared the original detailed description with the vague description `Looks things up.` for five questions.

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|---|---:|---:|---|---|
| Q-01 | 7 | 6 | `ANSWER: Ossbridge &#124; 4.6` | UNANSWERED |
| Q-03 | 5 | 4 | `ANSWER: Lindenmoor &#124; 5.3` | UNANSWERED |
| Q-08 | 5 | 4 | `ANSWER: Brightwater &#124; 72456.2` | UNANSWERED |
| Q-09 | 7 | 6 | `ANSWER: Millbrook &#124; 0.6` | UNANSWERED |
| Q-18 | 3 | 3 | `ANSWER: yes &#124; 40013.4` | UNANSWERED |

The detailed description answered **4/5 (80%)** correctly; the vague description answered **0/5 (0%)**. Q-08 was incorrect even with the detailed description. The vague agent did not know the valid lookup field names and returned `UNANSWERED` in all five cases. This suggests tool descriptions strongly affect tool-argument selection and completion.

### C2 — Three mistakes explained

**S1 Direct — Q-01.** Expected `ANSWER: Ossbridge | 4.6`; actual `ANSWER: Ossford | 0.3`. It selected the wrong district and wrong difference. Without a separate calculator, S1 had to identify and combine the numbers in its text response.

**S2 Think and Vote — Q-05.** Expected `ANSWER: Coldharbour | 14235`; actual `ANSWER: coldharbour | 14217.0`. The district was right, but the difference was **18 tenge per resident** too low. Five samples and a vote did not remove this numerical error.

**S3 Tools — Q-08.** Expected `ANSWER: Brightwater | 72.46` (million tenge); actual `ANSWER: Brightwater | 72456.2`. It selected the correct district but the output used the wrong magnitude/units. The log shows seven tool calls; the returned numerical output was roughly a thousand times the required million-tenge amount. The exact step introducing the scaling error would require inspecting all arithmetic arguments in the saved Q-08 trace.

### C3 — Which strategy I would use, and what would change it

| Strategy | Mean accuracy | Mean input tokens/run | Mean output tokens/run | Median seconds/question (mean across runs) |
|---|---:|---:|---:|---:|
| S1 direct | 22.5% | 43,600 | 353.5 | 1.19 |
| S2 think and vote | 75.0% | 219,600 | 13,124.5 | 9.51 |
| S3 tools | 77.5% | 37,350 | 3,503.5 | 4.46 |

I would choose **S3** for this task. It was slightly more accurate than S2, much faster, and used fewer tokens. I would choose **S1** instead if speed and low spending mattered much more than correctness, such as for a low-risk rough draft. I could choose **S2** if tool access was unavailable but I still needed better accuracy than S1. If I needed strict financial accuracy, I would require explicit unit checks and a final numeric validator even with S3.

### C4 — How sure I can be

| Strategy | Run 1 | Run 2 | Change |
|---|---:|---:|---:|
| S1 | 5/20 (25%) | 4/20 (20%) | -1 answer |
| S2 | 15/20 (75%) | 15/20 (75%) | 0 |
| S3 | 15/20 (75%) | 16/20 (80%) | +1 answer |

S3 was the strongest on average, but it beat S2 by only **one correct answer across 40 evaluated responses**. Two runs on only 20 questions are too small to claim that S3 will always win. S2 had equal total scores in both runs, but this does not prove its individual answers were identical. I would want a larger, more varied test set (for example 100–200 questions, with several independent runs) and a confidence interval before treating this small gap as reliable.

### Final questions

1. **When the model sends `tool_calls`, what has run?** The model has only requested a call. Python has not executed the function until my loop parses the request, runs the function, and returns the result.

2. **Why do arguments arrive as a string?** They are JSON text from the model. My loop uses `json.loads()` and validates required keys before passing them into a tool; otherwise the arguments may be invalid or misinterpreted.

3. **How many tokens do your two tool definitions add?** Serializing both tool definitions and measuring with `tiktoken` / `o200k_base` gave **200 tokens**. This is an estimate, since the API can serialize tools differently internally.

4. **How much more did S2 cost than S1?** With the assumed $0.20/$1.20 per-million rates, S1 cost about **$0.018289** over two runs and S2 cost about **$0.119339**, so S2 was about **6.53 times** as expensive (about **$0.10105** more). These are estimates, not verified billed costs.

5. **Which question needed the most rounds in S3, and why?** The maximum was **4 rounds**, shared by multiple questions. **Q-01** is one example. It required four lookups (population and area for two districts) and three calculations (two densities and their difference).

6. **How would lookup change for 100,000 documents?** I would use a database or search index rather than scanning raw text. I would retain source IDs, version metadata and correction rules so retrieved facts can still be checked.

7. **Why is calculate safe?** It parses expressions with `ast`, allows only basic arithmetic, rejects arbitrary Python calls and attributes, and limits input size and magnitude. The model can still supply wrong numbers or units, so safety does not guarantee a correct answer.

8. **Where did tools help?** Tools helped most on multi-document numerical comparisons: S3 had **77.5%** average accuracy versus S1 at **22.5%**. They did not fully solve errors in interpreting units, as Q-08 showed.
