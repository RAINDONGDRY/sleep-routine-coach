# sleep-routine-coach

**English** | [简体中文](README.zh-CN.md)

> A privacy-first sleep habit agent that helps you move toward a better schedule in small steps, reminds you when it is time to wind down, and uses simple goodnight and morning check-ins to track your routine.

Have you ever told yourself, more than once, that tomorrow would be the day you finally started sleeping and waking earlier?

You picture an unhurried morning: breakfast without rushing, a few pages of a book, a walk or a workout, and enough quiet time to decide what matters before the rest of the day starts asking for your attention.

So you move the alarm earlier and make a plan. It may even work for a few days. Then there is a late work night, a social event, twenty extra minutes on your phone, or one long weekend morning—and the routine quietly slips back to where it started. The next attempt comes with a stricter target, more alarms, and more pressure.

That does not necessarily mean you lack discipline. Many routine tools focus on waking you up in the morning while ignoring how the night ended. They are good at alarms and streaks, but not always good at knowing when to stop talking.

`sleep-routine-coach` focuses on one practical job: at an appropriate time each day, it reminds you to finish what you are doing, slow the pace, and leave some room between the day and sleep—instead of waiting until the next morning to discover that bedtime drifted again.

Goodnight and morning messages serve a different purpose. They are low-friction ways to record when you started preparing for sleep, when you reported waking up, and a small amount of optional context. Over time, those records can reveal descriptive patterns in your routine. They do not replace the daily wind-down reminder.

**Proactive, but restrained.** A wind-down stage sends at most one unanswered reminder. It does not chase you, and it stays quiet after you say goodnight. Data remains local by default, while reminder times, allowed hours, and delivery channels stay under your control. This is not a medical diagnostic tool and does not claim to treat or cure insomnia.

```text
Agent: You still have a little time before your planned bedtime.
       This could be a good moment to wrap up and slow things down.
       [Done] [Snooze] [Skip] [Turn off this reminder]

Agent: When you are ready for bed, just say goodnight.
       I will record the time and then stay quiet.
User: Goodnight
Agent: Goodnight 🌙 I recorded 23:06. I will stay quiet until morning.

User: Good morning
Agent: Good morning ☀️ I recorded 07:32. About how long did it take to fall asleep?
```

