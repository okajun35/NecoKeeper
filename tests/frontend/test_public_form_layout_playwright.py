import os
import socket
import threading
import time

import pytest

if os.getenv("RUN_PLAYWRIGHT") != "1":
    pytest.skip(
        "Playwright layout checks require RUN_PLAYWRIGHT=1.",
        allow_module_level=True,
    )

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import Error, sync_playwright

from app.main import app


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="function")
def live_server(test_db: object) -> str:
    port = _get_free_port()
    server, thread = _start_server(port)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=2)


def _start_server(port: int):
    import uvicorn

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        lifespan="off",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_for_port(port)
    return server, thread


def _wait_for_port(port: int, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            try:
                sock.connect(("127.0.0.1", port))
                return
            except OSError:
                time.sleep(0.1)
    raise RuntimeError("Test server did not start in time.")


VIEWPORTS = [
    {"name": "iphone-14", "width": 390, "height": 844},
    {"name": "android-small", "width": 360, "height": 800},
]


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=[v["name"] for v in VIEWPORTS])
def test_public_care_form_footer_does_not_overlap(
    live_server: str, test_animal: object, viewport: dict[str, int]
) -> None:
    url = f"{live_server}/public/care?animal_id={test_animal.id}"

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Error as exc:
            pytest.skip(f"Playwright browser not available: {exc}")

        context = browser.new_context(
            viewport={"width": viewport["width"], "height": viewport["height"]}
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector("#careFormFooter", state="attached")
        page.wait_for_selector("#volunteer", state="attached")
        page.evaluate("document.body.classList.remove('i18n-hidden')")

        position = page.eval_on_selector(
            "#careFormFooter", "el => getComputedStyle(el).position"
        )
        if position != "fixed":
            pytest.skip("Tailwind CSS not applied; layout check not reliable.")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(200)

        footer_box = page.locator("#careFormFooter").bounding_box()
        volunteer_box = page.locator("#volunteer").bounding_box()
        assert footer_box is not None
        assert volunteer_box is not None

        footer_top = footer_box["y"]
        volunteer_bottom = volunteer_box["y"] + volunteer_box["height"]
        assert volunteer_bottom <= footer_top - 4

        padding_bottom = page.eval_on_selector(
            ".care-form-container",
            "el => parseFloat(getComputedStyle(el).paddingBottom) || 0",
        )
        assert padding_bottom + 1 >= footer_box["height"]

        context.close()
        browser.close()
