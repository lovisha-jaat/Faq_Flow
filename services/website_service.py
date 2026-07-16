import re
from collections import deque
from urllib.parse import (
    urljoin,
    urlparse
)

import requests
from bs4 import BeautifulSoup

from services.file_service import (
    split_text_into_chunks
)


REQUEST_HEADERS = {
    "User-Agent": (
        "FAQFlowAI/1.0 "
        "(Company knowledge importer)"
    )
}


def normalize_url(url):
    url = str(url).strip()

    if not url.startswith(
        ("http://", "https://")
    ):
        url = "https://" + url

    return url


def is_same_domain(base_url, target_url):
    return (
        urlparse(base_url).netloc
        == urlparse(target_url).netloc
    )


def clean_page_text(soup):
    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "noscript",
        "svg",
        "form"
    ]):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def scrape_website(
    website_url,
    max_pages=10
):
    """
    Scrape public same-domain pages.

    max_pages prevents unlimited crawling.
    """

    website_url = normalize_url(
        website_url
    )

    parsed = urlparse(website_url)

    if parsed.scheme not in {
        "http",
        "https"
    }:
        raise ValueError(
            "Invalid website URL."
        )

    queue = deque([website_url])
    visited = set()
    all_chunks = []

    while queue and len(visited) < max_pages:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        try:
            response = requests.get(
                current_url,
                headers=REQUEST_HEADERS,
                timeout=12
            )

            response.raise_for_status()

        except requests.RequestException:
            continue

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "text/html" not in content_type:
            continue

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        page_title = (
            soup.title.get_text(strip=True)
            if soup.title
            else current_url
        )

        page_text = clean_page_text(soup)

        if len(page_text) >= 100:
            page_chunks = split_text_into_chunks(
                page_text,
                page_title
            )

            for chunk in page_chunks:
                chunk["source_type"] = "website"
                chunk["source_url"] = current_url

            all_chunks.extend(page_chunks)

        for link in soup.find_all(
            "a",
            href=True
        ):
            target_url = urljoin(
                current_url,
                link["href"]
            )

            target_url = target_url.split("#")[0]

            if not is_same_domain(
                website_url,
                target_url
            ):
                continue

            if target_url in visited:
                continue

            if any(
                target_url.lower().endswith(
                    extension
                )
                for extension in (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".zip",
                    ".mp4",
                    ".pdf"
                )
            ):
                continue

            queue.append(target_url)

    if not all_chunks:
        raise ValueError(
            "No readable public text was found on the website."
        )

    return all_chunks