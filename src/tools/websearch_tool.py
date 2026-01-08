import json
import anyio
from strands import tool
from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException


@tool
async def websearch(keywords: str, region: str = "us-en", max_results: int = 5) -> str:
    """
    Web search tool using **DuckDuckGo Search** via `ddgs.DDGS().text(...)`.

    Args:
        keywords: Search query string.
        region:   Region code (e.g., "us-en"). Default: "us-en".
        max_results: Number of results to return. Default: 5.

    Returns:
        A **pretty JSON string** list of results on success, e.g.:
        `[{"title": "...", "href": "...", "body": "..."}, ...]`
        - On rate-limit: `"Rate limit reached. Please try again later."`
        - On library/other errors: `"Search error: <message>"`
    """
    try:
        results = await anyio.to_thread.run_sync(
            lambda: DDGS().text(keywords, region=region, max_results=max_results)
        )
        return json.dumps(results or [], ensure_ascii=False, indent=2)
    except RatelimitException:
        return "Rate limit reached. Please try again later."
    except DDGSException as e:
        return f"Search error: {e}"
    except Exception as e:
        return f"Search error: {str(e)}"