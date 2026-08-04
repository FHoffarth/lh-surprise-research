# Lufthansa Surprise: Itinerary-Based Schedule Risk Report

**Reisedatum:** 07.08.2026 - 09.08.2026  
**Abflughafen:** Frankfurt/Main (FRA)  
**Nutzerprofil:** earliest_acceptable_outbound = 14:00 | outbound_risk_policy = reject_if_any_plausible_direct_flight_is_too_early  
**Mailand-Verifikation:** LIN wird laut Surprise-UI explizit als Ziel-Airport verwendet. MXP/BGY wurden vorschriftsmäßig ausgeschlossen.

## Ziele, die nach der 14:00-Uhr-Risikoregel verbleiben (KEEP)

- **Pula**

## Übersicht der Zielrangfolge & Risikoauswertung

| Zielstadt | IATA | Risiko-Klassifikation | Kombinationen (Gesamt / Gültig) | Hinflugsfenster (Gültig) | Entscheidung | Begründung |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| Florenz | FLR | `mixed` | 25 / 23 | 07:50 - 21:10 | **EXCLUDE** | Mixed schedule: 8 acceptable valid itineraries, but 15 depart before 14:00 Uhr. |
| Prag | PRG | `mixed` | 64 / 58 | 07:30 - 22:15 | **EXCLUDE** | Mixed schedule: 26 acceptable valid itineraries, but 32 depart before 14:00 Uhr. |
| Warschau | WAW | `mixed` | 42 / 36 | 07:10 - 20:45 | **EXCLUDE** | Mixed schedule: 18 acceptable valid itineraries, but 18 depart before 14:00 Uhr. |
| Krakau | KRK | `mixed` | 16 / 13 | 09:00 - 22:15 | **EXCLUDE** | Mixed schedule: 5 acceptable valid itineraries, but 8 depart before 14:00 Uhr. |
| Bologna | BLQ | `mixed` | 12 / 11 | 08:20 - 22:10 | **EXCLUDE** | Mixed schedule: 5 acceptable valid itineraries, but 6 depart before 14:00 Uhr. |
| Helsinki | HEL | `mixed` | 20 / 16 | 09:35 - 21:10 | **EXCLUDE** | Mixed schedule: 4 acceptable valid itineraries, but 12 depart before 14:00 Uhr. |
| Breslau | WRO | `mixed` | 9 / 8 | 08:20 - 20:30 | **EXCLUDE** | Mixed schedule: 2 acceptable valid itineraries, but 6 depart before 14:00 Uhr. |
| Basel | BSL | `mixed` | 9 / 8 | 09:35 - 22:00 | **EXCLUDE** | Mixed schedule: 2 acceptable valid itineraries, but 6 depart before 14:00 Uhr. |
| Sarajevo | SJJ | `mixed` | 4 / 3 | 10:10 - 20:25 | **EXCLUDE** | Mixed schedule: 1 acceptable valid itineraries, but 2 depart before 14:00 Uhr. |
| Pula | PUY | `safe` | 1 / 1 | 17:00 - 17:00 | **KEEP** | All 1 valid itinerary combination(s) depart at or after 14:00 Uhr. |
| Mailand (Linate) | LIN | `mixed` | 99 / 95 | 06:55 - 20:50 | **EXCLUDE** | Mixed schedule: 41 acceptable valid itineraries, but 54 depart before 14:00 Uhr. |

## Detaillierte Auswertung je Zielstadt (Gültige Kombinationen)

