import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from models.item import Item


URL = "https://ikinukitei.dmm.co.jp/article/category/selection/"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
    "Referer": "https://www.dmm.co.jp/"
}


DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S%z",
]


def parse_date(text: str) -> datetime | None:

    if not text:
        return None

    text = text.strip()

    for fmt in DATE_FORMATS:

        try:

            dt = datetime.strptime(text, fmt)

            return dt.astimezone(timezone.utc)

        except ValueError:
            pass

    return None


def fetch_html():

    session = requests.Session()

    session.headers.update(HEADERS)

    # 关键：模拟正常用户先访问主站
    try:
        session.get(
            "https://www.dmm.co.jp/",
            timeout=30
        )
    except Exception:
        pass

    # 关键 cookie（弱但有效）
    session.cookies.set(
        "age_check_done",
        "1",
        domain=".dmm.co.jp"
    )

    response = session.get(
        URL,
        timeout=30
    )

    print("FINAL URL:", response.url)
    print("STATUS:", response.status_code)

    return response.text


def parse():

    html = fetch_html()

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    articles = soup.select(
        "article.item"
    )

    items = []

    for article in articles:

        try:

            title_el = article.select_one(
                "h3.title a"
            )

            if not title_el:
                continue

            date_el = article.select_one(
                "time.date"
            )

            image_el = article.select_one(
                ".image"
            )

            title = title_el.get_text(strip=True)

            link = title_el.get("href", "")

            description = title

            pub_date = None

            if date_el:

                raw_date = date_el.get("datetime", "")

                pub_date = parse_date(raw_date)

                if pub_date is None:
                    print(
                        "[Ikinukitei] Date parse failed:",
                        repr(raw_date)
                    )

            image_url = ""

            if image_el:

                style = image_el.get("style", "")

                match = re.search(
                    r'url\((.*?)\)',
                    style
                )

                if match:
                    image_url = match.group(1).strip('"').strip("'")

            items.append(
                Item(
                    site="Ikinukitei",
                    category="selection",
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
                f"[Ikinukitei] Parse error: {e}"
            )

    return items
