# Lufthansa Surprise: Overnight-Dependent Schedule Risk Report

**Reisedatum:** 07.08.2026 - 09.08.2026  
**Abflughafen:** Frankfurt/Main (FRA)  
**Nutzerprofil:** earliest_acceptable_outbound = 14:00  
**Preise:** Baseline-Preis 129,00 €  
**Aufenthaltsregeln:**  
- 1 Übernachtung (one_night): min. 18 Stunden Aufenthalt  
- 2 Übernachtungen (two_nights): min. 36 Stunden Aufenthalt  

## Übersicht der Ergebnisse (Übernachtungsabhängiges Szenario)

| Zielstadt | IATA | Kombinationen (Gültig / Verworfene Stay) | Risiko (Gesamt) | Risiko 1 Nacht | Risiko 2 Nächte | Entscheidung | Begründung |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Florenz | FLR | 23 / 2 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 8 usable and 15 unusable combinations. |
| Prag | PRG | 58 / 6 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 26 usable and 32 unusable combinations. |
| Warschau | WAW | 36 / 6 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 18 usable and 18 unusable combinations. |
| Breslau | WRO | 8 / 1 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 2 usable and 6 unusable combinations. |
| Helsinki | HEL | 16 / 4 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 4 usable and 12 unusable combinations. |
| Bologna | BLQ | 11 / 1 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 5 usable and 6 unusable combinations. |
| Krakau | KRK | 13 / 3 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 5 usable and 8 unusable combinations. |
| Basel | BSL | 8 / 1 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 2 usable and 6 unusable combinations. |
| Sarajevo | SJJ | 3 / 1 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 1 usable and 2 unusable combinations. |
| Mailand (Linate) | LIN | 95 / 4 | `mixed` | `no_valid_itinerary` | `mixed` | **EXCLUDE** | Mixed schedule: 41 usable and 54 unusable combinations. |
| Pula | PUY | 3 / 0 | `safe` | `safe` | `safe` | **KEEP** | All 3 valid itineraries satisfy the 14:00 outbound constraint. |

## Korrektur-Vergleich zum ungenauen 18h-Stay-Szenario

Im vorigen Szenario wurden fälschlicherweise alle Kombinationen mit >= 18h als gültig gezählt, selbst wenn sie 2 Nächte betrafen (was min. 36h erfordert). Dies ist nun korrigiert.

| Zielstadt | Falsche Gültige (18h-Pauschal) | Korrekte Gültige (Übernachtungsbasiert) | Differenz (Verworfene Kombis) | Auswirkung |
| :--- | :---: | :---: | :---: | :--- |
| Florenz | 25 | 23 | 2 | ⚠️ 2 ungültige 2-Nächte-Kombis verworfen |
| Prag | 64 | 58 | 6 | ⚠️ 6 ungültige 2-Nächte-Kombis verworfen |
| Warschau | 42 | 36 | 6 | ⚠️ 6 ungültige 2-Nächte-Kombis verworfen |
| Breslau | 9 | 8 | 1 | ⚠️ 1 ungültige 2-Nächte-Kombis verworfen |
| Helsinki | 20 | 16 | 4 | ⚠️ 4 ungültige 2-Nächte-Kombis verworfen |
| Bologna | 12 | 11 | 1 | ⚠️ 1 ungültige 2-Nächte-Kombis verworfen |
| Krakau | 16 | 13 | 3 | ⚠️ 3 ungültige 2-Nächte-Kombis verworfen |
| Basel | 9 | 8 | 1 | ⚠️ 1 ungültige 2-Nächte-Kombis verworfen |
| Sarajevo | 4 | 3 | 1 | ⚠️ 1 ungültige 2-Nächte-Kombis verworfen |
| Mailand (Linate) | 99 | 95 | 4 | ⚠️ 4 ungültige 2-Nächte-Kombis verworfen |
| Pula | 1 | 3 | -2 | ⚠️ -2 ungültige 2-Nächte-Kombis verworfen |

## Auswertung Pula (PUY) nach Reiseschemen

- **Gesamt gültige Kombinationen:** 3 (Abgelehnt wegen Stay: 0)

| Reiseschema | Hinflugsdatum & -zeit | Rückflugsdatum & -zeit | Aufenthalt (Std.) | Übernachtungen | Status |
| :--- | :--- | :--- | :---: | :---: | :--- |
| 2026-08-07 → 2026-08-08 | 2026-08-07 17:00 | 2026-08-08 19:05 | 24.6 | 1 | `safe` (>=14:00) |
| 2026-08-07 → 2026-08-09 | 2026-08-07 17:00 | 2026-08-09 19:20 | 48.8 | 2 | `safe` (>=14:00) |
| 2026-08-08 → 2026-08-09 | 2026-08-08 16:55 | 2026-08-09 19:20 | 24.9 | 1 | `safe` (>=14:00) |

## Detaillierte Auflistung je Zielstadt (Gültige Kombinationen)

