# PrettyDiagrams

Generiert handgezeichnete Sketchnote-Diagramme aus Textbeschreibungen.

## Pipeline

1. **SVG Blueprint** — Claude generiert ein strukturiertes SVG mit 6 Layern und `<!-- IMAGE: ... -->` Placeholders
2. **QA Critique** — Sub-Agent prüft Overlaps, Spacing, Alignment und fixt Probleme
3. **Image Resolution** — Placeholders werden via Tavily Image Search in echte Referenzbilder aufgelöst
4. **Rendering** — Kie.ai Nano Banana Pro (Gemini) rendert das SVG als handgezeichnete Illustration (PNG)

## Architektur

```
User Prompt
    ↓
Claude Code (SVG Blueprint + QA)
    ↓
generate.py (Tavily + Kie.ai API)
    ↓
Hand-drawn PNG
```

## Usage

```bash
# SVG Blueprint generieren lassen (manuell oder via Chat Agent)
# Dann rendern:
python generate.py --svg blueprint.svg -o output.png

# Oder direkt aus Prompt:
python generate.py --prompt "How Kubernetes networking works" -o output.png
```

## ENV

- `KIE_API_KEY` — Kie.ai API Key (required)
- `TAVILY_API_KEY` — Tavily Search API Key (optional, für Referenzbilder)

## SVG Blueprint Regeln

- ViewBox: `0 0 900 550`
- 6 Layer (bottom→top): Background → Containers → Connectors → Icons/Figures → Text/Badges → Decorations + IMAGE Placeholders
- Keine `<rect>` — nur `<path>` mit 1-3px Wobble für Hand-drawn Feel
- Bezier Curves für Pfeile, Polygon-Heads
- Fonts: Comic Neue, Segoe Print, Patrick Hand
- Max 6 `<!-- IMAGE: beschreibung -->` Placeholders
- Layout-Patterns: Flow/Pipeline, Fan-Out, Convergence, Panel Grid, Central Hub, Before/After

## Integration

Wird später in den A2A Chat Agent (`#diagrams` Channel) integriert.
