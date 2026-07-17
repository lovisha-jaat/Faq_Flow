import re
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from services.file_service import split_text_into_chunks


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}


def normalize_url(url):
    url = str(url).strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url.rstrip("/")


def is_same_domain(base_url, target_url):
    base_domain = urlparse(base_url).netloc.lower()
    target_domain = urlparse(target_url).netloc.lower()

    return base_domain == target_domain


def clean_page_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "iframe",
        "form"
    ]):
        element.decompose()

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.body
        or soup
    )

    text = main_content.get_text(
        separator=" ",
        strip=True
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip(), soup


def scrape_with_requests(url):
    """
    First try the faster requests-based scraper.
    """

    try:
        response = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=20,
            allow_redirects=True
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "text/html" not in content_type:
            return "", None

        return clean_page_text(response.text)

    except requests.RequestException:
        return "", None


def scrape_with_browser(url):
    """
    Load JavaScript-rendered websites using Chromium.
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1366,
                "height": 768
            },
            user_agent=REQUEST_HEADERS["User-Agent"]
        )

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            # Wait for JavaScript content to appear.
            page.wait_for_timeout(4000)

            try:
                page.wait_for_load_state(
                    "networkidle",
                    timeout=15000
                )
            except Exception:
                # Some sites keep network requests open.
                pass

            html = page.content()

            return clean_page_text(html)

        finally:
            browser.close()


def extract_links(soup, current_url, base_url):
    links = []

    if not soup:
        return links

    ignored_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".svg",
        ".zip",
        ".mp4",
        ".mp3",
        ".css",
        ".js"
    )

    for link in soup.find_all("a", href=True):
        href = link.get("href", "").strip()

        if not href:
            continue

        if href.startswith((
            "#",
            "mailto:",
            "tel:",
            "javascript:"
        )):
            continue

        target_url = urljoin(
            current_url,
            href
        ).split("#")[0]

        if not is_same_domain(
            base_url,
            target_url
        ):
            continue

        if target_url.lower().endswith(
            ignored_extensions
        ):
            continue

        links.append(
            target_url.rstrip("/")
        )

    return links


def scrape_page(url):
    """
    Use requests first and browser rendering when needed.
    """

    text, soup = scrape_with_requests(url)

    # A short result usually means the page depends on JavaScript.
    if len(text) < 150:
        text, soup = scrape_with_browser(url)

    return text, soup


def scrape_website(
    website_url,
    max_pages=10
):
    website_url = normalize_url(
        website_url
    )

    parsed_url = urlparse(
        website_url
    )

    if parsed_url.scheme not in {
        "http",
        "https"
    }:
        raise ValueError(
            "Please enter a valid website URL."
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
            page_text, soup = scrape_page(
                current_url
            )

        except Exception as error:
            print(
                f"Unable to scrape {current_url}: {error}"
            )
            continue

        print(
            f"Scraped {current_url}: "
            f"{len(page_text)} characters"
        )

        if len(page_text) >= 100:
            page_title = current_url

            if soup and soup.title:
                title_text = soup.title.get_text(
                    strip=True
                )

                if title_text:
                    page_title = title_text

            page_chunks = split_text_into_chunks(
                page_text,
                page_title,
                chunk_size=800
            )

            for chunk in page_chunks:
                chunk["source_name"] = page_title
                chunk["source_type"] = "website"
                chunk["source_url"] = current_url

            all_chunks.extend(page_chunks)

        new_links = extract_links(
            soup,
            current_url,
            website_url
        )

        for link in new_links:
            if (
                link not in visited
                and link not in queue
            ):
                queue.append(link)

    if not all_chunks:
        raise ValueError(
            "The website opened, but no readable content "
            "could be extracted. The website may require "
            "login, block automated browsers, or load its "
            "data through a protected API."
        )

    return all_chunks