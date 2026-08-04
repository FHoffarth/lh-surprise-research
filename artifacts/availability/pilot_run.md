# Lufthansa Surprise Pilot Run Report

**Timestamp:** 2026-08-03T22:49:28.697127  
**Empfehlung:** `FIXES_REQUIRED`  
**Inventar unverändert (Konsistenz):** `Ja`  
**Eingabemethode:** React Datepicker UI interaction only (keine DOM-/JavaScript-Injektion)

## Bestätigte Suchparameter

- **Abflug:** Frankfurt/Main (FRA)
- **Hinflug:** 07.08.2026
- **Rückflug:** 09.08.2026
- **Reisende:** 1 Erwachsener
- **Klasse:** Economy
- **Flexibilität:** Volle Flexibilität
- **Thema:** Kunst und Kultur

## Übersicht der Testschritte

| Test-ID | Beschreibung | Aktive Ziele | Status | Preis | Param. verifiziert | Checkboxen verifiziert |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| `baseline_initial` | Initial Baseline (All 11 Targets) | FLR, PRG, WAW, WRO, HE... | **available** | 129,00€ | ✅ | ✅ |
| `group_1_flr_prg_waw` | Group 1 (FLR, PRG, WAW) | FLR, PRG, WAW | **available** | 177,52€ | ✅ | ✅ |
| `group_2_hel_blq_krk` | Group 2 (HEL, BLQ, KRK) | HEL, BLQ, KRK | **available** | 204,89€ | ✅ | ✅ |
| `single_target_prg` | Single Target Test (PRG) | PRG | **validation_failed** | - | ✅ | ❌ |
| `baseline_final` | Final Baseline (Inventory Consistency Check) | FLR, PRG, WAW, WRO, HE... | **available** | 129,00€ | ✅ | ✅ |

## Baseline-Stabilitätsvergleich

- **Initial Baseline:** Status = `available`, Preis = `129,00€`
- **Final Baseline:** Status = `available`, Preis = `129,00€`

> [!NOTE]
> Baseline-Inventar und Preis blieben über alle Testschritte hinweg exakt stabil und konsistent.

## Details je Testschritt

### `baseline_initial`: Initial Baseline (All 11 Targets)
- **Zeitraum:** 2026-08-03T22:47:09.521321 bis 2026-08-03T22:47:37.913293
- **Aktive Ziele:** `['FLR', 'PRG', 'WAW', 'WRO', 'HEL', 'BLQ', 'KRK', 'BSL', 'SJJ', 'LIN', 'PUY']`
- **Status:** `available`
- **Preis:** `129,00€`
- **Details:** Offer page loaded with price details

### `group_1_flr_prg_waw`: Group 1 (FLR, PRG, WAW)
- **Zeitraum:** 2026-08-03T22:47:40.924604 bis 2026-08-03T22:48:08.106460
- **Aktive Ziele:** `['FLR', 'PRG', 'WAW']`
- **Status:** `available`
- **Preis:** `177,52€`
- **Details:** Offer page loaded with price details

### `group_2_hel_blq_krk`: Group 2 (HEL, BLQ, KRK)
- **Zeitraum:** 2026-08-03T22:48:11.120797 bis 2026-08-03T22:48:38.341302
- **Aktive Ziele:** `['HEL', 'BLQ', 'KRK']`
- **Status:** `available`
- **Preis:** `204,89€`
- **Details:** Offer page loaded with price details

### `single_target_prg`: Single Target Test (PRG)
- **Zeitraum:** - bis -
- **Aktive Ziele:** `['PRG']`
- **Status:** `validation_failed`
- **Preis:** `None`
- **Details:** Checkbox state verification failed

### `baseline_final`: Final Baseline (Inventory Consistency Check)
- **Zeitraum:** 2026-08-03T22:49:03.214787 bis 2026-08-03T22:49:27.724909
- **Aktive Ziele:** `['FLR', 'PRG', 'WAW', 'WRO', 'HEL', 'BLQ', 'KRK', 'BSL', 'SJJ', 'LIN', 'PUY']`
- **Status:** `available`
- **Preis:** `129,00€`
- **Details:** Offer page loaded with price details

