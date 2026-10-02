# Mollier h,x-Diagramm

Interaktive Streamlit-Lehranwendung für Luftzustände und idealisierte Zustandsänderungen
bei der Planung von Lackierkabinen. Gestaltung angelehnt an die Lehr-Apps von
Prof. Dr.-Ing. Hendrik Dubbe, Hochschule Esslingen.

## Starten

Python 3.12 wird empfohlen.

```sh
pip install -r requirements.txt
streamlit run app.py
```

Für Streamlit Community Cloud: öffentliches Repository `dubbehendrik/Mollier-h-x`,
Branch `main`, Startdatei `app.py`. Die Veröffentlichung auf Streamlit erfolgt separat.
Die Anwendung benötigt keine Zugangsdaten und keine externen Datenabrufe zur Laufzeit.

## Bedienung

- Druckfeld mit Startwert 950 hPa und Reset.
- Zustand aus zwei unterschiedlichen Größen T, x, φ, ρ, h bestimmen. Die zehn
  Kombinationen werden im festen Diagrammbereich gelöst; mehrdeutige, widersprüchliche
  oder übersättigte Zustände werden abgewiesen.
- Punkt per Diagrammklick hinzufügen. Mit Maus über einem Punkt erscheinen dessen
  Werte; beim Bewegen im Diagramm werden T und x abgelesen. Tastatur: Diagramm
  fokussieren, Pfeiltasten (Umschalt für größere Schritte), Enter zum Hinzufügen.
- Alternativ Prozess und Zieltemperatur bzw. Zielbeladung wählen.
- Tabelle: Vorgaben und Namen bearbeiten, Reihenfolgenummern tauschen, Löschen
  markieren und Änderungen übernehmen. Angezeigte Punktnummern folgen der Sortierung.
- Jede Verbindung hat eine Prozessart. Änderungen behalten Endpunkte bei und prüfen
  die Verträglichkeit. Zielpunkt-Neuberechnung ist ausdrücklich auszulösen; sie hält
  beim Heizen/Kühlen T und sonst x fest. Nachfolgende Punkte bleiben unverändert.
- PNG, SVG und Excel exportieren. Nicht übernommene Tabellenänderungen sind nicht im
  Export. Ungültige Zustände/Prozesse müssen vor dem Export korrigiert werden.
- Beispiele ersetzen die aktuelle Punktfolge. „Punkte leeren“ startet eine neue Folge.

## Diagramm und Einheiten

Fester Bereich entsprechend der PDF-Vorlage: −15 bis 40 °C, 0 bis 20 g/kg trockene Luft.
Es gibt Linien für T, x, φ, h und ρ. Die Darstellung ist eine lineare Scherung des h,x-
Diagramms: `y = (h − 2501 w) / 1.006`, mit `w = x / 1000`. Die linke Temperaturskala
gilt bei x = 0; Isothermen sind leicht geneigt. Randabstände dienen der Beschriftung,
nicht als erweiterter Eingabebereich.

- **T**: Temperatur in °C.
- **x**: Wasserdampfmasse in g pro kg **trockener** Luft.
- **φ**: relative Feuchte in %, immer bezogen auf flüssiges Wasser.
- **h**: Enthalpie in kJ pro kg **trockener** Luft; Bezug trockene Luft und flüssiges
  Wasser bei 0 °C.
- **ρ**: Masse der gesamten feuchten Luft pro Volumen, kg/m³.
- Druck: hPa in der Oberfläche, Pa im Rechenkern; zulässig 500–1200 hPa.

## Winterliche Außenluft – verständlich erklärt

