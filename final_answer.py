from agent import invoke
from api_settings import APISettings
from structrure_output import json_response_function
import json


def final_result(state, settings: APISettings | None = None):

    system_prompt = """
You are a professional final response agent.

Your task is to generate the final answer for the user based on the information available in the provided state.

Use the relevant information from the state to answer the user's original request.

Rules:
* befor to the final responed make sure the formate follow the user requirnment
* Answer the user's request directly.
* Use the available results and information from the state.
* Do not mention internal agents, planning, evaluation, or orchestration.
* Do not invent information that is not supported by the state.
* If the available information is insufficient, clearly say so.
* Make the response clear, accurate, and well structured.
* Return only the final user-facing answer.

State:
"""

    data = json.dumps(state.model_dump())

    response = invoke(system_prompt, data, settings)
    # print("response", response.choices[0].message.content)
    # content = json_response_function(response.choices[0].message.content)
    return response.choices[0].message.content
