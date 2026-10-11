# Pipeline Project Analysis

## Goal understood

The intended flow is:

1. Receive a user query.
2. Decide whether the query is simple or needs planning.
3. For a planned query, choose the next tool.
4. Execute the tool.
5. Put the tool result back into shared state.
6. Let the planner inspect the updated state and choose the next step.
7. Evaluate the accumulated answer for correctness, relevance, and completeness.
8. If rejected, include the evaluator reason and correction in the next planning cycle.
9. If approved, generate the final answer.

This is a single iterative agent with an orchestrator loop. It does not need a separate autonomous agent for every step. A separate top-level router is useful only for deciding whether a request can be answered directly or needs the loop.

## Current mistakes

### 1. Planner output is untyped and not guaranteed to be JSON

`planner.py` defines a Pydantic `plan` model but never uses it. `invoke()` returns an OpenAI response, and the planner returns raw text. `pipliner.py` then removes code fences and calls `json.loads()`.

This breaks when the model returns commentary, invalid JSON, a missing field, or an unsupported tool. The declared schema provides no protection because it is not connected to the model call.

**Fix:** use structured output if the selected model supports it, or parse and validate the JSON immediately with `Plan.model_validate_json()`. Reject unknown tools and invalid inputs before execution.

### 2. The rejection branch calls the planner with the wrong object

In `pipliner.py`:

```python
planner(state.evaluator)
```

The planner expects a `State`, because it calls `state.model_dump_json()`. `state.evaluator` is only the evaluator result. The planner therefore loses the user query, search results, research results, and history. The returned plan is also ignored.

**Fix:** store the evaluator decision in state, then continue the loop. On the next iteration call `planner(state)` and assign its validated result to `state.plan`.

### 3. Evaluator output is treated as a dictionary even though it is a string

`evaluate.py` returns `response.choices[0].message.content`, which is raw text. `pipliner.py` assigns that text to `state.evaluator` and then uses:

```python
if evaluate["evaluator"] == "rejected":
```

This raises a string-indexing error unless the evaluator is changed to return a parsed dictionary. The evaluator also receives only the latest tool result, not the original request and accumulated evidence.

**Fix:** define an `Evaluation` Pydantic model, parse the response into it, and evaluate at least `user_input`, accumulated search/research results, and the proposed answer.

### 4. The pipeline generates a final answer even after rejection

The final-answer code runs after the rejection block regardless of the decision. The call to the planner in the rejection branch does not `continue`, so a rejected result can immediately produce a final answer.

**Fix:** use an explicit branch:

```python
if evaluation.status == "rejected":
    continue
if evaluation.status == "approved":
    return final_result(state)
```

Also stop with a clear failure message after the maximum number of iterations.

### 5. Search output and research input have incompatible shapes

`tools.search()` returns a list of URL strings. The planner is asked to produce `tool_input` as a string. `executer.py` passes that string directly to `resaerch()`. Since `resaerch()` loops over its input, a string can be processed one character at a time instead of one URL at a time.

**Fix:** make the plan input typed by tool, or keep research input in state. For example, let the research plan contain `urls: list[str]`, or have the executor call research with the URLs already stored in `state.search_result`.

### 6. The planner is not explicitly told when to finish

The prompt lists `search` and `research`, but the executor has a `none` branch and the planner schema has no finish action. There is no reliable contract for deciding that enough evidence exists and that evaluation/finalization should happen.

**Fix:** make the planner action an enum such as `search`, `research`, `draft`, or `finish`. The orchestrator should handle `finish` by creating a draft and sending it to the evaluator.

### 7. Evaluation is disconnected from the actual answer

The evaluator receives `state.result`, which is only the latest tool output. It cannot determine whether the complete response answers the user's request. It also does not receive the user's requirements in its input payload.

**Fix:** evaluate a draft answer against the original query and the evidence collected so far. Tool-result quality and final-answer quality are different checks.

### 8. The final-answer model call receives the wrong content type

`final_result()` passes the Pydantic `State` object directly as the `content` value to the OpenAI client. OpenAI chat message content should be text or a supported content structure. Serialize the state first, for example with `state.model_dump_json()`.

### 9. State mutation is weakly validated

`state.plan = planner_result` assigns a plain dictionary to a Pydantic field after the model has been created. Depending on Pydantic configuration, assignment validation may not happen. Later code assumes `state.plan` supports dictionary indexing.

**Fix:** validate explicitly:

```python
state.plan = Plan.model_validate(planner_result)
```

Use attribute access consistently: `state.plan.tool` and `state.plan.tool_input`.

### 10. The evaluator decision is not parsed or validated

