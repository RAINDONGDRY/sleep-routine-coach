from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "sleep-routine-coach"
SCRIPTS = SKILL / "scripts"


class CliCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name) / "data"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, script: str, *args: str, ok: bool = True):
        command = [sys.executable, str(SCRIPTS / script), "--data-dir", str(self.data), *args]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if ok and result.returncode != 0:
            self.fail(f"{command}\nstdout={result.stdout}\nstderr={result.stderr}")
        if not ok:
            self.assertNotEqual(result.returncode, 0)
            return result
        return json.loads(result.stdout)

    def init_profile(
        self,
        *,
        timezone: str = "America/Toronto",
        hydration: bool = False,
        consent: bool = True,
    ):
        args = [
            "init",
            "--timezone",
            timezone,
            "--target-wake-time",
            "07:30",
            "--sleep-window-start",
            "23:00",
            "--sleep-window-end",
            "07:30",
            "--reminder-intensity",
            "gentle",
            "--proactive-start",
            "19:00",
            "--proactive-end",
            "09:00",
        ]
        if consent:
            args.append("--consent")
        if hydration:
            args.extend(["--often-nocturia", "--hydration-reminder-enabled"])
        return self.run_cli("manage_profile.py", *args)

    def authorize_schedule(self):
        args = [
            "manage_profile.py",
            "authorize-schedule",
            "--confirm",
            "--channel",
            "telegram",
            "--target",
            "123456",
        ]
        profile = self.run_cli("manage_profile.py", "show")
        reminders = [
            "wind_down",
            "goodnight_invite",
            "sleep_time",
            "wake_target",
            "morning_checkin",
            "weekly_summary",
        ]
        if profile.get("hydration_reminder_enabled"):
            reminders.append("hydration_wrap")
        for reminder in reminders:
            args.extend(["--reminder", reminder])
        return self.run_cli(*args)

    def test_storage_refusal_writes_nothing(self):
        result = self.init_profile(consent=False)
        self.assertFalse(result["persisted"])
        self.assertFalse(self.data.exists())
        ephemeral = self.run_cli(
            "record_sleep_event.py",
            "--timezone",
            "America/Toronto",
            "goodnight",
            "--at",
            "2026-07-29T23:06:00-04:00",
        )
        self.assertFalse(ephemeral["persisted"])
        self.assertFalse(self.data.exists())
        refused_plan = self.run_cli(
            "manage_sleep_shift.py",
            "start",
            "--confirm",
            "--timezone",
            "America/Toronto",
            "--current-sleep-time",
            "03:00",
            "--current-wake-time",
            "12:00",
            "--target-sleep-time",
            "23:00",
            "--start-date",
            "2026-07-29",
            ok=False,
        )
        self.assertIn("explicit consent", refused_plan.stderr)
        self.assertFalse(self.data.exists())

    @unittest.skipIf(os.name == "nt", "POSIX permission modes are not portable to Windows")
    def test_local_files_use_private_permissions(self):
        self.init_profile()
        self.assertEqual(self.data.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.data / "profile.json").stat().st_mode & 0o777, 0o600)

    def test_normal_goodnight_morning_and_duplicate_events(self):
        self.init_profile()
        first = self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:06:00-04:00",
        )
        self.assertEqual(first["record"]["goodnight_at"], "2026-07-29T23:06:00-04:00")
        self.assertIsNone(first["record"]["estimated_sleep_at"])

        duplicate = self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:20:00-04:00",
        )
        self.assertEqual(duplicate["record"]["goodnight_at"], "2026-07-29T23:20:00-04:00")
        morning = self.run_cli(
            "record_sleep_event.py",
            "morning",
            "--at",
            "2026-07-30T07:32:00-04:00",
        )
        self.assertEqual(morning["record"]["date"], "2026-07-29")
        self.assertIsNone(morning["record"]["estimated_sleep_duration_minutes"])

        replaced = self.run_cli(
            "record_sleep_event.py",
            "morning",
            "--date",
            "2026-07-29",
            "--at",
            "2026-07-30T07:40:00-04:00",
        )
        self.assertEqual(replaced["record"]["morning_at"], "2026-07-30T07:40:00-04:00")
        audited = self.run_cli(
            "record_sleep_event.py", "show", "--date", "2026-07-29", "--include-audit"
        )
        actions = [entry["action"] for entry in audited["audit_history"]]
        self.assertIn("goodnight_replaced", actions)
        self.assertIn("morning_replaced", actions)

    def test_cross_midnight_metrics_and_missing_duration(self):
        self.init_profile()
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:00:00-04:00",
        )
        self.run_cli(
            "record_sleep_event.py",
            "morning",
            "--at",
            "2026-07-30T07:30:00-04:00",
        )
        missing = self.run_cli("calculate_sleep_metrics.py", "--date", "2026-07-29")
        self.assertEqual(missing["reported_window_minutes"], 510)
        self.assertIsNone(missing["estimated_sleep_duration_minutes"])

        self.run_cli(
            "record_sleep_event.py",
            "correct",
            "--date",
            "2026-07-29",
            "--field",
            "sleep_latency_minutes",
            "--value",
            "30",
        )
        self.run_cli(
            "record_sleep_event.py",
            "correct",
            "--date",
            "2026-07-29",
            "--field",
            "night_awakenings",
            "--value",
            "0",
        )
        complete = self.run_cli("calculate_sleep_metrics.py", "--date", "2026-07-29")
        self.assertEqual(complete["estimated_sleep_at"], "2026-07-29T23:30:00-04:00")
        self.assertEqual(complete["estimated_sleep_duration_minutes"], 480)

    def test_non_exact_button_answers_remain_categories(self):
        self.init_profile()
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:00:00-04:00",
        )
        self.run_cli(
            "record_sleep_event.py",
            "morning",
            "--at",
            "2026-07-30T07:30:00-04:00",
        )
        self.run_cli(
            "record_sleep_event.py",
            "correct",
            "--date",
            "2026-07-29",
            "--field",
            "sleep_latency_category",
            "--value",
            "quick",
        )
        record = self.run_cli(
            "record_sleep_event.py",
            "correct",
            "--date",
            "2026-07-29",
            "--field",
            "nocturia_category",
            "--value",
            "3_plus",
        )["record"]
        self.assertEqual(record["sleep_latency_category"], "quick")
        self.assertEqual(record["nocturia_category"], "3_plus")
        self.assertIsNone(record["sleep_latency_minutes"])
        self.assertIsNone(record["nocturia_count"])
        self.assertIsNone(record["estimated_sleep_duration_minutes"])

    def test_dst_spring_forward_and_fall_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            spring = Path(tmp) / "spring.json"
            spring.write_text(
                json.dumps(
                    {
                        "date": "2026-03-08",
                        "timezone": "America/Toronto",
                        "goodnight_at": "2026-03-08T01:30:00-05:00",
                        "sleep_latency_minutes": 60,
                        "morning_at": "2026-03-08T08:00:00-04:00",
                        "night_awakenings": 0,
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "calculate_sleep_metrics.py"), "--input", str(spring)],
                capture_output=True,
                text=True,
                check=True,
            )
            record = json.loads(result.stdout)
            self.assertEqual(record["estimated_sleep_at"], "2026-03-08T03:30:00-04:00")
            self.assertEqual(record["estimated_sleep_duration_minutes"], 270)

            fall = Path(tmp) / "fall.json"
            fall.write_text(
                json.dumps(
                    {
                        "date": "2026-11-01",
                        "timezone": "America/Toronto",
                        "goodnight_at": "2026-11-01T01:30:00-04:00",
                        "sleep_latency_minutes": 120,
                        "morning_at": "2026-11-01T08:00:00-05:00",
                        "night_awakenings": 0,
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "calculate_sleep_metrics.py"), "--input", str(fall)],
                capture_output=True,
                text=True,
                check=True,
            )
            record = json.loads(result.stdout)
            self.assertEqual(record["estimated_sleep_at"], "2026-11-01T02:30:00-05:00")
            self.assertEqual(record["estimated_sleep_duration_minutes"], 330)

    def test_timezone_normalization_and_next_day_correction(self):
        self.init_profile(timezone="Asia/Shanghai")
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T15:06:00Z",
        )
        record = self.run_cli(
            "record_sleep_event.py",
            "correct",
            "--date",
            "2026-07-29",
            "--field",
            "morning_at",
            "--value",
            "2026-07-30T07:00:00+08:00",
            "--reason",
            "Forgot to say good morning",
            "--include-audit",
        )["record"]
        self.assertEqual(record["goodnight_at"], "2026-07-29T23:06:00+08:00")
        self.assertEqual(record["morning_at"], "2026-07-30T07:00:00+08:00")
        self.assertEqual(record["provenance"]["morning_at"]["kind"], "reported")
        correction = next(
            entry for entry in record["audit_history"] if entry["reason"] == "Forgot to say good morning"
        )
        self.assertEqual(correction["source"], "user_correction")

    def test_direct_sleep_onset_report_preserves_raw_and_derives_latency(self):
        self.init_profile()
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:06:00-04:00",
        )
        record = self.run_cli(
            "record_sleep_event.py",
            "sleep-onset",
            "--date",
            "2026-07-29",
            "--at",
            "2026-07-30T01:00:00-04:00",
            "--reason",
            "User said they actually fell asleep at one",
            "--include-audit",
        )["record"]
        self.assertEqual(record["reported_sleep_at"], "2026-07-30T01:00:00-04:00")
        self.assertEqual(record["sleep_latency_minutes"], 114)
        self.assertEqual(record["estimated_sleep_at"], "2026-07-30T01:00:00-04:00")
        self.assertEqual(record["provenance"]["reported_sleep_at"]["kind"], "reported")
        self.assertEqual(record["provenance"]["sleep_latency_minutes"]["kind"], "derived")
        self.assertEqual(record["provenance"]["estimated_sleep_at"]["kind"], "estimated")

    def test_cancel_goodnight_preserves_audit(self):
        self.init_profile()
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:06:00-04:00",
        )
        cancelled = self.run_cli(
            "record_sleep_event.py",
            "cancel-goodnight",
            "--date",
            "2026-07-29",
            "--include-audit",
        )["record"]
        self.assertIsNone(cancelled["goodnight_at"])
        self.assertTrue(any(entry["action"] == "corrected" for entry in cancelled["audit_history"]))

    def test_delete_single_export_and_delete_all(self):
        self.init_profile()
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:06:00-04:00",
        )
        self.run_cli(
            "record_sleep_event.py",
            "correct",
            "--date",
            "2026-07-29",
            "--field",
            "goodnight_at",
            "--value",
            "2026-07-29T23:10:00-04:00",
            "--reason",
            "User corrected the time",
        )
        export_path = Path(self.temp.name) / "export.json"
        exported = self.run_cli("manage_profile.py", "export", "--output", str(export_path))
        self.assertTrue(exported["exported"])
        payload = json.loads(export_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["records"][0]["date"], "2026-07-29")
        self.assertEqual(payload["records"][0]["goodnight_at"], "2026-07-29T23:10:00-04:00")
        self.assertTrue(any(entry["reason"] == "User corrected the time" for entry in payload["records"][0]["audit_history"]))

        deleted = self.run_cli("record_sleep_event.py", "delete", "--date", "2026-07-29")
        self.assertTrue(deleted["deleted"])
        self.assertEqual(self.run_cli("record_sleep_event.py", "show"), [])
        all_deleted = self.run_cli("manage_profile.py", "delete-all", "--confirm")
        self.assertTrue(all_deleted["deleted"])
        self.assertFalse(self.data.exists())

    def test_schedule_requires_consent_and_never_creates_jobs(self):
        self.init_profile(hydration=True)
        plan = self.run_cli("build_reminder_schedule.py", "plan")
        self.assertFalse(plan["authorized"])
        self.assertEqual(plan["scheduler_requests"], [])
        self.assertEqual(plan["created_jobs"], [])

        self.authorize_schedule()
        authorized = self.run_cli("build_reminder_schedule.py", "plan", "--agent", "main")
        self.assertTrue(authorized["authorized"])
        self.assertEqual(authorized["created_jobs"], [])
        self.assertTrue(any(item["kind"] == "hydration_wrap" for item in authorized["items"]))
        wind_down = next(item for item in authorized["items"] if item["kind"] == "wind_down")
        self.assertEqual(wind_down["local_time"], "22:00")
        self.assertIn("开始收尾", wind_down["message"])
        self.assertTrue(
            all(request["operation"] == "openclaw.cron.create" for request in authorized["scheduler_requests"])
        )
        self.assertTrue(
            all(request["executable"] == "openclaw" for request in authorized["scheduler_requests"])
        )
        self.assertTrue(
            all(request["argv"][:2] == ["cron", "create"] for request in authorized["scheduler_requests"])
        )
        self.assertTrue(
            all(
                request["argv"][request["argv"].index("--tz") + 1] == "America/Toronto"
                for request in authorized["scheduler_requests"]
            )
        )
        self.assertTrue(all(request["validated"] for request in authorized["scheduler_requests"]))
        script_text = (SCRIPTS / "build_reminder_schedule.py").read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", script_text)
        self.assertNotIn("os.system", script_text)
        self.assertNotIn("shlex", script_text)
        registered = self.run_cli(
            "build_reminder_schedule.py",
            "register-job",
            "--schedule-id",
            "wind_down_daily",
            "--job-id",
            "job-123",
        )
        self.assertTrue(registered["registered"])
        jobs = self.run_cli("build_reminder_schedule.py", "list-jobs")
        self.assertEqual(jobs["wind_down_daily"]["job_id"], "job-123")
        removed = self.run_cli(
            "build_reminder_schedule.py", "unregister-job", "--schedule-id", "wind_down_daily"
        )
        self.assertTrue(removed["unregistered"])

    def test_scheduler_preview_keeps_target_as_one_argv_value(self):
        self.init_profile()
        target = "user; echo should-not-run"
        self.run_cli(
            "manage_profile.py",
            "authorize-schedule",
            "--confirm",
            "--channel",
            "telegram",
            "--target",
            target,
            "--reminder",
            "wind_down",
        )
        plan = self.run_cli("build_reminder_schedule.py", "plan")
        self.assertNotIn("commands", plan)
        request = plan["scheduler_requests"][0]
        target_index = request["argv"].index("--to") + 1
        self.assertEqual(request["argv"][target_index], target)
        self.assertEqual(
            request["execution_policy"],
            "Pass executable and argv separately; shell must be disabled.",
        )

    def test_gradual_sleep_shift_preview_preserves_sleep_opportunity(self):
        preview = self.run_cli(
            "manage_sleep_shift.py",
            "preview",
            "--timezone",
            "America/Toronto",
            "--current-sleep-time",
            "03:00",
            "--current-wake-time",
            "12:00",
            "--target-sleep-time",
            "23:00",
            "--start-date",
            "2026-07-29",
        )
        self.assertFalse(preview["persisted"])
        self.assertEqual(preview["direction"], "earlier")
        self.assertEqual(preview["sleep_opportunity_minutes"], 540)
        self.assertEqual(preview["target_wake_time"], "08:00")
        self.assertEqual(preview["estimated_minimum_days"], 32)
        self.assertEqual(len(preview["stages"]), 16)
        self.assertEqual(preview["stages"][0]["sleep_time"], "02:45")
        self.assertEqual(preview["stages"][0]["wake_time"], "11:45")
        self.assertEqual(preview["stages"][-1]["sleep_time"], "23:00")
        self.assertEqual(preview["stages"][-1]["wake_time"], "08:00")
        self.assertFalse(self.data.exists())

    def test_sleep_shift_rejects_hidden_sleep_opportunity_change(self):
        result = self.run_cli(
            "manage_sleep_shift.py",
            "preview",
            "--timezone",
            "America/Toronto",
            "--current-sleep-time",
            "03:00",
            "--current-wake-time",
            "12:00",
            "--target-sleep-time",
            "23:00",
            "--target-wake-time",
            "07:00",
            "--start-date",
            "2026-07-29",
            ok=False,
        )
        self.assertIn("preserves the current sleep opportunity", result.stderr)

    def test_sleep_shift_requires_consent_and_manual_stage_advance(self):
        self.init_profile()
        started = self.run_cli(
            "manage_sleep_shift.py",
            "start",
            "--confirm",
            "--current-sleep-time",
            "03:00",
            "--current-wake-time",
            "12:00",
            "--target-sleep-time",
            "23:00",
            "--start-date",
            "2026-07-29",
        )
        self.assertTrue(started["started"])
        self.assertEqual(started["current"]["current_stage"]["sleep_time"], "02:45")
        self.assertFalse(started["current"]["review_due"])
        self.authorize_schedule()
        reminder_plan = self.run_cli("build_reminder_schedule.py", "plan")
        self.assertEqual(
            next(item for item in reminder_plan["items"] if item["kind"] == "wind_down")["local_time"],
            "01:45",
        )
        self.assertEqual(
            next(item for item in reminder_plan["items"] if item["kind"] == "sleep_time")["local_time"],
            "02:45",
        )
        self.assertFalse(any(item["kind"] == "goodnight_invite" for item in reminder_plan["items"]))
        self.assertEqual(
            reminder_plan["sleep_shift"]["current_stage"]["sleep_time"],
            "02:45",
        )
        early = self.run_cli(
            "manage_sleep_shift.py",
            "advance",
            "--as-of",
            "2026-07-30",
            "--confirm",
            ok=False,
        )
        self.assertIn("Hold this stage", early.stderr)
        advanced = self.run_cli(
            "manage_sleep_shift.py",
            "advance",
            "--as-of",
            "2026-07-31",
            "--confirm",
        )
        self.assertEqual(advanced["current"]["current_stage"]["sleep_time"], "02:30")
        profile = self.run_cli("manage_profile.py", "show")
        self.assertEqual(profile["sleep_window_start"], "02:30")
        self.assertEqual(profile["target_wake_time"], "11:30")

    def test_sleep_shift_pause_export_and_stop_collection(self):
        self.init_profile()
        self.run_cli(
            "manage_sleep_shift.py",
            "start",
            "--confirm",
            "--current-sleep-time",
            "03:00",
            "--current-wake-time",
            "12:00",
            "--target-sleep-time",
            "23:00",
            "--start-date",
            "2026-07-29",
        )
        paused = self.run_cli("manage_sleep_shift.py", "pause")
        self.assertEqual(paused["plan"]["status"], "paused")
        resumed = self.run_cli(
            "manage_sleep_shift.py",
            "resume",
            "--as-of",
            "2026-08-01",
        )
        self.assertEqual(resumed["plan"]["status"], "active")
        exported = self.run_cli("manage_profile.py", "export")
        self.assertEqual(exported["sleep_shift_plan"]["status"], "active")
        self.run_cli("manage_profile.py", "stop-collection")
        shown = self.run_cli("manage_sleep_shift.py", "show")
        self.assertEqual(shown["status"], "paused")

    def test_sleep_shift_hold_move_back_and_cancel(self):
        self.init_profile()
        self.run_cli(
            "manage_sleep_shift.py",
            "start",
            "--confirm",
            "--current-sleep-time",
            "03:00",
            "--current-wake-time",
            "12:00",
            "--target-sleep-time",
            "23:00",
            "--start-date",
            "2026-07-29",
        )
        held = self.run_cli(
            "manage_sleep_shift.py",
            "hold",
            "--as-of",
            "2026-07-31",
            "--days",
            "3",
        )
        self.assertEqual(held["plan"]["review_on_or_after"], "2026-08-03")
        advanced = self.run_cli(
            "manage_sleep_shift.py",
            "advance",
            "--as-of",
            "2026-08-03",
            "--confirm",
        )
        self.assertEqual(advanced["plan"]["current_stage_index"], 2)
        moved_back = self.run_cli(
            "manage_sleep_shift.py",
            "back",
            "--as-of",
            "2026-08-04",
            "--confirm",
        )
        self.assertEqual(moved_back["plan"]["current_stage_index"], 1)
        cancelled = self.run_cli("manage_sleep_shift.py", "cancel", "--confirm")
        self.assertEqual(cancelled["plan"]["status"], "cancelled")

    def test_weekday_and_weekend_schedules_are_distinct(self):
        self.run_cli(
            "manage_profile.py",
            "init",
            "--consent",
            "--timezone",
            "America/Toronto",
            "--target-wake-time",
            "07:30",
            "--sleep-window-start",
            "23:00",
            "--sleep-window-end",
            "07:30",
            "--weekend-differs",
            "--weekend-wake-time",
            "08:00",
            "--weekend-sleep-window-start",
            "00:30",
            "--weekend-sleep-window-end",
            "08:00",
            "--proactive-start",
            "19:00",
            "--proactive-end",
            "09:00",
        )
        self.authorize_schedule()
        plan = self.run_cli("build_reminder_schedule.py", "plan")
        ids = {item["schedule_id"] for item in plan["items"]}
        self.assertIn("wind_down_weekday", ids)
        self.assertIn("wind_down_weekend", ids)
        self.assertIn("weekly_summary_weekly", ids)
        weekday = next(item for item in plan["items"] if item["schedule_id"] == "wake_target_weekday")
        weekend = next(item for item in plan["items"] if item["schedule_id"] == "wake_target_weekend")
        self.assertTrue(weekday["cron"].endswith("1-5"))
        self.assertTrue(weekend["cron"].endswith("0,6"))

    def test_reminder_sent_postpone_skip_disable_and_ignore_reduction(self):
        self.init_profile()
        self.authorize_schedule()
        stamp = "2026-07-29T20:00:00-04:00"
        sent = self.run_cli(
            "build_reminder_schedule.py", "action", "wind_down", "sent", "--at", stamp
        )
        self.assertTrue(sent["state"]["awaiting_reply"])
        blocked = self.run_cli(
            "build_reminder_schedule.py", "evaluate", "wind_down", "--at", stamp
        )
        self.assertFalse(blocked["send"])
        self.assertIn("already_sent_without_reply", blocked["reasons"])

        postponed = self.run_cli(
            "build_reminder_schedule.py",
            "action",
            "wind_down",
            "postpone",
            "--minutes",
            "20",
            "--at",
            stamp,
        )
        self.assertIn("20:20:00", postponed["snooze_until"])
        snoozed = self.run_cli(
            "build_reminder_schedule.py",
            "evaluate",
            "wind_down",
            "--at",
            "2026-07-29T20:10:00-04:00",
        )
        self.assertFalse(snoozed["send"])

        self.run_cli(
            "build_reminder_schedule.py", "action", "wind_down", "skip", "--at", stamp
        )
        skipped = self.run_cli(
            "build_reminder_schedule.py", "evaluate", "wind_down", "--at", stamp
        )
        self.assertIn("skipped_today", skipped["reasons"])

        for _ in range(3):
            reduced = self.run_cli(
                "build_reminder_schedule.py", "action", "morning_checkin", "ignored", "--at", stamp
            )
        self.assertEqual(reduced["state"]["frequency"], "every_other_day")
        self.assertTrue(reduced["ask_adjustment"])
        disabled = self.run_cli(
            "build_reminder_schedule.py", "action", "morning_checkin", "disable", "--at", stamp
        )
        self.assertFalse(disabled["state"]["enabled"])
        reduced_by_request = self.run_cli(
            "build_reminder_schedule.py", "action", "weekly_summary", "reduce", "--at", stamp
        )
        self.assertEqual(reduced_by_request["state"]["frequency"], "every_other_day")

    def test_goodnight_enters_quiet_suppression(self):
        self.init_profile()
        self.authorize_schedule()
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:06:00-04:00",
        )
        result = self.run_cli(
            "build_reminder_schedule.py",
            "evaluate",
            "goodnight_invite",
            "--at",
            "2026-07-29T23:10:00-04:00",
        )
        self.assertFalse(result["send"])
        self.assertIn("night_quiet", result["reasons"])

    def test_unanswered_reminders_auto_reduce_frequency(self):
        self.init_profile()
        self.authorize_schedule()
        dates = [
            "2026-07-29T20:00:00-04:00",
            "2026-07-30T20:00:00-04:00",
            "2026-07-31T20:00:00-04:00",
            "2026-08-01T20:00:00-04:00",
        ]
        self.run_cli("build_reminder_schedule.py", "action", "wind_down", "sent", "--at", dates[0])
        for stamp in dates[1:3]:
            evaluated = self.run_cli(
                "build_reminder_schedule.py", "evaluate", "wind_down", "--at", stamp
            )
            self.assertTrue(evaluated["send"])
            self.run_cli("build_reminder_schedule.py", "action", "wind_down", "sent", "--at", stamp)
        third_ignore = self.run_cli(
            "build_reminder_schedule.py", "evaluate", "wind_down", "--at", dates[3]
        )
        self.assertTrue(third_ignore["send"])
        self.assertTrue(third_ignore["ask_adjustment"])
        self.assertEqual(third_ignore["state"]["frequency"], "every_other_day")

    def test_stop_collection_suppresses_authorized_schedule(self):
        self.init_profile()
        self.authorize_schedule()
        self.run_cli("manage_profile.py", "stop-collection")
        result = self.run_cli(
            "build_reminder_schedule.py",
            "evaluate",
            "wake_target",
            "--at",
            "2026-07-30T07:30:00-04:00",
        )
        self.assertFalse(result["send"])
        self.assertIn("scheduling_not_authorized", result["reasons"])

    def test_weekly_summary_is_descriptive(self):
        self.init_profile()
        self.run_cli(
            "record_sleep_event.py",
            "goodnight",
            "--at",
            "2026-07-29T23:00:00-04:00",
        )
        self.run_cli(
            "record_sleep_event.py",
            "morning",
            "--at",
            "2026-07-30T07:00:00-04:00",
        )
        result = self.run_cli("summarize_week.py", "--end-date", "2026-07-30")
        self.assertEqual(result["recorded_nights"], 1)
        self.assertIn("descriptive", result["interpretation"])
        self.assertIsNone(result["median_estimated_sleep_duration_minutes"])


class StaticContractCase(unittest.TestCase):
    def test_skill_is_concise_and_references_progressive_files(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text.splitlines()), 500)
        for name in [
            "interaction-protocol.md",
            "data-schema.md",
            "safety-boundaries.md",
            "evidence-sources.md",
        ]:
            self.assertIn(name, text)

    def test_conversation_and_safety_contracts_are_explicit(self):
        protocol = (SKILL / "references" / "interaction-protocol.md").read_text(encoding="utf-8")
        safety = (SKILL / "references" / "safety-boundaries.md").read_text(encoding="utf-8")
        self.assertIn("one question per turn", protocol)
        self.assertIn("no more than two", protocol)
        self.assertIn("continues chatting", protocol)
        self.assertIn("Do not encourage dehydration", safety)
        self.assertIn("breathing pauses", safety)
        self.assertIn("Do not diagnose", safety)

    def test_repository_has_no_committed_runtime_data_patterns(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in [
            "sleep-records.json",
            "profile.json",
            "reminders.json",
            "sleep-shift-plan.json",
            "*.export.json",
        ]:
            self.assertIn(pattern, ignore)


if __name__ == "__main__":
    unittest.main()
