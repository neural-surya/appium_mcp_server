"""Singleton Appium session manager for the MCP server."""

import base64
import sys
from typing import Optional

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from config import load_config

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_manager: Optional["AppiumManager"] = None


def get_manager() -> "AppiumManager":
    """Return (or create) the singleton AppiumManager instance."""
    global _manager
    if _manager is None:
        _manager = AppiumManager()
    return _manager


# ---------------------------------------------------------------------------
# Locator strategy mapping
# ---------------------------------------------------------------------------
_STRATEGY_MAP = {
    "id": AppiumBy.ID,
    "xpath": AppiumBy.XPATH,
    "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
    "class_name": AppiumBy.CLASS_NAME,
    "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
    "ios_predicate": AppiumBy.IOS_PREDICATE,
    "ios_class_chain": AppiumBy.IOS_CLASS_CHAIN,
}


def _resolve_strategy(strategy: str):
    return _STRATEGY_MAP.get(strategy.lower(), AppiumBy.XPATH)


def _log(msg: str) -> None:
    """Log to stderr (STDIO transport must keep stdout clean)."""
    print(f"[appium-mcp] {msg}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# AppiumManager
# ---------------------------------------------------------------------------
class AppiumManager:
    def __init__(self) -> None:
        self.driver: Optional[webdriver.Remote] = None
        self.config: dict = load_config()

    # ------ session lifecycle ------

    def start_session(self) -> str:
        """Build capabilities from config and create the Appium session."""
        if self.driver is not None:
            return "Session already active"

        cfg = self.config
        platform = cfg["platform"].lower()
        appium_url = cfg.get("appium", {}).get("url", "http://localhost:4723")

        if platform == "android":
            acfg = cfg["android"]
            caps = {
                "platformName": "Android",
                "appium:automationName": "UiAutomator2",
                "appium:deviceName": acfg.get("device_name", "Android Emulator"),
                "appium:platformVersion": acfg.get("platform_version", "16"),
                "appium:newCommandTimeout": 3600,
                "appium:noReset": True,
                "appium:autoGrantPermissions": True,
            }
            if acfg.get("app_package"):
                caps["appium:appPackage"] = acfg["app_package"]
            if acfg.get("app_activity"):
                caps["appium:appActivity"] = acfg["app_activity"]
            if acfg.get("app_path"):
                caps["appium:app"] = acfg["app_path"]

        elif platform == "ios":
            icfg = cfg["ios"]
            caps = {
                "platformName": "iOS",
                "appium:automationName": "XCUITest",
                "appium:deviceName": icfg.get("device_name", "iPhone 15"),
                "appium:platformVersion": icfg.get("platform_version", "17.0"),
                "appium:newCommandTimeout": 3600,
                "appium:noReset": True,
                "appium:autoAcceptAlerts": True,
            }
            if icfg.get("bundle_id"):
                caps["appium:bundleId"] = icfg["bundle_id"]
            if icfg.get("app_path"):
                caps["appium:app"] = icfg["app_path"]
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        _log(f"Connecting to Appium at {appium_url} ({platform})")
        self.driver = webdriver.Remote(appium_url, options=_caps_to_options(caps))
        _log("Session started")
        return f"Session started on {platform}"

    def close_session(self) -> str:
        """Quit the Appium driver and reset the singleton."""
        global _manager
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
            _log("Session closed")
        _manager = None
        return "Session closed"

    # ------ queries ------

    def _is_session_alive(self) -> bool:
        """Check whether the Appium session is still valid."""
        if self.driver is None:
            return False
        try:
            # Use a mobile-safe command to probe the Appium server.
            # driver.title throws on native apps; get_window_size() works everywhere.
            self.driver.get_window_size()
            return True
        except Exception:
            return False

    def _ensure_driver(self) -> webdriver.Remote:
        if self.driver is None:
            raise RuntimeError("No active session. Call start_session first.")
        if not self._is_session_alive():
            _log("Session expired — reconnecting automatically")
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            self.start_session()
        return self.driver

    def take_screenshot(self) -> bytes:
        """Return raw PNG bytes of the current screen."""
        driver = self._ensure_driver()
        b64 = driver.get_screenshot_as_base64()
        return base64.b64decode(b64)

    def get_page_source(self) -> str:
        """Return the UI hierarchy as XML."""
        return self._ensure_driver().page_source

    # ------ element actions ------

    def tap(self, strategy: str, value: str) -> str:
        """Find an element and click it."""
        driver = self._ensure_driver()
        el = driver.find_element(_resolve_strategy(strategy), value)
        el.click()
        return f"Tapped element ({strategy}={value})"

    def tap_coordinates(self, x: int, y: int) -> str:
        """Tap at absolute screen coordinates."""
        self._ensure_driver().tap([(x, y)])
        return f"Tapped at ({x}, {y})"

    def type_text(self, strategy: str, value: str, text: str) -> str:
        """Find an element and type text into it."""
        driver = self._ensure_driver()
        el = driver.find_element(_resolve_strategy(strategy), value)
        el.send_keys(text)
        return f"Typed '{text}' into ({strategy}={value})"

    def clear_text(self, strategy: str, value: str) -> str:
        """Find an element and clear its text."""
        driver = self._ensure_driver()
        el = driver.find_element(_resolve_strategy(strategy), value)
        el.clear()
        return f"Cleared text in ({strategy}={value})"

    # ------ gestures ------

    def swipe(self, direction: str, duration: int = 800) -> str:
        """Swipe in a direction (up/down/left/right) using 80%/20% coordinates."""
        driver = self._ensure_driver()
        size = driver.get_window_size()
        w, h = size["width"], size["height"]

        if direction == "up":
            driver.swipe(w // 2, int(h * 0.8), w // 2, int(h * 0.2), duration)
        elif direction == "down":
            driver.swipe(w // 2, int(h * 0.2), w // 2, int(h * 0.8), duration)
        elif direction == "left":
            driver.swipe(int(w * 0.8), h // 2, int(w * 0.2), h // 2, duration)
        elif direction == "right":
            driver.swipe(int(w * 0.2), h // 2, int(w * 0.8), h // 2, duration)
        else:
            raise ValueError(f"Invalid direction: {direction}. Use up/down/left/right.")

        return f"Swiped {direction}"

    # ------ device buttons ------

    def press_back(self) -> str:
        """Press the Android back button."""
        self._ensure_driver().back()
        return "Pressed back"

    def press_home(self) -> str:
        """Press the home button via keycode."""
        driver = self._ensure_driver()
        driver.press_keycode(3)  # KEYCODE_HOME
        return "Pressed home"

    def hide_keyboard(self) -> str:
        """Hide the on-screen keyboard if visible."""
        driver = self._ensure_driver()
        try:
            driver.hide_keyboard()
        except Exception:
            pass  # keyboard may not be visible
        return "Keyboard hidden (or was not visible)"


# ---------------------------------------------------------------------------
# Helper — convert flat caps dict to UiAutomator2Options / XCUITestOptions
# ---------------------------------------------------------------------------
def _caps_to_options(caps: dict):
    """Convert a capabilities dict to an Appium Options object."""
    from appium.options.android import UiAutomator2Options
    from appium.options.ios import XCUITestOptions

    platform = caps.get("platformName", "").lower()
    if platform == "android":
        opts = UiAutomator2Options()
    else:
        opts = XCUITestOptions()

    for key, value in caps.items():
        if key == "platformName":
            continue
        # Strip 'appium:' prefix for the options setter
        clean_key = key.replace("appium:", "")
        opts.set_capability(key, value)

    return opts
