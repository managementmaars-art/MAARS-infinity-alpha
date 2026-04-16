# Android Serialization Offline Sync Patterns

## Selection Notes
- Category: `data-platform`
- Best fit when the request matches the trigger language in `SKILL.md` and the implementation focus is `Coordinate serialization, caching, conflict handling, and offline-first sync flows in Android apps.`
- Reach for neighboring skills only after this skill has framed the main problem.

## Default Review Sequence
1. Confirm the data source, persistence boundary, sync model, and device capability involved.
2. Model contracts explicitly before wiring network, storage, media, or background APIs.
3. Apply the recommended AndroidX or platform pattern with migration-safe defaults.
4. Validate offline, retry, and process death behavior against the sample apps and scenarios.
5. Escalate security, performance, or release risk to the linked supporting skills when needed.

## Handoff Shortlist
- `android-networking-retrofit-okhttp`
- `android-room-database`
