import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


bits_pipeline_report = load_module("bits_pipeline_report", "bits_pipeline_report.py")
watch_single_pipeline = load_module("watch_single_pipeline", "watch_single_pipeline.py")
watch_fixed_pipelines = load_module("watch_fixed_pipelines", "watch_fixed_pipelines.py")


class BitsPipelineReportHelpersTest(unittest.TestCase):
    def test_extract_last_run_id_prefers_pipeline_level_field(self):
        payload = {
            "pipeline": {
                "last_run_id": 1136934722050,
                "pipeline": {"last_run_id": 999},
            }
        }

        self.assertEqual(
            bits_pipeline_report.extract_last_run_id(payload),
            "1136934722050",
        )

    def test_extract_last_run_id_falls_back_to_nested_pipeline_field(self):
        payload = {
            "pipeline": {
                "pipeline": {
                    "last_run_id": 1136934722050,
                }
            }
        }

        self.assertEqual(
            bits_pipeline_report.extract_last_run_id(payload),
            "1136934722050",
        )

    def test_is_finished_run_status_accepts_terminal_numeric_and_string_values(self):
        self.assertTrue(bits_pipeline_report.is_finished_run_status(3))
        self.assertTrue(bits_pipeline_report.is_finished_run_status("failed"))
        self.assertFalse(bits_pipeline_report.is_finished_run_status(2))
        self.assertFalse(bits_pipeline_report.is_finished_run_status("running"))

    def test_build_output_paths_disables_stats_by_default(self):
        paths = bits_pipeline_report.build_output_paths("p1", "r1")

        self.assertIn("overview_csv", paths)
        self.assertIn("jobs_csv", paths)
        self.assertIn("top10_csv", paths)
        self.assertNotIn("stats_path", paths)

    def test_build_output_paths_can_enable_stats_explicitly(self):
        paths = bits_pipeline_report.build_output_paths("p1", "r1", include_stats=True)

        self.assertIn("stats_path", paths)


