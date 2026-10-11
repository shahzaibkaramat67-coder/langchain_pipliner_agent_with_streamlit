# from agent import model
from tools import search, resaerch
from state import State


def execute(state):
    plan = state.plan
    # tool_input = plan.get("tool_input")
    if plan["tool"] == "search":
        search_result = search.invoke(plan["tool_input"])
        state.search_result.append({"Tool": plan["tool"], "Result": search_result})
        return search_result

    elif plan["tool"] == "research":
        reserach_result = resaerch.invoke({"urls": plan["tool_input"]})
        state.reserach_result.append({"Tool": plan["tool"], "Result": reserach_result})
        return reserach_result

    elif plan["tool"] == "none":
        return None
