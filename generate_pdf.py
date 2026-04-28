import sys, os, uuid
from playwright.sync_api import sync_playwright

def generate_pdf(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Don't wait for networkidle – Twitch and similar sites never settle
        page.goto(url, wait_until="domcontentloaded", timeout=45000)

        # Give the page a few seconds to render its visible layout
        page.wait_for_timeout(4000)

        page.emulate_media(media="screen")
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()

if __name__ == "__main__":
    raw_input = sys.argv[1]

    # Auto-prepend scheme if missing
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
