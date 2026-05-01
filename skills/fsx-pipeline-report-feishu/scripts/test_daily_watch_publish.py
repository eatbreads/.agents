import importlib.util
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


daily_watch_publish = load_module("daily_watch_publish", "daily_watch_publish.py")


class DailyWatchPublishHelpersTest(unittest.TestCase):
    def test_get_chat_ids_prefers_array_and_compat_legacy_field(self):
        config = {"chat_ids": ["oc_1", "oc_2"], "chat_id": "oc_legacy"}
        self.assertEqual(daily_watch_publish.get_chat_ids(config), ["oc_1", "oc_2"])
        self.assertEqual(daily_watch_publish.get_chat_ids({"chat_id": "oc_legacy"}), ["oc_legacy"])

    def test_build_spreadsheet_title_uses_date(self):
        now = datetime(2026, 4, 12, 18, 5)

        title = daily_watch_publish.build_spreadsheet_title(now)

        self.assertEqual(title, "FSX 核心流水线每日看护-2026-04-12")

    def test_build_rule_fallback_report_contains_compact_summary(self):
        overview_rows = [
            {
                "pipeline_name": "北京全量",
                "总用例数": "3582",
                "总失败": "35",
                "总成功": "3545",
                "总跳过": "2",
                "总通过率": "98.97",
                "pipeline_id": "1073215225602",
            },
            {
                "pipeline_name": "廊坊灰度",
                "总用例数": "984",
                "总失败": "24",
                "总成功": "960",
                "总跳过": "0",
                "总通过率": "97.56",
                "pipeline_id": "656544971778",
            },
        ]

        text = daily_watch_publish.build_rule_fallback_report(
            overview_rows,
            datetime(2026, 4, 13, 9, 0),
        )

        self.assertIn("FSX 核心流水线每日看护报告（2026-04-13）", text)
        self.assertIn("标题：2026-04-13 FSX 客户端与代理流水线运行日报", text)
        self.assertIn("4,566 条用例", text)
        self.assertIn("各流水线运行情况汇总：", text)
        self.assertNotIn("随机故障注入-kill", text)

    def test_compose_final_message_appends_spreadsheet_link(self):
        text = daily_watch_publish.compose_final_message(
            "报告正文",
            daily_watch_publish.ResourceRef(token="b1", url="https://base.example"),
        )

        self.assertIn("报告正文", text)
        self.assertIn("https://base.example", text)

    def test_build_daily_watch_card_contains_oncall_links_and_top10(self):
        overview_rows = [
            {
                "pipeline_name": "FSx统一客户端_北京_全量流水线_vepfs/tos",
                "总用例数": "686",
                "总失败": "48",
                "总成功": "635",
                "总跳过": "3",
                "总通过率": "92.57",
                "pipeline_id": "1073215225602",
            },
            {
                "pipeline_name": "FSProxy_FileNAS_全量_流水线",
                "总用例数": "0",
                "总失败": "0",
                "总成功": "0",
                "总跳过": "0",
                "总通过率": "0.00",
                "pipeline_id": "865297825538",
            },
        ]
        top10_rows = [
            {
                "pipeline_name": "FSx统一客户端_北京_全量流水线_vepfs/tos",
                "jobName": "升级兼容性测试",
                "state": "failed",
                "failed_case": "14",
                "pipeline_id": "1073215225602",
            }
        ]
        oncall = {
            "open_ids": ["ou_primary", "ou_backup"],
        }

        card = daily_watch_publish.build_daily_watch_card(
            overview_rows,
            top10_rows,
            oncall,
            datetime(2026, 4, 27, 9, 0),
        )

        text = str(card)
        self.assertEqual(card["schema"], "2.0")
        self.assertIn("person_list", text)
        self.assertIn("ou_primary", text)
        self.assertIn("collapsible_panel", text)
        self.assertIn("TOP10", text)
        self.assertIn("升级兼容性测试", text)
        self.assertIn("https://bits.bytedance.net/devops/4082708738/pipeline/detail/1073215225602", text)

    def test_send_group_card_uses_interactive_message(self):
        with mock.patch.object(
            daily_watch_publish,
            "_run_command",
            return_value={"message_id": "om_card"},
        ) as run_command:
            payload = daily_watch_publish.send_group_card("oc_1", {"schema": "2.0"})

        self.assertEqual(payload, {"message_id": "om_card"})
        args = run_command.call_args.args[0]
        self.assertIn("--msg-type", args)
        self.assertEqual(args[args.index("--msg-type") + 1], "interactive")
        self.assertEqual(args[args.index("--chat-id") + 1], "oc_1")

    def test_send_group_messages_continues_after_single_chat_failure(self):
        with mock.patch.object(
            daily_watch_publish,
            "send_group_message",
            side_effect=[
                {"data": {"message_id": "om_ok"}},
                RuntimeError("send failed"),
                {"message_id": "om_ok_2"},
            ],
        ):
            results = daily_watch_publish.send_group_messages(
                ["oc_1", "oc_2", "oc_3"],
                "hello",
            )

        self.assertEqual(
            results,
            [
                {"chat_id": "oc_1", "status": "OK", "message_id": "om_ok"},
                {"chat_id": "oc_2", "status": "ERROR", "error": "send failed"},
                {"chat_id": "oc_3", "status": "OK", "message_id": "om_ok_2"},
            ],
        )

    def test_send_group_messages_raises_when_all_chats_fail(self):
        with mock.patch.object(
            daily_watch_publish,
            "send_group_message",
            side_effect=RuntimeError("all failed"),
        ):
            with self.assertRaises(daily_watch_publish.PublishError):
                daily_watch_publish.send_group_messages(["oc_1", "oc_2"], "hello")

    def test_read_csv_rows_reads_utf8_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "overview_all.csv"
            path.write_text("pipeline_name,总失败\n北京全量,35\n", encoding="utf-8")

            rows = daily_watch_publish.read_csv_rows(path)

        self.assertEqual(rows, [{"pipeline_name": "北京全量", "总失败": "35"}])

    def test_ensure_base_reuses_saved_base_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "overview_all.csv").write_text("a,b\n1,2\n", encoding="utf-8")
            (base / "top10_jobs_all.csv").write_text("c,d\n3,4\n", encoding="utf-8")
            (base / "jobs_all.csv").write_text("e,f\n5,6\n", encoding="utf-8")

            values = daily_watch_publish.build_combined_sheet_values(base, datetime(2026, 4, 12, 9, 0))

        self.assertEqual(values[0], ["2026-04-12 总览"])
        self.assertEqual(values[1], ["a", "b"])
        self.assertIn(["2026-04-12 TOP10"], values)
        self.assertIn(["2026-04-12 全量"], values)
        top10_index = values.index(["2026-04-12 TOP10"])
        full_index = values.index(["2026-04-12 全量"])
        self.assertLess(top10_index, full_index)

    def test_cleanup_local_outputs_removes_generated_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for filename in [
                daily_watch_publish.OVERVIEW_FILENAME,
                daily_watch_publish.TOP10_FILENAME,
                daily_watch_publish.JOBS_FILENAME,
            ]:
                (base / filename).write_text("x", encoding="utf-8")

            removed = daily_watch_publish.cleanup_local_outputs(base)

            self.assertEqual(
                removed,
                [
                    daily_watch_publish.OVERVIEW_FILENAME,
                    daily_watch_publish.TOP10_FILENAME,
                    daily_watch_publish.JOBS_FILENAME,
                ],
            )
            for filename in removed:
                self.assertFalse((base / filename).exists())

    def test_grant_department_view_permissions_calls_drive_api(self):
        with mock.patch.object(
            daily_watch_publish,
            "_run_command",
            return_value={"member": {"member_id": "od-1"}},
        ) as run_command:
            result = daily_watch_publish.grant_department_view_permissions(
                "sht_token",
                ["od-1", "od-2"],
            )

        self.assertEqual(len(result), 2)
        first_args = run_command.call_args_list[0].args[0]
        self.assertEqual(first_args[:5], ["lark-cli", "drive", "permission.members", "create", "--as"])
        self.assertIn("sht_token", first_args[first_args.index("--params") + 1])
        self.assertIn("opendepartmentid", first_args[first_args.index("--data") + 1])
        self.assertIn("department", first_args[first_args.index("--data") + 1])


if __name__ == "__main__":
    unittest.main()
