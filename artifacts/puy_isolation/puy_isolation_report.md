# Lufthansa Surprise: PUY Isolation-Test Abschlussbericht

**Ausgeführt am:** 2026-08-04T21:29:34.717886  

## Testergebnisse Übersicht

### Isolationstest Paar 1: BSL + SJJ (Kontrollziel: FLR)
| Testschritt | Konfiguration | Status | Preis | Intercepted Targets |
| :--- | :--- | :---: | :---: | :--- |
| Test 1 | PUY + BSL + SJJ | `available` | 214,03€ | ['BSL', 'SJJ', 'PUY'] |
| Test 2 | FLR + BSL + SJJ (PUY off) | `available` | - | ['FLR', 'BSL', 'SJJ'] |
| Test 3 | PUY + BSL + SJJ (Repeat) | `available` | 214,03€ | ['BSL', 'SJJ', 'PUY'] |

**Ergebnis:** Keine eindeutige Trigger-Wirkung nachgewiesen. (Status Test 1: `available`, Test 2: `available`).  

### Isolationstest Paar 2: WRO + SJJ (Kontrollziel: PRG)
| Testschritt | Konfiguration | Status | Preis | Intercepted Targets |
| :--- | :--- | :---: | :---: | :--- |
| Test 1 | PUY + WRO + SJJ | `available` | - | ['WRO', 'SJJ', 'PUY'] |
| Test 2 | PRG + WRO + SJJ (PUY off) | `available` | - | ['PRG', 'WRO', 'SJJ'] |
| Test 3 | PUY + WRO + SJJ (Repeat) | `available` | - | ['WRO', 'SJJ', 'PUY'] |

**Ergebnis:** Keine eindeutige Trigger-Wirkung nachgewiesen. (Status Test 1: `available`, Test 2: `available`).  

### Isolationstest Paar 3: BSL + WRO (Kontrollziel: WAW)
| Testschritt | Konfiguration | Status | Preis | Intercepted Targets |
| :--- | :--- | :---: | :---: | :--- |
| Test 1 | PUY + BSL + WRO | `available` | - | ['WRO', 'BSL', 'PUY'] |
| Test 2 | WAW + BSL + WRO (PUY off) | `available` | 177,53€ | ['WAW', 'WRO', 'BSL'] |
| Test 3 | PUY + BSL + WRO (Repeat) | `available` | - | ['WRO', 'BSL', 'PUY'] |

**Ergebnis:** Keine eindeutige Trigger-Wirkung nachgewiesen. (Status Test 1: `available`, Test 2: `available`).  

