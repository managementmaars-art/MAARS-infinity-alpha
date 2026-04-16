---
name: harmony-hdc
description: HarmonyOS device control and UI automation via raw HDC commands. Use for device/emulator discovery, USB or TCP connection, app launch/force-stop, tap/swipe/keyevent/text input, screenshots, UI dump, file transfer, and HDC troubleshooting.
---

# Harmony HDC

Reference for controlling HarmonyOS devices with raw `hdc` commands.

## Execution Constraints

- Use `hdc -t <device_id>` whenever more than one device is connected.
- Confirm screen resolution before coordinate actions: `hdc -t DEVICE shell wm size`.
- Ask for missing required inputs before executing (device id, bundle/ability, coordinates, file paths).
- Surface actionable stderr on failure (authorization, cable/network, tcp mode).

## Device And Server

```bash
# Start HDC server
hdc start

# Stop HDC server
hdc kill

# List targets
hdc list targets

# Target a specific device
hdc -t DEVICE <command>
```

## Connection

```bash
# Connect over TCP
hdc tconn <ip>:<port>

# Disconnect target
hdc -t DEVICE tdis
```

## Device State

```bash
# Device model/system info
hdc -t DEVICE shell param get const.product.model
hdc -t DEVICE shell param get const.ohos.fullname

# Screen size
hdc -t DEVICE shell wm size

# Foreground focus window
hdc -t DEVICE shell hidumper -s WindowManagerService -a '-a'

# Run raw shell command
hdc -t DEVICE shell <command>
```

## App Lifecycle

```bash
# List installed bundles
hdc -t DEVICE shell bm dump -a

# Start an ability
hdc -t DEVICE shell aa start -a <ability_name> -b <bundle_name>

# Start by URI
hdc -t DEVICE shell aa start -U <uri>

# Force-stop app by bundle
hdc -t DEVICE shell aa force-stop <bundle_name>
```

## Input Actions

```bash
# Tap
hdc -t DEVICE shell uitest uiInput click X Y

# Double tap
hdc -t DEVICE shell uitest uiInput click X Y && sleep 0.1 && hdc -t DEVICE shell uitest uiInput click X Y

# Long press
hdc -t DEVICE shell uitest uiInput longClick X Y

# Swipe
hdc -t DEVICE shell uitest uiInput swipe X1 Y1 X2 Y2 [duration_ms]

# Key event
hdc -t DEVICE shell uitest uiInput keyEvent Back
hdc -t DEVICE shell uitest uiInput keyEvent Home
hdc -t DEVICE shell uitest uiInput keyEvent Enter
```

## Text Input

```bash
# Text input (Harmony text input supports UTF-8)
hdc -t DEVICE shell uitest uiInput inputText "hello world"
```

## Screenshot And UI Dump

```bash
# Capture screenshot on device
hdc -t DEVICE shell snapshot_display -f /data/local/tmp/screen.jpeg

# Pull screenshot to local
hdc -t DEVICE file recv /data/local/tmp/screen.jpeg ./screen.jpeg

# Dump UI tree (JSON)
hdc -t DEVICE shell uitest dumpLayout -p /data/local/tmp/layout.json
hdc -t DEVICE file recv /data/local/tmp/layout.json ./layout.json
```

## File Transfer

```bash
# Push file to device
hdc -t DEVICE file send ./local.file /data/local/tmp/remote.file

# Pull file from device
hdc -t DEVICE file recv /data/local/tmp/remote.file ./remote.file
```

## App Install And Uninstall

```bash
# Install HAP
hdc -t DEVICE install /path/to/app.hap

# Install with replace
hdc -t DEVICE install -r /path/to/app.hap

# Uninstall by bundle
hdc -t DEVICE uninstall <bundle_name>
```

## Common KeyEvents

| KeyEvent | Description |
|---------|-------------|
| `Back` | Back button |
| `Home` | Home button |
| `Enter` | Enter/confirm |
| `Power` | Power button |
| `VolumeUp` | Volume up |
| `VolumeDown` | Volume down |
