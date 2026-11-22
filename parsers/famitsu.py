import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from models.item import Item


URL = "https://www.famitsu.com/category/interview/page/1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

ABSOLUTE_FORMATS = [
    "%Y.%m.%d %H:%M",
    "%Y.%m.%d",
    "%Y年%m月%d日 %H:%M",
    "%Y年%m月%d日",
]


def parse_relative_date(text: str) -> datetime | None:

    text = text.strip()

    now = datetime.now().replace(microsecond=0)

    if text == "昨日":
        return now - timedelta(days=1)

    if text == "一昨日":
        return now - timedelta(days=2)

    patterns = [
        (r"(\d+)分前", "minutes"),
        (r"(\d+)時間前", "hours"),
        (r"(\d+)日前", "days"),
        (r"(\d+)週間前", "weeks"),
        (r"(\d+)(?:か月|ヶ月)前", "months"),
        (r"(\d+)年前", "years"),
    ]

    for pattern, unit in patterns:

        match = re.search(pattern, text)

        if not match:
            continue

        value = int(match.group(1))

        if unit == "minutes":
            return now - timedelta(minutes=value)

        if unit == "hours":
            return now - timedelta(hours=value)

        if unit == "days":
            return now - timedelta(days=value)

        if unit == "weeks":
            return now - timedelta(weeks=value)

        if unit == "months":
            return now - timedelta(days=value * 30)

        if unit == "years":
            return now - timedelta(days=value * 365)

    for fmt in ABSOLUTE_FORMATS:

        try:
            return datetime.strptime(text, fmt)
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

    # 不依赖哈希化 class：只取 main 里有 <time> 的列表卡片
    main = soup.select_one("main") or soup

    items = []
    seen = set()

    for card in main.select("li"):

        try:

            # 原生广告位和推荐位没有发布时间，先按结构排除
            date_el = card.select_one("time")

            if not date_el:
                continue

            # 已知广告卡片再按稳定 class 兜一次
            if card.select_one(
                ".ad-native-campaign, [class*='adText']"
            ):
                continue

            # 标题取卡片里文字最长的文章链接，不用哈希 class
            anchors = [
                a
                for a in card.select('a[href*="/article/"]')
                if len(a.get_text(strip=True)) >= 15
            ]

            title_el = (
                max(
                    anchors,
                    key=lambda a: len(a.get_text(strip=True))
                )
                if anchors
                else None
            )

            if not title_el:
                continue

            link = urljoin(
                "https://www.famitsu.com",
                title_el.get("href", "")
            )

            if "/article/" not in link or link in seen:
                continue

            seen.add(link)

            title = title_el.get_text(
                strip=True
            )

            desc_el = card.select_one(
                'a[class*="lead"]'
            )

            description = (
                desc_el.get_text(" ", strip=True)
                if desc_el
                else title
            )

            raw_date = (
                date_el.get("datetime")
                or date_el.get_text(strip=True)
            )

            pub_date = parse_relative_date(
                raw_date
            )

            image_url = ""

            img_el = card.select_one("img")

            if img_el:

                image_url = (
                    img_el.get("src")
                    or img_el.get("data-src")
                    or img_el.get("data-original")
                    or ""
                )

                image_url = urljoin(
                    "https://www.famitsu.com",
                    image_url
                )

            items.append(
                Item(
                    site="Famitsu",
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
                f"[Famitsu] Parse error: {e}"
            )

    return items
