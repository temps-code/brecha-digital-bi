"""Verify the exact public checkout, not merely an HTTP 200 from Streamlit."""
import os
import re
import time
from collections.abc import Callable

SITE_URL = 'https://brecha-digital-bolivia-bi.streamlit.app/'


def wait_for_revision(
    probe: Callable[[str], bool], expected: str, *, timeout: float = 720,
    interval: float = 15, clock: Callable[[], float] = time.monotonic,
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


def main() -> None:
    from playwright.sync_api import Error, sync_playwright

    expected = os.environ['EXPECTED_SHA']
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        def probe(revision: str) -> bool:
            try:
                page.goto(SITE_URL, wait_until='domcontentloaded', timeout=15000)
                page.get_by_text(
                    f'Versión desplegada: {revision}', exact=True,
                ).wait_for(state='visible', timeout=10000)
                return True
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
