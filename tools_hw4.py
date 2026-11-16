
import ast
import json
import re
import math
import operator
import difflib
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "corpus.jsonl"

with open(DATA_PATH, encoding="utf-8") as f:
    corpus = [json.loads(line) for line in f if line.strip()]

profiles = {
    d["title"].split(" district profile")[0]: d
    for d in corpus
    if "district profile (2025)" in d["title"]
}

FIELDS = {
    "population_2025": [
        r"2025 census (?:recorded|counted) ([\d,]+) residents",
        r"([\d,]+) in 2025"
    ],
    "population_2020": [
        r"2020 census had recorded ([\d,]+)",
        r"([\d,]+) in 2020",
        r"up from ([\d,]+) at the 2020 census"
    ],
    "area_km2": [
        r"covers ([\d,.]+) square kilometres",
        r"over ([\d,.]+) square kilometres",
        r"on an area of ([\d,.]+) square kilometres"
    ],
    "budget_2025": [
        r"budget for 2025 was set at ([\d,.]+) million",
        r"2025 budget amounted to ([\d,.]+) million",
        r"2025 budget was ([\d,.]+) million"
    ],
    "water_2025": [
        r"water use in 2025 came to ([\d,]+) megalitres",
        r"used ([\d,]+) megalitres",
        r"used ([\d,]+) cubic metres"
    ],
    "schools": [
        r"There are (\d+) schools",
        r"has (\d+) schools",
        r"runs (\d+) schools"
    ],
    "pupils": [
        r"attended by ([\d,]+) pupils",
        r"enrolled ([\d,]+) pupils",
        r"with ([\d,]+) pupils enrolled"
    ],
    "roads_km": [
        r"network is ([\d,.]+) km",
        r"keeps ([\d,.]+) km",
        r"maintains ([\d,.]+) km"
    ],
    "founded_year": [
        r"founded in (\d{4})"
    ]
}

UNITS = {
    "population_2025": "residents",
    "population_2020": "residents",
    "area_km2": "km2",
    "budget_2025": "million tenge",
    "water_2025": "megalitres",
    "schools": "schools",
    "pupils": "pupils",
    "roads_km": "km",
    "founded_year": "year"
}

def lookup(district, field):
    try:
        if not isinstance(district, str) or not isinstance(field, str):
            return {"error": "District and field must be strings"}

        if len(district) > 100 or len(field) > 100:
            return {"error": "Input is too long"}

        district = district.strip()
        field = field.strip()

        if district not in profiles:
            suggestions = difflib.get_close_matches(
                district, profiles.keys(), n=2, cutoff=0.5
            )
            return {
                "error": "Unknown district",
                "suggestions": suggestions
            }

        if field == "water_tariff_2025":
            tariff = next(d for d in corpus if d["id"] == "NR-15")
            match = re.search(
                r"tariff is ([\d.]+) tenge per cubic metre",
                tariff["text"], re.I
            )
            if not match:
                return {"error": "Tariff not found"}
            return {
                "value": float(match.group(1)),
                "unit": "tenge/m3",
                "source": "NR-15"
            }

        if field not in FIELDS:
            return {"error": "Unknown field: " + field}

        if district == "Brightwater" and field == "area_km2":
            correction = next(d for d in corpus if d["id"] == "NR-16")
            match = re.search(
                r"correct area is ([\d.]+)",
                correction["text"], re.I
            )
            if not match:
                return {"error": "Correction not found"}
            return {
                "value": float(match.group(1)),
                "unit": "km2",
                "source": "NR-16"
            }

        doc = profiles[district]

        for pattern in FIELDS[field]:
            match = re.search(pattern, doc["text"], re.I)
            if match:
                value = float(match.group(1).replace(",", ""))

                if field == "water_2025" and "cubic metres" in match.group(0):
                    value /= 1000

                return {
                    "value": value,
                    "unit": UNITS[field],
                    "source": doc["id"]
                }

        return {"error": "Field not found in current profile"}

    except Exception as e:
        return {"error": str(e)}


OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv
}

def calculate(expression):
    try:
        if not isinstance(expression, str):
            return {"error": "Expression must be a string"}

        if not expression.strip() or len(expression) > 200:
            return {"error": "Invalid expression length"}

        tree = ast.parse(expression, mode="eval")

        if sum(1 for _ in ast.walk(tree)) > 100:
            return {"error": "Expression is too complex"}

        def solve(node):
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                value = node.value

            elif isinstance(node, ast.BinOp) and type(node.op) in OPS:
                left = solve(node.left)
                right = solve(node.right)
                value = OPS[type(node.op)](left, right)

            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
                value = solve(node.operand)
                if isinstance(node.op, ast.USub):
                    value = -value

            else:
                raise ValueError("Unsupported operation")

            if not math.isfinite(value) or abs(value) > 1e12:
                raise ValueError("Number too large")

            return value

        return {"result": solve(tree.body)}

    except (SyntaxError, ValueError, ZeroDivisionError,
            OverflowError, RecursionError) as e:
        return {"error": str(e)}
