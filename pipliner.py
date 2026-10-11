from planner import planner
from memory import Memory
from executer import execute
from tools import search, resaerch
from evaluate import evaluator
from final_answer import final_result
import json
from rich import print
from state import State, AgentHistory


# def pipliner(query, stack, memory):
def pipliner(state: State):

    memory = Memory()

    max_itrate = 5
    for step in range(max_itrate):
        print("INPUT ENTERING INTO THE PANNING.....")
        planner_result = planner(state)
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

        print("NOW FLOW ENTERING INTO THE EXECUTE.....")
        state.result = execute(state)
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

        print("NOW FLOW ENTERING INTO THE evaluator.....")
        evaluate = evaluator(state.user_input, state.result, state.history)
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
            print("NOW EVALUATION APPROVED NOW PREPAIRING FOR THE FINAL RESPONSE .....")
            result = final_result(state)
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