The Skill follows the general [Agent Skills `SKILL.md` specification](https://agentskills.io/specification) and can use OpenClaw Cron for explicitly authorized proactive reminders.

## Try it

Install from the repository into the current OpenClaw workspace:

```bash
openclaw skills install ./skills/sleep-routine-coach --as sleep-routine-coach
```

Then start a conversation:

```text
Use $sleep-routine-coach to help me build a gentle, privacy-first sleep routine.
```

Installation does not create scheduled jobs or begin saving data. Setup asks one question at a time and requests explicit local-storage consent before anything is persisted.

Install from ClawHub:

```bash
openclaw skills install @raindongdry/sleep-routine-coach
```

The installation command and Cron arguments were checked against the [official OpenClaw Skills documentation](https://docs.openclaw.ai/tools/skills) and local OpenClaw `2026.7.1-2` CLI help on 2026-07-29. See the [Chinese installation guide](docs/INSTALLATION.zh-CN.md) for the full setup.

## How it supports you

- **Moves late schedules gradually.** If your usual schedule is 03:00–12:00, the agent can build a reviewable series of 15-minute stages instead of demanding an overnight jump to 23:00.
- **A daily cue to start preparing.** The approved reminder time is based on your sleep window, with separate weekday and weekend schedules when needed.
- **No bedtime notification flood.** Each stage sends at most one unanswered reminder. Repeatedly ignored reminders automatically become less frequent.
- **Goodnight is a record, not a demand.** It captures when you started preparing for sleep, not when the agent imagines you actually fell asleep. Recording it immediately starts quiet mode.
- **Good morning is the data entry point for the day.** It records your reported wake time and asks no more than two short questions for later trend analysis.
- **Real life can be corrected.** Statements such as “I actually fell asleep at 1,” “that goodnight did not count,” or “I woke at 7 but forgot to say good morning” can update the record naturally.
- **Reminders respond to your choices.** Mark one done, snooze it, skip it, or turn it off. Continued silence reduces the frequency.
- **Your data stays under your control.** View, correct, export, delete one day, delete everything, or stop collection locally.
- **No invented precision.** Scripts handle midnight crossings, timezones, and daylight-saving changes. If actual sleep onset is unknown, it remains unknown.

## Move your sleep time without an overnight reset

Suppose you usually sleep around 03:00 and wake around 12:00, but want to work toward 23:00. By default, the Skill proposes 15-minute stages and holds each stage for two nights:

| Stage | Wind down | Planned sleep time | Planned wake time |
| --- | ---: | ---: | ---: |
| 1 | 01:45 | 02:45 | 11:45 |
| 2 | 01:30 | 02:30 | 11:30 |
| … | … | … | … |
| 16 | 22:00 | 23:00 | 08:00 |

The wake time moves with the sleep time, preserving the original nine-hour sleep opportunity. The agent reminds you at the current stage’s wind-down and sleep times, then asks at the review date whether you want to continue, hold, move back, pause, or cancel. It never advances simply because a calendar date passed, and a missing goodnight or morning report is not treated as success.

The 15–30 minute step range is based on public sleep-habit guidance documented in the [evidence notes](skills/sleep-routine-coach/references/evidence-sources.md). Holding a stage for two nights is this project’s conservative default, not a medical prescription. The feature is habit support: it does not diagnose a circadian disorder, prescribe melatonin or personalized light therapy, or shorten your sleep opportunity without a separate explicit decision.

Try it with:

```text
Use $sleep-routine-coach. I usually sleep from 03:00 to 12:00 and want to move toward 23:00. Show me a gradual plan first.
```

## Why this is not another streak tracker

Sleep routines are not perfect straight lines. Travel, work, caregiving, mood, and physical circumstances all change what is realistic on a given night. This project does not count broken streaks, show red failure banners, or interpret an occasional late night as a character flaw.

It asks more useful questions: Did the wind-down reminder help you start wrapping up earlier? Is your schedule gradually becoming more stable? Which reminder times are useful, and which reminders should be reduced or removed? Goodnight and morning records help answer those questions. Weekly summaries describe only the available observations; they do not grade you or turn correlation into causation.

## Design boundaries

`goodnight_at` means “started preparing for sleep,” not actual sleep onset. `morning_at` is the time the user reported being awake, not necessarily the time they got out of bed. Their difference is only a reported time window and is never presented as sleep duration. Missing values remain null, and weekly summaries report descriptive patterns without causal claims.

Exact-time reminders use OpenClaw Cron or an equivalent scheduler. Heartbeat is reserved for periodic, adaptive checks within authorized active hours. `SKILL.md` cannot run in the background by itself. The scheduling script emits structured `executable` and `argv` previews; it never runs OpenClaw or emits a command string for shell evaluation.

## Privacy model

The default data-directory order is:

1. `SLEEP_ROUTINE_DATA_DIR`
2. `$XDG_DATA_HOME/sleep-routine-coach`
3. `~/.local/share/sleep-routine-coach`

Local files are `profile.json`, `sleep-records.json`, `reminders.json`, and—only after a gradual plan is explicitly confirmed—`sleep-shift-plan.json`. The scripts use directory mode `0700` and file mode `0600` where supported. Every record requires explicit consent, and `.gitignore` excludes runtime files and exports from the repository.

“Local storage” describes only the files managed by this Skill. Your configured model provider and messaging channels may still process conversation or reminder content according to their own policies. See the [privacy notice](PRIVACY.md).

## Data fields

Core fields include:

`date`, `timezone`, `goodnight_at`, `sleep_latency_minutes`, `reported_sleep_at`, `estimated_sleep_at`, `morning_at`, `out_of_bed_at`, `night_awakenings`, `nocturia_count`, `rested_score`, `notes`, `source`, `created_at`, and `updated_at`.

Additional fields include `night_awake_minutes`, `reported_window_minutes`, `estimated_sleep_duration_minutes`, `provenance`, and `audit_history` for bounded estimates, source distinctions, and correction history. See the full [data schema](skills/sleep-routine-coach/references/data-schema.md).

## Data controls

These commands operate only on the local data directory you specify:

```bash
python3 skills/sleep-routine-coach/scripts/manage_profile.py --data-dir /private/path show
python3 skills/sleep-routine-coach/scripts/manage_sleep_shift.py --data-dir /private/path show
python3 skills/sleep-routine-coach/scripts/manage_profile.py --data-dir /private/path export --output sleep.export.json
python3 skills/sleep-routine-coach/scripts/record_sleep_event.py --data-dir /private/path delete --date 2026-07-29
python3 skills/sleep-routine-coach/scripts/manage_profile.py --data-dir /private/path delete-all --confirm
```

Stopping collection revokes scheduling consent. Existing external Cron jobs still require a separately confirmed disable or delete operation so that local scripts never make hidden external changes.

## Health and hydration boundaries

The project does not impose one universal “last glass of water” time and does not encourage dehydration. The optional evening hydration reminder is offered only to users who report disruptive nighttime urination and explicitly enable it. Small sips remain appropriate when thirsty.

The Skill does not provide individualized hydration advice for pregnancy, intense exercise, hot environments, kidney or cardiovascular disease, diabetes, or diuretic use. Persistent nighttime urination—especially with loud snoring, breathing pauses or gasping, unusual thirst, or pain—prompts a recommendation to seek professional evaluation. Health language is based only on the documented [NIH/NHLBI, NIDDK, AASM, and NHS sources](skills/sleep-routine-coach/references/evidence-sources.md).

## Development and validation

The project uses only the Python standard library (Python 3.10+ with `zoneinfo` timezone data):

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/sleep-routine-coach
```

Tests cover normal goodnight/morning flows, midnight crossings, DST, duplicate events, later corrections, declined storage, gradual stage calculations and controls, shift-aware reminders, quiet mode, adaptive reminder frequency, missing values, export and deletion, safety boundaries, and the requirement that unauthorized Cron jobs are never created.

## Project structure

```text
skills/sleep-routine-coach/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
└── references/
tests/
docs/
```

See the [Chinese conversation examples](docs/EXAMPLES.zh-CN.md). Contributions are welcome; read the [contributing guide](CONTRIBUTING.md) and [security policy](SECURITY.md).

## License

Repository code and documentation use the [MIT License](LICENSE), with copyright held by project contributors. ClawHub currently distributes its hosted Skill bundle under MIT-0 terms; publishers should confirm acceptance before publishing there.