### Florenz (FLR)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 23 (Verworfen: 2)
- **Schlechteste zulässige Kombination:** Hinflug Air Dolomiti EN 8852 (2026-08-07 07:50) / Rückflug Air Dolomiti EN 8855 (2026-08-09 13:50) - Aufenthalt: 52.3 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Air Dolomiti EN 8854 (2026-08-07 11:10) | Air Dolomiti EN 8855 (2026-08-09 13:50) | 49.0 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8854 (2026-08-07 11:10) | Air Dolomiti EN 8853 (2026-08-09 10:15) | 45.4 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8854 (2026-08-07 11:10) | Air Dolomiti EN 8859 (2026-08-09 19:10) | 54.3 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8854 (2026-08-07 11:10) | Air Dolomiti EN 8861 (2026-08-09 06:30) | 41.7 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8854 (2026-08-07 11:10) | Air Dolomiti EN 8857 (2026-08-09 14:20) | 49.5 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8856 (2026-08-07 12:20) | Air Dolomiti EN 8855 (2026-08-09 13:50) | 47.8 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8856 (2026-08-07 12:20) | Air Dolomiti EN 8853 (2026-08-09 10:15) | 44.2 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8856 (2026-08-07 12:20) | Air Dolomiti EN 8859 (2026-08-09 19:10) | 53.2 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8856 (2026-08-07 12:20) | Air Dolomiti EN 8861 (2026-08-09 06:30) | 40.5 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8856 (2026-08-07 12:20) | Air Dolomiti EN 8857 (2026-08-09 14:20) | 48.3 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8858 (2026-08-07 16:50) | Air Dolomiti EN 8855 (2026-08-09 13:50) | 43.3 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8858 (2026-08-07 16:50) | Air Dolomiti EN 8853 (2026-08-09 10:15) | 39.8 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8858 (2026-08-07 16:50) | Air Dolomiti EN 8859 (2026-08-09 19:10) | 48.7 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8858 (2026-08-07 16:50) | Air Dolomiti EN 8861 (2026-08-09 06:30) | 36.0 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8858 (2026-08-07 16:50) | Air Dolomiti EN 8857 (2026-08-09 14:20) | 43.8 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8852 (2026-08-07 07:50) | Air Dolomiti EN 8855 (2026-08-09 13:50) | 52.3 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8852 (2026-08-07 07:50) | Air Dolomiti EN 8853 (2026-08-09 10:15) | 48.8 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8852 (2026-08-07 07:50) | Air Dolomiti EN 8859 (2026-08-09 19:10) | 57.7 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8852 (2026-08-07 07:50) | Air Dolomiti EN 8861 (2026-08-09 06:30) | 45.0 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8852 (2026-08-07 07:50) | Air Dolomiti EN 8857 (2026-08-09 14:20) | 52.8 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8860 (2026-08-07 21:10) | Air Dolomiti EN 8855 (2026-08-09 13:50) | 39.0 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8860 (2026-08-07 21:10) | Air Dolomiti EN 8859 (2026-08-09 19:10) | 44.3 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8860 (2026-08-07 21:10) | Air Dolomiti EN 8857 (2026-08-09 14:20) | 39.5 | 2 | Akzeptabel ✅ |

---

