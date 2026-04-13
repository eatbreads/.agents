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
