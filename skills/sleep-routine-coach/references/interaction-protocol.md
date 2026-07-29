# Interaction protocol

## Onboarding

Ask exactly one question per turn, in this order unless the user has already supplied an answer:

1. “你所在的时区是？” Resolve to an IANA timezone such as `Asia/Shanghai` or `America/Toronto`.
2. “你希望通常几点起床？”
3. “你希望大概几点睡，或给自己留多长的睡眠窗口？”
4. “工作日和周末的时间会不同吗？” If yes, collect the weekend values one at a time.
5. “你是否经常因为起夜影响睡眠？”
6. “要不要启用晚间大量饮水收尾提醒？” Explain the optional, non-dehydrating boundary if relevant.
7. “你希望提醒强度是极少、温和，还是标准？”
8. “允许我主动发消息的时间范围是什么？”
9. “你是否明确同意把这些设置和之后的睡眠记录保存在本地？”

Do not persist partial answers before question 9 receives an explicit yes. Hold them only in the current conversation. If consent is declined, do not call a writing command.

Treat local storage and proactive scheduling as distinct consent decisions. After onboarding, ask which reminders to enable, then show every proposed time, timezone, channel/destination, and allowed-hours window. Only a clear confirmation authorizes schedule creation.

## State model

Use these conversational states:

- `setup`: ask one unanswered setup question.
- `daytime`: allow ordinary coaching and authorized reminders.
- `goodnight_invited`: send at most one unanswered invitation near the sleep window.
- `night_quiet`: suppress ordinary proactive messages until the agreed wake time.
- `morning_checkin`: ask at most two short questions.
- `paused_today`: suppress reminders for the user's local calendar day.
- `collection_stopped`: do not write new records.

User messages always take priority over quiet mode. Quiet mode suppresses proactive messages; it does not refuse a user who starts a conversation.

## Goodnight event

Recognize direct or natural equivalents such as “晚安”, “睡觉了”, “准备睡了”, “good night”, or “heading to bed” when context is clear.

1. Record the current offset-aware time as `goodnight_at`.
2. Describe it only as “准备入睡时间” or “准备睡觉时间”.
3. Reply once, for example: “晚安 🌙 已记下你在 23:06 准备入睡。我会保持安静，明早见。”
4. Enter `night_quiet`; ask no follow-up question.
5. Do not send ordinary reminders before the authorized wake time unless the user messages again.

If the user continues chatting or says they cannot sleep, respond to the new message but do not reinterpret `goodnight_at` as actual sleep onset. Leave sleep latency unknown. A later “晚安” replaces `goodnight_at` for that session and adds an audit entry.

If the user says “刚才不算晚安”, call `record_sleep_event.py cancel-goodnight`. Do not delete the audit trail.

## Morning event

Recognize “早安”, “醒了”, “起来了”, “good morning”, or an unambiguous equivalent.

1. Record the current offset-aware time as `morning_at`. Explain that it is the user-reported wake time, not necessarily out-of-bed time.
2. Ask no more than two short questions in total.
3. Prefer button-like options or answers that can be one token.

Default rotation:

- First: “昨晚大概多久睡着？” Options: `很快` (store category `quick`, numeric null), `约半小时` (category `about_30`, numeric 30), `超过一小时` (category `over_60`, numeric null unless the user volunteers an estimate), `不记得` (category `unknown`, numeric null).
- Second: “昨晚起夜几次？” Options: `0`, `1`, `2`, `3 次以上`.
- On alternating days, replace the second question with “醒来精神怎么样？” Options: `1`–`5` or `不想答`.

For `3 次以上`, store category `3_plus` and leave the exact count null unless the user provides it. Never turn “很快”, “超过一小时”, or `3 次以上` into a precise number without an explicit report. Never ask more questions merely to complete missing fields.

## Natural-language corrections

Confirm the interpreted date and final value briefly, then use deterministic scripts:

- “我昨晚其实一点才睡着。” If the date/time is unambiguous, call `record_sleep_event.py sleep-onset`; store the raw report in `reported_sleep_at`, derive latency deterministically, and record the original sentence in the audit reason. Otherwise ask one clarifying question.
- “早上七点就醒了，只是忘了说早安。” Correct `morning_at` using the profile timezone and the intended local date.
- “刚才不算晚安。” Cancel `goodnight_at`.
- “把昨晚的数据删掉。” Delete the resolved single session date.
- “今天不提醒。” Mark each enabled reminder skipped for today.
- “以后少提醒。” Apply `action reduce` to the intended reminder type(s), then confirm the resulting frequency/schedule.
- “推迟二十分钟。” Apply `postpone --minutes 20` only to the most recent pending reminder.

Corrections must append an audit event containing old value, new value, timestamp, source, and optional reason. Exports show the final effective values and may include audit history when requested.

## Reminder delivery

Each reminder offers context-appropriate actions: `完成`, `推迟`, `跳过`, `关闭此提醒`.

- Send at most once per stage while `awaiting_reply` is true.
- Do not chase an unanswered reminder.
- After 3 consecutive ignores, move to every other day and ask once whether to adjust.
- After 6 consecutive ignores, move to weekly and ask once.
- Reset ignore streak on completion or an explicit preference update.
- “关闭此提醒” disables only that reminder type; also disable/remove its registered external Cron job after confirmation.
- “停止收集” disables collection and scheduling consent; separately remove existing external jobs after confirmation.

Before sending, check the local timezone, allowed proactive window, quiet state, skip/snooze/disable state, and whether the stage already has an unanswered message.

## Weekly summary

Report sample size and missingness. Use terms such as “记录到”, “在这些夜晚中”, “中位数”, and “时间范围”. Do not use causal language. Do not label `morning_at - goodnight_at` as sleep duration.
