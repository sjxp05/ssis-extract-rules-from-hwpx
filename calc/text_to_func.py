from calc.constants import CONSTANTS
from calc.json_format import JsonFormat, StepFormat
import math
import json

rule_sentences = """
[
    {
        "field": "본인부담금",
        "params": ["월한도액", "본인부담률", "본인부담금상한액"],
        "steps": [
            {"op": "multiply", "inputs": ["월한도액", "본인부담률"], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -2], "output": "temp2"},
            {"op": "cap_max", "inputs": ["temp2", "본인부담금상한액"], "output": "본인부담금"}
        ]
    },
    {
        "field": "확장형월한도액",
        "params": ["월한도액", "기본단가"],
        "steps": [
            {"op": "multiply", "inputs": ["기본단가", 22], "output": "temp1"},
            {"op": "subtract", "inputs": ["월한도액", "temp1"], "output": "temp2"},
            {"op": "roundup", "inputs": ["temp2", -3], "output": "확장형월한도액"}
        ]
    },
    {
        "field": "활동보조30분",
        "params": ["기본단가"],
        "steps": [
            {"op": "multiply", "inputs": ["기본단가", 0.5], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -1], "output": "활동보조30분"}
        ]
    },
    {
        "field": "활동보조30분심야",
        "params": ["기본단가"],
        "steps": [
            {"op": "multiply", "inputs": ["기본단가", 0.5], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -1], "output": "temp2"},
            {"op": "multiply", "inputs": ["temp2", 1.5], "output": "temp3"},
            {"op": "rounddown", "inputs": ["temp3", -1], "output": "활동보조30분심야"}
        ]
    },
    {
        "field": "방문목욕40분",
        "params": ["방문목욕기본단가"],
        "steps": [
            {"op": "multiply", "inputs": ["방문목욕기본단가", 0.8], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -1], "output": "방문목욕40분"}
        ]
    }
]
"""

rules_dict = json.loads(rule_sentences)

rules_json = [JsonFormat(s) for s in rules_dict]


def resolve_operand(operand, variables: dict):
    if type(operand) is str:
        if operand in CONSTANTS:
            return CONSTANTS[operand]
        return variables[operand]
    return operand


def round_down(value, digits):
    factor = 10 ** (-digits)
    return math.floor(value / factor) * factor


def round_up(value, digits):
    factor = 10 ** (-digits)
    return math.ceil(value / factor) * factor


def calculate_step(step: StepFormat, variables: dict, opnd1=None, opnd2=None):
    if opnd1 is None:
        opnd1 = resolve_operand(step.inputs[0], variables)
    if opnd2 is None:
        opnd2 = resolve_operand(step.inputs[1], variables)

    if step.op == "add":
        output_value = opnd1 + opnd2
    elif step.op == "subtract":
        output_value = opnd1 - opnd2
    elif step.op == "multiply":
        output_value = opnd1 * opnd2
    elif step.op == "divide":
        output_value = opnd1 / opnd2
    elif step.op == "rounddown":
        output_value = round_down(opnd1, opnd2)
    elif step.op == "roundup":
        output_value = round_up(opnd1, opnd2)
    elif step.op == "cap_max":
        output_value = opnd2 if opnd1 > opnd2 else opnd1
    else:
        raise ValueError(f"Unknown op: {step.op}")

    variables[step.output] = output_value
    return output_value


def calculate_field(field_name: str, params: dict = None):
    params = params or {}

    rule = next((r for r in rules_json if r.field == field_name), None)
    if rule is None:
        raise ValueError(f"Unknown field: {field_name}")

    variables = {}
    for step in rule.steps:
        opnd1 = params.get(step.inputs[0])
        opnd2 = params.get(step.inputs[1])
        calculate_step(step, variables, opnd1, opnd2)

    return variables[field_name]


print(
    calculate_field(
        "본인부담금",
        {
            "월한도액": CONSTANTS["월한도액"][13],
            "본인부담률": CONSTANTS["본인부담률"]["다"],
        },
    )
)

print(calculate_field("활동보조30분심야"))
