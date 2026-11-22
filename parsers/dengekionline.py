from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from models.item import Item


URL = "https://dengekionline.com/category/interview/page/1"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

DATE_FORMATS = [
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
]


def parse_date(text: str) -> datetime | None:

    if not text:
        return None

    text = text.strip()

    for fmt in DATE_FORMATS:

        try:

            dt = datetime.strptime(
                text,
                fmt
            )

            return dt.replace(
                tzinfo=timezone.utc
            )

        except ValueError:
            pass

    return None


def parse():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "lxml"
    )

    # 不用哈希化后的 class 名做定位：只认语义结构与文章链接
    main = soup.select_one("main") or soup

    articles = main.select("li")

    items = []
    seen = set()

    for article in articles:

        try:

            link_el = article.select_one(
                'a[href*="/article/"]'
            )

            # 有 <time> 的才是栏目正文；编辑推荐位/广告没有发布时间
            date_el = article.select_one("time")

            if not link_el or not date_el:
                continue

            title_el = article.select_one("p")

            title = (
                title_el.get_text(strip=True)
                if title_el
                else link_el.get_text(" ", strip=True)
            )

            link = urljoin(
                "https://dengekionline.com",
                link_el.get("href", "")
            )

            if "osusume_banner" in link or link in seen:
                continue

            seen.add(link)

            desc_el = article.select_one(
                '[class*="description"]'
            )

            description = (
                desc_el.get_text(" ", strip=True)
                if desc_el
                else title
            )

            raw_date = date_el.get_text(
                " ",
                strip=True
            )

            pub_date = parse_date(
                raw_date
            )

            if pub_date is None:

                print(
                    "[Dengeki Online] Date parse failed:",
                    repr(raw_date)
                )

            image_url = ""

            img_el = article.select_one("img")

            if img_el:

                image_url = (
                    img_el.get("src")
                    or img_el.get("data-src")
                    or img_el.get("data-lazy-src")
                    or ""
                )

                image_url = urljoin(
                    "https://dengekionline.com",
                    image_url
                )

            items.append(
                Item(
                    site="Dengeki Online",
                    category="interview",
                    title=title,
                    link=link,
                    description=description,
                    image_url=image_url,
                    pub_date=pub_date,
                    tags=[]
                )
            )

        except Exception as e:

            print(
                f"[Dengeki Online] Parse error: {e}"
            )

    return items
