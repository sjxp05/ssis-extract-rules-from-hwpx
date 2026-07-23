import json
import math
from app.calc.json_format import FieldFormat, StepFormat
from app.calc.constants import CONSTANTS, LOOKUP_MAPPINGS

with open("form.json", "r", encoding="utf-8") as f:
    data: list = json.load(f)

rules = [FieldFormat(d) for d in data]


def resolve_inputs(inputs: list, variables: dict) -> list:
    resolved = []
    for i in inputs:
        if i in variables.keys():
            resolved.append(variables[i])
            continue

        if i in CONSTANTS.keys():
            value = CONSTANTS[i]
            if value is not dict:
                resolved.append(value)
                continue

        resolved.append(i)
    return resolved


def round_down(value, digits):
    factor = 10 ** (-digits)
    return math.floor(value / factor) * factor


def round_up(value, digits):
    factor = 10 ** (-digits)
    return math.ceil(value / factor) * factor


def calculate_step(step: StepFormat, variables: dict):
    opnds = resolve_inputs(step.inputs, variables)
    print(opnds)

    if step.op == "add":
        result = sum(opnds)
    elif step.op == "subtract":
        result = opnds[0] - opnds[1]
    elif step.op == "multiply":
        result = opnds[0] * opnds[1]
    elif step.op == "rounddown":
        result = round_down(opnds[0], opnds[1])
    elif step.op == "roundup":
        result = round_up(opnds[0], opnds[1])
    elif step.op == "if_eq":
        if opnds[0] == opnds[1]:
            result = step.value
        else:
            return
    elif step.op == "cap_max":
        result = min(opnds)
    elif step.op == "lookup_constant":
        constant_name = LOOKUP_MAPPINGS["_".join(opnds)]
        result = CONSTANTS[constant_name]
    elif step.op == "lookup_table":
        table_name = LOOKUP_MAPPINGS[
            step.inputs[0] + (("_" + opnds[1]) if len(opnds) > 1 else "")
        ]
        result = CONSTANTS[table_name][opnds[0]]

    variables[step.output] = result


def calculate_field(field_name: str, params: dict = {}):
    rule = next((r for r in rules if r.field == field_name), None)

    variables = {}
    for k, v in params.items():
        variables[k] = v
    print(variables)

    for step in rule.steps:
        calculate_step(step, variables)

        if step.output == field_name and step.output in variables.keys():
            return variables[field_name]
