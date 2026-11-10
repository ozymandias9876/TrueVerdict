import os
import unittest
from playwright.sync_api import sync_playwright

class TestChromeExtension(unittest.TestCase):
    def test_extension_loads_and_renders_popup(self):
        ext_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extension"))
        self.assertTrue(os.path.exists(ext_path), f"Extension path not found: {ext_path}")

        with sync_playwright() as p:
            # Launch persistent context with extension loaded
            user_data_dir = "/tmp/trueverdict-test-profile"
            args = [
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--headless=new"
            ]

            context = p.chromium.launch_persistent_context(
                user_data_dir,
                args=args,
                headless=True
            )

            # Wait for background/service worker or open extension popup directly
            # In Chrome, extension pages can be loaded directly from file or chrome-extension://
            page = context.new_page()

            # Force the offline rule-engine path regardless of whether server.py is running
            api_prefix = "http://127.0.0.1:8787"
            page.route(f"{api_prefix}/**", lambda route: route.abort())

            # Listen to console errors (the aborted API request is expected)
            console_errors = []
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text)
                if msg.type == "error" and not msg.location.get("url", "").startswith(api_prefix)
                else None,
            )

            # Directly load popup.html via file URL
            popup_path = os.path.join(ext_path, "popup", "popup.html")
            page.goto(f"file://{popup_path}")

            # Verify title and UI elements exist
            title = page.title()
            self.assertEqual(title, "TrueVerdict")

            # Click Demo button to populate demo data
            demo_btn = page.locator("#load-demo-btn")
            self.assertTrue(demo_btn.is_visible())
            demo_btn.click()

            # Wait for results view to become visible
            results_view = page.locator("#results-view")
            results_view.wait_for(state="visible", timeout=3000)

            # Check Product Title
            product_title = page.locator("#product-title").text_content()
            self.assertIn("Sony WH-1000XM5", product_title)

            # Check Verdict Badge
            verdict = page.locator("#verdict-badge").text_content()
            self.assertTrue(verdict in ["DO NOT BUY", "PROCEED WITH CAUTION"])

            # Check Durability Breakdown
            durability_text = page.locator("#durability-verdict-text").text_content()
            self.assertTrue(len(durability_text) > 0)
            print(f"Durability verdict rendered: {durability_text}")

            # Check Fatal Flaws
            flaw_elements = page.locator(".flaw-pill").all_text_contents()
            self.assertTrue(len(flaw_elements) > 0)
            print(f"Fatal flaws rendered: {flaw_elements}")

            # Check Reddit Section
            reddit_summary = page.locator("#reddit-summary").text_content()
            self.assertTrue(len(reddit_summary) > 0)

            # Check Buy Me A Coffee link
            coffee_link = page.locator(".coffee-btn")
            self.assertTrue(coffee_link.is_visible())
            self.assertIn("buymeacoffee.com", coffee_link.get_attribute("href"))

            # Check console errors
            self.assertEqual(len(console_errors), 0, f"Encountered console errors: {console_errors}")

            # Save screenshot of popup for artifact visual presentation
            screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, "popup_preview.png")
            page.screenshot(path=screenshot_path)
            print(f"Saved extension popup screenshot to: {screenshot_path}")

            context.close()

if __name__ == "__main__":
    unittest.main()
