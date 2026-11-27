"""Capture original viewport PNGs of official reports served only on loopback."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright


EVIDENCE = Path(__file__).resolve().parents[1] / "evidence/phase5"


class Reports(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".log": "text/plain; charset=utf-8"}


def main():
    output = EVIDENCE / "screenshots"
    output.mkdir(exist_ok=True)
    with ThreadingHTTPServer(("127.0.0.1", 0), partial(Reports, directory=EVIDENCE)) as server:
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={"width": 1200, "height": 1060}, device_scale_factor=1)
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin)
                           else route.abort())
                for run in ("P5-L01", "P5-L04"):
                    result = page.goto(f"{origin}/runs/{run}/dashboard.html", wait_until="networkidle")
                    assert result.status == 200
                    page.get_by_text("Overview", exact=True).first.wait_for()
                    page.screenshot(path=output / f"{run}-dashboard.png")
                page.set_viewport_size({"width": 1200, "height": 860})
                page.goto(f"{origin}/runs/P5-L04/console.log")
                raw = page.locator("pre")
                assert "p(95)<=500" in raw.inner_text()
                raw.evaluate("""element => {
                    const text = element.firstChild;
                    const start = text.textContent.indexOf('THRESHOLDS');
                    const boundary = new Range();
                    boundary.setStart(text, start);
                    boundary.setEnd(text, start + 10);
                    window.scrollTo(0, window.scrollY + boundary.getBoundingClientRect().top - 28);
                }""")
                page.screenshot(path=output / "P5-L04-k6-terminal.png")
                page.goto(f"{origin}/recovery/pytest.html", wait_until="networkidle")
                page.get_by_text("test_booking_recovers_after_database_commit_dependency_failure",
                                 exact=False).first.wait_for()
                page.screenshot(path=output / "recovery-pytest.png")
                print(f"Chromium {browser.version}, Playwright full viewport PNGs")
                browser.close()
        finally:
            server.shutdown()
            worker.join()


if __name__ == "__main__":
    main()
