# OpenClaw Auto-Updater

A skill for OpenClaw that automatically updates your agent every night.

## What It Does

This skill sets up a nightly cron job that runs an external shell script — the script runs independently of the agent, so it works even when the gateway restarts.

## Why a Script?

When OpenClaw updates, the gateway restarts — which kills any running agent commands. By using a standalone shell script (not agent commands), the update runs successfully without needing the agent to be active.

## Installation

Copy the `auto-updater` folder to your skills directory:

```bash
cp -r auto-updater ~/.openclaw/skills/
```

Restart your OpenClaw gateway:

```bash
openclaw gateway restart
```

## Setup

Once installed, say **"Set up auto-updater"** and I'll:
1. Copy the update script to `~/update-openclaw.sh`
2. Create a cron job that runs at 4 AM daily

## The Script

Location: `~/update-openclaw.sh`

```bash
#!/bin/bash
set -e

LOG_FILE="$HOME/openclaw-update.log"

log() {
    echo "[$(date)] $1" | tee -a "$LOG_FILE"
}

log "Starting OpenClaw update..."
openclaw gateway stop
openclaw update.run
openclaw gateway start
log "Update complete!"
```

## Usage

- **"Set up auto-updater"** - Creates the cron job
- **"Update yourself now"** - Runs the script immediately
- **"Change update time to [time]"** - Updates the schedule

## Change Update Time

The cron runs at 4 AM by default. To change:

```bash
crontab -e
# Change: 0 4 * * * ~/update-openclaw.sh
```

## Manual Run

```bash
~/update-openclaw.sh
```

Check logs: `~/openclaw-update.log`

## Troubleshooting

### Update Failed

Check the log:
```bash
cat ~/openclaw-update.log
```

Run manually to see errors:
```bash
~/update-openclaw.sh
```

### Cron Not Running

```bash
crontab -l  # List cron jobs
```

## Requirements

- OpenClaw v2026.02+ 
- Gateway running in local mode
- Internet connection for updates