### Florenz (FLR)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 25 / 23
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Air Dolomiti EN 8852 (07:50) / Rückflug Air Dolomiti EN 8855 (13:50) - Aufenthalt: 52.3 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Air Dolomiti EN 8854 (11:10) | Air Dolomiti EN 8855 (13:50) | 49.0 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8854 (11:10) | Air Dolomiti EN 8853 (10:15) | 45.4 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8854 (11:10) | Air Dolomiti EN 8859 (19:10) | 54.3 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8854 (11:10) | Air Dolomiti EN 8861 (06:30) | 41.7 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8854 (11:10) | Air Dolomiti EN 8857 (14:20) | 49.5 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8856 (12:20) | Air Dolomiti EN 8855 (13:50) | 47.8 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8856 (12:20) | Air Dolomiti EN 8853 (10:15) | 44.2 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8856 (12:20) | Air Dolomiti EN 8859 (19:10) | 53.2 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8856 (12:20) | Air Dolomiti EN 8861 (06:30) | 40.5 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8856 (12:20) | Air Dolomiti EN 8857 (14:20) | 48.3 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8858 (16:50) | Air Dolomiti EN 8855 (13:50) | 43.3 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8858 (16:50) | Air Dolomiti EN 8853 (10:15) | 39.8 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8858 (16:50) | Air Dolomiti EN 8859 (19:10) | 48.7 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8858 (16:50) | Air Dolomiti EN 8861 (06:30) | 36.0 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8858 (16:50) | Air Dolomiti EN 8857 (14:20) | 43.8 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8852 (07:50) | Air Dolomiti EN 8855 (13:50) | 52.3 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8852 (07:50) | Air Dolomiti EN 8853 (10:15) | 48.8 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8852 (07:50) | Air Dolomiti EN 8859 (19:10) | 57.7 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8852 (07:50) | Air Dolomiti EN 8861 (06:30) | 45.0 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8852 (07:50) | Air Dolomiti EN 8857 (14:20) | 52.8 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8860 (21:10) | Air Dolomiti EN 8855 (13:50) | 39.0 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8860 (21:10) | Air Dolomiti EN 8859 (19:10) | 44.3 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8860 (21:10) | Air Dolomiti EN 8857 (14:20) | 39.5 | Akzeptabel (>= 14:00) |

---

### Prag (PRG)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 64 / 58
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 1392 (07:30) / Rückflug Condor DE 4406 (08:50) - Aufenthalt: 48.3 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Condor DE 4411 (20:25) | Lufthansa LH 1395 (11:45) | 38.3 | Akzeptabel (>= 14:00) |
| Condor DE 4411 (20:25) | Condor DE 4410 (12:00) | 38.6 | Akzeptabel (>= 14:00) |
| Condor DE 4411 (20:25) | Condor DE 4408 (17:00) | 43.6 | Akzeptabel (>= 14:00) |
| Condor DE 4411 (20:25) | Lufthansa LH 1401 (18:40) | 45.2 | Akzeptabel (>= 14:00) |
| Condor DE 4411 (20:25) | Lufthansa LH 1397 (14:10) | 40.8 | Akzeptabel (>= 14:00) |
| Condor DE 4409 (09:40) | Condor DE 4406 (08:50) | 46.0 | Zu früh (< 14:00) ❌ |
| Condor DE 4409 (09:40) | Lufthansa LH 1395 (11:45) | 48.9 | Zu früh (< 14:00) ❌ |
| Condor DE 4409 (09:40) | Condor DE 4410 (12:00) | 49.2 | Zu früh (< 14:00) ❌ |
| Condor DE 4409 (09:40) | Condor DE 4408 (17:00) | 54.2 | Zu früh (< 14:00) ❌ |
| Condor DE 4409 (09:40) | Lufthansa LH 1393 (09:10) | 46.3 | Zu früh (< 14:00) ❌ |
| Condor DE 4409 (09:40) | Lufthansa LH 1401 (18:40) | 55.8 | Zu früh (< 14:00) ❌ |
| Condor DE 4409 (09:40) | Lufthansa LH 1403 (06:10) | 43.3 | Zu früh (< 14:00) ❌ |
| Condor DE 4409 (09:40) | Lufthansa LH 1397 (14:10) | 51.3 | Zu früh (< 14:00) ❌ |
| Condor DE 4407 (15:00) | Condor DE 4406 (08:50) | 40.8 | Akzeptabel (>= 14:00) |
| Condor DE 4407 (15:00) | Lufthansa LH 1395 (11:45) | 43.8 | Akzeptabel (>= 14:00) |
| Condor DE 4407 (15:00) | Condor DE 4410 (12:00) | 44.0 | Akzeptabel (>= 14:00) |
| Condor DE 4407 (15:00) | Condor DE 4408 (17:00) | 49.0 | Akzeptabel (>= 14:00) |
| Condor DE 4407 (15:00) | Lufthansa LH 1393 (09:10) | 41.2 | Akzeptabel (>= 14:00) |
| Condor DE 4407 (15:00) | Lufthansa LH 1401 (18:40) | 50.7 | Akzeptabel (>= 14:00) |
| Condor DE 4407 (15:00) | Lufthansa LH 1403 (06:10) | 38.2 | Akzeptabel (>= 14:00) |
| Condor DE 4407 (15:00) | Lufthansa LH 1397 (14:10) | 46.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1392 (07:30) | Condor DE 4406 (08:50) | 48.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1392 (07:30) | Lufthansa LH 1395 (11:45) | 51.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1392 (07:30) | Condor DE 4410 (12:00) | 51.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1392 (07:30) | Condor DE 4408 (17:00) | 56.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1392 (07:30) | Lufthansa LH 1393 (09:10) | 48.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1392 (07:30) | Lufthansa LH 1401 (18:40) | 58.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1392 (07:30) | Lufthansa LH 1403 (06:10) | 45.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1392 (07:30) | Lufthansa LH 1397 (14:10) | 53.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Condor DE 4406 (08:50) | 45.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Lufthansa LH 1395 (11:45) | 48.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Condor DE 4410 (12:00) | 49.0 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Condor DE 4408 (17:00) | 54.0 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Lufthansa LH 1393 (09:10) | 46.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Lufthansa LH 1401 (18:40) | 55.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Lufthansa LH 1403 (06:10) | 43.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1394 (10:00) | Lufthansa LH 1397 (14:10) | 51.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Condor DE 4406 (08:50) | 43.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Lufthansa LH 1395 (11:45) | 46.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Condor DE 4410 (12:00) | 46.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Condor DE 4408 (17:00) | 51.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Lufthansa LH 1393 (09:10) | 43.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Lufthansa LH 1401 (18:40) | 53.0 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Lufthansa LH 1403 (06:10) | 40.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1396 (12:40) | Lufthansa LH 1397 (14:10) | 48.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1400 (16:45) | Condor DE 4406 (08:50) | 39.1 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1400 (16:45) | Lufthansa LH 1395 (11:45) | 42.0 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1400 (16:45) | Condor DE 4410 (12:00) | 42.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1400 (16:45) | Condor DE 4408 (17:00) | 47.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1400 (16:45) | Lufthansa LH 1393 (09:10) | 39.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1400 (16:45) | Lufthansa LH 1401 (18:40) | 48.9 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1400 (16:45) | Lufthansa LH 1403 (06:10) | 36.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1400 (16:45) | Lufthansa LH 1397 (14:10) | 44.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1402 (22:15) | Lufthansa LH 1395 (11:45) | 36.5 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1402 (22:15) | Condor DE 4410 (12:00) | 36.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1402 (22:15) | Condor DE 4408 (17:00) | 41.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1402 (22:15) | Lufthansa LH 1401 (18:40) | 43.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1402 (22:15) | Lufthansa LH 1397 (14:10) | 38.9 | Akzeptabel (>= 14:00) |

