from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

class BrowserRuntime:
    """
    Manages the physical Playwright instance lifecycle inside the CLI.
    Keeps a persistent browser context open across discrete tool calls instead
    of opening/closing the browser for every single LangGraph step.
    """
    def __init__(self):
        self._pw = None
        self._browser = None
        self._context = None
        self._pages = []
        self._active_page_index = 0
        self.dialog_handler_action = "accept"  # Default dialog behavior
        self.dialog_handler_prompt = ""
        self.console_logs = []
        self.failed_requests = []


    def start(self, headless: bool = False):
        if not self._pw:
            print("🚀 Starting physical Playwright Automation runtime engine...")
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=headless)
            
            # Context required for Tracing, Network interception, and Video recording
            self._context = self._browser.new_context(
                record_video_dir="data/artifacts/videos",
                viewport={'width': 1280, 'height': 800}
            )
            self._create_new_page()

    def _create_new_page(self) -> Page:
        page = self._context.new_page()
        # Automatically handle pesky JS dialogs (alert/confirm/prompt) so the LLM doesn't hang!
        page.on("dialog", self._handle_dialog)
        page.on("console", self._handle_console)
        page.on("requestfinished", self._handle_request_finished)
        
        self._pages.append(page)
        self._active_page_index = len(self._pages) - 1
        return page

    def _handle_console(self, msg):
        """Captures JS errors and warnings for the failure analyst."""
        if msg.type in ["error", "warning"]:
            self.console_logs.append({
                "type": msg.type,
                "text": msg.text,
                "location": msg.location
            })

    def _handle_request_finished(self, request):
        """Captures failed network calls (4xx/5xx) to correlate with UI failures."""
        response = request.response()
        if response and response.status >= 400:
            self.failed_requests.append({
                "url": request.url,
                "method": request.method,
                "status": response.status,
                "status_text": response.status_text
            })

    def reset_logs(self):
        """Clears logs for a fresh mission run."""
        self.console_logs = []
        self.failed_requests = []


    def _handle_dialog(self, dialog):
        """Auto-responds to JS alerts using the configured LLM behavior parameter"""
        print(f"🪟 [Browser] Intercepted {dialog.type} dialog: {dialog.message}")
        if self.dialog_handler_action == "accept":
            dialog.accept(self.dialog_handler_prompt)
        else:
            dialog.dismiss()

    def get_context(self) -> BrowserContext:
        if not self._context:
            self.start()
        return self._context

    def get_page(self) -> Page:
        """Returns the active browser tab"""
        if not self._pages:
            self.start()
        return self._pages[self._active_page_index]

    def set_active_page(self, index: int):
        """Switches the active tab for the LLM"""
        if 0 <= index < len(self._pages):
            self._active_page_index = index
            self._pages[self._active_page_index].bring_to_front()
            return True
        return False

    def create_tab(self) -> Page:
        return self._create_new_page()

    def stop(self):
        """Clean teardown so zombie Chrome processes do not stick in host memory"""
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()
            
        self._pw = None
        self._browser = None
        self._context = None
        self._pages = []

# A persistent execution process accessible across the graph
runtime = BrowserRuntime()
