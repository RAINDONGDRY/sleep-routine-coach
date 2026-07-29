# Changelog

All notable changes to this project are documented here.

## [0.1.3] - 2026-07-29

Product-positioning clarification:

- Made the authorized daily wind-down reminder the primary coaching loop.
- Clarified that goodnight and morning messages are low-friction data collection events.
- Updated the reminder copy, README demo, interaction protocol, and UI metadata.

## [0.1.2] - 2026-07-29

ClawHub review hardening:

- Declared Python and optional data-directory requirements using official `metadata.openclaw` fields.
- Added portable tool-access metadata without preauthorizing scheduler changes.
- Added language selection, localized consent, and fail-closed comprehension rules.
- Added bilingual examples while preserving the same stored categories and behavior.

## [0.1.1] - 2026-07-29

Security hardening:

- Replaced shell command previews with typed `executable` and `argv` scheduler requests.
- Added scheduler identifier and delivery-target validation.
- Declared data, process, and optional scheduler access in Skill metadata.
- Added regression coverage proving delivery targets remain a single inert argument.

## [0.1.0] - 2026-07-29

Initial public release:

- Privacy-first goodnight and morning sleep-habit workflow.
- Consent-gated local storage, corrections, export, and deletion.
- DST-safe deterministic sleep calculations and descriptive summaries.
- Consent-gated OpenClaw Cron previews with quiet hours and reminder controls.
- Non-diagnostic hydration, nocturia, and sleep-safety boundaries.
- Chinese documentation, examples, tests, and GitHub Actions.
