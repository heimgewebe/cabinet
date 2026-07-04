# Cabinet Home

Cabinet ordnet Repositories, Projekte, Prüfungen und nächste Schritte.

## Entree

- [README](README.md) — kanonischer Schnellstart fuer Menschen und GitHub.
- [Agent Entry](AGENTS.md) — Lesereihenfolge, Wahrheitsgrenzen und Stop-Kriterien fuer LLMs und Agenten.
- [Ecosystem Map v0](docs/blueprints/ecosystem-map-v0.md) — Systemkarte, Dateien, Pflegeprinzipien und Reifekriterien.
- [Mermaidkarte](rendered/ecosystem-map.mmd) — gerenderte Graphansicht.
- [Heim-PC Operatorium Index v0](docs/blueprints/heim-pc-operatorium-index-v0.md) — heim-pc als lokale Operatorium-Schicht.

## Aktive Räume

- [Bestand](bestand/index.md) – Repositories, Projekte, Quellen und Beziehungen
- [Prüfung](pruefung/index.md) – Läufe, Belege, Befunde, Widersprüche und Risiken
- [Steuerung](steuerung/index.md) – Lage, Entscheidungen, Aufgaben, Blocker und Übergaben

## Legacy-Sammlungen

Vorzimmer, Heimgewebe, Weltgewebe, Werkstatt, Labor und Betrieb bleiben an ihren bisherigen Pfaden lesbar. Ihre `.cabinet`-Manifeste kennzeichnen sie als `legacy-collection`; sie sind keine aktiven Top-Level-Räume mehr. Inhalte werden weiterhin einzeln als `keep`, `move`, `split`, `archive` oder `delete` klassifiziert.

Der Repository-Cutover ist versioniert. Ob eine bereits laufende lokale Cabinet-Instanz den neuen Baum eingelesen hat, muss nach Pull und Neustart durch einen Runtime-Smoke bestätigt werden.
