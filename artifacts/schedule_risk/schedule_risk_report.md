# Lufthansa Surprise: Schedule Risk Engine Report

**Reisedatum:** Freitag, 07.08.2026  
**Abflughafen:** Frankfurt/Main (FRA)  
**Früheste akzeptable Abflugzeit:** 14:00 Uhr  
**Risikopolitik:** `reject_if_any_plausible_direct_flight_is_too_early` (Ausschließen, wenn ein möglicher Direktflug vor der akzeptablen Zeit liegt)  

## Übersicht der Ergebnisse

| Zielstadt | IATA | Risiko-Klassifikation | Entscheidung | Gründe |
| :--- | :---: | :---: | :---: | :--- |
| Breslau | WRO | `mixed` | **EXCLUDE** | Mixed flight schedule: 1 acceptable flight(s), but 2 flight(s) depart too early (before 14:00) |
| Prag | PRG | `mixed` | **EXCLUDE** | Mixed flight schedule: 4 acceptable flight(s), but 4 flight(s) depart too early (before 14:00) |
| Warschau | WAW | `mixed` | **EXCLUDE** | Mixed flight schedule: 4 acceptable flight(s), but 3 flight(s) depart too early (before 14:00) |

## Detaillierte Flugplanauswertung

### Breslau (WRO) - Risikoklassifikation: `mixed`

- **Entscheidung:** EXCLUDE
- **Unsicherheitshinweis:** Lufthansa Surprise could assign an unacceptable early flight segment.

#### Gefundene Flüge (Dedupliziert):

| Flugnummer | Abflugzeit | Ankunftszeit | Bewertung |
| :--- | :---: | :---: | :---: |
| Air Dolomiti EN 8766 | 08:20 | 09:45 | Zwei-Früh (< 14:00) ❌ |
| Lufthansa LH 1374 | 12:50 | 14:15 | Zwei-Früh (< 14:00) ❌ |
| Lufthansa LH 1376 | 20:30 | 21:55 | Akzeptabel (>= 14:00) |

### Prag (PRG) - Risikoklassifikation: `mixed`

- **Entscheidung:** EXCLUDE
- **Unsicherheitshinweis:** Lufthansa Surprise could assign an unacceptable early flight segment.

#### Gefundene Flüge (Dedupliziert):

| Flugnummer | Abflugzeit | Ankunftszeit | Bewertung |
| :--- | :---: | :---: | :---: |
| Condor DE 4411 | 20:25 | 21:25 | Akzeptabel (>= 14:00) |
| Condor DE 4409 | 09:40 | 10:50 | Zwei-Früh (< 14:00) ❌ |
| Condor DE 4407 | 15:00 | 16:00 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1392 | 07:30 | 08:30 | Zwei-Früh (< 14:00) ❌ |
| Lufthansa LH 1394 | 10:00 | 11:00 | Zwei-Früh (< 14:00) ❌ |
| Lufthansa LH 1396 | 12:40 | 13:40 | Zwei-Früh (< 14:00) ❌ |
| Lufthansa LH 1400 | 16:45 | 17:45 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1402 | 22:15 | 23:15 | Akzeptabel (>= 14:00) |

### Warschau (WAW) - Risikoklassifikation: `mixed`

- **Entscheidung:** EXCLUDE
- **Unsicherheitshinweis:** Lufthansa Surprise could assign an unacceptable early flight segment.

#### Gefundene Flüge (Dedupliziert):

| Flugnummer | Abflugzeit | Ankunftszeit | Bewertung |
| :--- | :---: | :---: | :---: |
| LOT LO 378 | 17:30 | 19:20 | Akzeptabel (>= 14:00) |
| LOT LO 380 | 19:50 | 21:35 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1346 | 07:10 | 08:50 | Zwei-Früh (< 14:00) ❌ |
| Lufthansa LH 1348 | 11:50 | 13:30 | Zwei-Früh (< 14:00) ❌ |
| Lufthansa LH 1350 | 16:40 | 18:20 | Akzeptabel (>= 14:00) |
| Lufthansa LH 1352 | 20:45 | 22:25 | Akzeptabel (>= 14:00) |
| LOT LO 382 | 10:35 | 12:25 | Zwei-Früh (< 14:00) ❌ |