### Prag (PRG)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 58 (Verworfen: 6)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 1392 (2026-08-07 07:30) / Rückflug Condor DE 4406 (2026-08-09 08:50) - Aufenthalt: 48.3 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Condor DE 4411 (2026-08-07 20:25) | Lufthansa LH 1395 (2026-08-09 11:45) | 38.3 | 2 | Akzeptabel ✅ |
| Condor DE 4411 (2026-08-07 20:25) | Condor DE 4410 (2026-08-09 12:00) | 38.6 | 2 | Akzeptabel ✅ |
| Condor DE 4411 (2026-08-07 20:25) | Condor DE 4408 (2026-08-09 17:00) | 43.6 | 2 | Akzeptabel ✅ |
| Condor DE 4411 (2026-08-07 20:25) | Lufthansa LH 1401 (2026-08-09 18:40) | 45.2 | 2 | Akzeptabel ✅ |
| Condor DE 4411 (2026-08-07 20:25) | Lufthansa LH 1397 (2026-08-09 14:10) | 40.8 | 2 | Akzeptabel ✅ |
| Condor DE 4409 (2026-08-07 09:40) | Condor DE 4406 (2026-08-09 08:50) | 46.0 | 2 | Zu früh ❌ |
| Condor DE 4409 (2026-08-07 09:40) | Lufthansa LH 1395 (2026-08-09 11:45) | 48.9 | 2 | Zu früh ❌ |
| Condor DE 4409 (2026-08-07 09:40) | Condor DE 4410 (2026-08-09 12:00) | 49.2 | 2 | Zu früh ❌ |
| Condor DE 4409 (2026-08-07 09:40) | Condor DE 4408 (2026-08-09 17:00) | 54.2 | 2 | Zu früh ❌ |
| Condor DE 4409 (2026-08-07 09:40) | Lufthansa LH 1393 (2026-08-09 09:10) | 46.3 | 2 | Zu früh ❌ |
| Condor DE 4409 (2026-08-07 09:40) | Lufthansa LH 1401 (2026-08-09 18:40) | 55.8 | 2 | Zu früh ❌ |
| Condor DE 4409 (2026-08-07 09:40) | Lufthansa LH 1403 (2026-08-09 06:10) | 43.3 | 2 | Zu früh ❌ |
| Condor DE 4409 (2026-08-07 09:40) | Lufthansa LH 1397 (2026-08-09 14:10) | 51.3 | 2 | Zu früh ❌ |
| Condor DE 4407 (2026-08-07 15:00) | Condor DE 4406 (2026-08-09 08:50) | 40.8 | 2 | Akzeptabel ✅ |
| Condor DE 4407 (2026-08-07 15:00) | Lufthansa LH 1395 (2026-08-09 11:45) | 43.8 | 2 | Akzeptabel ✅ |
| Condor DE 4407 (2026-08-07 15:00) | Condor DE 4410 (2026-08-09 12:00) | 44.0 | 2 | Akzeptabel ✅ |
| Condor DE 4407 (2026-08-07 15:00) | Condor DE 4408 (2026-08-09 17:00) | 49.0 | 2 | Akzeptabel ✅ |
| Condor DE 4407 (2026-08-07 15:00) | Lufthansa LH 1393 (2026-08-09 09:10) | 41.2 | 2 | Akzeptabel ✅ |
| Condor DE 4407 (2026-08-07 15:00) | Lufthansa LH 1401 (2026-08-09 18:40) | 50.7 | 2 | Akzeptabel ✅ |
| Condor DE 4407 (2026-08-07 15:00) | Lufthansa LH 1403 (2026-08-09 06:10) | 38.2 | 2 | Akzeptabel ✅ |
| Condor DE 4407 (2026-08-07 15:00) | Lufthansa LH 1397 (2026-08-09 14:10) | 46.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Condor DE 4406 (2026-08-09 08:50) | 48.3 | 2 | Zu früh ❌ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Lufthansa LH 1395 (2026-08-09 11:45) | 51.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Condor DE 4410 (2026-08-09 12:00) | 51.5 | 2 | Zu früh ❌ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Condor DE 4408 (2026-08-09 17:00) | 56.5 | 2 | Zu früh ❌ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Lufthansa LH 1393 (2026-08-09 09:10) | 48.7 | 2 | Zu früh ❌ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Lufthansa LH 1401 (2026-08-09 18:40) | 58.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Lufthansa LH 1403 (2026-08-09 06:10) | 45.7 | 2 | Zu früh ❌ |
| Lufthansa LH 1392 (2026-08-07 07:30) | Lufthansa LH 1397 (2026-08-09 14:10) | 53.7 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Condor DE 4406 (2026-08-09 08:50) | 45.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Lufthansa LH 1395 (2026-08-09 11:45) | 48.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Condor DE 4410 (2026-08-09 12:00) | 49.0 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Condor DE 4408 (2026-08-09 17:00) | 54.0 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Lufthansa LH 1393 (2026-08-09 09:10) | 46.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Lufthansa LH 1401 (2026-08-09 18:40) | 55.7 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Lufthansa LH 1403 (2026-08-09 06:10) | 43.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1394 (2026-08-07 10:00) | Lufthansa LH 1397 (2026-08-09 14:10) | 51.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Condor DE 4406 (2026-08-09 08:50) | 43.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Lufthansa LH 1395 (2026-08-09 11:45) | 46.1 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Condor DE 4410 (2026-08-09 12:00) | 46.3 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Condor DE 4408 (2026-08-09 17:00) | 51.3 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Lufthansa LH 1393 (2026-08-09 09:10) | 43.5 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Lufthansa LH 1401 (2026-08-09 18:40) | 53.0 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Lufthansa LH 1403 (2026-08-09 06:10) | 40.5 | 2 | Zu früh ❌ |
| Lufthansa LH 1396 (2026-08-07 12:40) | Lufthansa LH 1397 (2026-08-09 14:10) | 48.5 | 2 | Zu früh ❌ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Condor DE 4406 (2026-08-09 08:50) | 39.1 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Lufthansa LH 1395 (2026-08-09 11:45) | 42.0 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Condor DE 4410 (2026-08-09 12:00) | 42.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Condor DE 4408 (2026-08-09 17:00) | 47.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Lufthansa LH 1393 (2026-08-09 09:10) | 39.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Lufthansa LH 1401 (2026-08-09 18:40) | 48.9 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Lufthansa LH 1403 (2026-08-09 06:10) | 36.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1400 (2026-08-07 16:45) | Lufthansa LH 1397 (2026-08-09 14:10) | 44.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1402 (2026-08-07 22:15) | Lufthansa LH 1395 (2026-08-09 11:45) | 36.5 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1402 (2026-08-07 22:15) | Condor DE 4410 (2026-08-09 12:00) | 36.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1402 (2026-08-07 22:15) | Condor DE 4408 (2026-08-09 17:00) | 41.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1402 (2026-08-07 22:15) | Lufthansa LH 1401 (2026-08-09 18:40) | 43.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1402 (2026-08-07 22:15) | Lufthansa LH 1397 (2026-08-09 14:10) | 38.9 | 2 | Akzeptabel ✅ |

---

