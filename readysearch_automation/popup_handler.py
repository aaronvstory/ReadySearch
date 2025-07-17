"""Pop-up and dialog handling module."""

import asyncio
import logging
from playwright.async_api import Page, Dialog
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PopupHandler:
    """Handles various types of pop-ups and dialogs."""
    
    def __init__(self, page: Page):
        self.page = page
        self.dialog_responses = {
            'alert': True,
            'confirm': True,
            'prompt': 'OK'
        }
        
    async def setup_dialog_handlers(self):
        """Set up automatic dialog handling."""
        async def handle_dialog(dialog: Dialog):
            dialog_type = dialog.type
            message = dialog.message
            
            logger.info(f"Handling {dialog_type} dialog: {message}")
            
            if dialog_type == 'alert':
                await dialog.accept()
            elif dialog_type == 'confirm':
                await dialog.accept()
            elif dialog_type == 'prompt':
                await dialog.accept(self.dialog_responses['prompt'])
            else:
                logger.warning(f"Unknown dialog type: {dialog_type}")
                await dialog.accept()
                
        self.page.on("dialog", handle_dialog)
        
    async def handle_modal_popups(self) -> bool:
        """
        Handle modal pop-ups and overlays.
        
        Returns:
            True if any pop-ups were handled
        """
        handled = False
        
        # Common modal selectors
        modal_selectors = [
            # Generic modal patterns
            '[class*="modal"]',
            '[class*="popup"]', 
            '[class*="overlay"]',
            '[role="dialog"]',
            '[class*="lightbox"]',
            
            # Cookie banners
            '[class*="cookie"]',
            '[id*="cookie"]',
            '[class*="gdpr"]',
            
            # Newsletter/subscription popups
            '[class*="newsletter"]',
            '[class*="subscribe"]',
            '[class*="signup"]',
            
            # Loading screens
            '[class*="loading"]',
            '[class*="spinner"]',
            
            # Common close button patterns
            '.close',
            '.close-button',
            '[aria-label*="close"]',
            '[title*="close"]'
        ]
        
        for selector in modal_selectors:
            try:
                # Check if modal exists
                modal = await self.page.query_selector(selector)
                if modal:
                    # Check if modal is visible
                    is_visible = await modal.is_visible()
                    if is_visible:
                        logger.info(f"Found visible modal with selector: {selector}")
                        
                        # Try to find and click close button
                        close_handled = await self._try_close_modal(modal)
                        if close_handled:
                            handled = True
                            await asyncio.sleep(0.5)  # Wait for modal to close
                            
            except Exception as e:
                logger.debug(f"Error checking selector {selector}: {str(e)}")
                continue
                
        return handled
        
    async def _try_close_modal(self, modal_element) -> bool:
        """
        Try various methods to close a modal.
        
        Args:
            modal_element: The modal element
            
        Returns:
            True if modal was successfully closed
        """
        close_selectors = [
            # Direct close buttons
            'button:has-text("Close")',
            'button:has-text("×")',
            'button:has-text("✕")',
            '[aria-label*="close"]',
            '[title*="close"]',
            '.close',
            '.close-btn',
            '.close-button',
            
            # Cancel/dismiss buttons
            'button:has-text("Cancel")',
            'button:has-text("Dismiss")',
            'button:has-text("No thanks")',
            'button:has-text("Skip")',
            
            # Generic buttons that might close
            'button[class*="close"]',
            'a[class*="close"]',
            'span[class*="close"]'
        ]
        
        # Try to find close button within modal
        for close_selector in close_selectors:
            try:
                close_button = await modal_element.query_selector(close_selector)
                if close_button:
                    is_visible = await close_button.is_visible()
                    is_enabled = await close_button.is_enabled()
                    
                    if is_visible and is_enabled:
                        logger.info(f"Clicking close button: {close_selector}")
                        await close_button.click()
                        return True
                        
            except Exception as e:
                logger.debug(f"Error with close selector {close_selector}: {str(e)}")
                continue
                
        # Try clicking outside modal (backdrop click)
        try:
            # Get modal bounding box
            box = await modal_element.bounding_box()
            if box:
                # Click outside the modal
                await self.page.click('body', position={'x': 10, 'y': 10})
                logger.info("Tried backdrop click to close modal")
                return True
        except Exception as e:
            logger.debug(f"Backdrop click failed: {str(e)}")
            
        # Try pressing Escape key
        try:
            await self.page.keyboard.press('Escape')
            logger.info("Tried Escape key to close modal")
            return True
        except Exception as e:
            logger.debug(f"Escape key failed: {str(e)}")
            
        return False
        
    async def wait_for_page_ready(self, timeout: int = 10000):
        """
        Wait for page to be ready and handle any immediate pop-ups.
        
        Args:
            timeout: Maximum time to wait in milliseconds
        """
        try:
            # Wait for network to be idle
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            
            # Small delay to let any delayed pop-ups appear
            await asyncio.sleep(1)
            
            # Handle any modal pop-ups
            await self.handle_modal_popups()
            
            # Another small delay after handling pop-ups
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"Error waiting for page ready: {str(e)}")
            
    async def handle_cookie_consent(self) -> bool:
        """
        Specifically handle cookie consent banners.
        
        Returns:
            True if cookie consent was handled
        """
        cookie_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Accept All")',
            'button:has-text("I Accept")',
            'button:has-text("OK")',
            'button:has-text("Agree")',
            'button:has-text("Continue")',
            '[id*="accept"]',
            '[class*="accept"]'
        ]
        
        for selector in cookie_selectors:
            try:
                button = await self.page.query_selector(selector)
                if button:
                    is_visible = await button.is_visible()
                    if is_visible:
                        logger.info(f"Accepting cookies with: {selector}")
                        await button.click()
                        await asyncio.sleep(0.5)
                        return True
            except Exception as e:
                logger.debug(f"Cookie consent selector failed {selector}: {str(e)}")
                continue
                
        return False

    async def handle_readysearch_popups(self) -> bool:
        """
        Handle ReadySearch-specific popups and alerts.
        
        Returns:
            True if any ReadySearch popups were handled
        """
        handled = False
        
        # ReadySearch-specific popup patterns
        readysearch_selectors = [
            # Alert messages
            '.alert',
            '.alert-message',
            '.popup-message',
            '[class*="alert"]',
            
            # Modal dialogs
            '.modal',
            '.popup',
            '[role="dialog"]',
            '[class*="modal"]',
            '[class*="popup"]',
            
            # Specific ReadySearch elements
            '[class*="records"]',
            '[class*="multiple"]'
        ]
        
        for selector in readysearch_selectors:
            try:
                popup = await self.page.query_selector(selector)
                if popup:
                    is_visible = await popup.is_visible()
                    if is_visible:
                        # Check if this is the "multiple records" popup
                        text_content = await popup.text_content()
                        if text_content and "MULTIPLE RECORDS" in text_content.upper():
                            logger.info("Found ReadySearch multiple records popup")
                            handled_popup = await self._handle_multiple_records_popup(popup)
                            if handled_popup:
                                handled = True
                                continue
                        
                        # Try generic popup handling
                        handled_popup = await self._try_close_modal(popup)
                        if handled_popup:
                            handled = True
                            
            except Exception as e:
                logger.debug(f"Error checking ReadySearch popup {selector}: {str(e)}")
                continue
                
        return handled

    async def _handle_multiple_records_popup(self, popup_element) -> bool:
        """
        Handle the specific "ONE PERSON MAY HAVE MULTIPLE RECORDS" popup.
        
        Args:
            popup_element: The popup element
            
        Returns:
            True if popup was handled successfully
        """
        try:
            # ReadySearch-specific OK button selectors
            ok_selectors = [
                'button:has-text("OK")',
                'input[value="OK"]',
                'button:has-text("Continue")',
                'button:has-text("Proceed")',
                '.ok-button',
                '[class*="ok"]',
                'button[type="button"]',
                'button[type="submit"]'
            ]
            
            # Try to find and click OK button within the popup
            for ok_selector in ok_selectors:
                try:
                    ok_button = await popup_element.query_selector(ok_selector)
                    if ok_button:
                        is_visible = await ok_button.is_visible()
                        is_enabled = await ok_button.is_enabled()
                        
                        if is_visible and is_enabled:
                            logger.info(f"Clicking OK on multiple records popup: {ok_selector}")
                            await ok_button.click()
                            await asyncio.sleep(0.5)  # Wait for popup to close
                            return True
                            
                except Exception as e:
                    logger.debug(f"OK button selector {ok_selector} failed: {str(e)}")
                    continue
            
            # If no OK button found, try clicking the popup itself
            try:
                await popup_element.click()
                logger.info("Clicked on multiple records popup directly")
                return True
            except Exception as e:
                logger.debug(f"Direct popup click failed: {str(e)}")
            
            # Try pressing Enter key
            try:
                await self.page.keyboard.press('Enter')
                logger.info("Pressed Enter to dismiss multiple records popup")
                return True
            except Exception as e:
                logger.debug(f"Enter key for popup failed: {str(e)}")
                
            return False
            
        except Exception as e:
            logger.warning(f"Error handling multiple records popup: {str(e)}")
            return False