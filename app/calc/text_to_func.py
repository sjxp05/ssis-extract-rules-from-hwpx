from app.calc.constants import CONSTANTS
from app.calc.json_format import JsonFormat, StepFormat
import math
import json

rule_sentences = """
[
    {
        "field": "본인부담금",
        "steps": [
            {"op": "lookup_default", "inputs": ["등급", "본인부담률", 0], "output": "rate"},
            {"op": "multiply", "inputs": ["월한도액", "rate"], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -2], "output": "temp2"},
            {"op": "cap_max", "inputs": ["temp2", "본인부담금상한액"], "output": "temp3"},
            {"op": "lookup_default", "inputs": ["등급", "본인부담금_고정액", "temp3"], "output": "본인부담금"}
        ]
    },
    {
        "field": "확장형본인부담금",
        "steps": [
            {"op": "lookup_default", "inputs": ["등급", "본인부담률", 0], "output": "rate"},
            {"op": "multiply", "inputs": ["확장형월한도액", "rate"], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -2], "output": "temp2"},
            {"op": "cap_max", "inputs": ["temp2", "본인부담금상한액"], "output": "temp3"},
            {"op": "lookup_default", "inputs": ["등급", "확장형본인부담금_고정액", "temp3"], "output": "확장형본인부담금"}
        ]
    },
    {
        "field": "확장형월한도액",
        "steps": [
            {"op": "multiply", "inputs": ["기본단가", 22], "output": "temp1"},
            {"op": "subtract", "inputs": ["월한도액", "temp1"], "output": "temp2"},
            {"op": "roundup", "inputs": ["temp2", -3], "output": "확장형월한도액"}
        ]
    },
    {
        "field": "활동보조30분",
        "steps": [
            {"op": "multiply", "inputs": ["기본단가", 0.5], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -1], "output": "활동보조30분"}
        ]
    },
    {
        "field": "활동보조30분심야",
        "steps": [
            {"op": "multiply", "inputs": ["기본단가", 0.5], "output": "temp1"},
            {"op": "rounddown", "inputs": ["temp1", -1], "output": "temp2"},
            {"op": "multiply", "inputs": ["temp2", 1.5], "output": "temp3"},
            {"op": "rounddown", "inputs": ["temp3", -1], "output": "활동보조30분심야"}
        ]
    },
    {
        "field": "방문목욕40분",
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


def resolve_step_inputs(step: StepFormat, variables: dict, params: dict):
    resolved = []
    for raw in step.inputs:
        if type(raw) is str and raw in params:
            resolved.append(params[raw])
        else:
            resolved.append(resolve_operand(raw, variables))
    return resolved


def round_down(value, digits):
    factor = 10 ** (-digits)
    return math.floor(value / factor) * factor


def round_up(value, digits):
    factor = 10 ** (-digits)
    return math.ceil(value / factor) * factor


def calculate_step(step: StepFormat, variables: dict, params: dict):
    opnds = resolve_step_inputs(step, variables, params)

    if step.op == "add":
        output_value = opnds[0] + opnds[1]
    elif step.op == "subtract":
        output_value = opnds[0] - opnds[1]
    elif step.op == "multiply":
        output_value = opnds[0] * opnds[1]
    elif step.op == "divide":
        output_value = opnds[0] / opnds[1]
    elif step.op == "rounddown":
        output_value = round_down(opnds[0], opnds[1])
    elif step.op == "roundup":
        output_value = round_up(opnds[0], opnds[1])
    elif step.op == "cap_max":
        output_value = opnds[1] if opnds[0] > opnds[1] else opnds[0]
    elif step.op == "lookup_default":
        key, table, default = opnds
        output_value = table.get(key, default)
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
        calculate_step(step, variables, params)

    return variables[field_name]
