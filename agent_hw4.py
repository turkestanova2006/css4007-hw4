
import json
import time
from pathlib import Path
from openai import OpenAI
from tools_hw4 import lookup, calculate

MODEL = "gpt-5.6-luna"
MAX_ROUNDS = 12

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup",
            "description": (
                "Find facts about Nine Rivers districts. "
                "IMPORTANT: The field must be exactly one of: "
                "population_2025, population_2020, area_km2, "
                "budget_2025, water_2025, water_tariff_2025, "
                "schools, pupils, roads_km, founded_year. "
                "For population density, call lookup separately "
                "for population_2025 and area_km2, then use "
                "calculate to divide population by area. "
                "Use corrected 2025 data and ignore archived profiles. "
                "Return the value, unit and source ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "district": {"type": "string"},
                    "field": {"type": "string"}
                },
                "required": ["district", "field"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Safely calculate arithmetic expressions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        }
    }
]

SYSTEM = """
Answer Nine Rivers questions using lookup and calculate.
Never invent facts. Apply corrections and check units.
Use calculate for arithmetic.
Return exactly: ANSWER: <name or yes/no> | <number>. Round the final number to one decimal place for Q-09. Do not add units or extra text after the number. Example: ANSWER: Millbrook | 0.6
If information is missing, return UNANSWERED.
"""

def run_agent(question, question_id="Q-test", client=None, tools=None):
    client = client or OpenAI(timeout=90, max_retries=2)
    tools = tools or TOOLS

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question}
    ]

    log = {
        "question_id": question_id,
        "question": question,
        "answer": "UNANSWERED",
        "status": "unanswered",
        "tool_calls": [],
        "input_tokens": 0,
        "output_tokens": 0
    }

    start = time.perf_counter()

    try:
        for round_no in range(1, MAX_ROUNDS + 1):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                reasoning_effort="none"
            )

            msg = response.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))

            log["input_tokens"] += response.usage.prompt_tokens
            log["output_tokens"] += response.usage.completion_tokens

            if not msg.tool_calls:
                log["answer"] = msg.content or "UNANSWERED"
                log["status"] = (
                    "answered" if "ANSWER:" in log["answer"]
                    else "unanswered"
                )
                break

            for call in msg.tool_calls:
                try:
                    args = json.loads(call.function.arguments)
                    if not isinstance(args, dict):
                        raise ValueError("Arguments must be an object")

                    if call.function.name == "lookup":
                        if set(args) != {"district", "field"}:
                            raise ValueError("Invalid lookup arguments")
                        result = lookup(**args)

                    elif call.function.name == "calculate":
                        if set(args) != {"expression"}:
                            raise ValueError("Invalid calculate arguments")
                        result = calculate(**args)

                    else:
                        result = {"error": "Unknown tool"}

                except (ValueError, TypeError) as e:
                    result = {"error": str(e)}

                log["tool_calls"].append({
                    "round": round_no,
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                    "result": result
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })

        log["rounds"] = round_no

    except Exception as e:
        log["status"] = "api_error"
        log["error"] = str(e)
        log["rounds"] = 0

    log["seconds"] = round(time.perf_counter() - start, 3)
    log["tool_call_count"] = len(log["tool_calls"])
    log["conversation"] = messages

    output = Path("outputs/b3")
    output.mkdir(parents=True, exist_ok=True)

    (output / f"{question_id}.json").write_text(
        json.dumps(log, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return log
