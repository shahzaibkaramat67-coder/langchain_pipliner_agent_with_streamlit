from langchain.tools import tool
from tavily import TavilyClient
import os

import requests
from bs4 import BeautifulSoup


def search_web(query: str, api_key: str | None = None) -> list[str]:
    if api_key is None:
        api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("The web search API key is not configured.")

    search_result = TavilyClient(api_key=api_key).search(query=query, max_results=5)
    return [item["url"] for item in search_result["results"]]


@tool
def search(query):
    """
    search the given quey and return the result
    """

    return search_web(query)


@tool
def resaerch(urls):
    """
    get all urls and research deeply for better and efficent answers

    """
    print("urls", urls)

    content = ""

    for url in urls:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            )
        }
        try:
            response = requests.get(url=url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("URL Failed", {e})

        # print("response:", response.status_code)

        if response.status_code != 200:
            print("Skipping:", url)
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        for tags in soup.find_all(
            [
                "nav",
                "header",
                "footer",
                "aside",
                "script",
                "style",
                "noscript",
                "iframe",
                "form",
                "button",
                "svg",
            ]
        ):
            tags.decompose()

        text = soup.get_text(separator=" ", strip=True)
        content += text[:8000]
    return content