---

### Warschau (WAW)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 42 / 36
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 1346 (07:10) / Rückflug LOT LO 381 (07:40) - Aufenthalt: 46.8 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| LOT LO 378 (17:30) | LOT LO 381 (07:40) | 36.3 | Akzeptabel (>= 14:00) |
| LOT LO 378 (17:30) | Lufthansa LH 1351 (19:10) | 47.8 | Akzeptabel (>= 14:00) |
| LOT LO 378 (17:30) | Lufthansa LH 1347 (09:40) | 38.3 | Akzeptabel (>= 14:00) |
| LOT LO 378 (17:30) | Lufthansa LH 1349 (14:25) | 43.1 | Akzeptabel (>= 14:00) |
| LOT LO 378 (17:30) | LOT LO 379 (17:00) | 45.7 | Akzeptabel (>= 14:00) |
| LOT LO 380 (19:50) | Lufthansa LH 1351 (19:10) | 45.6 | Akzeptabel (>= 14:00) |
| LOT LO 380 (19:50) | Lufthansa LH 1347 (09:40) | 36.1 | Akzeptabel (>= 14:00) |
| LOT LO 380 (19:50) | Lufthansa LH 1349 (14:25) | 40.8 | Akzeptabel (>= 14:00) |
| LOT LO 380 (19:50) | LOT LO 379 (17:00) | 43.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1346 (07:10) | LOT LO 381 (07:40) | 46.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1346 (07:10) | Lufthansa LH 1351 (19:10) | 58.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1346 (07:10) | Lufthansa LH 1347 (09:40) | 48.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1346 (07:10) | Lufthansa LH 1353 (06:40) | 45.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1346 (07:10) | Lufthansa LH 1349 (14:25) | 53.6 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1346 (07:10) | LOT LO 379 (17:00) | 56.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1348 (11:50) | LOT LO 381 (07:40) | 42.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1348 (11:50) | Lufthansa LH 1351 (19:10) | 53.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1348 (11:50) | Lufthansa LH 1347 (09:40) | 44.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1348 (11:50) | Lufthansa LH 1353 (06:40) | 41.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1348 (11:50) | Lufthansa LH 1349 (14:25) | 48.9 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1348 (11:50) | LOT LO 379 (17:00) | 51.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1350 (16:40) | LOT LO 381 (07:40) | 37.3 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1350 (16:40) | Lufthansa LH 1351 (19:10) | 48.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1350 (16:40) | Lufthansa LH 1347 (09:40) | 39.3 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1350 (16:40) | Lufthansa LH 1353 (06:40) | 36.3 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1350 (16:40) | Lufthansa LH 1349 (14:25) | 44.1 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1350 (16:40) | LOT LO 379 (17:00) | 46.7 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1352 (20:45) | Lufthansa LH 1351 (19:10) | 44.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1352 (20:45) | Lufthansa LH 1349 (14:25) | 40.0 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1352 (20:45) | LOT LO 379 (17:00) | 42.6 | Akzeptabel (>= 14:00) |
| LOT LO 382 (10:35) | LOT LO 381 (07:40) | 43.2 | Zu früh (< 14:00) ❌ |
| LOT LO 382 (10:35) | Lufthansa LH 1351 (19:10) | 54.8 | Zu früh (< 14:00) ❌ |
| LOT LO 382 (10:35) | Lufthansa LH 1347 (09:40) | 45.2 | Zu früh (< 14:00) ❌ |
| LOT LO 382 (10:35) | Lufthansa LH 1353 (06:40) | 42.2 | Zu früh (< 14:00) ❌ |
| LOT LO 382 (10:35) | Lufthansa LH 1349 (14:25) | 50.0 | Zu früh (< 14:00) ❌ |
| LOT LO 382 (10:35) | LOT LO 379 (17:00) | 52.6 | Zu früh (< 14:00) ❌ |

