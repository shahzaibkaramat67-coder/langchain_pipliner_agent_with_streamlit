# from agent import model
from api_settings import APISettings
from tools import resaerch, search_web
from state import State


def execute(state, settings: APISettings | None = None):
    plan = state.plan
    # tool_input = plan.get("tool_input")
    if plan["tool"] == "search":
        search_result = search_web(
            plan["tool_input"],
            settings.tavily_api_key if settings else None,
        )
        state.search_result.append({"Tool": plan["tool"], "Result": search_result})
        return search_result

    elif plan["tool"] == "research":
        reserach_result = resaerch.invoke({"urls": plan["tool_input"]})
        state.reserach_result.append({"Tool": plan["tool"], "Result": reserach_result})
        return reserach_result

    elif plan["tool"] == "none":
        return None
