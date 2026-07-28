import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from models.item import Item


URL = "https://gamebiz.jp/news/tag/17196"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
}


DATE_FORMAT = "%Y.%m.%d %H:%M"


def parse_date(text: str):

    if not text:
        return None

    text = text.strip()

    try:
        return datetime.strptime(
            text,
            DATE_FORMAT
        )
    except ValueError:
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


    items = []


    articles = soup.select(
        'div[class*="article"][class*="horizontal"]'
    )


    for article in articles:

        try:

            # title
            title_el = article.select_one(
                ".article__title"
            )

            if not title_el:
                continue

            title = title_el.get_text(
                strip=True
            )


            # url
            link_el = article.select_one(
                ".article__link"
            )

            if not link_el:
                continue

            link = link_el.get("href", "")

            if link.startswith("/"):
                link = "https://gamebiz.jp" + link


            # description/category
            category_el = article.select_one(
                ".article__category"
            )

            description = (
                category_el.get_text(strip=True)
                if category_el
                else title
            )


            # date
            date_el = article.select_one(
                ".article__published-at"
            )

            pub_date = (
                parse_date(
                    date_el.get_text(strip=True)
                )
                if date_el
                else None
            )


            # image
            image_url = ""

            img_el = article.select_one(
                ".media-image"
            )

            if img_el:

                image_url = (
                    img_el.get("src")
                    or img_el.get("data-src")
                    or ""
                )


            items.append(
                Item(
                    site="GAMEBIZ",
                    category="interview",
                    title=title,
                    link=link,
                    description=description,
                    image_url=image_url,
                    pub_date=pub_date,
                    tags=[
                        "gamebiz"
                    ]
                )
            )


        except Exception as e:

            print(
                f"[GAMEBIZ] Parse error: {e}"
            )


    return items
