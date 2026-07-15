class StepFormat:
    op: str
    inputs: list[str | int | float]
    output: str

    def __init__(self, step_dict: dict):
        self.op = step_dict["op"]
        self.inputs = step_dict["inputs"]
        self.output = step_dict["output"]


class JsonFormat:
    field: str
    params: list[str]
    steps: list[StepFormat]

    def __init__(self, rule_dict: dict):
        self.field = rule_dict["field"]
        self.params = rule_dict["params"]
        self.steps = [StepFormat(step) for step in rule_dict["steps"]]
