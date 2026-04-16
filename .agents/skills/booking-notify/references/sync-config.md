# Sync Configuration

Configuration for the scheduled booking sync process.

## Sync Interval

Default: Every 6 hours (21600 seconds) via launchd `StartInterval`.

## State Management

The sync process maintains a state file to track previously seen bookings:

- **Location**: `~/own/amonic/state/calcom-sync-state.json`
- **Format**: JSON object with `lastSyncAt` timestamp and `knownBookingIds` array
- **Rotation**: State file is overwritten each cycle

```json
{
  "lastSyncAt": "2026-02-14T12:00:00Z",
  "knownBookingIds": [12345, 12346, 12347],
  "lastBookingCount": 3
}
```

## Change Detection

1. Fetch all bookings since `lastSyncAt`
2. Compare against `knownBookingIds`
3. New IDs = NEW BOOKING notification
4. Missing IDs = check status (CANCELLED or RESCHEDULED)
5. Update state file

## Circuit Breaker

- **File**: `/tmp/calcom-sync-circuit.json`
- **Threshold**: 3 consecutive failures
- **Cooldown**: 10 minutes
- **Auto-reset**: On successful sync

## Audit Logging

All sync events logged to NDJSON:

- `sync.started` — Sync cycle begins
- `sync.bookings_found` — Number of bookings fetched
- `sync.new_booking` — New booking detected
- `sync.cancellation` — Cancellation detected
- `sync.completed` — Sync cycle ends
- `sync.error` — Error during sync

Retention: 14 days with auto-pruning.
