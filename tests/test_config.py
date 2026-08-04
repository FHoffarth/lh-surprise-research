"""Tests for configuration, CLI parsing and date validation."""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import date
from pathlib import Path

import pytest

from src.config import Config, _parse_date, build_arg_parser, load_config


class TestDateParsing:
    def test_valid_iso_date(self):
        d = _parse_date("2026-08-07")
        assert d == date(2026, 8, 7)

    def test_invalid_format_raises(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_date("07.08.2026")

    def test_invalid_date_raises(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_date("2026-13-01")

    def test_non_date_raises(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_date("not-a-date")


class TestConfigValidation:
    def test_valid_config(self):
        cfg = Config(
            origin="FRA",
            departure=date(2026, 8, 7),
            return_date=date(2026, 8, 9),
            adults=1,
        )
        assert cfg.origin == "FRA"
        assert cfg.adults == 1

    def test_return_before_departure_raises(self):
        with pytest.raises(ValueError, match="return_date must be on or after"):
            Config(
                origin="FRA",
                departure=date(2026, 8, 9),
                return_date=date(2026, 8, 7),
                adults=1,
            )

    def test_same_day_is_valid(self):
        cfg = Config(
            origin="FRA",
            departure=date(2026, 8, 7),
            return_date=date(2026, 8, 7),
            adults=1,
        )
        assert cfg.departure == cfg.return_date

    def test_invalid_origin_raises(self):
        with pytest.raises(ValueError, match="Invalid IATA"):
            Config(
                origin="FRANK",
                departure=date(2026, 8, 7),
                return_date=date(2026, 8, 9),
                adults=1,
            )

    def test_empty_origin_raises(self):
        with pytest.raises(ValueError):
            Config(
                origin="",
                departure=date(2026, 8, 7),
                return_date=date(2026, 8, 9),
                adults=1,
            )

    def test_adults_zero_raises(self):
        with pytest.raises(ValueError, match="adults must be between"):
            Config(
                origin="FRA",
                departure=date(2026, 8, 7),
                return_date=date(2026, 8, 9),
                adults=0,
            )

    def test_adults_ten_raises(self):
        with pytest.raises(ValueError):
            Config(
                origin="FRA",
                departure=date(2026, 8, 7),
                return_date=date(2026, 8, 9),
                adults=10,
            )


class TestConfigDateStrings:
    def setup_method(self):
        self.cfg = Config(
            origin="MUC",
            departure=date(2026, 8, 7),
            return_date=date(2026, 8, 9),
            adults=2,
        )

    def test_departure_str_de(self):
        assert self.cfg.departure_str_de == "07.08.2026"

    def test_return_str_de(self):
        assert self.cfg.return_str_de == "09.08.2026"

    def test_departure_iso(self):
        assert self.cfg.departure_iso == "2026-08-07"

    def test_return_iso(self):
        assert self.cfg.return_iso == "2026-08-09"


class TestCLIArgParser:
    def test_defaults(self):
        parser = build_arg_parser()
        args = parser.parse_args([])
        # When no args given, load_config applies built-in defaults
        cfg = load_config(args)
        assert cfg.origin == "FRA"
        assert cfg.headless is False
        assert cfg.smoke_test_only is False

    def test_headed_flag(self):
        parser = build_arg_parser()
        args = parser.parse_args(["--headed"])
        assert args.headless is False

    def test_headless_flag(self):
        parser = build_arg_parser()
        args = parser.parse_args(["--headless"])
        assert args.headless is True

    def test_headed_and_headless_mutually_exclusive(self):
        parser = build_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--headed", "--headless"])

    def test_smoke_test_flag(self):
        parser = build_arg_parser()
        args = parser.parse_args(["--smoke-test"])
        assert args.smoke_test_only is True

    def test_origin_flag(self):
        parser = build_arg_parser()
        args = parser.parse_args(["--origin", "MUC"])
        assert args.origin == "MUC"

    def test_date_flags(self):
        parser = build_arg_parser()
        args = parser.parse_args(["--departure", "2026-09-01", "--return-date", "2026-09-05"])
        assert args.departure == date(2026, 9, 1)
        assert args.return_date == date(2026, 9, 5)

    def test_adults_flag(self):
        parser = build_arg_parser()
        args = parser.parse_args(["--adults", "3"])
        assert args.adults == 3


class TestJSONConfig:
    def test_load_from_json(self, tmp_path):
        cfg_data = {
            "origin": "MUC",
            "departure": "2026-09-01",
            "return_date": "2026-09-03",
            "adults": 2,
            "headless": True,
            "smoke_test_only": True,
        }
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(cfg_data), encoding="utf-8")

        parser = build_arg_parser()
        args = parser.parse_args(["--config", str(cfg_file)])
        cfg = load_config(args)

        assert cfg.origin == "MUC"
        assert cfg.departure == date(2026, 9, 1)
        assert cfg.return_date == date(2026, 9, 3)
        assert cfg.adults == 2
        assert cfg.headless is True
        assert cfg.smoke_test_only is True

    def test_missing_config_file_raises(self, tmp_path):
        parser = build_arg_parser()
        args = parser.parse_args(["--config", str(tmp_path / "nonexistent.json")])
        with pytest.raises(FileNotFoundError):
            load_config(args)
