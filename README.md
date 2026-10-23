# LangChain Pipeline Agent with Streamlit

A research-focused AI agent built with LangChain and a Streamlit UI. The application lets users ask questions, plans a multi-step research workflow, searches the web, gathers relevant source material, evaluates the evidence, and returns a grounded answer.

## Project Overview

This project combines:

- A LangChain-based reasoning pipeline
- A planner/executor/evaluator workflow
- Web search and page research capabilities
- A Streamlit chat interface for end-user interaction
- Support for OpenAI-compatible LLM APIs and Tavily search

The system is designed to behave like a research assistant: it breaks down the user's request, selects the next action, gathers evidence from the web, and answers using the most relevant findings.

## Why this project exists

The repository implements an agentic research pipeline where the model does not answer from memory alone. Instead, it can:

1. understand the user query,
2. decide whether a search or deeper research is needed,
3. retrieve useful sources,
4. inspect content from those sources,
5. evaluate whether the result is sufficient,
6. generate a final answer based on evidence.

This makes it useful for research, summarization, information gathering, and source-backed answering.

## Key Features

- Multi-step planning workflow
- Search and research tool orchestration
- Evaluator step to validate answer quality
- Final answer generation using an LLM
- Streamlit web app for interactive use
- OpenAI-compatible model endpoint support
- Tavily-powered web search integration
- Session-based conversational UI

## Tech Stack

- Python
- LangChain
- Streamlit
- Pydantic
- OpenAI-compatible APIs
- Tavily API
- Requests, BeautifulSoup, and related libraries
- dotenv for environment configuration

## Repository Structure

```text
.
├── agent.py                 # OpenAI-compatible LLM client wrapper
├── api_settings.py          # API configuration loader
├── evaluate.py              # Evaluation logic for checking answer quality
├── executer.py              # Execution layer for planned tasks
├── final_answer.py          # Final response generation
├── main.py                  # Entry point for execution
├── memory.py                # Memory abstraction
├── pipliner.py              # Main pipeline orchestration
├── planner.py               # Planning logic for tool selection
├── requirements.txt         # Python dependencies
├── state.py                 # Shared application state model
├── streamlit_app.py         # Streamlit user interface
├── tools.py                 # Search and research helper tools
├── PROJECT_ANALYSIS.md      # Project analysis and architecture notes
├── .streamlit               # Streamlit configuration folder
├── .gitignore
└── README.md
```

## How it works

The project follows a planning loop:

- User enters a question in the Streamlit app
- The planner decides the next step
- Search or research tools gather evidence
- The system stores intermediate results in shared state
- The evaluator checks whether enough information is available
- If approved, the final answer generator returns a response

## Environment Variables

Create a `.env` file in the project root and configure the following values:

```bash
FREELLMAPI_BASE_URL="https://your-model-provider.com/v1"
FREELLMAPI_API_KEY="your_api_key"
FREELLMAPI_MODEL="your_model_name"
TAVILY_API_KEY="your_tavily_key"
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/shahzaibkaramat67-coder/langchain_pipliner_agent_with_streamlit.git
cd langchain_pipliner_agent_with_streamlit
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

Start the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Then open the local URL shown in the terminal in your browser.

## Example Use Cases

- Research a technical topic
- Compare tools or frameworks
- Gather web-based evidence for an answer
- Summarize findings from multiple sources
- Explore questions with a structured AI workflow

## Notes

This project is an experimental agent pipeline and is meant to support research-focused AI workflows. Its architecture emphasizes iterative planning, evidence gathering, and answer validation.

## License

This project does not currently include a license file. If you plan to publish or share it publicly, it is recommended to add an appropriate open-source license such as MIT or Apache 2.0.

## Author

Created by Shahzaib Karamat

## Project Name

LangChain Pipeline Agent with Streamlit
