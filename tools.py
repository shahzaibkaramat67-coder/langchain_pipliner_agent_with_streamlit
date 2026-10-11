from langchain.tools import tool
from tavily import TavilyClient

import requests
from bs4 import BeautifulSoup

search_engine = TavilyClient()


@tool
def search(query):
    """
    search the given quey and return the result
    """

    serach_state = []
    # state = {}

    search_result = search_engine.search(query=query, max_results=5)
    for item in search_result["results"]:
        title = item["title"]
        URl = item["url"]
        content = item["content"]
        serach_state.append(URl)

    return serach_state


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
