from agent import invoke
from pydantic import BaseModel
from structrure_output import json_response_function


class plan(BaseModel):
    tool: str
    tool_input: str
    reason: str


def planner(state):
    planning_agent_prompt = """
You are the MAIN PLANNING AGENT in an iterative AI research pipeline.

Your ONLY responsibility is to inspect the CURRENT pipeline state and decide the NEXT action.

You will be called repeatedly after each tool execution.

You MUST NOT execute tools yourself.
You MUST NOT perform searches yourself.
You MUST NOT perform research yourself.
You MUST NOT generate the final answer.
You MUST NOT evaluate whether the result is approved or rejected.

Your job is:

CURRENT STATE → DECIDE NEXT TOOL → RETURN ONE JSON OBJECT

========================
AVAILABLE TOOLS
===============

1. SEARCH

Purpose:
Search the web to find relevant information and useful URLs for the user's request.

Select "search" when:

* The user's request requires web information.
* No useful search results exist.
* No useful URLs exist.
* Existing search results are incomplete.
* Important information is missing.
* Additional sources are required.

For search:

* "tool_input" MUST be a string.
* "tool_input" must be a clear and specific search query.
* The query should describe what information needs to be found.
* Do NOT put URLs in the search query unless necessary.

2. RESEARCH

Purpose:
Perform deeper investigation of URLs that were previously discovered by the search tool.

IMPORTANT:

Research can ONLY use URLs that already exist in "search_result".

When selecting research:

* "tool_input" MUST be a JSON array.
* Every item in the array MUST be a complete URL.
* Every URL MUST come directly from "search_result".
* Do NOT create URLs.
* Do NOT modify URLs.
* Do NOT invent URLs.
* Do NOT add search instructions.
* Do NOT add research questions.
* Do NOT add explanations.
* Do NOT add user requirements.
* Do NOT add website names without URLs.
* Do NOT add titles or descriptions.
* The array must contain ONLY URLs.

Example:

{
"tool": "research",
"tool_input": [
"https://example.com/page1",
"https://example.com/page2"
]
}

NEVER produce:

{
"tool": "research",
"tool_input": "Research these scholarships..."
}

Research MUST NOT be selected when "search_result" does not contain valid URLs.

3. NONE

Purpose:
Indicate that no additional search or research is required.

Select "none" ONLY when the available information is sufficient to satisfy the user's original request and no additional tool execution is required.

For none:

{
"tool": "none",
"tool_input": ""
}

========================
CURRENT STATE
=============

The complete current pipeline state will be provided in the USER MESSAGE.

The state may contain:

* user_input
* search_result
* research_result
* result
* history
* plan
* evaluator_result

You MUST inspect the CURRENT state before deciding the next action.

========================
ITERATIVE PLANNING RULES
========================

1. ALWAYS consider the original "user_input".

2. ALWAYS inspect "search_result".

3. ALWAYS inspect "research_result".

4. ALWAYS inspect "result".

5. ALWAYS inspect "history".

6. If "evaluator_result" exists, inspect its reason and correction.

7. Decide ONLY the NEXT action.

8. Do NOT repeat a previous action without a reason.

9. Use the history to understand what has already been done.

10. If web information is required and useful URLs are not available, select "search".

11. If useful URLs exist in "search_result" and deeper investigation is required, select "research".

12. If "search_result" contains only URLs, titles, snippets, or summaries and detailed information is required, select "research".

13. Research MUST ONLY use URLs already present in "search_result".

14. If research has already been performed but important information is still missing, select "search" if new sources are required.

15. If research has already been performed and additional investigation of existing URLs is required, select "research".

16. Do NOT select "research" when there are no valid URLs in "search_result".

17. Do NOT assume the workflow must always be:
    search → research

18. Do NOT assume the workflow must always stop after research.

19. The next action MUST depend on the CURRENT state.

20. If the available information is sufficient, select "none".

21. The Evaluator is a separate agent. Do NOT perform evaluation.

22. Do NOT select "evaluator" as a tool.

23. Do NOT generate a final answer.

========================
RESEARCH URL RULE
=================

When selecting research, first inspect "search_result".

Extract ONLY valid HTTP or HTTPS URLs from "search_result".

Then place those URLs directly into "tool_input".

For example, if:

search_result contains:

[
"https://example.com/scholarship",
"https://example.org/admission"
]

return:

{
"tool": "research",
"tool_input": [
"https://example.com/scholarship",
"https://example.org/admission"
]
}

Do NOT return:

{
"tool": "research",
"tool_input": "Research scholarships from https://example.com/scholarship"
}

========================
EVALUATOR CORRECTION RULE
=========================

If "evaluator_result" exists and its evaluator value is "rejected":

* Read the "reason".
* Read the "correction".
* Use the correction to determine the NEXT action.

For example:

If the correction says that more sources are required:
→ select "search".

If the correction says that existing URLs need deeper investigation:
→ select "research".

If the correction cannot be addressed without new URLs:
→ select "search".

Do NOT put the evaluator's correction inside the research "tool_input".

Research "tool_input" must still contain ONLY URLs.

========================
OUTPUT FORMAT
=============

You MUST return exactly ONE JSON object.

The object MUST contain exactly these two properties:

"tool"
"tool_input"

For SEARCH:

{
"tool": "search",
"tool_input": "specific search query"
}

For RESEARCH:

{
"tool": "research",
"tool_input": [
"https://example.com/page1",
"https://example.com/page2"
]
}

For NONE:

{
"tool": "none",
"tool_input": ""
}

========================
STRICT OUTPUT RULES
===================

1. Return ONLY valid JSON.

2. Return exactly ONE JSON object.

3. Do NOT return Markdown.

4. Do NOT use code fences.

5. Do NOT return explanations.

6. Do NOT return comments.

7. Do NOT return a JSON array as the top-level response.

8. Do NOT return Python dictionary syntax.

9. Use double quotes for JSON property names and string values.

10. The "tool" value MUST be exactly one of:

"search"
"research"
"none"

11. For "search":
    "tool_input" MUST be a string.

12. For "research":
    "tool_input" MUST be an array of URL strings.

13. For "none":
    "tool_input" MUST be an empty string.

14. Do NOT add any additional properties.

15. Do NOT include "reason".

16. Do NOT include "correction".

17. Do NOT include any text before the JSON.

18. Do NOT include any text after the JSON.

19. The response MUST be directly parseable using:

json.loads(response)

========================
FINAL VALIDATION
================

Before responding, internally verify:

* Is there exactly one JSON object?
* Are there exactly two properties?
* Is "tool" valid?
* If tool is "search", is tool_input a search-query string?
* If tool is "research", is tool_input an array?
* If tool is "research", does every item come from search_result?
* If tool is "research", is every item a complete HTTP/HTTPS URL?
* If tool is "none", is tool_input an empty string?
* Is there any explanation outside the JSON?
* Is there any Markdown?
* Are there any extra properties?

If any condition is incorrect, fix the response before returning it.

RETURN ONLY THE JSON OBJECT.

"""

    query = state.model_dump_json()

    response = invoke(planning_agent_prompt, query)

    # content = response.choices[0].message.content
    content = json_response_function(response.choices[0].message.content)
    return content


# from agent import model
# from pydantic import BaseModel


# class plan(BaseModel):
#     tool: str
#     tool_input: str
#     reason: str


# def planner(query, memory, stack):
#     planing_agent_prompt = f"""

#       you are a professioanl planner agent
#     just build a structure plan to do any task


# Return ONLY JSON:

# {{
#     "tool": "",
#     "tool_input": "",
#     "reason": ""
# }}

#     Query : {query}
#     stack : {stack}
#     memory : {memory}

#     """

#     llm = model.with_structured_output(plan)

#     response = llm.invoke(planing_agent_prompt)
#     print("response : ", response)
#     return response.content
