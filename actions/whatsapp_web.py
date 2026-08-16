# actions/whatsapp_web.py
# WhatsApp Web integration via Playwright — QR code pairing, persistent session,
# message sending and incoming message monitoring.
#
# Flow:
#   1. connect() opens WhatsApp Web in a headless Chromium browser
#   2. If not paired, extracts the QR code canvas and returns it as a base64 PNG
#   3. User scans the QR with their phone → WhatsApp Web logs in
#   4. Session (cookies + localStorage) is saved to %LOCALAPPDATA%/Brahma Echo/whatsapp_session/
#   5. On reconnect, the saved session is restored — no QR needed
#   6. send_message() and listen() work over the browser connection

from __future__ import annotations

import asyncio
import base64
import json
import os
import time
from pathlib import Path

from brahma_paths import get_user_data_dir


# ---------------------------------------------------------------------------
# Session storage
# ---------------------------------------------------------------------------

def _session_dir() -> Path:
    d = get_user_data_dir() / "whatsapp_session"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# WhatsAppWebClient — async singleton
# ---------------------------------------------------------------------------

class WhatsAppWebClient:
    """
    Manages a persistent Playwright browser session for WhatsApp Web.

    Usage:
        client = WhatsAppWebClient()
        await client.connect(on_qr=display_qr_callback)
        await client.send_message("John", "Hello from Brahma Echo!")
    """

    WHATSAPP_URL = "https://web.whatsapp.com/"

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._connected = False
        self._paired = False
        self._on_qr_callback = None
        self._on_message_callback = None
        self._listener_task = None

    # -- Connection -------------------------------------------------------

    async def connect(self, on_qr=None, on_paired=None, headless: bool = True):
        """
        Opens WhatsApp Web. If not previously paired, extracts the QR code
        and calls on_qr(base64_png_string). When the user scans it,
        calls on_paired().
        """
        from playwright.async_api import async_playwright

        self._on_qr_callback = on_qr
        session_path = _session_dir()

        self._playwright = await async_playwright().start()

        # Use a persistent context so cookies + localStorage survive restarts
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
            ],
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        self._page = self._context.pages[0] if self._context.pages else await self._context.new_page()
        await self._page.goto(self.WHATSAPP_URL, wait_until="domcontentloaded")

        # Wait a moment for the page to load
        await asyncio.sleep(3)

        # Check if already paired (session restored)
        if await self._is_paired():
            self._paired = True
            self._connected = True
            if on_paired:
                await on_paired()
            return {"status": "paired", "qr": None}

        # Not paired — extract QR code
        qr_b64 = await self._extract_qr()
        if qr_b64 and on_qr:
            await on_qr(qr_b64)

        # Wait for the user to scan (poll for up to 120 seconds)
        for _ in range(120):
            await asyncio.sleep(1)
            if await self._is_paired():
                self._paired = True
                self._connected = True
                if on_paired:
                    await on_paired()
                return {"status": "paired", "qr": qr_b64}

        return {"status": "timeout", "qr": qr_b64}

    async def _is_paired(self) -> bool:
        """Check if WhatsApp Web shows the chat list (meaning we're logged in)."""
        try:
            # WhatsApp Web shows a canvas QR when not logged in,
            # and the chat list when logged in
            login_canvas = await self._page.query_selector("canvas[aria-label='Scan this QR code to pair a device']")
            if login_canvas:
                return False
            # Check for the chat search box or chat list — means we're logged in
            search = await self._page.query_selector("div[contenteditable='true'][data-tab='3']")
            if search:
                return True
            # Fallback: check for the "Keep your phone connected" text
            body_text = await self._page.inner_text("body")
            if "Keep your phone connected" in body_text:
                return True
            return False
        except Exception:
            return False

    async def _extract_qr(self) -> str | None:
        """Extract the QR code from the WhatsApp Web canvas as a base64 PNG."""
        try:
            # WhatsApp Web renders the QR on a canvas element
            canvas = await self._page.query_selector("canvas[aria-label='Scan this QR code to pair a device']")
            if not canvas:
                # Try alternate selectors
                canvas = await self._page.query_selector("canvas")
                if not canvas:
                    return None

            # Use JS to extract the canvas content as base64 PNG
            b64 = await self._page.evaluate("""
                () => {
                    const canvas = document.querySelector("canvas[aria-label='Scan this QR code to pair a device']") || document.querySelector("canvas");
                    if (!canvas) return null;
                    return canvas.toDataURL("image/png").replace(/^data:image\\/png;base64,/, "");
                }
            """)
            return b64
        except Exception as e:
            print(f"[WhatsAppWeb] QR extraction error: {e}")
            return None

    # -- Send message -----------------------------------------------------

    async def send_message(self, contact_name: str, message: str) -> str:
        """
        Send a message to a WhatsApp contact by name.
        Uses the WhatsApp Web search to find the contact, then types and sends.
        """
        if not self._paired or not self._page:
            return "WhatsApp Web is not connected. Please pair first."

        try:
            # Open search
            search_box = await self._page.query_selector("div[contenteditable='true'][data-tab='3']")
            if not search_box:
                return "Could not find WhatsApp Web search box."

            # Clear and type contact name
            await search_box.click()
            await self._page.keyboard.press("Control+a")
            await self._page.keyboard.type(contact_name)
            await asyncio.sleep(1.5)

            # Click the first search result (the contact)
            # WhatsApp Web shows results in a list — click the first one
            contact_result = await self._page.query_selector("div[role='listitem']")
            if contact_result:
                await contact_result.click()
                await asyncio.sleep(1.0)
            else:
                # Try pressing Enter to select first result
                await self._page.keyboard.press("Enter")
                await asyncio.sleep(1.0)

            # Type the message in the message input box
            msg_box = await self._page.query_selector("div[contenteditable='true'][data-tab='10']")
            if not msg_box:
                # Fallback: try footer div
                msg_box = await self._page.query_selector("footer div[contenteditable='true']")
                if not msg_box:
                    return "Could not find WhatsApp Web message input box."

            await msg_box.click()
            await self._page.keyboard.type(message)
            await asyncio.sleep(0.3)
            await self._page.keyboard.press("Enter")

            return f"Message sent to {contact_name} via WhatsApp Web."

        except Exception as e:
            return f"WhatsApp Web send error: {e}"

    # -- Listen for incoming messages ------------------------------------

    async def start_listening(self, on_message=None):
        """
        Start monitoring WhatsApp Web for incoming messages.
        Calls on_message(sender_name, message_text) for each new message.
        """
        self._on_message_callback = on_message
        self._listener_task = asyncio.create_task(self._listen_loop())

    async def _listen_loop(self):
        """Poll for new messages in the currently open chat."""
        last_messages = set()
        while self._paired and self._page:
            try:
                # Get all message bubbles in the current chat
                messages = await self._page.query_selector_all("div.message-in span.selectable-text")
                for msg_el in messages:
                    text = await msg_el.inner_text()
                    if text and text not in last_messages:
                        last_messages.add(text)
                        if self._on_message_callback:
                            # Try to get sender name
                            sender = "Unknown"
                            try:
                                sender_el = await msg_el.evaluate(
                                    "el => el.closest('div')?.parentElement?.querySelector('span[dir=\"auto\"]')?.innerText || 'Unknown'"
                                )
                                if sender_el:
                                    sender = sender_el
                            except Exception:
                                pass
                            await self._on_message_callback(sender, text)
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5)

    async def stop_listening(self):
        if self._listener_task:
            self._listener_task.cancel()
            self._listener_task = None

    # -- Disconnect -------------------------------------------------------

    async def disconnect(self):
        """Close the browser and save the session."""
        await self.stop_listening()
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()
        self._connected = False
        self._paired = False
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None

    # -- Status -----------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        return self._connected and self._paired

    @property
    def is_paired(self) -> bool:
        return self._paired


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_client: WhatsAppWebClient | None = None

