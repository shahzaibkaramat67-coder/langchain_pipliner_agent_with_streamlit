import json


def json_response_function(data):
    plan_custom_methond = data.replace("```json", "").replace("```", "").strip()
    content = json.loads(plan_custom_methond)
    return content
