from playwright.sync_api import sync_playwright
from openai import OpenAI
def fetch_chapter_and_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1")

        page.screenshot(path="chapter_1_screenshot.png")

        content = page.inner_text("div.mw-parser-output")
        with open("chapter_1.txt", "w", encoding="utf-8") as f:
            f.write(content)

        browser.close()

fetch_chapter_and_screenshot()

def generate_or_review_content(prompt):
    client = OpenAI(api_key="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",
                    base_url="https://openrouter.ai/api/v1")

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5000
    )
    return response.choices[0].message.content
