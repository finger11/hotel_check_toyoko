import sys
import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

URL = "https://www.toyoko-inn.com/korea/search/result/?prefecture=45&people=2&room=1&smoking=noSmoking&start=2026-05-13&end=2026-05-14"
KEYWORD = "객실 선택"

def main() -> int:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    result = {
        "ok": True,
        "checked_at": now,
        "url": URL,
        "keyword": KEYWORD,
        "found": False,
        "match_count": 0,
        "note": "",
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                locale="ko-KR",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 2000},
            )
            page = context.new_page()

            page.goto(URL, wait_until="domcontentloaded", timeout=60000)

            # 네트워크 idle 대기(안 떨어질 수도 있으니 예외 허용)
            try:
                page.wait_for_load_state("networkidle", timeout=60000)
            except PWTimeoutError:
                pass

            # 버튼이 렌더링될 시간을 조금 더 준다(최대 20초)
            try:
                page.wait_for_timeout(2000)
                page.wait_for_selector("button", timeout=20000)
            except PWTimeoutError:
                # 버튼이 없는 화면이어도 실패로 두지 않고 found=False로 종료
                result["note"] = "button 셀렉터가 시간 내 로딩되지 않음(객실 없음/차단/지연 가능)."
                print(json.dumps(result, ensure_ascii=False))
                browser.close()
                return 0

            # "객실 선택" 텍스트를 가진 button 찾기
            locator = page.locator("button", has_text=KEYWORD)
            cnt = locator.count()

            result["match_count"] = cnt
            result["found"] = cnt > 0

            browser.close()

    except Exception as e:
        # 접속 실패/차단 등 진짜 오류만 ok=false로 처리
        result["ok"] = False
        result["note"] = f"렌더링/탐지 실패: {type(e).__name__}: {e}"

    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
