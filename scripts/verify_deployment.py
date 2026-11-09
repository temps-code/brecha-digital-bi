"""Verify the exact public checkout, not merely an HTTP 200 from Streamlit."""
import os
import re
import time
from collections.abc import Callable
from urllib.parse import urljoin, urlsplit

SITE_URL = 'https://brecha-digital-bolivia-bi.streamlit.app/'


def wait_for_revision(
    probe: Callable[[str], bool], expected: str, *, timeout: float = 180,
    interval: float = 3, clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Fail closed if the exact expected commit never appears."""
    if not re.fullmatch(r'[0-9a-f]{40}', expected):
        raise ValueError('EXPECTED_SHA must be a full Git commit SHA')
    deadline = clock() + timeout
    while clock() < deadline:
        if probe(expected):
            return
        sleep(min(interval, max(0, deadline - clock())))
    raise TimeoutError(f'Production did not report commit {expected}')


def revision_visible(page, expected: str) -> bool:
    """Check the page and only Streamlit Cloud's same-origin app frame."""
    marker = f'Versión desplegada: {expected}'
    if page.main_frame.get_by_text(marker, exact=True).is_visible():
        return True

    origin = urlsplit(SITE_URL)

    def is_app_url(url: str) -> bool:
        parsed = urlsplit(urljoin(SITE_URL, url))
        return (parsed.scheme, parsed.netloc, parsed.path) == (
            origin.scheme, origin.netloc, '/~/+/',
        )

    for frame in page.frames:
        if frame == page.main_frame or not is_app_url(frame.url):
            continue
        element = frame.frame_element()
        if (element.get_attribute('title') == 'streamlitApp'
                and is_app_url(element.get_attribute('src') or '')
                and frame.get_by_text(marker, exact=True).is_visible()):
            return True
    return False


def main() -> None:
    from playwright.sync_api import Error, sync_playwright

    expected = os.environ['EXPECTED_SHA']
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        last_navigation = float('-inf')

        def probe(revision: str) -> bool:
            nonlocal last_navigation
            try:
                # Let the iframe finish rendering between checks. Repeated
                # navigation would reset startup before the marker can appear.
                now = time.monotonic()
                if now - last_navigation >= 30:
                    last_navigation = now
                    page.goto(SITE_URL, wait_until='domcontentloaded', timeout=15000)
                return revision_visible(page, revision)
            except Error:
                print('Waiting for Streamlit to serve the expected revision...', flush=True)
                return False

        try:
            wait_for_revision(probe, expected)
            print(f'Verified {expected} at {SITE_URL}')
        finally:
            browser.close()


if __name__ == '__main__':
    main()
