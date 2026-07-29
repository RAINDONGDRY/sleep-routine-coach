# Contributing

Contributions are welcome from project contributors.

1. Open an issue for material changes to the consent model, medical boundary, data schema, or reminder behavior.
2. Keep `SKILL.md` concise and put detail in directly linked references.
3. Use only reliable first-party medical or public-health sources; record the URL and verification date.
4. Add deterministic tests for time, DST, deletion, consent, and scheduling changes.
5. Never add real user health data, channel identifiers, keys, or generated local data.

Run:

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/sleep-routine-coach
```

Keep language supportive and non-diagnostic. Pull requests that introduce universal fluid restriction, shame-based streaks, hidden persistence, or automatic scheduling will not be accepted.

