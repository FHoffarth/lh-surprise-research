"""Configuration dataclass, CLI argument parser and JSON config loader."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional


DEFAULT_PRIDE_CITIES: list[str] = [
    "Amsterdam",
    "Prag",
    "Prague",
    "Antwerpen",
    "Antwerp",
    "Reykjavik",
    "Reykjavík",
    "Nürnberg",
    "Nuremberg",
    "Nuernberg",
    "Braunschweig",
    "Brunswick",
    "Kopenhagen",
    "Copenhagen",
]

BASE_URL = "https://www.lufthansa-surprise.com/travel-theme"


@dataclass
class Config:
    origin: str = "FRA"
    departure: date = field(default_factory=lambda: date(2026, 8, 7))
    return_date: date = field(default_factory=lambda: date(2026, 8, 9))
    adults: int = 1
    headless: bool = False
    language: str = "de"
    currency: str = "EUR"
    output_dir: Path = field(default_factory=lambda: Path("artifacts"))
    smoke_test_only: bool = False
    pride_cities: list[str] = field(default_factory=lambda: list(DEFAULT_PRIDE_CITIES))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.origin or len(self.origin) != 3:
            raise ValueError(f"Invalid IATA origin code: {self.origin!r}")
        if not isinstance(self.departure, date):
            raise TypeError("departure must be a date object")
        if not isinstance(self.return_date, date):
            raise TypeError("return_date must be a date object")
        if self.return_date < self.departure:
            raise ValueError("return_date must be on or after departure")
        if self.adults < 1 or self.adults > 9:
            raise ValueError(f"adults must be between 1 and 9, got {self.adults}")

    @property
    def departure_str_de(self) -> str:
        """German date format DD.MM.YYYY."""
        return self.departure.strftime("%d.%m.%Y")

    @property
    def return_str_de(self) -> str:
        """German date format DD.MM.YYYY."""
        return self.return_date.strftime("%d.%m.%Y")

    @property
    def departure_iso(self) -> str:
        return self.departure.isoformat()

    @property
    def return_iso(self) -> str:
        return self.return_date.isoformat()


def _parse_date(value: str) -> date:
    """Parse ISO date string YYYY-MM-DD."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}. Expected format: YYYY-MM-DD"
        ) from exc


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lh-surprise-scraper",
        description=(
            "Read-only analyzer for the Lufthansa Surprise booking page. "
            "No booking, no payment, no purchase will be executed."
        ),
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="Path to JSON configuration file (overrides CLI defaults)",
    )
    # Use SUPPRESS as default so we can detect whether arg was explicitly provided
    parser.add_argument("--origin", default=argparse.SUPPRESS, help="IATA departure airport code (default: FRA)")
    parser.add_argument(
        "--departure",
        type=_parse_date,
        default=argparse.SUPPRESS,
        metavar="YYYY-MM-DD",
        help="Outbound flight date (default: 2026-08-07)",
    )
    parser.add_argument(
        "--return-date",
        dest="return_date",
        type=_parse_date,
        default=argparse.SUPPRESS,
        metavar="YYYY-MM-DD",
        help="Return flight date (default: 2026-08-09)",
    )
    parser.add_argument(
        "--adults", type=int, default=argparse.SUPPRESS,
        help="Number of adult passengers (default: 1)"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--headed", dest="headless", action="store_false",
        default=argparse.SUPPRESS,
        help="Run browser in headed mode (default)"
    )
    mode.add_argument(
        "--headless", dest="headless", action="store_true",
        default=argparse.SUPPRESS,
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--smoke-test",
        dest="smoke_test_only",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Only process the first theme (smoke test mode)",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default=argparse.SUPPRESS,
        help="Directory for output files (default: artifacts)",
    )
    return parser


def load_config(args: Optional[argparse.Namespace] = None) -> Config:
    """Build Config from CLI args, optionally loading a JSON file first.

    Priority (highest to lowest):
    1. Explicitly provided CLI arguments
    2. JSON config file values
    3. Built-in defaults
    """
    if args is None:
        parser = build_arg_parser()
        args = parser.parse_args()

    # Built-in defaults
    kwargs: dict = {
        "origin": "FRA",
        "departure": date(2026, 8, 7),
        "return_date": date(2026, 8, 9),
        "adults": 1,
        "headless": False,
        "smoke_test_only": False,
    }

    # Load JSON config (overrides built-in defaults)
    if hasattr(args, "config") and args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with config_path.open(encoding="utf-8") as fh:
            file_cfg = json.load(fh)
        for key, value in file_cfg.items():
            if key == "departure":
                kwargs["departure"] = date.fromisoformat(value)
            elif key == "return_date":
                kwargs["return_date"] = date.fromisoformat(value)
            elif key == "output_dir":
                kwargs["output_dir"] = Path(value)
            elif key == "pride_cities":
                kwargs["pride_cities"] = list(value)
            else:
                kwargs[key] = value

    # CLI args override JSON where explicitly provided (SUPPRESS means attr absent if not set)
    if hasattr(args, "origin"):
        kwargs["origin"] = args.origin.upper()
    if hasattr(args, "departure"):
        v = args.departure
        kwargs["departure"] = v if isinstance(v, date) else _parse_date(str(v))
    if hasattr(args, "return_date"):
        v = args.return_date
        kwargs["return_date"] = v if isinstance(v, date) else _parse_date(str(v))
    if hasattr(args, "adults"):
        kwargs["adults"] = args.adults
    if hasattr(args, "headless"):
        kwargs["headless"] = args.headless
    if hasattr(args, "smoke_test_only"):
        kwargs["smoke_test_only"] = args.smoke_test_only
    if hasattr(args, "output_dir") and args.output_dir:
        kwargs["output_dir"] = Path(args.output_dir)

    return Config(**kwargs)
