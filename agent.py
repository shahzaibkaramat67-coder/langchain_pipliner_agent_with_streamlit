import os
from dotenv import load_dotenv

# from langchain_openai import ChatOpenAI
from openai import OpenAI

# from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

url = os.getenv("FREELLMAPI_BASE_URL")
key = os.getenv("FREELLMAPI_API_KEY")
llm = os.getenv("FREELLMAPI_MODEL")


# url = os.getenv("OPENROUTER_BASE_URL")
# key = os.getenv("OPENROUTER_API_KEY")
# llm = os.getenv("OPENROUTER_MODEL")

# print("url:", url)
# print("key:", key)
# print("llm:", llm)

# model = ChatOpenAI(
#     base_url=url,
#     api_key=key,
#     model=llm,
# )
client = OpenAI(
    base_url=url,
    api_key=key,
)


def invoke(prompt, content):
    return client.chat.completions.create(
        model=llm,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
    )


# def stream(prompt, content):
#     return client.chat.completions.create(
#         model=llm,
#         messages=[
#             {"role": "system", "content": prompt},
#             {"role": "user", "content": content},
#         ],
#         stream=True,
#     )


# response = model.invoke("waht is ai in short")
# print("model", model

# response = model.invoke("Explain what an AI agent is in simple words.")

# base_url = "https://generativelanguage.googleapis.com/v1beta"
# print(response.content)
# model = ChatGoogleGenerativeAI(
#     model=os.getenv("GEMINI_API_MODEL"),
# )
# print("model", model)
# model.invoke()


#  Tool=[search, resaerch]
#     system_message="""

# You are a professioanl saerch agent


# take the query form the user and saerch on it
# and return result

# you have the tools
# you can use any tools form them for the take but
# you must carefull about it and follow the ruls

# Ruls:
# - analsis the user query
# - take the right tool for the query
# - find the best data
# - select only most ralivent result according to the user query
# - after search get most ralivent nearable efficient result for then next agent

# """,

# agent = create_agent(model=model)
