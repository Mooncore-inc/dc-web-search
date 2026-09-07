import httpx

from typing import Literal
from pydantic import Field
from demon_cry_base import BaseModule, ModuleConfig, ModuleParameters

class WebSearchParams(ModuleParameters):
    query: str = Field(description="Search query (supports Google dorks)")
    category: Literal["general", "images", "files", "it", "social media", "news"] = Field(
        default="general",
        description="Search category"
    )
    time_range: Literal["day", "week", "month", "year", "all"] = Field(
        default="all",
        description="Time filter"
    )


class WebSearchConfig(ModuleConfig):
    searxng_url: str = "http://localhost:8080"

class WebSearch(BaseModule):
    name = "web_search"
    description = "Search web via SearXNG. Supports Google dorks (site:, filetype:)"
    category = "search"
    config_model = WebSearchConfig
    parameters_model = WebSearchParams

    async def execute(self, config: WebSearchConfig, params: WebSearchParams) -> dict:
        try:
            request_params = {
                "q": params.query,
                "format": "json",
                "categories": params.category,
            }
            if params.time_range and params.time_range != "all":
                request_params["time_range"] = params.time_range

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{config.searxng_url}/search",
                    params=request_params,
                )
                response.raise_for_status()

            data = response.json()

            warnings = []
            for engine, reason in data.get("unresponsive_engines", []):
                warnings.append(f"{engine}: {reason}")

            results = []
            for r in data.get("results", [])[:10]:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": (lambda c: c[:150] + "..." if len(c) > 150 else c)(r.get("content", "")),
                    "engine": r.get("engine", "unknown"),
                })

            resp = {
                "query": params.query,
                "category": params.category,
                "time_range": params.time_range,
                "results": results,
                "total_found": len(results),
            }
            if warnings:
                resp["warnings"] = warnings
            return resp

        except Exception as e:
            return {"error": str(e), "query": params.query}
