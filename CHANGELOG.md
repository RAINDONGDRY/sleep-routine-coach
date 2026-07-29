# Changelog

All notable changes to this project are documented here.

## [0.2.1] - 2026-07-29

Shorter setup and flexible sleep duration:

- Reduced the normal onboarding path to timezone, rough sleep-time anchor, and storage consent.
- Combined exact scheduling details into one final confirmation instead of asking twice.
- Deferred wake reminders, weekend differences, hydration, intensity, and summaries until requested.
- Made wake time independent and optional in gradual plans; no fixed sleep-duration target is required.
- Added quick-profile defaults and reminder planning without a wake-time field.

## [0.2.0] - 2026-07-29

Gradual sleep-time adjustment:

- Added deterministic 15/30-minute sleep phase-shift plans with explicit stage confirmation.
- Preserved baseline sleep opportunity by shifting sleep and wake times together.
- Added hold, advance, step-back, pause, resume, cancel, export, and audit controls.
- Integrated stage-specific wind-down, sleep-time, wake, and morning reminder previews.
- Added authoritative circadian-rhythm evidence, medical boundaries, examples, and tests.

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
