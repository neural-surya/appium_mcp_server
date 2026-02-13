# Appium MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that lets AI assistants like Claude control mobile devices through Appium. It exposes Appium actions — tapping, typing, swiping, screenshots, and more — as MCP tools.

## Prerequisites

- **Python 3.10+**
- **Appium 2.x** server installed and running
- **Android SDK** (for Android testing) or **Xcode** (for iOS testing)
- A running **emulator/simulator** or connected **physical device**

### Install Appium

```bash
npm install -g appium

# Install the driver for your platform
appium driver install uiautomator2   # Android
appium driver install xcuitest       # iOS
```

## Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd appium_mcp_server
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # macOS/Linux
   # .venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   ```

3. **Configure your device and app**

   Edit `config/test_config.json`:

   ```json
   {
     "platform": "android",

     "android": {
       "app_package": "com.example.myapp",
       "app_activity": ".MainActivity",
       "device_name": "Android Emulator",
       "platform_version": "16",
       "app_path": ""
     },

     "ios": {
       "bundle_id": "com.example.myapp",
       "device_name": "iPhone 15",
       "platform_version": "17.0",
       "app_path": ""
     },

     "appium": {
       "url": "http://localhost:4723"
     }
   }
   ```

   | Field | Description |
   |---|---|
   | `platform` | `"android"` or `"ios"` |
   | `app_package` / `bundle_id` | Your app's package name or bundle identifier |
   | `app_activity` | Android launch activity (e.g. `".MainActivity"`) |
   | `device_name` | Emulator/simulator name or physical device name |
   | `platform_version` | OS version on the device |
   | `app_path` | Absolute path to `.apk`/`.ipa` file (leave empty if the app is already installed) |
   | `appium.url` | Appium server URL (default `http://localhost:4723`) |

4. **Start the Appium server**

   ```bash
   appium
   ```

5. **Start an emulator/simulator or connect a device**

   ```bash
   # Android — launch an AVD
   emulator -avd <avd_name>

   # iOS — open a simulator
   open -a Simulator
   ```

## Adding to Your MCP Client

### Claude Desktop

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "appium": {
      "command": "/absolute/path/to/appium_mcp_server/.venv/bin/python",
      "args": ["/absolute/path/to/appium_mcp_server/server.py"]
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add appium /absolute/path/to/appium_mcp_server/.venv/bin/python /absolute/path/to/appium_mcp_server/server.py
```

> **Important:** Use the absolute path to the Python binary inside `.venv` so that the correct dependencies are available.

## Available Tools

| Tool | Description |
|---|---|
| `start_session` | Start an Appium session (call once at the beginning) |
| `close_session` | Close the active session and release the device |
| `take_screenshot` | Capture a screenshot of the current screen |
| `get_page_source` | Get the UI hierarchy as XML (useful for finding element locators) |
| `tap` | Tap an element by locator strategy and value |
| `tap_coordinates` | Tap at absolute screen coordinates (x, y) |
| `type_text` | Type text into an element |
| `clear_text` | Clear the text content of an element |
| `swipe` | Swipe in a direction (up / down / left / right) |
| `press_back` | Press the Android back button |
| `press_home` | Press the home button |
| `hide_keyboard` | Dismiss the on-screen keyboard |

### Locator Strategies

The `tap`, `type_text`, and `clear_text` tools accept a `strategy` parameter:

| Strategy | Example Value |
|---|---|
| `id` | `com.example:id/login_btn` |
| `xpath` | `//android.widget.Button[@text='Login']` |
| `accessibility_id` | `login_button` |
| `class_name` | `android.widget.EditText` |
| `android_uiautomator` | `new UiSelector().text("Login")` |
| `ios_predicate` | `label == "Login"` |
| `ios_class_chain` | `**/XCUIElementTypeButton[\`label == "Login"\`]` |

## Example Prompt

> Start an Appium session. Take a screenshot to see the current screen. Then get the page source to find the email and password field locators. Enter "user@example.com" as email and "mypassword" as password, tap the Login button, and take a screenshot of the result.

## Project Structure

```
appium_mcp_server/
├── server.py              # MCP server — defines all tools
├── appium_manager.py      # Appium session manager (singleton)
├── config/
│   ├── __init__.py        # Config loader
│   └── test_config.json   # Device and app configuration
├── requirements.txt
└── README.md
```

## License

MIT
