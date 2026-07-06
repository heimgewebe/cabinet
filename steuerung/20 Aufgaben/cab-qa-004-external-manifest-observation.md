# CAB-QA-004 — Externe Manifestreferenzen beobachten

Status: blocked — no valid external manifest observed
Datum: 2026-07-05
Organfuehrung: Cabinet -> RepoBrief/Lenskit

## Entscheidung

Cabinet soll externe RepoBrief-/Lenskit-Dumps nicht erzeugen. Nach CAB-QA-003 kann Cabinet aber pruefen, ob externe Manifestreferenzen beobachtet und formal vertragskonform registriert sind.

## These

Der External-Dump-Quellenvertrag ist wirksam: Die Spezifikation existiert, und der Maintenance Report hat keine epistemische Spezifikationsluecke mehr.

## Antithese

Ohne konkrete `latestManifestPath`- und `latestManifestGeneratedAt`-Werte bleiben die registrierten Quellen nur erwartete Oberflaechen. Das ist keine Freshness-Evidenz und erst recht keine Claim-Wahrheit.

## Synthese

CAB-QA-004 beobachtet externe Manifestreferenzen read-only. Wenn RepoBrief/Lenskit gueltige Manifestorte liefern, darf Cabinet nur diese Referenzen in `registry/ecosystem/external-dump-sources.json` eintragen. Wenn sie fehlen, bleibt die Leerstelle sichtbar.

## Scope

- Externe RepoBrief-/Lenskit-Manifestorte fuer `cabinet` und `main` pruefen.
- Nur belegte relative Pfade eintragen, die `manifestPattern` erfuellen.
- `latestManifestGeneratedAt` nur aus dem externen Manifest bzw. dessen verifizierter Metadatenquelle uebernehmen.
- `scripts/validate_external_dump_sources.py` und den Maintenance Report erneut laufen lassen.
- Keine Dump-Erzeugung, keine Bureau-Task-Erzeugung, kein Runtime-Effekt.

## Stop-Kriterium

Stop, wenn kein aktuelles externes Manifest belegbar ist, ein Pfad nicht zum Contract passt oder die Quelle nur informell behauptet statt reproduzierbar nachweisbar ist.

## Target-Proof

- `python3 scripts/validate_external_dump_sources.py`
- `python3 scripts/write_cabinet_maintenance_report.py --check --json`
- Maintenance Report zeigt entweder weniger `manifest-unobserved`-Findings oder eine explizit dokumentierte Leerstelle.

## Epistemische Leere

Aktuelle externe Manifestreferenzen fehlen weiterhin. Noetig fuer Freshness-Scan ueber konkrete RepoBrief-/Lenskit-Dumps. Beobachtung 2026-07-06 dokumentiert die Leerstelle ohne Registry-Mutation.

## Beobachtung 2026-07-06

Ergebnis: Stop, keine Registry-Aktualisierung.

Begruendung: Im Cabinet-Repo existiert kein `external/`-Manifestpfad. In `/home/alex/repos/merges` wurden fuer Cabinet nur alte `*_merge.output_health.json`-Sidecars und Source-Card-Verzeichnisse gesehen, aber kein aktuelles `*_merge.bundle.manifest.json` oder `*_merge.agent_entry_manifest.json`. iCloud-Manifesttreffer waren nicht als Cabinet-RepoBrief-/Lenskit-Dumpmanifest belegbar.

Befund: `pruefung/30 Befunde/cab-qa-004-external-manifest-observation-2026-07-06.md`