class WatchSinglePipelineTest(unittest.TestCase):
    def test_run_watch_skips_when_latest_run_not_finished(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = io.StringIO()
            with mock.patch.object(
                watch_single_pipeline,
                "exchange_secret_for_jwt",
                return_value="jwt",
            ), mock.patch.object(
                watch_single_pipeline,
                "fetch_openapi_json",
                side_effect=[
                    {"pipeline": {"last_run_id": 1136934722050}},
                    {"pipeline_run": {"run_id": 1136934722050, "run_status": 2}},
                ],
            ), mock.patch.object(
                watch_single_pipeline.bits_pipeline_report,
                "run_report",
            ) as run_report_mock, redirect_stdout(output):
                watch_single_pipeline.run_watch(output_dir=tmpdir)

        run_report_mock.assert_not_called()
        self.assertIn("SKIP", output.getvalue())
        self.assertIn("1136934722050", output.getvalue())

    def test_run_watch_generates_report_when_latest_run_finished(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(
                watch_single_pipeline,
                "exchange_secret_for_jwt",
                return_value="jwt",
            ), mock.patch.object(
                watch_single_pipeline,
                "fetch_openapi_json",
                side_effect=[
                    {"pipeline": {"last_run_id": 1136934722050}},
                    {"pipeline_run": {"run_id": 1136934722050, "run_status": 3}},
                ],
            ), mock.patch.object(
                watch_single_pipeline.bits_pipeline_report,
                "run_report",
            ) as run_report_mock:
                watch_single_pipeline.run_watch(output_dir=tmpdir)

        run_report_mock.assert_called_once_with(
            watch_single_pipeline.PIPELINE_ID,
            "1136934722050",
            dry_run=False,
            output_dir=tmpdir,
            include_stats=bits_pipeline_report.DEFAULT_INCLUDE_STATS,
            write_files=True,
        )


class WatchFixedPipelinesTest(unittest.TestCase):
    def test_write_aggregate_csvs_creates_three_combined_files(self):
        report_rows = [
            {
                "pipeline_id": "p1",
                "pipeline_name": "Pipe 1",
                "run_id": "r1",
                "run_seq": "11",
                "overview_row": {
                    "总用例数": 10,
                    "总失败": 1,
                    "总成功": 9,
                    "总跳过": 0,
                    "总通过率": "90.00",
                },
                "job_rows": [
                    {
                        "jobName": "job-a",
                        "state": "failed",
                        "failed_case": 1,
                        "该节点失败数/总失败数(%)": "100.00",
                        "case_num": 10,
                        "该节点失败数/该节点总用例数(%)": "10.00",
                        "succeed_case": 9,
                        "skipped_case": 0,
                        "jobId": "j1",
                        "jobRunId": "jr1",
                    }
                ],
                "top10_rows": [
                    {
                        "jobName": "job-a",
                        "state": "failed",
                        "failed_case": 1,
                        "该节点失败数/总失败数(%)": "100.00",
                        "case_num": 10,
                        "该节点失败数/该节点总用例数(%)": "10.00",
                        "succeed_case": 9,
                        "skipped_case": 0,
                        "jobId": "j1",
                        "jobRunId": "jr1",
                    },
                    {
                        "jobName": "job-b",
                        "state": "succeed",
                        "failed_case": 0,
                        "该节点失败数/总失败数(%)": "0.00",
                        "case_num": 5,
                        "该节点失败数/该节点总用例数(%)": "0.00",
                        "succeed_case": 5,
                        "skipped_case": 0,
                        "jobId": "j2",
                        "jobRunId": "jr2",
                    }
                ],
            },
            {
                "pipeline_id": "p2",
                "pipeline_name": "Pipe 2",
                "run_id": "r2",
                "run_seq": "22",
                "overview_row": {
                    "总用例数": 20,
                    "总失败": 0,
                    "总成功": 20,
                    "总跳过": 0,
                    "总通过率": "100.00",
                },
                "job_rows": [],
                "top10_rows": [],
            },
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            watch_fixed_pipelines.write_aggregate_csvs(report_rows, output_dir=tmpdir)
            base = Path(tmpdir)

            self.assertTrue((base / "overview_all.csv").exists())
            self.assertTrue((base / "jobs_all.csv").exists())
            self.assertTrue((base / "top10_jobs_all.csv").exists())

            overview_text = (base / "overview_all.csv").read_text(encoding="utf-8")
            jobs_text = (base / "jobs_all.csv").read_text(encoding="utf-8")
            top10_text = (base / "top10_jobs_all.csv").read_text(encoding="utf-8")

            self.assertIn("pipeline_name,总用例数,总失败,总成功,总跳过,总通过率,run_seq,pipeline_id,run_id", overview_text)
            self.assertIn("Pipe 1,10,1,9,0,90.00,11,p1,r1", overview_text)
            self.assertIn("Pipe 2,20,0,20,0,100.00,22,p2,r2", overview_text)
            self.assertIn("pipeline_name,jobName,state,failed_case", jobs_text)
            self.assertIn("pipeline_name,jobName,state,failed_case", top10_text)
            self.assertIn("Pipe 1,job-a,failed,1", top10_text)
            self.assertNotIn("job-b", top10_text)

    def test_run_all_watches_processes_fixed_ids_in_order(self):
        results = [
            {
                "pipeline_id": "1073215225602",
                "status": "OK",
                "run_id": "1",
                "report_data": {
                    "pipeline_id": "1073215225602",
                    "pipeline_name": "Pipe 1",
                    "run_id": "1",
                    "run_seq": "11",
                    "overview_row": {},
                    "job_rows": [],
                    "top10_rows": [],
                },
            },
            {"pipeline_id": "656544971778", "status": "SKIP", "run_id": "2"},
            {
                "pipeline_id": "410812259074",
                "status": "OK",
                "run_id": "3",
                "report_data": {
                    "pipeline_id": "410812259074",
                    "pipeline_name": "Pipe 3",
                    "run_id": "3",
                    "run_seq": "33",
                    "overview_row": {},
                    "job_rows": [],
                    "top10_rows": [],
                },
            },
            {"pipeline_id": "1119183026434", "status": "ERROR", "error": "boom"},
            {
                "pipeline_id": "865297825538",
                "status": "OK",
                "run_id": "5",
                "report_data": {
                    "pipeline_id": "865297825538",
                    "pipeline_name": "Pipe 5",
                    "run_id": "5",
                    "run_seq": "55",
                    "overview_row": {},
                    "job_rows": [],
                    "top10_rows": [],
                },
            },
        ]
        output = io.StringIO()

        with mock.patch.object(
            watch_fixed_pipelines.watch_single_pipeline,
            "exchange_secret_for_jwt",
            return_value="jwt",
        ), mock.patch.object(
            watch_fixed_pipelines,
            "run_watch_for_pipeline",
            side_effect=results,
        ) as run_watch_mock, mock.patch.object(
            watch_fixed_pipelines,
            "write_aggregate_csvs",
        ) as write_aggregate_mock, redirect_stdout(output):
            summary = watch_fixed_pipelines.run_all_watches(output_dir="/tmp/fake")

        self.assertEqual(
            [call.args[0] for call in run_watch_mock.call_args_list],
            watch_fixed_pipelines.PIPELINE_IDS,
        )
        write_aggregate_mock.assert_called_once()
        self.assertEqual(summary["ok_count"], 3)
        self.assertEqual(summary["skip_count"], 1)
        self.assertEqual(summary["error_count"], 1)
        self.assertIn("total=5", output.getvalue())

    def test_run_all_watches_continues_after_one_pipeline_error(self):
        calls = []
        output = io.StringIO()

        def fake_run_watch(pipeline_id, cloud_jwt, output_dir):
            calls.append(pipeline_id)
            if pipeline_id == "656544971778":
                raise RuntimeError("broken")
            return {"pipeline_id": pipeline_id, "status": "OK", "run_id": f"run-{pipeline_id}"}

        with mock.patch.object(
            watch_fixed_pipelines.watch_single_pipeline,
            "exchange_secret_for_jwt",
            return_value="jwt",
        ), mock.patch.object(
            watch_fixed_pipelines,
            "run_watch_for_pipeline",
            side_effect=fake_run_watch,
        ), redirect_stdout(output):
            summary = watch_fixed_pipelines.run_all_watches(output_dir="/tmp/fake")

        self.assertEqual(calls, watch_fixed_pipelines.PIPELINE_IDS)
        self.assertEqual(summary["ok_count"], 4)
        self.assertEqual(summary["error_count"], 1)
        self.assertIn("ERROR pipeline=656544971778", output.getvalue())


if __name__ == "__main__":
    unittest.main()
