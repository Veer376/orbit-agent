from playwright.sync_api import sync_playwright, Page, Browser, Playwright

class BrowserController:
    def __init__(self, viewport_width=1024, viewport_height=768):
        try:
            self.playwright: Playwright = sync_playwright().start()
            self.browser: Browser = self.playwright.chromium.launch(
                headless=False, # Keep False for debugging, True for headless
                chromium_sandbox=True,
                env={},
                args=["--disable-extensions", "--disable-file-system"]
            )
            self.page: Page = self.browser.new_page()
            self.page.set_viewport_size({"width": viewport_width, "height": viewport_height})
            print("    BROWSER_GENT >> Browser initialized.")
            
        except Exception as e:
            print(f"    Error during browser initialization: {e}")
            # Attempt cleanup if partial initialization occurred
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
            raise # Re-raise the exception

    def navigate(self, url: str):
        try:
            self.page.goto(url, wait_until='load', timeout=60000) # Wait for load, reasonable timeout
            print("    BROWSER_AGENT >> Navigation successful.")
        except Exception as e:
            print(f"    Error navigating to {url}: {e}")
            # Decide how to handle navigation errors (e.g., raise, return status)

    def close(self):
        print("    Closing browser controller...")
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
                print("    Browser closed.")
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
                print("    Playwright stopped.")
        except Exception as e:
            print(f"    Error during closing: {e}")
        