Die relative Feuchte bezieht sich hier immer auf flüssiges Wasser. Unter 0 °C verwenden
wir unterkühltes Wasser als Rechenbezug. Dadurch bleibt die Bedeutung der Prozentangabe
beim Erwärmen kalter Außenluft gleich. Das bedeutet nicht, dass Wasser in einer realen
Anlage unter 0 °C flüssig bleiben muss: Reif, Eis und Kühlervereisung werden nicht berechnet.
Kalte Außenluft darf eingegeben und erwärmt werden; Wasserabscheidung unter 0 °C wird
abgewiesen. Bei Mess- und Wetterdaten muss der Feuchtebezug (Wasser oder Eis) geprüft werden.
Ein negativer angezeigter Taupunkt ist ein Taupunkt bezüglich unterkühltem Wasser, kein Frostpunkt.

## Stoffwerte und Prozessmodelle

Ideales Gemisch trockener Luft und Wasserdampf nach ASHRAE 2017/PsychroLib:

```
pv = φ * psat(T)                     # φ als Anteil 0…1
w = 0.621945 * pv / (p - pv)          # kg/kg trockene Luft
h = 1.006*T + w*(2501 + 1.86*T)       # kJ/kg trockene Luft
ρ = p*(1+w)/(287.042*(T+273.15)*(1+1.607858*w))
```

Sättigungsdampfdruck: ASHRAE-Wasserbeziehung ab 0 °C; darunter Murphy & Koop (2005),
Gl. 10, mit dem konstanten Verhältnis `p_AShRAE(0) / p_MK(0)` normiert, damit die
Kurve bei 0 °C stetig ist. Keine automatische Umschaltung auf Eis, kein Enhancement-
Faktor. Dies ist eine dokumentierte Abweichung vom PsychroLib-Standard unter 0 °C.

- **Erwärmen:** x konstant.
- **Kühlen:** x konstant bis zum Taupunkt, anschließend gesättigte Luft mit
  kontinuierlicher Kondensatabscheidung. Abgeschiedene Wassermasse = x_start − x_ende.
  Keine mitgeführten Tröpfchen und keine Wiederverdunstung abgeschiedenen Wassers.
- **Isotherme Be-/Entfeuchtung:** T konstant, idealisiert mit Wärmeausgleich.
- **Isenthalpe Befeuchtung:** h konstant, Näherung für Verdunstungsbefeuchtung;
  Enthalpie des zugeführten Wassers wird in dieser Näherung vernachlässigt.
- **Freie Verbindung:** gestrichelte geometrische Verbindung, kein Prozessmodell.

Δh ist eine Luftzustandsdifferenz. Bei Kondensatabscheidung ist sie **nicht** die
vollständige Kühlerwärmebilanz: die Enthalpie des austretenden Kondensats fehlt.
Keine Leistungen, Luftmengen, Kühler-Bypassfaktoren, Druckverluste oder Mischprozesse.
Für eine reale Anlagenauslegung sind diese Aspekte zusätzlich zu berücksichtigen.

## Quellen

- [PsychroLib API und ASHRAE-Verweise](https://psychrometrics.github.io/psychrolib/api_docs.html)
- [PsychroLib Referenzimplementierung](https://github.com/psychrometrics/psychrolib)
- [Murphy & Koop 2005, DOI 10.1256/qj.04.94](https://doi.org/10.1256/qj.04.94)
- [UCAR: Dampfdruckgleichungen](https://www.eol.ucar.edu/data-software/conventions-and-standards/water-vapor-pressure-formulations)

## Prüfungen

```sh
pip install -r requirements-dev.txt
python -m pytest -q
```

Die Tests prüfen alle zehn Eingabepaare, PsychroLib-Referenzwerte oberhalb 0 °C,
Wasserbezug im Frostbereich, Sättigungsübergang, Prozessgrenzen, Bedienungsabläufe
und Export. Rechenkern, Diagramm, Export und Oberfläche sind getrennte Module.

Das HSE-Logo wird aus der bestehenden Lehr-App übernommen. An Logo/Marken werden
keine zusätzlichen Nutzungsrechte eingeräumt. Die Original-PDF wird nicht mitveröffentlicht.
