---
name: antigravity-disable-auto-update-macos
description: Find and disable Antigravity's auto-update behavior on macOS by verifying its Electron/VS Code update setting and editing the user settings file.
---

When to use
- The user says Antigravity keeps checking/downloading/updating on macOS.
- You need the safest setting-based way to stop update attempts instead of guessing at plist keys or deleting caches.

Goal
- Confirm whether the installed Antigravity app uses the VS Code/Electron update service.
- Identify the supported `update.mode` values from the app bundle.
- Instruct or apply the correct user setting in `~/Library/Application Support/Antigravity/User/settings.json`.

Steps
1. Confirm the app and its updater traces exist.
   - Search for app support, preferences, and ShipIt/updater files:
     - `~/Library/Application Support/Antigravity/`
     - `~/Library/Preferences/com.google.antigravity.plist`
     - `~/Library/Caches/com.google.antigravity.ShipIt/`
   - Useful evidence in logs:
     - `update#setState checking for updates`
     - `update#setState downloading`

2. Do not assume plist keys control updates.
   - The preference plist may only contain generic macOS state and not the real update toggle.
   - Check `~/Library/Application Support/Antigravity/User/settings.json` first.

3. Verify the app bundle’s update mechanism before giving advice.
   - Inspect the bundled JS/resources under:
     - `/Applications/Antigravity.app/Contents/Resources/app/`
   - Search for strings such as:
     - `update.mode`
     - `checkForUpdates`
     - `disableUpdates`
     - `ShipIt`
     - `squirrel`
   - Confirm code paths showing `update.mode` behavior. In the inspected Antigravity build, the bundle used a VS Code/Electron update service that reads `update.mode` and supports:
     - `none`
     - `manual`
     - `start`

4. Apply the setting-based fix.
   - Edit `~/Library/Application Support/Antigravity/User/settings.json`.
   - Preferred hard stop:
     - `"update.mode": "none"`
   - Safer alternatives if the user still wants manual control:
     - `"manual"` = only manual checks
     - `"start"` = check at startup only

5. Preserve existing settings.
   - Merge the new key into the JSON instead of replacing unrelated preferences.
   - Example:

```json
{
  "workbench.colorTheme": "Solarized Light",
  "update.mode": "none"
}
```

6. Tell the user to fully quit and relaunch Antigravity.
   - A full restart is needed so the new update mode is picked up cleanly.

Verification
- Reopen Antigravity and inspect logs under `~/Library/Application Support/Antigravity/logs/`.
- Repeated transitions like `checking for updates` / `downloading` should stop when `update.mode` is `none`.

Pitfalls
- Do not invent undocumented plist flags if the bundle already exposes `update.mode`.
- Do not rely on deleting ShipIt caches as the primary fix; that is temporary and does not change app behavior.
- `settings.json` may initially contain only theme/editor preferences; that does not mean update settings are unsupported.
- Large bundle/resource searches can be noisy; searching specifically for `update.mode` and `checkForUpdates` is much more effective than broad `update` scans.
