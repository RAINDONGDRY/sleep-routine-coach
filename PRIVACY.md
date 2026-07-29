# Privacy

## Summary

sleep-routine-coach uses consent-gated local JSON files. It does not require an account, API key, analytics service, or cloud database.

## Consent

- The Agent must obtain explicit consent before persisting the profile or any sleep event.
- Proactive scheduling requires a separate confirmation covering exact times, timezone, allowed hours, channel, and destination.
- Installing the Skill grants neither consent.
- Declining storage leaves the current conversation usable but creates no local data.

## Stored data

The profile contains routine preferences, storage/scheduling consent, and optional channel routing. Sleep records contain the fields documented in `references/data-schema.md`, provenance, and correction audit history. Reminder state contains enabled/disabled, snooze, skip, pending reply, and ignore-frequency information. If the user explicitly starts a gradual adjustment plan, `sleep-shift-plan.json` contains its baseline and target sleep-time anchors, optional wake references, stage schedule, current stage, review date, status, and audit history. It does not require a fixed sleep-duration target.

Default location is `~/.local/share/sleep-routine-coach`, with `SLEEP_ROUTINE_DATA_DIR` and `XDG_DATA_HOME` overrides. Best-effort permissions are `0700` for the directory and `0600` for files.

## User controls

Users can view, correct, export, delete one date, delete everything, or stop collection. Single-day deletion removes that day's record and audit history. Full deletion removes the profile, records, reminder state, and sleep-shift plan without a hidden tombstone. Stopping collection pauses an active plan and revokes scheduling consent.

Stopping collection revokes the Skill's scheduling consent, but external OpenClaw Cron jobs must be removed separately after confirmation because those jobs live outside this local data store.

## Boundaries

“Local” describes files created by this Skill. The user's configured model provider, OpenClaw Gateway, operating-system backups, messaging channels, or export destination may process or retain content under their own policies. Users should review those systems before putting sensitive notes in records.

The Skill must not extract health information from unrelated conversation or commit runtime data to Git.