---

### Krakau (KRK)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 16 / 13
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 1362 (09:00) / Rückflug Lufthansa LH 1371 (06:00) - Aufenthalt: 43.4 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Lufthansa LH 1362 (09:00) | Lufthansa LH 1371 (06:00) | 43.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1362 (09:00) | Lufthansa LH 1369 (19:30) | 56.9 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1362 (09:00) | Lufthansa LH 1363 (11:10) | 48.6 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1362 (09:00) | Lufthansa LH 1365 (13:20) | 50.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1368 (17:00) | Lufthansa LH 1369 (19:30) | 48.9 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1368 (17:00) | Lufthansa LH 1363 (11:10) | 40.6 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1368 (17:00) | Lufthansa LH 1365 (13:20) | 42.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1370 (22:15) | Lufthansa LH 1369 (19:30) | 43.7 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1370 (22:15) | Lufthansa LH 1365 (13:20) | 37.5 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1364 (10:40) | Lufthansa LH 1371 (06:00) | 41.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1364 (10:40) | Lufthansa LH 1369 (19:30) | 55.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1364 (10:40) | Lufthansa LH 1363 (11:10) | 46.9 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1364 (10:40) | Lufthansa LH 1365 (13:20) | 49.1 | Zu früh (< 14:00) ❌ |

---

### Bologna (BLQ)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 12 / 11
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 282 (08:20) / Rückflug Lufthansa LH 287 (18:30) - Aufenthalt: 56.7 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Lufthansa LH 282 (08:20) | Lufthansa LH 287 (18:30) | 56.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 282 (08:20) | Air Dolomiti EN 8885 (06:10) | 44.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 282 (08:20) | Air Dolomiti EN 8881 (14:45) | 52.9 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8880 (12:30) | Lufthansa LH 287 (18:30) | 52.5 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8880 (12:30) | Air Dolomiti EN 8885 (06:10) | 40.2 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8880 (12:30) | Air Dolomiti EN 8881 (14:45) | 48.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 286 (16:20) | Lufthansa LH 287 (18:30) | 48.7 | Akzeptabel (>= 14:00) |
| Lufthansa LH 286 (16:20) | Air Dolomiti EN 8885 (06:10) | 36.3 | Akzeptabel (>= 14:00) |
| Lufthansa LH 286 (16:20) | Air Dolomiti EN 8881 (14:45) | 44.9 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8884 (22:10) | Lufthansa LH 287 (18:30) | 42.8 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8884 (22:10) | Air Dolomiti EN 8881 (14:45) | 39.1 | Akzeptabel (>= 14:00) |

