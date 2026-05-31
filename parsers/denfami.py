from datetime import datetime
from bs4 import BeautifulSoup
import requests

from models.item import Item


URL = "https://news.denfaminicogamer.jp/category/interview"


def parse() -> list[Item]:
    response = requests.get(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/136.0 Safari/537.36"
            )
        },
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    items: list[Item] = []

    article_list = soup.select_one(
        "section.articleContent.row.related ul.gridList"
    )

    if not article_list:
        return items

    for li in article_list.select("li"):
        a = li.select_one("a.flxBox")

        if not a:
            continue

        title_el = li.select_one("span.title")
        time_el = li.select_one("time")
        img_el = li.select_one("img")

        title = title_el.get_text(strip=True) if title_el else ""

        link = a.get("href", "")

        image_url = img_el.get("src", "") if img_el else ""

        pub_date = None

        if time_el:
            date_str = time_el.get("datetime")

            if date_str:
                try:
                    y, m, d = map(int, date_str.split("-"))
                    pub_date = datetime(y, m, d)
                except Exception:
                    pass

        items.append(
            Item(
                site="denfaminicogamer",
                category="interview",
                title=title,
                link=link,
                description="",
                image_url=image_url,
                pub_date=pub_date,
                tags=[],
            )
        )

    return items
