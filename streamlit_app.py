from typing import Any
from urllib.parse import urlsplit

from openai import APIConnectionError, OpenAIError
import streamlit as st
from dotenv import load_dotenv

from agent import invoke
from api_settings import APISettings
from state import State

load_dotenv()

st.set_page_config(
    page_title="Research assistant",
    page_icon=":material/travel_explore:",
    layout="wide",
)

SUGGESTIONS = [
    "Research the latest developments in AI",
    "Compare the best options for my goals",
    "Find reliable sources about a topic",
]

st.session_state.setdefault("messages", [])
st.session_state.setdefault("api_settings", APISettings.from_environment())


def get_missing_settings(settings: APISettings) -> list[str]:
    missing = [
        label
        for label, value in (
            ("Language model endpoint", settings.base_url),
            ("Language model API key", settings.api_key),
            ("Language model name", settings.model),
            ("Web search API key", settings.tavily_api_key),
        )
        if not value
    ]
    if settings.base_url and not has_valid_endpoint(settings.base_url):
        missing.insert(0, "A valid HTTP or HTTPS language model endpoint")
    return missing


def has_valid_endpoint(endpoint: str) -> bool:
    try:
        parsed = urlsplit(endpoint)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False


def get_model_endpoint_label(settings: APISettings) -> str:
    endpoint = settings.base_url
    try:
        parsed = urlsplit(endpoint)
        if not parsed.hostname:
            return "the configured language-model endpoint"
        port = parsed.port
    except ValueError:
        return "the configured language-model endpoint"
    return f"{parsed.hostname}:{port}" if port else parsed.hostname


