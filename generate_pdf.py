import sys, os, uuid
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

def generate_pdf(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.emulate_media(media="screen")
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()

if __name__ == "__main__":
    raw_input = sys.argv[1]

    # If it already has a protocol, use it directly
    if raw_input.startswith(("http://", "https://")):
        url = raw_input
    else:
        # Otherwise treat it as a search query, but use DuckDuckGo Lite
        # to avoid Google's CAPTCHA from cloud IPs.
        query = quote_plus(raw_input)
        url = f"https://lite.duckduckgo.com/lite/?q={query}"

    out_dir = sys.argv[2] if len(sys.argv) > 2 else "pdfs"
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex[:8]}.pdf"
    full_path = os.path.join(out_dir, filename)

    generate_pdf(url, full_path)
    print(f"PDF generated: {full_path}")
