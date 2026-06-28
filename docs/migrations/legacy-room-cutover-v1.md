# Legacy-Room-Visibility-Cutover v1

## Zweck

Dieser Cutover trennt die aktive Navigation von der historischen Ablage.

Ziel sind genau drei aktive Räume: `bestand`, `pruefung` und `steuerung`. Die sechs alten Verzeichnisse bleiben vollständig versioniert und lesbar; erst der kontrollierte Apply-Schritt entfernt ihre Room-Manifeste und ersetzt sie durch Legacy-Marker.

## Sicherheitsprinzip

Der Cutover löscht keine Fachinhalte und verschiebt keine Inhaltsdatei automatisch. Er verändert nur die Raum-Erkennung, den Layoutvertrag und die maschinenlesbaren Migrationsmarker.

Vor jeder Änderung werden die betroffenen Manifestbytes und die Layout-Policy außerhalb des Repositories gesichert. Ein Mischzustand wird abgewiesen. Bei einem Fehler wird automatisch zurückgerollt.

## Bedienung

Quell- oder Zielzustand prüfen:

```bash
python3 scripts/legacy_room_visibility_cutover.py check
```

Cutover transaktional auf den ausgecheckten Branch anwenden:

```bash
python3 scripts/legacy_room_visibility_cutover.py apply
```

Danach werden die erzeugten Änderungen wie ein normaler Patch geprüft und committet. Ein Backup kann explizit zurückgerollt werden:

```bash
python3 scripts/legacy_room_visibility_cutover.py rollback BACKUP-ID
```

## Folgearbeit

Jede Inhaltsdatei wird später anhand belegter Consumer und Links als `keep`, `move`, `split`, `archive` oder `delete` klassifiziert. Bis dahin bleibt ihr alter Pfad erhalten.

Ein erfolgreicher Repositorytest belegt die Struktur des versionierten Snapshots. Er belegt nicht, dass eine bereits laufende lokale Cabinet-Instanz den neuen Baum ohne Neustart eingelesen hat.