### Warschau (WAW)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 36 (Verworfen: 6)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 1346 (2026-08-07 07:10) / Rückflug LOT LO 381 (2026-08-09 07:40) - Aufenthalt: 46.8 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| LOT LO 378 (2026-08-07 17:30) | LOT LO 381 (2026-08-09 07:40) | 36.3 | 2 | Akzeptabel ✅ |
| LOT LO 378 (2026-08-07 17:30) | Lufthansa LH 1351 (2026-08-09 19:10) | 47.8 | 2 | Akzeptabel ✅ |
| LOT LO 378 (2026-08-07 17:30) | Lufthansa LH 1347 (2026-08-09 09:40) | 38.3 | 2 | Akzeptabel ✅ |
| LOT LO 378 (2026-08-07 17:30) | Lufthansa LH 1349 (2026-08-09 14:25) | 43.1 | 2 | Akzeptabel ✅ |
| LOT LO 378 (2026-08-07 17:30) | LOT LO 379 (2026-08-09 17:00) | 45.7 | 2 | Akzeptabel ✅ |
| LOT LO 380 (2026-08-07 19:50) | Lufthansa LH 1351 (2026-08-09 19:10) | 45.6 | 2 | Akzeptabel ✅ |
| LOT LO 380 (2026-08-07 19:50) | Lufthansa LH 1347 (2026-08-09 09:40) | 36.1 | 2 | Akzeptabel ✅ |
| LOT LO 380 (2026-08-07 19:50) | Lufthansa LH 1349 (2026-08-09 14:25) | 40.8 | 2 | Akzeptabel ✅ |
| LOT LO 380 (2026-08-07 19:50) | LOT LO 379 (2026-08-09 17:00) | 43.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1346 (2026-08-07 07:10) | LOT LO 381 (2026-08-09 07:40) | 46.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1346 (2026-08-07 07:10) | Lufthansa LH 1351 (2026-08-09 19:10) | 58.3 | 2 | Zu früh ❌ |
| Lufthansa LH 1346 (2026-08-07 07:10) | Lufthansa LH 1347 (2026-08-09 09:40) | 48.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1346 (2026-08-07 07:10) | Lufthansa LH 1353 (2026-08-09 06:40) | 45.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1346 (2026-08-07 07:10) | Lufthansa LH 1349 (2026-08-09 14:25) | 53.6 | 2 | Zu früh ❌ |
| Lufthansa LH 1346 (2026-08-07 07:10) | LOT LO 379 (2026-08-09 17:00) | 56.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1348 (2026-08-07 11:50) | LOT LO 381 (2026-08-09 07:40) | 42.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1348 (2026-08-07 11:50) | Lufthansa LH 1351 (2026-08-09 19:10) | 53.7 | 2 | Zu früh ❌ |
| Lufthansa LH 1348 (2026-08-07 11:50) | Lufthansa LH 1347 (2026-08-09 09:40) | 44.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1348 (2026-08-07 11:50) | Lufthansa LH 1353 (2026-08-09 06:40) | 41.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1348 (2026-08-07 11:50) | Lufthansa LH 1349 (2026-08-09 14:25) | 48.9 | 2 | Zu früh ❌ |
| Lufthansa LH 1348 (2026-08-07 11:50) | LOT LO 379 (2026-08-09 17:00) | 51.5 | 2 | Zu früh ❌ |
| Lufthansa LH 1350 (2026-08-07 16:40) | LOT LO 381 (2026-08-09 07:40) | 37.3 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1350 (2026-08-07 16:40) | Lufthansa LH 1351 (2026-08-09 19:10) | 48.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1350 (2026-08-07 16:40) | Lufthansa LH 1347 (2026-08-09 09:40) | 39.3 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1350 (2026-08-07 16:40) | Lufthansa LH 1353 (2026-08-09 06:40) | 36.3 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1350 (2026-08-07 16:40) | Lufthansa LH 1349 (2026-08-09 14:25) | 44.1 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1350 (2026-08-07 16:40) | LOT LO 379 (2026-08-09 17:00) | 46.7 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1352 (2026-08-07 20:45) | Lufthansa LH 1351 (2026-08-09 19:10) | 44.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1352 (2026-08-07 20:45) | Lufthansa LH 1349 (2026-08-09 14:25) | 40.0 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1352 (2026-08-07 20:45) | LOT LO 379 (2026-08-09 17:00) | 42.6 | 2 | Akzeptabel ✅ |
| LOT LO 382 (2026-08-07 10:35) | LOT LO 381 (2026-08-09 07:40) | 43.2 | 2 | Zu früh ❌ |
| LOT LO 382 (2026-08-07 10:35) | Lufthansa LH 1351 (2026-08-09 19:10) | 54.8 | 2 | Zu früh ❌ |
| LOT LO 382 (2026-08-07 10:35) | Lufthansa LH 1347 (2026-08-09 09:40) | 45.2 | 2 | Zu früh ❌ |
| LOT LO 382 (2026-08-07 10:35) | Lufthansa LH 1353 (2026-08-09 06:40) | 42.2 | 2 | Zu früh ❌ |
| LOT LO 382 (2026-08-07 10:35) | Lufthansa LH 1349 (2026-08-09 14:25) | 50.0 | 2 | Zu früh ❌ |
| LOT LO 382 (2026-08-07 10:35) | LOT LO 379 (2026-08-09 17:00) | 52.6 | 2 | Zu früh ❌ |

