# Component Admission v1

## Zweck

Der Component-Admission-Vertrag verhindert, dass neue dauerhafte Systemkomponenten ohne begründeten Nutzen und klaren Lebenszyklus in Heimgewebe verbleiben. Er ist ein statischer Zulassungsnachweis, keine neue Control Plane.

Im Geltungsbereich sind katalogisierte Repositories, Services, dauerhafte Hintergrundprozesse und öffentliche Operator-Surfaces. Der am Einführungszeitpunkt vorhandene Bestand ist in `policy/component-admission.v1.json` grandfathered. Dadurch blockiert der neue Vertrag bestehende Komponenten nicht rückwirkend.

## Zulassungsklassen

Jede neue dauerhafte Komponente verwendet genau eine Klasse:

- `replace`: ersetzt eine bestehende Komponente oder Funktion;
- `reduce`: reduziert belegbar Betriebs-, Wartungs- oder Operatorlast;
- `enable`: schafft eine neue dauerhafte Fähigkeit mit benanntem Consumer;
- `experimental`: zeitlich überprüfbare Erprobung mit Erfolgskriterium und Review-Datum.

Eine neue Komponente muss in `registry/ecosystem/nodes.json` katalogisiert sein und in `registry/ecosystem/component-admissions.v1.json` einen Zulassungsnachweis besitzen, sofern sie nicht zum grandfathered Ausgangsbestand gehört.

## Pflichtnachweise

Der Zulassungsnachweis enthält:

- die Komponentenidentität und -art;
- den stabilen Zweck, identisch zum Systemkatalog-Knoten;
- mindestens einen konkreten Consumer;
- eine explizite Referenz auf die Wahrheitsautorität oder ausdrücklich `none:<Begründung>`;
- Betriebsabhängigkeiten, auch als explizit leere Liste;
- die erwartete Wartungslast;
- einen Review- oder Stilllegungspfad;
- eine quellengebundene Referenz, typischerweise auf einen Bureau-Task oder einen reviewed PR;
- ausdrückliche Nicht-Claims.

`experimental` verlangt zusätzlich ein messbares Erfolgskriterium und ein ISO-Datum `reviewBy`. Das Datum ist ein Review-Anker; v1 erzeugt daraus weder automatisch einen Task noch eine Abschaltung.

## Wahrheitsgrenzen

- Systemkatalog besitzt nur die stabile Semantik des Zulassungsvertrags und der katalogisierten Komponente.
- Bureau bleibt Autorität für Aufgabe, Priorität und Closeout.
- Grabowski und die jeweiligen Primärsysteme bleiben Autorität für Ausführung und Runtime.
- Die Zulassung beweist weder Runtime-Gesundheit noch Merge-, Deploy- oder Dispatch-Bereitschaft.
- Es gibt keinen globalen Komplexitätswert und kein pauschales WIP-Limit.

## Validierung

`scripts/validate_system_catalog.py` ruft `validate_component_admissions()` auf. Dadurch gilt:

1. Der heutige Bestand bleibt grandfathered.
2. Ein neuer Knoten der Typen `repository`, `service`, `background_process` oder `operator_surface` benötigt Admission-Evidenz.
3. Unvollständige oder widersprüchliche Admission-Evidenz lässt die Repository-Validierung fehlschlagen.
4. Admission-Einträge für nicht existente oder bereits grandfathered Komponenten werden abgewiesen.

Neue Hintergrundprozesse und Operator-Surfaces werden als stabile Katalogknoten mit `process:`- beziehungsweise `surface:`-Identität modelliert. Flüchtige Prozesse und UI-Zustände gehören ausdrücklich nicht in diesen Vertrag.
