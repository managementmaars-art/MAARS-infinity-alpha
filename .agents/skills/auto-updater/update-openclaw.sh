#!/bin/bash
# OpenClaw Auto-Updater Script
# Run this via cron or launchd to update OpenClaw independently
# Usage: ./update-openclaw.sh

set -e

LOG_FILE="$HOME/openclaw-update.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting OpenClaw update..."

# Stop the gateway
log "Stopping gateway..."
openclaw gateway stop

# Run the update
log "Running update..."
openclaw update.run

# Restart the gateway  
log "Restarting gateway..."
openclaw gateway start

log "Update complete!"