---

### Breslau (WRO)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 8 (Verworfen: 1)
- **Schlechteste zulässige Kombination:** Hinflug Air Dolomiti EN 8766 (2026-08-07 08:20) / Rückflug Lufthansa LH 1377 (2026-08-09 06:25) - Aufenthalt: 44.7 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Air Dolomiti EN 8766 (2026-08-07 08:20) | Lufthansa LH 1377 (2026-08-09 06:25) | 44.7 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8766 (2026-08-07 08:20) | Air Dolomiti EN 8767 (2026-08-09 10:30) | 48.8 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8766 (2026-08-07 08:20) | Lufthansa LH 1375 (2026-08-09 14:40) | 52.9 | 2 | Zu früh ❌ |
| Lufthansa LH 1374 (2026-08-07 12:50) | Lufthansa LH 1377 (2026-08-09 06:25) | 40.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1374 (2026-08-07 12:50) | Air Dolomiti EN 8767 (2026-08-09 10:30) | 44.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1374 (2026-08-07 12:50) | Lufthansa LH 1375 (2026-08-09 14:40) | 48.4 | 2 | Zu früh ❌ |
| Lufthansa LH 1376 (2026-08-07 20:30) | Air Dolomiti EN 8767 (2026-08-09 10:30) | 36.6 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1376 (2026-08-07 20:30) | Lufthansa LH 1375 (2026-08-09 14:40) | 40.8 | 2 | Akzeptabel ✅ |

---

### Helsinki (HEL)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 16 (Verworfen: 4)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 848 (2026-08-07 09:35) / Rückflug Finnair AY 1411 (2026-08-09 07:40) - Aufenthalt: 42.6 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Finnair AY 1416 (2026-08-07 19:20) | Lufthansa City Airlines VL 849 (2026-08-09 13:45) | 39.0 | 2 | Akzeptabel ✅ |
| Finnair AY 1416 (2026-08-07 19:20) | Lufthansa City Airlines VL 851 (2026-08-09 18:15) | 43.5 | 2 | Akzeptabel ✅ |
| Lufthansa LH 848 (2026-08-07 09:35) | Finnair AY 1411 (2026-08-09 07:40) | 42.6 | 2 | Zu früh ❌ |
| Lufthansa LH 848 (2026-08-07 09:35) | Lufthansa City Airlines VL 853 (2026-08-09 06:45) | 41.7 | 2 | Zu früh ❌ |
| Lufthansa LH 848 (2026-08-07 09:35) | Lufthansa City Airlines VL 849 (2026-08-09 13:45) | 48.7 | 2 | Zu früh ❌ |
| Lufthansa LH 848 (2026-08-07 09:35) | Lufthansa City Airlines VL 851 (2026-08-09 18:15) | 53.2 | 2 | Zu früh ❌ |
| Lufthansa LH 852 (2026-08-07 21:10) | Lufthansa City Airlines VL 849 (2026-08-09 13:45) | 37.1 | 2 | Akzeptabel ✅ |
| Lufthansa LH 852 (2026-08-07 21:10) | Lufthansa City Airlines VL 851 (2026-08-09 18:15) | 41.6 | 2 | Akzeptabel ✅ |
| Lufthansa City Airlines VL 850 (2026-08-07 13:40) | Finnair AY 1411 (2026-08-09 07:40) | 38.5 | 2 | Zu früh ❌ |
| Lufthansa City Airlines VL 850 (2026-08-07 13:40) | Lufthansa City Airlines VL 853 (2026-08-09 06:45) | 37.6 | 2 | Zu früh ❌ |
| Lufthansa City Airlines VL 850 (2026-08-07 13:40) | Lufthansa City Airlines VL 849 (2026-08-09 13:45) | 44.6 | 2 | Zu früh ❌ |
| Lufthansa City Airlines VL 850 (2026-08-07 13:40) | Lufthansa City Airlines VL 851 (2026-08-09 18:15) | 49.1 | 2 | Zu früh ❌ |
| Finnair AY 1412 (2026-08-07 11:30) | Finnair AY 1411 (2026-08-09 07:40) | 40.8 | 2 | Zu früh ❌ |
| Finnair AY 1412 (2026-08-07 11:30) | Lufthansa City Airlines VL 853 (2026-08-09 06:45) | 39.8 | 2 | Zu früh ❌ |
| Finnair AY 1412 (2026-08-07 11:30) | Lufthansa City Airlines VL 849 (2026-08-09 13:45) | 46.8 | 2 | Zu früh ❌ |
| Finnair AY 1412 (2026-08-07 11:30) | Lufthansa City Airlines VL 851 (2026-08-09 18:15) | 51.3 | 2 | Zu früh ❌ |

---

