# Lufthansa Surprise: PUY Differential-Test Abschlussbericht

**Ausgeführt am:** 2026-08-04T21:21:14.016024  

## Testergebnisse Übersicht

| Test | Beschreibung | Status | Preis | Checkboxen bewiesen |
| :--- | :--- | :---: | :---: | :---: |
| Test A | All 11 active (Baseline) | `available` | 129,00€ | ✅ |
| Test B | PUY deactivated | `available` | 138,58€ | ✅ |
| Test C | PUY re-activated (Repeat) | `available` | 129,00€ | ✅ |

## Interpretation & Abhängigkeitsbewertung

- **Ergebnis-Klassifikation:** `PUY_not_necessary_for_offer`
- **Aussage:** `PUY` ist nicht notwendig für das Zustandekommen eines Deals. Preisunterschied: 129,00€ (mit PUY) vs. 138,58€ (ohne PUY).

## Request-Parametervalidierung (Test A)
- **Suchdaten:** `2026-08-07 bis 2026-08-09`  
- **Aufenthaltsdauer:** `minStay: 1 | maxStay: 1 | availableStayValues: [1, 2]`  
- **Übertragene Zielcodes:** `11 targets: ['Florenz', 'Prag', 'Warschau', 'Breslau', 'Helsinki', 'Bologna', 'Krakau', 'Basel', 'Sarajevo', 'Mailand', 'Pula']`  
