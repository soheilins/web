import sys, os, uuid
from playwright.sync_api import sync_playwright

# Desktop viewport – change the resolution if needed
VIEWPORT = {"width": 1280, "height": 720}

def generate_pdf(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT)   # <-- set viewport here

        # Wait for the HTML to load (good for live sites like Twitch)
        page.goto(url, wait_until="domcontentloaded", timeout=45000)

        # Give additional time for visible rendering
        page.wait_for_timeout(4000)

        page.emulate_media(media="screen")
        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            scale=1.0          # avoid automatic shrinking
        )
        browser.close()

if __name__ == "__main__":
    raw_input = sys.argv[1]

    # Auto-prepend https:// if missing
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
