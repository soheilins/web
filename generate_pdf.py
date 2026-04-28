import sys, os, uuid, time
from playwright.sync_api import sync_playwright

def expand_all(page):
    """Automatically expand common collapsible elements."""
    # 1. Open all <details>
    page.evaluate("""() => {
        document.querySelectorAll('details:not([open])').forEach(el => el.open = true);
    }""")

    # 2. Click standard expanders
    expand_selectors = [
        "[aria-expanded='false']",
        "button.show-more", "button.expand", "button.load-more",
        "a.expand", "a.load-more",
        "[data-action='expand']",
        ".accordion-toggle",
        ".collapsible-header",
        ".read-more", ".see-more", ".show-more",
        ".expand-section", ".toggle-content",
        "[class*='expand']:not(body):not(html)",
    ]
    for selector in expand_selectors:
        try:
            elements = page.query_selector_all(selector)
            for el in elements:
                try:
                    if el.is_visible() and el.is_enabled():
                        el.click(force=True)
                        page.wait_for_timeout(400)
                except:
                    pass
        except:
            pass

    # 3. Repeatedly hit "load more" buttons
    for _ in range(5):
        load_more = page.query_selector(
            "button:has-text('Load more'), a:has-text('Load more'), "
            "button:has-text('Show more'), a:has-text('Show more')"
        )
        if load_more and load_more.is_visible():
            try:
                load_more.click(force=True)
                page.wait_for_timeout(1500)
            except:
                break
        else:
            break

    page.wait_for_timeout(2000)


def apply_custom_clicks(page, click_string):
    """
    Click buttons/links that contain the given text(s).
    `click_string` is a comma-separated list of button texts (e.g. "show, show more").
    """
    if not click_string:
        return

    texts = [t.strip() for t in click_string.split(",") if t.strip()]
    for text in texts:
        try:
            # Match any element with this text (buttons, links, etc.)
            elements = page.get_by_text(text, exact=False)
            count = elements.count()
            for i in range(count):
                el = elements.nth(i)
                if el.is_visible() and el.is_enabled():
                    el.click(force=True)
                    page.wait_for_timeout(500)
        except:
            pass


def generate_pdf(url, output_path, extra_clicks=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.emulate_media(media="screen")

        # Always run auto-expand first
        expand_all(page)

        # Apply any user-requested extra clicks
        apply_custom_clicks(page, extra_clicks)

        # Final scroll to trigger lazy images
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()


if __name__ == "__main__":
    url = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "pdfs"
    extra_clicks = sys.argv[3] if len(sys.argv) > 3 else ""

    os.makedirs(out_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex[:8]}.pdf"
    full_path = os.path.join(out_dir, filename)

    generate_pdf(url, full_path, extra_clicks)
    print(f"PDF generated: {full_path}")
