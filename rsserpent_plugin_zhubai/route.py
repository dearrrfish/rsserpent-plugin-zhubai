import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict

from rsserpent.utils import HTTPClient, cached


path = "/zhubai/{sub:str}"


@cached
async def provider(sub: str) -> Dict[str, Any]:
    """Zhubai newsletter full content feed."""
    u = f"https://{sub}.zhubai.love"
    async with HTTPClient() as http:
        response = await http.get(
            f"{u}/api/publications/{sub}/posts?publication_id_type=token&limit=20",
            headers={
                "Referer": u,
            },
        )
        data = response.json()["data"]
        publication = data[0]["publication"]

    return {
        "title": publication["name"],
        "link": u,
        "description": publication["description"],
        "items": [
            {
                "title": item["title"],
                "link": f"{u}/posts/{item['id']}",
                "description": parse_content(item["content"]),
                "author": item["author"]["name"],
                "pub_date": datetime.fromtimestamp(
                    int(item["publication"]["updated_at"] / 1000), tz=timezone.utc
                ).isoformat(),
            }
            for item in data
        ],
    }


def parse_content(content: str) -> str:
    """Parse post content from JSON string to HTML."""
    elems = json.loads(content)
    html = "".join([translate(elem) for elem in elems])
    return f"<div>{html}</div>"


def translate_text(e: Dict[str, Any]) -> str:
    """Translate text block."""
    if not e.get("text"):
        return ""
    style = ""
    if e.get("bold") is True:
        style += "font-weight: bold;"
    if e.get("italic") is True:
        style += "font-style: italic;"
    if style != "":
        style = f' style="{style}"'
    return f"<span{style}>{e['text']}</span>"


def translate(e: Dict[str, Any]) -> str:
    """Translate content block to html."""
    if "type" not in e:
        return translate_text(e)

    children = ""
    if "children" in e:
        children = "".join([translate(c) for c in e["children"]])

    translators: Dict[str, Callable[[Dict[str, Any]], str]] = {
        "divider": lambda _: "<div><hr></div>",
        "block-code": lambda _: f"<pre>{children}</pre>",
        "block-quote": lambda _: f"<blockquote>{children}</blockquote>",
        "bulleted-list": lambda _: f"<ul>{children}</ul>",
        "list-item": lambda _: f"<li>{children}</li>",
        "heading-one": lambda _: f"<h1>{children}</h1>",
        "heading-two": lambda _: f"<h2>{children}</h2>",
        "image": lambda x: f"<figure><div><img src=\"{x['url']}\"></div></figure>",
        "link": lambda x: f"<a href=\"{x['url']}\" target=\"_black\">{children}</a>",
        "paywall": lambda x: "<div><b>PAYWALL BREAK</b></div>",
    }

    html = ""
    e_type = e["type"]
    if e_type in translators:
        html = translators[e_type](e)

    return html
