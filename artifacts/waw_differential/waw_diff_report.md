# Lufthansa Surprise: WAW Differential-Test Report

**Ausgeführt am:** 2026-08-04T18:02:49.279881  

## Testergebnisse Übersicht

| Test-ID | Beschreibung | Status | Preis | Param. verifiziert | Checkboxen verifiziert |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `waw_inactive` | WAW deactivated (10 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `waw_active_baseline` | WAW activated again (Baseline - 11 targets) | `available` | 129,00€ | ✅ | ✅ |
| `deactivate_flr` | Deactivate FLR (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_prg` | Deactivate PRG (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_wro` | Deactivate WRO (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_hel` | Deactivate HEL (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_blq` | Deactivate BLQ (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_krk` | Deactivate KRK (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_bsl` | Deactivate BSL (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_sjj` | Deactivate SJJ (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |
| `deactivate_lin` | Deactivate LIN (WAW + remaining 9 targets active) | `available` | 140,32€ | ✅ | ✅ |
| `deactivate_puy` | Deactivate PUY (WAW + remaining 9 targets active) | `available` | 138,58€ | ✅ | ✅ |

## Wichtigste Erkenntnisse

- **WAW als Deal-Trigger:** `Nein` / `Unbestimmt` (Status ohne WAW ist `available`).
- **Ziele, die den Baseline-Preis von 129,00€ nicht beeinflussen:** `[]`
- **Ziele, die den Preis oder Status beeinflussen:** `['FLR (Status: available, Preis: 138,58€)', 'PRG (Status: available, Preis: 138,58€)', 'WRO (Status: available, Preis: 138,58€)', 'HEL (Status: available, Preis: 138,58€)', 'BLQ (Status: available, Preis: 138,58€)', 'KRK (Status: available, Preis: 138,58€)', 'BSL (Status: available, Preis: 138,58€)', 'SJJ (Status: available, Preis: 138,58€)', 'LIN (Status: available, Preis: 140,32€)', 'PUY (Status: available, Preis: 138,58€)']`