def get_client() -> WhatsAppWebClient:
    global _client
    if _client is None:
        _client = WhatsAppWebClient()
    return _client


# ---------------------------------------------------------------------------
# Synchronous wrappers for main.py integration
# ---------------------------------------------------------------------------

def pair_whatsapp(qr_callback=None, paired_callback=None) -> dict:
    """
    Synchronous wrapper to connect and pair WhatsApp Web.
    qr_callback(base64_png) is called when the QR code is ready.
    paired_callback() is called when pairing succeeds.
    Returns {"status": "paired"|"timeout"|"error", "qr": base64_png|None}
    """
    client = get_client()

    async def _on_qr(b64):
        if qr_callback:
            qr_callback(b64)

    async def _on_paired():
        if paired_callback:
            paired_callback()

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(client.connect(on_qr=_on_qr, on_paired=_on_paired))
        loop.close()
        return result
    except Exception as e:
        return {"status": "error", "qr": None, "error": str(e)}


def send_whatsapp_web(receiver: str, message: str) -> str:
    """
    Synchronous wrapper to send a message via WhatsApp Web.
    Falls back gracefully if not connected.
    """
    client = get_client()
    if not client.is_paired:
        return "WhatsApp Web is not paired. Please pair first using the QR code."

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(client.send_message(receiver, message))
        loop.close()
        return result
    except Exception as e:
        return f"WhatsApp Web error: {e}"


def is_whatsapp_web_connected() -> bool:
    """Check if WhatsApp Web is connected and paired."""
    client = get_client()
    return client.is_connected


def disconnect_whatsapp_web():
    """Disconnect WhatsApp Web."""
    client = get_client()
    if client.is_connected:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(client.disconnect())
            loop.close()
        except Exception:
            pass
