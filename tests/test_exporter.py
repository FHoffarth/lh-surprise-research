"""Tests for CSV, JSON and Markdown export, and run_summary.json structure."""

from __future__ import annotations

import csv
import json
import time
from datetime import date
from pathlib import Path

import pytest

from src.config import Config
from src.exporter import Exporter
from src.extractor import ThemeData


def _make_config(tmp_path: Path) -> Config:
    return Config(
        origin="FRA",
        departure=date(2026, 8, 7),
        return_date=date(2026, 8, 9),
        adults=1,
        output_dir=tmp_path,
    )


def _make_theme(
    index: int = 0,
    name: str = "Kunst & Kultur",
    price: float = 99.0,
    available: bool = True,
    pool: list | None = None,
) -> ThemeData:
    t = ThemeData(
        theme_index=index,
        theme_name=name,
        price_min=price,
        price_raw=f"{price} €",
        confirmed_available=available,
        destination_pool=pool or ["Nordeuropa", "Amsterdam"],
        url=f"https://www.lufthansa-surprise.com/travel-theme/{index}",
    )
    return t


class TestJSONExport:
    def test_results_json_created(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        themes = [_make_theme()]
        paths = exporter.export_all(
            themes=themes, failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        assert Path(paths["results_json"]).exists()

    def test_json_structure(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        themes = [_make_theme(index=0), _make_theme(index=1, name="Sonnenziele", price=149.0)]
        paths = exporter.export_all(
            themes=themes, failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        data = json.loads(Path(paths["results_json"]).read_text(encoding="utf-8"))
        assert "themes" in data
        assert "metadata" in data
        assert "failed_themes" in data
        assert len(data["themes"]) == 2
        assert data["metadata"]["origin"] == "FRA"

    def test_json_all_fields_present(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        t = _make_theme()
        paths = exporter.export_all(
            themes=[t], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        data = json.loads(Path(paths["results_json"]).read_text(encoding="utf-8"))
        theme_dict = data["themes"][0]
        required_fields = [
            "theme_name", "destination_pool", "excludable_destinations",
            "mentioned_cities", "confirmed_available", "price_min", "price_max",
            "pride_cities_found", "extraction_warnings"
        ]
        for field in required_fields:
            assert field in theme_dict, f"Missing field: {field}"


class TestCSVExport:
    def test_results_csv_created(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        paths = exporter.export_all(
            themes=[_make_theme()], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        assert Path(paths["results_csv"]).exists()

    def test_csv_has_headers(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        paths = exporter.export_all(
            themes=[_make_theme()], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        with Path(paths["results_csv"]).open(encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            headers = reader.fieldnames
        expected = ["theme_name", "price_min", "destination_pool", "confirmed_available"]
        for h in expected:
            assert h in headers, f"Missing CSV header: {h}"

    def test_csv_row_count(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        themes = [_make_theme(i) for i in range(3)]
        paths = exporter.export_all(
            themes=themes, failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        with Path(paths["results_csv"]).open(encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 3

    def test_csv_empty_themes(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        paths = exporter.export_all(
            themes=[], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        with Path(paths["results_csv"]).open(encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 0


class TestMarkdownExport:
    def test_report_md_created(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        paths = exporter.export_all(
            themes=[_make_theme()], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        assert Path(paths["report_md"]).exists()

    def test_report_contains_metadata(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        paths = exporter.export_all(
            themes=[_make_theme()], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        content = Path(paths["report_md"]).read_text(encoding="utf-8")
        assert "FRA" in content
        assert "2026" in content
        assert "1 Erwachsener" in content

    def test_report_contains_theme_name(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        paths = exporter.export_all(
            themes=[_make_theme(name="Sonnenziele")], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        content = Path(paths["report_md"]).read_text(encoding="utf-8")
        assert "Sonnenziele" in content

    def test_report_pride_badge(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        t = _make_theme(pool=["Amsterdam", "Paris"])
        paths = exporter.export_all(
            themes=[t], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        content = Path(paths["report_md"]).read_text(encoding="utf-8")
        assert "🏳️‍🌈" in content
        assert "Amsterdam" in content

    def test_sorting_available_first(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        unavail = _make_theme(index=0, name="Unavailable Theme", available=False, price=50.0)
        avail = _make_theme(index=1, name="Available Theme", available=True, price=150.0)
        paths = exporter.export_all(
            themes=[unavail, avail], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        content = Path(paths["report_md"]).read_text(encoding="utf-8")
        # Available theme should appear before unavailable in the table
        pos_avail = content.find("Available Theme")
        pos_unavail = content.find("Unavailable Theme")
        assert pos_avail < pos_unavail, "Available theme should appear first"


class TestRunSummary:
    def test_run_summary_created(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        paths = exporter.export_all(
            themes=[], failed_themes=[], screenshots_saved=[],
            network_response_count=0, start_time=time.time(), end_time=time.time(),
            blocked=False, captcha_detected=False, abort_reason=None,
        )
        assert Path(paths["run_summary"]).exists()

    def test_run_summary_required_fields(self, tmp_path):
        cfg = _make_config(tmp_path)
        exporter = Exporter(cfg)
        st = time.time()
        paths = exporter.export_all(
            themes=[_make_theme()],
            failed_themes=[{"index": 1, "name": "Failed", "error": "timeout", "error_type": "Timeout"}],
            screenshots_saved=["a.png", "b.png"],
            network_response_count=3,
            start_time=st,
            end_time=st + 42.5,
            blocked=False,
            captcha_detected=False,
            abort_reason=None,
            playwright_version="1.47.0",
            browser_version="120.0.6099.28",
            smoke_test_mode=True,
        )
        summary = json.loads(Path(paths["run_summary"]).read_text(encoding="utf-8"))

        required = [
            "run_id", "start_time", "end_time", "duration_seconds",
            "url_tested", "input_parameters", "browser_info",
            "themes_attempted", "themes_successful", "themes_failed",
            "failed_themes", "blocked", "captcha_detected", "abort_reason",
            "screenshots_saved", "network_responses_saved", "smoke_test_mode",
        ]
        for field in required:
            assert field in summary, f"Missing run_summary field: {field}"

        assert summary["themes_successful"] == 1
        assert summary["themes_failed"] == 1
        assert summary["screenshots_saved"] == 2
        assert summary["network_responses_saved"] == 3
        assert summary["smoke_test_mode"] is True
        assert summary["browser_info"]["playwright_version"] == "1.47.0"
        assert abs(summary["duration_seconds"] - 42.5) < 0.1
