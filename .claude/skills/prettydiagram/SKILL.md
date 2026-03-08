---
name: prettydiagram
description: >
  Generiert handgezeichnete Sketchnote-Diagramme aus Textbeschreibungen.
  Zweistufig: erst Plan zur Freigabe, dann SVG + Rendering via Kie.ai.
  Use when user asks for a diagram, sketch, illustration, or visual explanation
  of a concept, architecture, or workflow. Trigger phrases: "zeichne", "diagram",
  "sketchnote", "illustriere", "visualisiere".
---

# PrettyDiagram

Generiert handgezeichnete Sketchnote-Illustrationen aus Textbeschreibungen.

Base directory: /home/jadefalkner/work/prettydiagrams

## Workflow

### Schritt 1: Plan erstellen

Erstelle aus der Beschreibung des Users einen **kurzen, strukturierten Plan** im folgenden Format:

```
## Diagramm-Plan: <Titel>

**Farbschema**: <red-white | red | warm | ocean | neon>
**Detailgrad**: <minimal | standard | detailed>
**Layout**: <Pattern — z.B. Flow, Fan-Out, Central Hub, Panel Grid>
**Komponenten** (max 8):
- <Name> — <Farbe> — <kurze Beschreibung>
- ...

**Connectors**:
- <Von> → <Nach> — <Label, optional> — <Stil: solid/dashed>
- ...

**IMAGE Placeholders** (max 6):
- <!-- IMAGE: beschreibung -->
- ...

**Extras**: <Badges, Deko-Elemente>
```

**STOP hier.** Warte auf explizite Freigabe vom User bevor du weiterarbeitest.
In Mattermost zählt Daumen-hoch oder Haken als Freigabe.

### Schritt 2: SVG Blueprint generieren

Nach Freigabe: Generiere das SVG nach den Regeln in `references/svg-rules.md`.

Lies die Regeln:
```
Read references/svg-rules.md
```

Wichtig:
- ViewBox `0 0 900 550`
- Nur `<path>` mit Wobble, keine `<rect>` für Container
- 6 Layer einhalten
- QA: Prüfe auf Overlaps, Spacing, Lesbarkeit

Speichere das SVG unter `examples/<titel-slug>.svg`.

### Schritt 3: Rendering via Kie.ai

Führe aus:

```bash
cd /home/jadefalkner/work/prettydiagrams
source .venv/bin/activate 2>/dev/null || true
python generate.py --svg examples/<titel-slug>.svg -o output/<titel-slug>.png
```

Default: 2K Auflösung.

### Schritt 4: Ergebnis zeigen

Öffne das generierte Bild:

```bash
xdg-open output/<titel-slug>.png
```

Teile dem User den Pfad mit und frage ob Anpassungen gewünscht sind.

## Voraussetzungen

- `KIE_API_KEY` in `/home/jadefalkner/work/prettydiagrams/.env`
- `TAVILY_API_KEY` optional (für Referenzbilder aus IMAGE Placeholders)
- Python-Deps: `httpx`, `python-dotenv`
