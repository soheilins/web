import sys, os, uuid
from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 1280, "height": 720}

def generate_pdf(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT)

        # Wait only for the DOM (Twitch never reaches networkidle)
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        page.emulate_media(media="screen")

        # Measure the full scrollable page height for a single‑page PDF
        page_height = page.evaluate("document.documentElement.scrollHeight")
        page_width = VIEWPORT["width"]   # capture exactly the viewport width

        page.pdf(
            path=output_path,
            width=f"{page_width}px",
            height=f"{page_height}px",
            print_background=True
        )
        browser.close()

if __name__ == "__main__":
    raw_input = sys.argv[1]

    if raw_input.startswith(("http://", "https://")):
        url = raw_input
    else:
        url = "https://" + raw_input

    out_dir = sys.argv[2] if len(sys.argv) > 2 else "pdfs"
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex[:8]}.pdf"
    full_path = os.path.join(out_dir, filename)

    generate_pdf(url, full_path)
    print(f"PDF generated: {full_path}")
