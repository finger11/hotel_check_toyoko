import sys
import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

URL = "https://www.toyoko-inn.com/korea/search/result/?prefecture=45&people=2&room=1&smoking=noSmoking&start=2026-05-13&end=2026-05-14"
KEYWORD = "객실 선택"

def main():
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    result = {
        "ok": True,
        "checked_at": now,
        "url": URL,
        "found": False,
        "count": 0,
        "note": ""
    }

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                locale="ko-KR",
                user_agent="Mozilla/5.0",
                viewport={"width":1280,"height":2000}
            )

            page = context.new_page()

            page.goto(URL, wait_until="domcontentloaded", timeout=60000)

            try:
                page.wait_for_load_state("networkidle", timeout=60000)
            except PWTimeoutError:
                pass

            page.wait_for_selector("button", timeout=20000)

            locator = page.locator("button", has_text=KEYWORD)

            count = locator.count()

            result["count"] = count
            result["found"] = count > 0

            browser.close()

    except Exception as e:
        result["ok"] = False
        result["note"] = str(e)

    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