### Bologna (BLQ)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 11 (Verworfen: 1)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 282 (2026-08-07 08:20) / Rückflug Lufthansa LH 287 (2026-08-09 18:30) - Aufenthalt: 56.7 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Lufthansa LH 282 (2026-08-07 08:20) | Lufthansa LH 287 (2026-08-09 18:30) | 56.7 | 2 | Zu früh ❌ |
| Lufthansa LH 282 (2026-08-07 08:20) | Air Dolomiti EN 8885 (2026-08-09 06:10) | 44.3 | 2 | Zu früh ❌ |
| Lufthansa LH 282 (2026-08-07 08:20) | Air Dolomiti EN 8881 (2026-08-09 14:45) | 52.9 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8880 (2026-08-07 12:30) | Lufthansa LH 287 (2026-08-09 18:30) | 52.5 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8880 (2026-08-07 12:30) | Air Dolomiti EN 8885 (2026-08-09 06:10) | 40.2 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8880 (2026-08-07 12:30) | Air Dolomiti EN 8881 (2026-08-09 14:45) | 48.8 | 2 | Zu früh ❌ |
| Lufthansa LH 286 (2026-08-07 16:20) | Lufthansa LH 287 (2026-08-09 18:30) | 48.7 | 2 | Akzeptabel ✅ |
| Lufthansa LH 286 (2026-08-07 16:20) | Air Dolomiti EN 8885 (2026-08-09 06:10) | 36.3 | 2 | Akzeptabel ✅ |
| Lufthansa LH 286 (2026-08-07 16:20) | Air Dolomiti EN 8881 (2026-08-09 14:45) | 44.9 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8884 (2026-08-07 22:10) | Lufthansa LH 287 (2026-08-09 18:30) | 42.8 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8884 (2026-08-07 22:10) | Air Dolomiti EN 8881 (2026-08-09 14:45) | 39.1 | 2 | Akzeptabel ✅ |

---

### Krakau (KRK)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 13 (Verworfen: 3)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 1362 (2026-08-07 09:00) / Rückflug Lufthansa LH 1371 (2026-08-09 06:00) - Aufenthalt: 43.4 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Lufthansa LH 1362 (2026-08-07 09:00) | Lufthansa LH 1371 (2026-08-09 06:00) | 43.4 | 2 | Zu früh ❌ |
| Lufthansa LH 1362 (2026-08-07 09:00) | Lufthansa LH 1369 (2026-08-09 19:30) | 56.9 | 2 | Zu früh ❌ |
| Lufthansa LH 1362 (2026-08-07 09:00) | Lufthansa LH 1363 (2026-08-09 11:10) | 48.6 | 2 | Zu früh ❌ |
| Lufthansa LH 1362 (2026-08-07 09:00) | Lufthansa LH 1365 (2026-08-09 13:20) | 50.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1368 (2026-08-07 17:00) | Lufthansa LH 1369 (2026-08-09 19:30) | 48.9 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1368 (2026-08-07 17:00) | Lufthansa LH 1363 (2026-08-09 11:10) | 40.6 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1368 (2026-08-07 17:00) | Lufthansa LH 1365 (2026-08-09 13:20) | 42.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1370 (2026-08-07 22:15) | Lufthansa LH 1369 (2026-08-09 19:30) | 43.7 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1370 (2026-08-07 22:15) | Lufthansa LH 1365 (2026-08-09 13:20) | 37.5 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1364 (2026-08-07 10:40) | Lufthansa LH 1371 (2026-08-09 06:00) | 41.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1364 (2026-08-07 10:40) | Lufthansa LH 1369 (2026-08-09 19:30) | 55.2 | 2 | Zu früh ❌ |
| Lufthansa LH 1364 (2026-08-07 10:40) | Lufthansa LH 1363 (2026-08-09 11:10) | 46.9 | 2 | Zu früh ❌ |
| Lufthansa LH 1364 (2026-08-07 10:40) | Lufthansa LH 1365 (2026-08-09 13:20) | 49.1 | 2 | Zu früh ❌ |

---

### Basel (BSL)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 8 (Verworfen: 1)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 1202 (2026-08-07 09:35) / Rückflug Lufthansa LH 1203 (2026-08-09 11:00) - Aufenthalt: 48.4 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Lufthansa LH 1202 (2026-08-07 09:35) | Lufthansa LH 1203 (2026-08-09 11:00) | 48.4 | 2 | Zu früh ❌ |
| Lufthansa LH 1202 (2026-08-07 09:35) | Lufthansa LH 1205 (2026-08-09 14:40) | 52.1 | 2 | Zu früh ❌ |
| Lufthansa LH 1202 (2026-08-07 09:35) | Lufthansa LH 1209 (2026-08-09 06:00) | 43.4 | 2 | Zu früh ❌ |
| Lufthansa LH 1204 (2026-08-07 12:55) | Lufthansa LH 1203 (2026-08-09 11:00) | 45.1 | 2 | Zu früh ❌ |
| Lufthansa LH 1204 (2026-08-07 12:55) | Lufthansa LH 1205 (2026-08-09 14:40) | 48.8 | 2 | Zu früh ❌ |
| Lufthansa LH 1204 (2026-08-07 12:55) | Lufthansa LH 1209 (2026-08-09 06:00) | 40.1 | 2 | Zu früh ❌ |
| Lufthansa LH 1208 (2026-08-07 22:00) | Lufthansa LH 1203 (2026-08-09 11:00) | 36.0 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1208 (2026-08-07 22:00) | Lufthansa LH 1205 (2026-08-09 14:40) | 39.7 | 2 | Akzeptabel ✅ |

