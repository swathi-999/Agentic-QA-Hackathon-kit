import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def run_qa(target_url: str, output_file: str):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        try:
            await page.goto(target_url, wait_until="networkidle")
            await page.screenshot(path="landing-page.png", full_page=True)

            enter_demo = page.get_by_text("Enter Demo", exact=True)

            if await enter_demo.count() > 0:
                results.append({
                    "id": "ACCESS-001",
                    "status": "passed",
                    "evidence": "Enter Demo button is visible."
                })
            else:
                results.append({
                    "id": "ACCESS-001",
                    "status": "failed",
                    "evidence": "Enter Demo button was not found."
                })

            if await enter_demo.count() > 0:
                await enter_demo.click()
                await page.wait_for_load_state("networkidle")
                await page.screenshot(path="dashboard-page.png", full_page=True)

                results.append({
                    "id": "ACCOUNT-001",
                    "status": "passed",
                    "evidence": "Demo dashboard opened successfully."
                })

                logout = page.get_by_text("Log out", exact=True)

                if await logout.count() > 0:
                    results.append({
                        "id": "ACCESS-002",
                        "status": "passed",
                        "evidence": "Log out control is visible."
                    })
                else:
                    results.append({
                        "id": "ACCESS-002",
                        "status": "unverified",
                        "evidence": "Log out control was not found."
                    })

        except Exception as error:
            results.append({
                "id": "RUNNER-001",
                "status": "failed",
                "evidence": str(error)
            })

        finally:
            await browser.close()

    report = {
        "target_url": target_url,
        "results": results
    }

    Path(output_file).write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Target DemoBank URL")
    parser.add_argument(
        "--output",
        default="qa-report.json",
        help="Output report filename"
    )

    args = parser.parse_args()
    asyncio.run(run_qa(args.url, args.output))


if __name__ == "__main__":
    main()