---

### Helsinki (HEL)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 20 / 16
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 848 (09:35) / Rückflug Finnair AY 1411 (07:40) - Aufenthalt: 42.6 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Finnair AY 1416 (19:20) | Lufthansa City Airlines VL 849 (13:45) | 39.0 | Akzeptabel (>= 14:00) |
| Finnair AY 1416 (19:20) | Lufthansa City Airlines VL 851 (18:15) | 43.5 | Akzeptabel (>= 14:00) |
| Lufthansa LH 848 (09:35) | Finnair AY 1411 (07:40) | 42.6 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 848 (09:35) | Lufthansa City Airlines VL 853 (06:45) | 41.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 848 (09:35) | Lufthansa City Airlines VL 849 (13:45) | 48.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 848 (09:35) | Lufthansa City Airlines VL 851 (18:15) | 53.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 852 (21:10) | Lufthansa City Airlines VL 849 (13:45) | 37.1 | Akzeptabel (>= 14:00) |
| Lufthansa LH 852 (21:10) | Lufthansa City Airlines VL 851 (18:15) | 41.6 | Akzeptabel (>= 14:00) |
| Lufthansa City Airlines VL 850 (13:40) | Finnair AY 1411 (07:40) | 38.5 | Zu früh (< 14:00) ❌ |
| Lufthansa City Airlines VL 850 (13:40) | Lufthansa City Airlines VL 853 (06:45) | 37.6 | Zu früh (< 14:00) ❌ |
| Lufthansa City Airlines VL 850 (13:40) | Lufthansa City Airlines VL 849 (13:45) | 44.6 | Zu früh (< 14:00) ❌ |
| Lufthansa City Airlines VL 850 (13:40) | Lufthansa City Airlines VL 851 (18:15) | 49.1 | Zu früh (< 14:00) ❌ |
| Finnair AY 1412 (11:30) | Finnair AY 1411 (07:40) | 40.8 | Zu früh (< 14:00) ❌ |
| Finnair AY 1412 (11:30) | Lufthansa City Airlines VL 853 (06:45) | 39.8 | Zu früh (< 14:00) ❌ |
| Finnair AY 1412 (11:30) | Lufthansa City Airlines VL 849 (13:45) | 46.8 | Zu früh (< 14:00) ❌ |
| Finnair AY 1412 (11:30) | Lufthansa City Airlines VL 851 (18:15) | 51.3 | Zu früh (< 14:00) ❌ |

---

### Breslau (WRO)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 9 / 8
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Air Dolomiti EN 8766 (08:20) / Rückflug Lufthansa LH 1377 (06:25) - Aufenthalt: 44.7 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Air Dolomiti EN 8766 (08:20) | Lufthansa LH 1377 (06:25) | 44.7 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8766 (08:20) | Air Dolomiti EN 8767 (10:30) | 48.8 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8766 (08:20) | Lufthansa LH 1375 (14:40) | 52.9 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1374 (12:50) | Lufthansa LH 1377 (06:25) | 40.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1374 (12:50) | Air Dolomiti EN 8767 (10:30) | 44.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1374 (12:50) | Lufthansa LH 1375 (14:40) | 48.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1376 (20:30) | Air Dolomiti EN 8767 (10:30) | 36.6 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1376 (20:30) | Lufthansa LH 1375 (14:40) | 40.8 | Akzeptabel (>= 14:00) |

---

### Basel (BSL)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 9 / 8
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 1202 (09:35) / Rückflug Lufthansa LH 1203 (11:00) - Aufenthalt: 48.4 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Lufthansa LH 1202 (09:35) | Lufthansa LH 1203 (11:00) | 48.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1202 (09:35) | Lufthansa LH 1205 (14:40) | 52.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1202 (09:35) | Lufthansa LH 1209 (06:00) | 43.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1204 (12:55) | Lufthansa LH 1203 (11:00) | 45.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1204 (12:55) | Lufthansa LH 1205 (14:40) | 48.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1204 (12:55) | Lufthansa LH 1209 (06:00) | 40.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1208 (22:00) | Lufthansa LH 1203 (11:00) | 36.0 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1208 (22:00) | Lufthansa LH 1205 (14:40) | 39.7 | Akzeptabel (>= 14:00) |

