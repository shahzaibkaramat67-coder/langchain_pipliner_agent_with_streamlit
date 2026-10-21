from planner import planner
from memory import Memory
from executer import execute
from tools import search, resaerch
from evaluate import evaluator
from final_answer import final_result
import json
from typing import Callable
from api_settings import APISettings
from rich import print
from state import State, AgentHistory


# def pipliner(query, stack, memory):
def pipliner(
    state: State,
    progress_callback: Callable[[str], None] | None = None,
    settings: APISettings | None = None,
):

    memory = Memory()

    max_itrate = 5
    for step in range(max_itrate):
        if progress_callback:
            stage = (
                "Planner is planning a follow-up step..."
                if step
                else "Planner is analyzing your request..."
            )
            progress_callback(stage)
        print("INPUT ENTERING INTO THE PANNING.....")
        planner_result = planner(state, settings)
        print("plan_result :", planner_result)

        print("THE PLANNER RETUENING THE RESPONSE.....")
        # plan_result = planner(query, memory, stack)
        print("\n\n\n Plan :", planner_result, "\n\n")

        state.plan = planner_result
        state.history.append(
            AgentHistory(
                agent="planner", input=str(state.user_input), output=str(state.plan)
            )
        )
        print("HISTORY UPDATE SUCCESSFULLY.....")
        # stack["plan_result"] = plan_result

        if progress_callback:
            tool = planner_result.get("tool")
            stage = {
                "search": "Search agent is searching the web...",
                "research": "Research agent is investigating source pages...",
                "none": "Pipeline is preparing the findings for evaluation...",
            }.get(tool, "Pipeline is executing the planned step...")
            progress_callback(stage)
        print("NOW FLOW ENTERING INTO THE EXECUTE.....")
        state.result = execute(state, settings)
        print("NOW THE EXECUTION IS DONE.....")
        state.history.append(
            AgentHistory(
                agent="execute", input=str(state.plan), output=str(state.result)
            )
        )

        print("HISTORY UPDATE SUCCESSFULLY.....")
        # memory.add_memory({executor})
        # stack
        # stack["executor"] = executor

        if progress_callback:
            progress_callback("Evaluator is checking the gathered information...")
        print("NOW FLOW ENTERING INTO THE evaluator.....")
        evaluate = evaluator(state.user_input, state.result, state.history, settings)
        state.evaluator = evaluate
        print("NOW THE evaluator IS DONE.....")
        state.history.append(
            AgentHistory(
                agent="evaluator", input=str(state.result), output=str(evaluate)
            )
        )

        print("HISTORY UPDATE SUCCESSFULLY.....")
        if evaluate["evaluator"] == "rejected":
            print("Reason:", evaluate["reason"])
            print("Correction:", evaluate["correction"])
            continue

        if evaluate["evaluator"] == "approved":
            if progress_callback:
                progress_callback("Final answer agent is preparing your answer...")
            print("NOW EVALUATION APPROVED NOW PREPAIRING FOR THE FINAL RESPONSE .....")
            result = final_result(state, settings)
            return result
        memory.add_memory(result, "AI")
        return result
    return "Maximum iterations reached without an approved result."

    # Tool = plan_result["tool"]
    # if Tool == "search":
    #     search_result = search(plan_result["tool_input"])
    #     memory.add_memory(Tool, search_result)
    #     stack.append({"Tool": Tool, "Tool_output": search_result})
    # elif Tool == "research":
    #     research_result = resaerch(plan_result["tool_input"])
    #     memory.add_memory(Tool, research_result)
    #     stack.append({"Tool": Tool, "Tool_output": research_result})
    # elif Tool == "none":
    #     memory.add_memory(Tool, "no tool use")
    #     stack.append({"Tool": Tool, "Tool_output": "no output comes"})
    # plan_custom_methond = (
    #     plan_result.replace("```json", "").replace("```", "").strip()
    # )

    # print("plan_custom_methond :", plan_custom_methond)

    # planner_result = json.loads(plan_custom_methond)
    # print("planner_result with json : ", planner_result)