The evaluator prompt requests JSON, but prompt instructions alone do not guarantee JSON. There is no handling for malformed JSON, missing status, or an unexpected decision.

**Fix:** parse into a strict model such as `Evaluation(status, reason, correction)` and treat parse failure as a controlled error that can trigger one retry or a terminal failure.

### 11. Memory currently has no effect

`Memory()` is created inside `pipliner()` on every request, only the final answer is stored, and the stored memory is never read by the planner or final answer. The `Memory` instance in `main.py` is separate and also unused.

**Fix:** either remove memory until it is needed, or create one memory instance at application scope and explicitly inject relevant memories into the initial state. Do not call it conversation memory if it only stores the current final answer.

### 12. The research tool is fragile for real web pages

`requests.get()` has no user-agent, does not verify that the response is HTML, and one failed URL aborts the entire research step. It also concatenates unlimited page text, which can exceed the model context window.

**Fix:** handle each URL independently, use a bounded character/token budget, record per-URL errors, and preserve source URLs with extracted text. This is especially important for research quality and evaluator traceability.

### 13. Configuration and naming make debugging harder

There are several typos and ambiguous names: `pipliner`, `executer`, `resaerch`, `reserach_result`, `max_itrate`, and `mian.py` in the broader projects. They do not all cause immediate runtime failure, but they make imports and maintenance error-prone. `agent.py` also prints configuration details during import.

**Fix:** rename gradually when touching modules, use `pipeline`, `executor`, `research`, `research_result`, and `max_iterations`, and validate required environment variables at startup without printing secrets or configuration noise.

## Recommended architecture

Use one shared state and one explicit orchestrator. Keep the planner, executor, evaluator, and final-answer generator as ordinary functions with typed input/output.

```text
user query
   |
   v
router: simple? --------------------> direct answer
   |
   v
planner(state)
   |
   v
executor(plan, state)
   |
   v
state.evidence and state.history updated
   |
   +--> planner chooses another tool --------+
   |                                         |
   +--> planner chooses draft                 |
                    |                        |
                    v                        |
              draft answer                   |
                    |                        |
                    v                        |
              evaluator(state)               |
                |             |              |
             approved       rejected         |
                |             |              |
                v             +--> state.evaluator -> planner
          final answer
```

The important rule is that every cycle receives the complete state. A rejection is feedback, not a separate input that replaces the state.

## Suggested typed contracts

```python
class Plan(BaseModel):
    action: Literal["search", "research", "draft"]
    query: str | None = None
    urls: list[str] = Field(default_factory=list)
    reason: str


class Evaluation(BaseModel):
    status: Literal["approved", "rejected"]
    reason: str
    correction: str


class State(BaseModel):
    user_input: str
    search_results: list[SearchResult] = Field(default_factory=list)
    research_results: list[ResearchResult] = Field(default_factory=list)
    draft: str = ""
    plan: Plan | None = None
    evaluation: Evaluation | None = None
    history: list[AgentHistory] = Field(default_factory=list)
```

Avoid storing arbitrary strings where the next component expects a dictionary or list. The type boundary is the main reliability boundary in this system.

## Orchestrator behavior

A robust loop should do the following:

1. Initialize `State(user_input=query)`.
2. If a router says the request is simple, call the final-answer function once with no tools.
3. Otherwise call `planner(state)`.
4. Validate the plan.
5. Execute exactly one action.
6. Update evidence and history.
7. If the action is `draft`, generate a draft and evaluate it.
8. If rejected, save the reason and correction and continue with the same state.
9. If approved, return the final answer.
10. Enforce a maximum step count and return a controlled incomplete-result message when reached.

Do not let the planner execute tools itself. Do not let the executor decide whether the answer is good. Do not let the evaluator replace the shared state.

## Priority order for implementation

1. Fix parsing and validation for `Plan` and `Evaluation`.
2. Fix the rejection loop so it preserves and updates `State`.
3. Fix the search-to-research data contract.
4. Add an explicit `draft` action and evaluate the draft, not a raw tool result.
5. Serialize state before sending it to the final-answer model.
6. Add the simple-query router after the planned loop works.
7. Add bounded, fault-tolerant web extraction and useful source metadata.
8. Add tests for: search then research, rejected then replanned, approved final answer, malformed planner JSON, malformed evaluator JSON, and maximum iterations.

## Bottom line

The project has the right high-level idea, but its current implementation is not yet a reliable iterative agent. The largest blockers are unvalidated LLM output, incompatible data shapes, the broken rejection branch, and finalization after rejection. Fix those control-flow and type-boundary problems before adding more agents or tools. A single orchestrator with a typed shared state is sufficient for the behavior you described.