---

### Sarajevo (SJJ)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 4 / 3
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 1544 (10:10) / Rückflug Lufthansa LH 1545 (11:25) - Aufenthalt: 47.5 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Lufthansa LH 1546 (20:25) | Lufthansa LH 1545 (11:25) | 37.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1544 (10:10) | Lufthansa LH 1545 (11:25) | 47.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 1544 (10:10) | Lufthansa LH 1547 (06:15) | 42.3 | Zu früh (< 14:00) ❌ |

---

### Pula (PUY)
- **Risikoklassifikation:** `safe` | **Entscheidung:** KEEP
- **Verbindungen (Gesamt / Gültig >= 36h):** 1 / 1
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 1398 (17:00) / Rückflug Lufthansa LH 1399 (19:20) - Aufenthalt: 48.8 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| Lufthansa LH 1398 (17:00) | Lufthansa LH 1399 (19:20) | 48.8 | Akzeptabel (>= 14:00) |

---

### Mailand (Linate) (LIN)
- **Risikoklassifikation:** `mixed` | **Entscheidung:** EXCLUDE
- **Verbindungen (Gesamt / Gültig >= 36h):** 99 / 95
- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug Lufthansa LH 246 (06:55) / Rückflug Lufthansa LH 275 (15:20) - Aufenthalt: 55.1 Std.

#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):

| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |
| :--- | :--- | :---: | :--- |
| easyJet U2 5404 (09:10) | Lufthansa LH 275 (15:20) | 53.0 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | easyJet U2 5403 (07:00) | 44.7 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | Lufthansa LH 279 (19:40) | 57.3 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | easyJet U2 5427 (18:10) | 55.8 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | Lufthansa LH 273 (12:40) | 50.3 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | Air Dolomiti EN 8801 (10:30) | 48.2 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | Lufthansa LH 247 (09:00) | 46.7 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | Lufthansa LH 249 (11:20) | 49.0 | Zu früh (< 14:00) ❌ |
| easyJet U2 5404 (09:10) | Lufthansa LH 255 (18:50) | 56.5 | Zu früh (< 14:00) ❌ |
| easyJet U2 5428 (20:10) | Lufthansa LH 275 (15:20) | 42.0 | Akzeptabel (>= 14:00) |
| easyJet U2 5428 (20:10) | Lufthansa LH 279 (19:40) | 46.3 | Akzeptabel (>= 14:00) |
| easyJet U2 5428 (20:10) | easyJet U2 5427 (18:10) | 44.8 | Akzeptabel (>= 14:00) |
| easyJet U2 5428 (20:10) | Lufthansa LH 273 (12:40) | 39.3 | Akzeptabel (>= 14:00) |
| easyJet U2 5428 (20:10) | Air Dolomiti EN 8801 (10:30) | 37.2 | Akzeptabel (>= 14:00) |
| easyJet U2 5428 (20:10) | Lufthansa LH 249 (11:20) | 38.0 | Akzeptabel (>= 14:00) |
| easyJet U2 5428 (20:10) | Lufthansa LH 255 (18:50) | 45.5 | Akzeptabel (>= 14:00) |
| Air Dolomiti EN 8800 (08:45) | Lufthansa LH 275 (15:20) | 53.3 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | easyJet U2 5403 (07:00) | 45.0 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | Lufthansa LH 279 (19:40) | 57.7 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | easyJet U2 5427 (18:10) | 56.2 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | Lufthansa LH 273 (12:40) | 50.7 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | Air Dolomiti EN 8801 (10:30) | 48.5 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | Lufthansa LH 247 (09:00) | 47.0 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | Lufthansa LH 249 (11:20) | 49.3 | Zu früh (< 14:00) ❌ |
| Air Dolomiti EN 8800 (08:45) | Lufthansa LH 255 (18:50) | 56.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | Lufthansa LH 275 (15:20) | 48.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | easyJet U2 5403 (07:00) | 40.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | Lufthansa LH 279 (19:40) | 53.0 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | easyJet U2 5427 (18:10) | 51.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | Lufthansa LH 273 (12:40) | 46.0 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | Air Dolomiti EN 8801 (10:30) | 43.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | Lufthansa LH 247 (09:00) | 42.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | Lufthansa LH 249 (11:20) | 44.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 274 (13:25) | Lufthansa LH 255 (18:50) | 52.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | Lufthansa LH 275 (15:20) | 51.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | easyJet U2 5403 (07:00) | 43.0 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | Lufthansa LH 279 (19:40) | 55.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | easyJet U2 5427 (18:10) | 54.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | Lufthansa LH 273 (12:40) | 48.7 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | Air Dolomiti EN 8801 (10:30) | 46.5 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | Lufthansa LH 247 (09:00) | 45.0 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | Lufthansa LH 249 (11:20) | 47.3 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 272 (10:45) | Lufthansa LH 255 (18:50) | 54.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 276 (16:15) | Lufthansa LH 275 (15:20) | 45.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | easyJet U2 5403 (07:00) | 37.5 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | Lufthansa LH 279 (19:40) | 50.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | easyJet U2 5427 (18:10) | 48.7 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | Lufthansa LH 273 (12:40) | 43.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | Air Dolomiti EN 8801 (10:30) | 41.0 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | Lufthansa LH 247 (09:00) | 39.5 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | Lufthansa LH 249 (11:20) | 41.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 276 (16:15) | Lufthansa LH 255 (18:50) | 49.3 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | Lufthansa LH 275 (15:20) | 44.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | easyJet U2 5403 (07:00) | 36.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | Lufthansa LH 279 (19:40) | 49.1 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | easyJet U2 5427 (18:10) | 47.6 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | Lufthansa LH 273 (12:40) | 42.1 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | Air Dolomiti EN 8801 (10:30) | 39.9 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | Lufthansa LH 247 (09:00) | 38.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | Lufthansa LH 249 (11:20) | 40.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 278 (17:20) | Lufthansa LH 255 (18:50) | 48.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 280 (20:50) | Lufthansa LH 275 (15:20) | 41.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 280 (20:50) | Lufthansa LH 279 (19:40) | 45.6 | Akzeptabel (>= 14:00) |
| Lufthansa LH 280 (20:50) | easyJet U2 5427 (18:10) | 44.1 | Akzeptabel (>= 14:00) |
| Lufthansa LH 280 (20:50) | Lufthansa LH 273 (12:40) | 38.6 | Akzeptabel (>= 14:00) |
| Lufthansa LH 280 (20:50) | Air Dolomiti EN 8801 (10:30) | 36.4 | Akzeptabel (>= 14:00) |
| Lufthansa LH 280 (20:50) | Lufthansa LH 249 (11:20) | 37.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 280 (20:50) | Lufthansa LH 255 (18:50) | 44.8 | Akzeptabel (>= 14:00) |
| Lufthansa LH 246 (06:55) | Lufthansa LH 275 (15:20) | 55.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | easyJet U2 5403 (07:00) | 46.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | Lufthansa LH 279 (19:40) | 59.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | easyJet U2 5427 (18:10) | 57.9 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | Lufthansa LH 273 (12:40) | 52.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | Air Dolomiti EN 8801 (10:30) | 50.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | Lufthansa LH 247 (09:00) | 48.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | Lufthansa LH 249 (11:20) | 51.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 246 (06:55) | Lufthansa LH 255 (18:50) | 58.6 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | Lufthansa LH 275 (15:20) | 52.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | easyJet U2 5403 (07:00) | 44.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | Lufthansa LH 279 (19:40) | 57.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | easyJet U2 5427 (18:10) | 55.6 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | Lufthansa LH 273 (12:40) | 50.1 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | Air Dolomiti EN 8801 (10:30) | 47.9 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | Lufthansa LH 247 (09:00) | 46.4 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | Lufthansa LH 249 (11:20) | 48.8 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 248 (09:15) | Lufthansa LH 255 (18:50) | 56.2 | Zu früh (< 14:00) ❌ |
| Lufthansa LH 254 (16:40) | Lufthansa LH 275 (15:20) | 45.3 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | easyJet U2 5403 (07:00) | 37.0 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | Lufthansa LH 279 (19:40) | 49.7 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | easyJet U2 5427 (18:10) | 48.2 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | Lufthansa LH 273 (12:40) | 42.7 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | Air Dolomiti EN 8801 (10:30) | 40.5 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | Lufthansa LH 247 (09:00) | 39.0 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | Lufthansa LH 249 (11:20) | 41.3 | Akzeptabel (>= 14:00) |
| Lufthansa LH 254 (16:40) | Lufthansa LH 255 (18:50) | 48.8 | Akzeptabel (>= 14:00) |

---