def extract_source_urls(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.startswith(("https://", "http://")) else []
    if isinstance(value, dict):
        return [
            url
            for nested_value in value.values()
            for url in extract_source_urls(nested_value)
        ]
    if isinstance(value, (list, tuple)):
        return [url for item in value for url in extract_source_urls(item)]
    return []


def render_sources(sources: Any) -> None:
    valid_sources = extract_source_urls(sources)
    if not valid_sources:
        return

    st.caption("Sources found")
    for index, source in enumerate(dict.fromkeys(valid_sources), start=1):
        st.link_button(f"Source {index}", source, icon=":material/open_in_new:")


def render_trace(trace: dict[str, Any]) -> None:
    history = trace.get("history") or []
    sources = trace.get("search_result") or []
    if not history and not sources:
        return

    with st.expander("Research trail", icon=":material/account_tree:"):
        for index, item in enumerate(history, start=1):
            agent = item.get("agent", "Agent").replace("_", " ").title()
            with st.expander(f"{index}. {agent}"):
                st.caption("Input")
                st.write(item.get("input") or "No input recorded.")
                st.caption("Output")
                st.write(item.get("output") or "No output recorded.")

        render_sources(sources)

        research_results = trace.get("reserach_result") or []
        if research_results:
            with st.expander("Research excerpts"):
                for item in research_results:
                    st.write(item.get("Result", ""))


def render_message(message: dict[str, Any]) -> None:
    role = message["role"]
    with st.chat_message(role):
        if message.get("error"):
            st.error(message["error"], title="Request failed")
        else:
            st.markdown(message["content"])
            if role == "assistant":
                render_sources(message.get("sources", []))
                render_trace(message.get("trace", {}))


def clear_conversation() -> None:
    st.session_state.messages = []
    st.session_state.prompt_suggestions = None


with st.sidebar:
    settings = st.session_state.api_settings
    st.title("Research desk", anchor=False)
    st.caption("A web research assistant powered by your agent pipeline")

    st.subheader("Pipeline")
    st.caption("Plan → search and research → evaluate → answer")

    st.subheader("API setup")
    st.caption(
        "Connect an OpenAI-compatible model API and a Tavily search key. "
        "Settings stay in this browser session."
    )
    with st.form("api_settings_form"):
        base_url = st.text_input(
            "Model API endpoint",
            value=settings.base_url,
            placeholder="https://api.example.com/v1",
            help="Use the base URL provided by your model API provider.",
        )
        api_key = st.text_input(
            "Model API key",
            value=settings.api_key,
            type="password",
        )
        model = st.text_input(
            "Model name",
            value=settings.model,
            placeholder="For example: gpt-4o-mini",
        )
        tavily_api_key = st.text_input(
            "Tavily search API key",
            value=settings.tavily_api_key,
            type="password",
        )
        save_settings = st.form_submit_button(
            "Save API settings",
            type="primary",
            width="stretch",
        )
    if save_settings:
        st.session_state.api_settings = APISettings(
            base_url=base_url.strip(),
            api_key=api_key.strip(),
            model=model.strip(),
            tavily_api_key=tavily_api_key.strip(),
        )
        st.success("API settings saved for this session.")

    settings = st.session_state.api_settings
    missing_settings = get_missing_settings(settings)
    missing_model_settings = [
        setting
        for setting in missing_settings
        if setting != "Web search API key"
    ]
    if st.button(
        "Test model connection",
        disabled=bool(missing_model_settings),
        width="stretch",
    ):
        try:
            invoke("Reply with OK.", "Connection test.", settings)
        except APIConnectionError:
            st.error(
                f"Could not connect to the model API at "
                f"{get_model_endpoint_label(settings)}. Check the endpoint and try again.",
                title="Connection failed",
            )
        except OpenAIError as error:
            st.error(
                f"The model API test failed ({type(error).__name__}). "
                "Check the endpoint, API key, and model name."
            )
        else:
            st.success("Model API connection is working.")

    st.subheader("Connections")
    if missing_settings:
        st.warning(
            "Configure all four API settings above to enable requests.",
            title="Setup required",
        )
        for setting in missing_settings:
            st.code(setting, language=None)
    else:
        st.success("All required API settings are configured.")

    st.metric("Questions in this session", len(st.session_state.messages) // 2)
    st.button(
        "Clear conversation",
        icon=":material/delete_sweep:",
        width="stretch",
        on_click=clear_conversation,
    )

st.title("Research assistant", icon=":material/travel_explore:")
st.write(
    "Ask a question. The agent can search the web, investigate relevant pages, "
    "and return a grounded response."
)

for message in st.session_state.messages:
    render_message(message)

suggestion = None
if not st.session_state.messages:
    suggestion = st.pills(
        "Try asking",
        SUGGESTIONS,
        disabled=bool(missing_settings),
        label_visibility="collapsed",
        key="prompt_suggestions",
    )

prompt = st.chat_input(
    "Ask a question or describe what you want to research",
    disabled=bool(missing_settings),
    max_chars=4000,
)
prompt = prompt or (suggestion if not missing_settings else None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message(st.session_state.messages[-1])

    with st.chat_message("assistant"):
        with st.status("Working through your request", expanded=True) as status:
            from pipliner import pipliner

            state = State(user_input=prompt)

            def update_agent_status(stage: str) -> None:
                status.update(label=stage, state="running", expanded=True)
                status.write(stage)

            try:
                response = pipliner(
                    state,
                    progress_callback=update_agent_status,
                    settings=settings,
                )
            except APIConnectionError:
                endpoint = get_model_endpoint_label(settings)
                message = (
                    f"Could not connect to the language-model API at {endpoint}. "
                    "Start its OpenAI-compatible API server and make sure it is "
                    "listening at the configured address, or update the model "
                    "API endpoint in the sidebar. The API key is not shown here."
                )
                status.update(label="Language-model connection failed", state="error")
                st.error(message, title="Model API is unreachable")
                st.session_state.messages.append(
                    {"role": "assistant", "content": "", "error": message}
                )
                response = None
            except OpenAIError as error:
                message = (
                    f"The model API rejected the request "
                    f"({type(error).__name__}). Check the endpoint, API key, "
                    "and model name in the sidebar."
                )
                status.update(label="Language-model request failed", state="error")
                st.error(message, title="Model API request failed")
                st.session_state.messages.append(
                    {"role": "assistant", "content": "", "error": message}
                )
                response = None

            if response is not None:
                if not isinstance(response, str) or not response.strip():
                    raise RuntimeError(
                        "The research pipeline returned an empty answer."
                    )
                status.update(label="Research complete", state="complete", expanded=True)

        if response is not None:
            result = {
                "role": "assistant",
                "content": response,
                "sources": state.search_result,
                "trace": state.model_dump(),
            }
            st.markdown(response)
            render_sources(result["sources"])
            render_trace(result["trace"])
            st.session_state.messages.append(result)
