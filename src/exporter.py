"""Export results as JSON, CSV, Markdown report and run_summary.json."""

from __future__ import annotations

import csv
import json
import platform
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .config import Config
from .extractor import ThemeData
from .utils import find_pride_cities_in_pool


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Exporter:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._output_dir = config.output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def export_all(
        self,
        themes: list[ThemeData],
        failed_themes: list[dict],
        screenshots_saved: list[str],
        network_response_count: int,
        start_time: float,
        end_time: float,
        blocked: bool,
        captcha_detected: bool,
        abort_reason: Optional[str],
        playwright_version: str = "unknown",
        browser_version: str = "unknown",
        smoke_test_mode: bool = False,
    ) -> dict[str, str]:
        """
        Export all output files.
        Returns dict mapping output type to file path.
        """
        # Add Pride city marking to themes
        themes_with_pride = self._mark_pride_cities(themes)

        # Sort: available first, then by price, then by destination pool size
        sorted_themes = self._sort_themes(themes_with_pride)

        paths: dict[str, str] = {}
        paths["results_json"] = self._export_json(sorted_themes, failed_themes)
        paths["results_csv"] = self._export_csv(sorted_themes)
        paths["report_md"] = self._export_markdown(sorted_themes, failed_themes)
        paths["run_summary"] = self._export_run_summary(
            themes=sorted_themes,
            failed_themes=failed_themes,
            screenshots_saved=screenshots_saved,
            network_response_count=network_response_count,
            start_time=start_time,
            end_time=end_time,
            blocked=blocked,
            captcha_detected=captcha_detected,
            abort_reason=abort_reason,
            playwright_version=playwright_version,
            browser_version=browser_version,
            smoke_test_mode=smoke_test_mode,
        )
        return paths

    def _mark_pride_cities(self, themes: list[ThemeData]) -> list[ThemeData]:
        """Mark Pride cities in destination pools and mentioned cities."""
        for theme in themes:
            all_cities = theme.destination_pool + theme.mentioned_cities + theme.excludable_destinations
            theme.pride_cities_found = find_pride_cities_in_pool(
                all_cities, self._config.pride_cities
            )
        return themes

    def _sort_themes(self, themes: list[ThemeData]) -> list[ThemeData]:
        """Sort: confirmed available first, then by price, then by pool size."""
        def sort_key(t: ThemeData) -> tuple:
            # 0 = available, 1 = unknown, 2 = unavailable
            avail = 0 if t.confirmed_available is True else (2 if t.confirmed_available is False else 1)
            price = t.price_min if t.price_min is not None else float("inf")
            pool_size = -len(t.destination_pool)  # negative so larger is first
            return (avail, price, pool_size)
        return sorted(themes, key=sort_key)

    def _export_json(self, themes: list[ThemeData], failed_themes: list[dict]) -> str:
        path = self._output_dir / "results.json"
        data = {
            "metadata": {
                "exported_at": _iso_now(),
                "origin": self._config.origin,
                "departure": self._config.departure_iso,
                "return_date": self._config.return_iso,
                "adults": self._config.adults,
            },
            "themes": [t.to_dict() for t in themes],
            "failed_themes": failed_themes,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    def _export_csv(self, themes: list[ThemeData]) -> str:
        path = self._output_dir / "results.csv"
        fieldnames = [
            "theme_index", "theme_name", "description",
            "destination_pool", "excludable_destinations", "mentioned_cities",
            "confirmed_available", "price_min", "price_max", "price_raw", "price_per_person",
            "cabin_classes", "flight_times", "direct_flights_only",
            "pride_cities_found", "url", "screenshot_path", "extraction_warnings",
        ]
        with path.open("w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for t in themes:
                d = t.to_dict()
                # Flatten list fields to pipe-separated strings
                for key in ["destination_pool", "excludable_destinations", "mentioned_cities",
                            "cabin_classes", "flight_times", "pride_cities_found", "extraction_warnings"]:
                    d[key] = " | ".join(d[key]) if d[key] else ""
                # Remove raw_page_text if present
                d.pop("raw_page_text", None)
                writer.writerow(d)
        return str(path)

    def _export_markdown(self, themes: list[ThemeData], failed_themes: list[dict]) -> str:
        path = self._output_dir / "report.md"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        cfg = self._config

        lines: list[str] = [
            "# Lufthansa Surprise – Analysebericht",
            "",
            "## Abfrageparameter",
            "",
            f"| Parameter | Wert |",
            f"|-----------|------|",
            f"| Zeitpunkt der Abfrage | {now} |",
            f"| Abflughafen | {cfg.origin} |",
            f"| Hinflug | {cfg.departure_str_de} |",
            f"| Rückflug | {cfg.return_str_de} |",
            f"| Reisende | {cfg.adults} Erwachsener |",
            f"| Währung | {cfg.currency} |",
            f"| Geprüfte URL | https://www.lufthansa-surprise.com/travel-theme |",
            "",
        ]

        # Themes table
        lines += [
            "## Ergebnisse – Reisethemen",
            "",
            "Sortierung: Verfügbar → Günstigster Preis → Größter Zielpool",
            "",
            "| # | Reisethema | Preis (min) | Verfügbar | Zielpool | Pride-Städte | Kabinenklasse |",
            "|---|-----------|-------------|-----------|----------|-------------|---------------|",
        ]
        for t in themes:
            avail = "✅" if t.confirmed_available is True else ("❌" if t.confirmed_available is False else "❓")
            price = f"{t.price_min:.2f} €" if t.price_min is not None else "–"
            pool = ", ".join(t.destination_pool[:5]) + ("…" if len(t.destination_pool) > 5 else "")
            pride = " 🏳️‍🌈 " + ", ".join(t.pride_cities_found) if t.pride_cities_found else ""
            cabin = ", ".join(t.cabin_classes) or "–"
            lines.append(
                f"| {t.theme_index} | {t.theme_name or '–'} | {price} | {avail} | {pool or '–'} | {pride or '–'} | {cabin} |"
            )

        lines += ["", ""]

        # Detail sections
        lines += ["## Details je Reisethema", ""]
        for t in themes:
            pride_badge = " 🏳️‍🌈" if t.pride_cities_found else ""
            lines += [
                f"### {t.theme_index}. {t.theme_name or 'Unbekannt'}{pride_badge}",
                "",
            ]
            if t.description:
                lines += [f"> {t.description}", ""]
            lines += [
                f"**URL:** {t.url or '–'}",
                f"**Preis:** {t.price_raw or '–'} (min: {t.price_min}, max: {t.price_max})",
                f"**Pro Person:** {'Ja' if t.price_per_person else ('Nein' if t.price_per_person is False else 'Unbekannt')}",
                f"**Verfügbar:** {'Ja' if t.confirmed_available else ('Nein' if t.confirmed_available is False else 'Unbekannt')}",
                f"**Zielpool:** {', '.join(t.destination_pool) or '–'}",
                f"**Ausschließbare Ziele:** {', '.join(t.excludable_destinations) or '–'}",
                f"**Genannte Städte (unbestätigt):** {', '.join(t.mentioned_cities) or '–'}",
                f"**Kabinenklassen:** {', '.join(t.cabin_classes) or '–'}",
                f"**Flugzeiten:** {', '.join(t.flight_times) or '–'}",
                f"**Nur Direktflüge:** {'Ja' if t.direct_flights_only else ('Nein' if t.direct_flights_only is False else 'Unbekannt')}",
            ]
            if t.pride_cities_found:
                lines.append(f"**🏳️‍🌈 Pride-Städte im Pool:** {', '.join(t.pride_cities_found)}")
            if t.extraction_warnings:
                lines += ["", "**⚠️ Hinweise:**"]
                for w in t.extraction_warnings:
                    lines.append(f"- {w}")
            if t.screenshot_path:
                lines += ["", f"![Screenshot]({t.screenshot_path})"]
            lines += ["", "---", ""]

        # Failed themes
        if failed_themes:
            lines += ["## Fehlgeschlagene Themen", ""]
            for f in failed_themes:
                lines.append(f"- **{f.get('name', f.get('index', '?'))}**: {f.get('error', '–')} ({f.get('error_type', '?')})")
            lines += [""]

        # Uncertainties
        lines += [
            "## Unsicherheiten und Einschränkungen",
            "",
            "- Das konkrete Reiseziel wird bei Lufthansa Surprise erst nach Buchung und Zahlung enthüllt.",
            "- 'Genannte Städte' sind Erwähnungen im Fließtext und **keine bestätigten buchbaren Ziele**.",
            "- 'Zielpool' zeigt die vom System angebotene Kategorie, nicht einzelne Destinationen.",
            "- Verfügbarkeitsstatus ist 'Unbekannt', sofern kein explizites Signal gefunden wurde.",
            "- Flugzeiten können aus dem Kontext gerissen sein und sind nicht garantiert aktuell.",
            "- Die Pride-Markierung basiert auf Textübereinstimmungen und ist kein offizielles Merkmal.",
            "",
        ]

        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _export_run_summary(
        self,
        themes: list[ThemeData],
        failed_themes: list[dict],
        screenshots_saved: list[str],
        network_response_count: int,
        start_time: float,
        end_time: float,
        blocked: bool,
        captcha_detected: bool,
        abort_reason: Optional[str],
        playwright_version: str,
        browser_version: str,
        smoke_test_mode: bool,
    ) -> str:
        path = self._output_dir / "run_summary.json"
        summary = {
            "run_id": str(uuid.uuid4()),
            "start_time": datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(),
            "end_time": datetime.fromtimestamp(end_time or time.time(), tz=timezone.utc).isoformat(),
            "duration_seconds": round((end_time or time.time()) - start_time, 2),
            "url_tested": "https://www.lufthansa-surprise.com/travel-theme",
            "input_parameters": {
                "origin": self._config.origin,
                "departure": self._config.departure_iso,
                "return_date": self._config.return_iso,
                "adults": self._config.adults,
                "headless": self._config.headless,
            },
            "browser_info": {
                "playwright_version": playwright_version,
                "browser": "chromium",
                "browser_version": browser_version,
                "platform": platform.system(),
            },
            "themes_attempted": len(themes) + len(failed_themes),
            "themes_successful": len(themes),
            "themes_failed": len(failed_themes),
            "failed_themes": failed_themes,
            "blocked": blocked,
            "captcha_detected": captcha_detected,
            "abort_reason": abort_reason,
            "screenshots_saved": len(screenshots_saved),
            "screenshot_paths": screenshots_saved,
            "network_responses_saved": network_response_count,
            "smoke_test_mode": smoke_test_mode,
        }
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)
