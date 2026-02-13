"""Appium MCP Server — exposes mobile device control as MCP tools."""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image

from appium_manager import get_manager

mcp = FastMCP("appium")


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------

@mcp.tool()
def start_session() -> str:
    """Start an Appium session using the config in config/test_config.json.
    Call this once at the beginning. Do NOT call it again before each action —
    the session persists across tool calls until close_session is called."""
    return get_manager().start_session()


@mcp.tool()
def close_session() -> str:
    """Close the active Appium session and release the device."""
    return get_manager().close_session()


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

@mcp.tool()
def take_screenshot() -> Image:
    """Take a screenshot of the current device screen.
    Returns the image so you can see what is on screen."""
    png_bytes = get_manager().take_screenshot()
    return Image(data=png_bytes, format="png")


@mcp.tool()
def get_page_source() -> str:
    """Get the UI hierarchy of the current screen as XML.
    Use this to discover element locators (resource-id, xpath, accessibility id, etc.)."""
    return get_manager().get_page_source()


# ---------------------------------------------------------------------------
# Element actions
# ---------------------------------------------------------------------------

@mcp.tool()
def tap(strategy: str, value: str) -> str:
    """Tap on an element found by the given locator strategy.

    Args:
        strategy: Locator strategy — one of: id, xpath, accessibility_id,
                  class_name, android_uiautomator, ios_predicate, ios_class_chain
        value: The locator value (e.g. "com.app:id/login_btn" for id strategy)
    """
    return get_manager().tap(strategy, value)


@mcp.tool()
def tap_coordinates(x: int, y: int) -> str:
    """Tap at absolute screen coordinates.

    Args:
        x: Horizontal pixel coordinate
        y: Vertical pixel coordinate
    """
    return get_manager().tap_coordinates(x, y)


@mcp.tool()
def type_text(strategy: str, value: str, text: str) -> str:
    """Type text into an element found by the given locator strategy.

    Args:
        strategy: Locator strategy (id, xpath, accessibility_id, etc.)
        value: The locator value
        text: The text to type into the element
    """
    return get_manager().type_text(strategy, value, text)


@mcp.tool()
def clear_text(strategy: str, value: str) -> str:
    """Clear the text content of an element found by the given locator strategy.

    Args:
        strategy: Locator strategy (id, xpath, accessibility_id, etc.)
        value: The locator value
    """
    return get_manager().clear_text(strategy, value)


# ---------------------------------------------------------------------------
# Gestures
# ---------------------------------------------------------------------------

@mcp.tool()
def swipe(direction: str) -> str:
    """Swipe on the device screen in the given direction.

    Args:
        direction: One of: up, down, left, right
    """
    return get_manager().swipe(direction)


# ---------------------------------------------------------------------------
# Device buttons
# ---------------------------------------------------------------------------

@mcp.tool()
def press_back() -> str:
    """Press the device back button (Android)."""
    return get_manager().press_back()


@mcp.tool()
def press_home() -> str:
    """Press the device home button."""
    return get_manager().press_home()


@mcp.tool()
def hide_keyboard() -> str:
    """Hide the on-screen keyboard if it is currently visible."""
    return get_manager().hide_keyboard()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
