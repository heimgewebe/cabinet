# Befund — CAB-QA-004 externe Manifestreferenzen

Datum: 2026-07-06
Branch: `docs/cabqa4`
Quelle: lokaler `main` nach PR #74, `registry/ecosystem/external-dump-sources.json`, `/home/alex/repos/merges`, `/home/alex/iCloud/Drive`.

## These

CAB-QA-004 soll die nach PR #72/#73 noch offenen externen RepoBrief-/Lenskit-Manifestreferenzen beobachten und nur belegte Referenzen in Cabinet registrieren.

## Antithese

Ein vorhandenes Merge-Artefakt oder ein `output_health`-Sidecar ist noch kein gültiges Manifest im Sinne des neuen Contracts. Cabinet darf keine Scheinfreshness erzeugen, indem es alte oder unvollständige Artefakte als beobachtete Manifestquelle einträgt.

## Synthese

Keine Registry-Aktualisierung. Die Quellen bleiben `unobserved`. Der Lauf dokumentiert die Leerstelle und hält CAB-QA-004 blockiert, bis RepoBrief/Lenskit ein passendes Manifest liefert.

## Belegt

- `registry/ecosystem/external-dump-sources.json` enthält weiterhin zwei Quellen: `external-dump:repobrief` und `external-dump:lenskit`.
- Beide Quellen stehen auf `observation.status = unobserved`.
- Im Cabinet-Repo existiert kein `external/`-Manifestpfad.
- In `/home/alex/repos/merges` wurden fuer `cabinet` nur alte `cabinet-max-..._merge.output_health.json` sowie Source-Card-Verzeichnisse gesehen.
- Fuer `cabinet` wurde dort kein `*_merge.bundle.manifest.json` und kein `*_merge.agent_entry_manifest.json` gesehen.
- In `/home/alex/iCloud/Drive` gefundene Manifest-Dateien gehoerten nicht zu einem aktuellen Cabinet-RepoBrief-/Lenskit-Dumpmanifest.

## Nicht als Beleg akzeptiert

- `*_merge.output_health.json` allein.
- Source-Card-Verzeichnisse ohne Bundle-Manifest.
- Lenskit-Schema-Dateien fuer Manifestformate.
- Beliebige `manifest.json`-Dateien ohne Bezug zu `external/{family}/{repository}/{ref}/manifest.json`.

## Ergebnis

CAB-QA-004 wird als beobachteter Stop dokumentiert. Die korrekte naechste Aktion bleibt bei RepoBrief/Lenskit: ein aktuelles, relatives Manifest fuer `cabinet/main` publizieren oder einen stabilen Manifest-Ort benennen.

## Registry-Entscheidung

`registry/ecosystem/external-dump-sources.json` bleibt unveraendert. Das ist Absicht: fehlende Evidenz ist keine beobachtete Quelle.

## Target-Proof

- External-Dump-Validator muss weiterhin PASS bleiben.
- Maintenance Report darf weiterhin `manifest-unobserved` melden.
- Es darf kein `latestManifestPath` eingetragen werden, solange kein contract-konformer Manifestpfad belegbar ist.
