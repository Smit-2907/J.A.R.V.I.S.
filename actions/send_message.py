# actions/send_message.py
# Universal messaging — WhatsApp, Telegram, Instagram
# Improved with window focus control and better reliability.

import time
import pyautogui
import pyperclip
import os
import sys

try:
    import win32gui
    import win32con
    _WIN32 = True
except ImportError:
    _WIN32 = False

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

def _focus_window(title_part: str) -> bool:
    """Uses win32gui to find and focus a window by title fragment."""
    if not _WIN32: return False
    
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_part.lower() in title.lower():
                windows.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    if windows:
        hwnd = windows[0]
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            return True
        except Exception:
            pass
    return False

def _open_app(app_name: str) -> bool:
    """Focuses existing app or launches via Windows search."""
    if _focus_window(app_name):
        time.sleep(1.0)
        return True
        
    try:
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write(app_name, interval=0.03)
        time.sleep(0.6)
        pyautogui.press("enter")
        time.sleep(5.0) 
        return True
    except Exception as e:
        print(f"[SendMessage] Could not open {app_name}: {e}")
        return False

def _search_contact(contact: str, is_whatsapp: bool = False):
    """Universal search and select contact."""
    if is_whatsapp:
        # Ctrl+Alt+N or Ctrl+N starts a new chat / search in WhatsApp Desktop
        pyautogui.hotkey("ctrl", "alt", "n")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "n")
    else:
        pyautogui.hotkey("ctrl", "f")
    
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    time.sleep(0.8)
    pyautogui.write(contact, interval=0.05)
    time.sleep(2.0)  # Wait for search results to populate
    pyautogui.press("enter")
    time.sleep(1.0)
    # Double enter to be sure or escape to clear focus
    pyautogui.press("enter")
    time.sleep(0.5)

def _send_whatsapp(receiver: str, message: str) -> str:
    """Reliable WhatsApp messaging via desktop app."""
    try:
        if not _open_app("WhatsApp"):
            return "Could not open or find WhatsApp, sir."

        _search_contact(receiver, is_whatsapp=True)
        
        time.sleep(1.0)
        # Type a small character and backspace to ensure focus
        pyautogui.write(" ")
        pyautogui.press("backspace")
        
        pyperclip.copy(message)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")

        return f"Message successfully sent to {receiver} via WhatsApp."

    except Exception as e:
        return f"WhatsApp messaging failed: {e}"

def _send_instagram(receiver: str, message: str) -> str:
    """Sends Instagram DM via browser."""
    try:
        import webbrowser
        webbrowser.open("https://www.instagram.com/direct/new/")
        time.sleep(4.0)

        pyautogui.write(receiver, interval=0.04)
        time.sleep(1.5)
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.5)
        
        # Tab to message box (usually 3-4 tabs)
        for _ in range(4):
            pyautogui.press("tab")
            time.sleep(0.1)
        pyautogui.press("enter")
        time.sleep(0.5)

        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)
        pyautogui.press("enter")

        return f"Instagram message sent to {receiver}."
    except Exception as e:
        return f"Instagram error: {e}"

def _send_telegram(receiver: str, message: str) -> str:
    """Reliable Telegram messaging via desktop app."""
    try:
        if not _open_app("Telegram"):
            return "Could not open Telegram, sir."

        _search_contact(receiver)

        pyperclip.copy(message)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)
        pyautogui.press("enter")

        return f"Telegram message sent to {receiver}."
    except Exception as e:
        return f"Telegram error: {e}"

def send_message(parameters: dict, player=None, **kwargs) -> str:
    """Main entry point for the messaging tool."""
    params   = parameters or {}
    receiver = params.get("receiver", "").strip()
    message  = params.get("message_text", "").strip()
    platform = params.get("platform", "whatsapp").lower()

    if not receiver: return "Sir, I need a recipient name."
    if not message:  return "Sir, what should I say in the message?"

    if player:
        player.write_log(f"SYS: Messaging {receiver} on {platform}...")

    if "whatsapp" in platform or "wp" in platform:
        result = _send_whatsapp(receiver, message)
    elif "instagram" in platform or "ig" in platform:
        result = _send_instagram(receiver, message)
    elif "telegram" in platform or "tg" in platform:
        result = _send_telegram(receiver, message)
    else:
        # Fallback for generic apps
        if _open_app(platform):
            _search_contact(receiver)
            pyperclip.copy(message)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            result = f"Sent message to {receiver} via {platform}."
        else:
            result = f"I couldn't open {platform} to send that message, sir."

    if player:
        player.write_log(f"AI: {result}")
    return result