---

### Sarajevo (SJJ)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 3 (Verworfen: 1)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 1544 (2026-08-07 10:10) / Rückflug Lufthansa LH 1545 (2026-08-09 11:25) - Aufenthalt: 47.5 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| Lufthansa LH 1546 (2026-08-07 20:25) | Lufthansa LH 1545 (2026-08-09 11:25) | 37.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 1544 (2026-08-07 10:10) | Lufthansa LH 1545 (2026-08-09 11:25) | 47.5 | 2 | Zu früh ❌ |
| Lufthansa LH 1544 (2026-08-07 10:10) | Lufthansa LH 1547 (2026-08-09 06:15) | 42.3 | 2 | Zu früh ❌ |

---

### Mailand (Linate) (LIN)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (1 Nacht / 2 Nächte):** 0 / 95 (Verworfen: 4)
- **Schlechteste zulässige Kombination:** Hinflug Lufthansa LH 246 (2026-08-07 06:55) / Rückflug Lufthansa LH 275 (2026-08-09 15:20) - Aufenthalt: 55.1 Std. (Nächte: 2)

| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |
| :--- | :--- | :---: | :---: | :--- |
| easyJet U2 5404 (2026-08-07 09:10) | Lufthansa LH 275 (2026-08-09 15:20) | 53.0 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | easyJet U2 5403 (2026-08-09 07:00) | 44.7 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | Lufthansa LH 279 (2026-08-09 19:40) | 57.3 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | easyJet U2 5427 (2026-08-09 18:10) | 55.8 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | Lufthansa LH 273 (2026-08-09 12:40) | 50.3 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 48.2 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | Lufthansa LH 247 (2026-08-09 09:00) | 46.7 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | Lufthansa LH 249 (2026-08-09 11:20) | 49.0 | 2 | Zu früh ❌ |
| easyJet U2 5404 (2026-08-07 09:10) | Lufthansa LH 255 (2026-08-09 18:50) | 56.5 | 2 | Zu früh ❌ |
| easyJet U2 5428 (2026-08-07 20:10) | Lufthansa LH 275 (2026-08-09 15:20) | 42.0 | 2 | Akzeptabel ✅ |
| easyJet U2 5428 (2026-08-07 20:10) | Lufthansa LH 279 (2026-08-09 19:40) | 46.3 | 2 | Akzeptabel ✅ |
| easyJet U2 5428 (2026-08-07 20:10) | easyJet U2 5427 (2026-08-09 18:10) | 44.8 | 2 | Akzeptabel ✅ |
| easyJet U2 5428 (2026-08-07 20:10) | Lufthansa LH 273 (2026-08-09 12:40) | 39.3 | 2 | Akzeptabel ✅ |
| easyJet U2 5428 (2026-08-07 20:10) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 37.2 | 2 | Akzeptabel ✅ |
| easyJet U2 5428 (2026-08-07 20:10) | Lufthansa LH 249 (2026-08-09 11:20) | 38.0 | 2 | Akzeptabel ✅ |
| easyJet U2 5428 (2026-08-07 20:10) | Lufthansa LH 255 (2026-08-09 18:50) | 45.5 | 2 | Akzeptabel ✅ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | Lufthansa LH 275 (2026-08-09 15:20) | 53.3 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | easyJet U2 5403 (2026-08-09 07:00) | 45.0 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | Lufthansa LH 279 (2026-08-09 19:40) | 57.7 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | easyJet U2 5427 (2026-08-09 18:10) | 56.2 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | Lufthansa LH 273 (2026-08-09 12:40) | 50.7 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 48.5 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | Lufthansa LH 247 (2026-08-09 09:00) | 47.0 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | Lufthansa LH 249 (2026-08-09 11:20) | 49.3 | 2 | Zu früh ❌ |
| Air Dolomiti EN 8800 (2026-08-07 08:45) | Lufthansa LH 255 (2026-08-09 18:50) | 56.8 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | Lufthansa LH 275 (2026-08-09 15:20) | 48.7 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | easyJet U2 5403 (2026-08-09 07:00) | 40.3 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | Lufthansa LH 279 (2026-08-09 19:40) | 53.0 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | easyJet U2 5427 (2026-08-09 18:10) | 51.5 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | Lufthansa LH 273 (2026-08-09 12:40) | 46.0 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 43.8 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | Lufthansa LH 247 (2026-08-09 09:00) | 42.3 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | Lufthansa LH 249 (2026-08-09 11:20) | 44.7 | 2 | Zu früh ❌ |
| Lufthansa LH 274 (2026-08-07 13:25) | Lufthansa LH 255 (2026-08-09 18:50) | 52.2 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | Lufthansa LH 275 (2026-08-09 15:20) | 51.3 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | easyJet U2 5403 (2026-08-09 07:00) | 43.0 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | Lufthansa LH 279 (2026-08-09 19:40) | 55.7 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | easyJet U2 5427 (2026-08-09 18:10) | 54.2 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | Lufthansa LH 273 (2026-08-09 12:40) | 48.7 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 46.5 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | Lufthansa LH 247 (2026-08-09 09:00) | 45.0 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | Lufthansa LH 249 (2026-08-09 11:20) | 47.3 | 2 | Zu früh ❌ |
| Lufthansa LH 272 (2026-08-07 10:45) | Lufthansa LH 255 (2026-08-09 18:50) | 54.8 | 2 | Zu früh ❌ |
| Lufthansa LH 276 (2026-08-07 16:15) | Lufthansa LH 275 (2026-08-09 15:20) | 45.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | easyJet U2 5403 (2026-08-09 07:00) | 37.5 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | Lufthansa LH 279 (2026-08-09 19:40) | 50.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | easyJet U2 5427 (2026-08-09 18:10) | 48.7 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | Lufthansa LH 273 (2026-08-09 12:40) | 43.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 41.0 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | Lufthansa LH 247 (2026-08-09 09:00) | 39.5 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | Lufthansa LH 249 (2026-08-09 11:20) | 41.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 276 (2026-08-07 16:15) | Lufthansa LH 255 (2026-08-09 18:50) | 49.3 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | Lufthansa LH 275 (2026-08-09 15:20) | 44.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | easyJet U2 5403 (2026-08-09 07:00) | 36.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | Lufthansa LH 279 (2026-08-09 19:40) | 49.1 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | easyJet U2 5427 (2026-08-09 18:10) | 47.6 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | Lufthansa LH 273 (2026-08-09 12:40) | 42.1 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 39.9 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | Lufthansa LH 247 (2026-08-09 09:00) | 38.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | Lufthansa LH 249 (2026-08-09 11:20) | 40.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 278 (2026-08-07 17:20) | Lufthansa LH 255 (2026-08-09 18:50) | 48.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 280 (2026-08-07 20:50) | Lufthansa LH 275 (2026-08-09 15:20) | 41.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 280 (2026-08-07 20:50) | Lufthansa LH 279 (2026-08-09 19:40) | 45.6 | 2 | Akzeptabel ✅ |
| Lufthansa LH 280 (2026-08-07 20:50) | easyJet U2 5427 (2026-08-09 18:10) | 44.1 | 2 | Akzeptabel ✅ |
| Lufthansa LH 280 (2026-08-07 20:50) | Lufthansa LH 273 (2026-08-09 12:40) | 38.6 | 2 | Akzeptabel ✅ |
| Lufthansa LH 280 (2026-08-07 20:50) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 36.4 | 2 | Akzeptabel ✅ |
| Lufthansa LH 280 (2026-08-07 20:50) | Lufthansa LH 249 (2026-08-09 11:20) | 37.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 280 (2026-08-07 20:50) | Lufthansa LH 255 (2026-08-09 18:50) | 44.8 | 2 | Akzeptabel ✅ |
| Lufthansa LH 246 (2026-08-07 06:55) | Lufthansa LH 275 (2026-08-09 15:20) | 55.1 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | easyJet U2 5403 (2026-08-09 07:00) | 46.8 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | Lufthansa LH 279 (2026-08-09 19:40) | 59.4 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | easyJet U2 5427 (2026-08-09 18:10) | 57.9 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | Lufthansa LH 273 (2026-08-09 12:40) | 52.4 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 50.2 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | Lufthansa LH 247 (2026-08-09 09:00) | 48.8 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | Lufthansa LH 249 (2026-08-09 11:20) | 51.1 | 2 | Zu früh ❌ |
| Lufthansa LH 246 (2026-08-07 06:55) | Lufthansa LH 255 (2026-08-09 18:50) | 58.6 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | Lufthansa LH 275 (2026-08-09 15:20) | 52.8 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | easyJet U2 5403 (2026-08-09 07:00) | 44.4 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | Lufthansa LH 279 (2026-08-09 19:40) | 57.1 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | easyJet U2 5427 (2026-08-09 18:10) | 55.6 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | Lufthansa LH 273 (2026-08-09 12:40) | 50.1 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 47.9 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | Lufthansa LH 247 (2026-08-09 09:00) | 46.4 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | Lufthansa LH 249 (2026-08-09 11:20) | 48.8 | 2 | Zu früh ❌ |
| Lufthansa LH 248 (2026-08-07 09:15) | Lufthansa LH 255 (2026-08-09 18:50) | 56.2 | 2 | Zu früh ❌ |
| Lufthansa LH 254 (2026-08-07 16:40) | Lufthansa LH 275 (2026-08-09 15:20) | 45.3 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | easyJet U2 5403 (2026-08-09 07:00) | 37.0 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | Lufthansa LH 279 (2026-08-09 19:40) | 49.7 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | easyJet U2 5427 (2026-08-09 18:10) | 48.2 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | Lufthansa LH 273 (2026-08-09 12:40) | 42.7 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | Air Dolomiti EN 8801 (2026-08-09 10:30) | 40.5 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | Lufthansa LH 247 (2026-08-09 09:00) | 39.0 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | Lufthansa LH 249 (2026-08-09 11:20) | 41.3 | 2 | Akzeptabel ✅ |
| Lufthansa LH 254 (2026-08-07 16:40) | Lufthansa LH 255 (2026-08-09 18:50) | 48.8 | 2 | Akzeptabel ✅ |

---

