# SVG Blueprint Regeln

## ViewBox
- Immer `0 0 900 550`

## 6 Layer (bottom → top)
1. **Background** — Warm cream `#FDF6E3`, wobbly `<path>` border (1-3px offset)
2. **Containers** — Farbige Boxen als `<path>` (nicht `<rect>`!), 1-3px Wobble für Hand-drawn Feel
3. **Connectors** — Bezier Curves (`C`), dashed für hierarchisch, solid für Datenfluss. `<polygon>` Arrow-Heads
4. **Icons/Figures** — Kleine SVG-Inline-Icons oder `<!-- IMAGE: beschreibung -->` Placeholders
5. **Text/Badges** — Labels, Pill-Badges (`<rect rx>`), Beschriftungen
6. **Decorations** — Emoji-Deko, Sterne, Confetti (sparsam, max 4-5)

## Farbschemata

### `warm` (Default) — Whiteboard/Sketchnote
- Background: `#FDF6E3` (Cream)
- Containers: Coral `#E8927C`, Blue `#B4D7E8`, Green `#D4E8B4`, Gold `#FFE4B8`, Lavender `#E8D5E8`, Tan `#E8D5B7`
- Connectors: Coral `#E8927C`, Green `#7FB069`, Purple `#9B8EC4`
- Badges: Coral `#E8927C` (white text), Green `#7FB069` (white text), Gold `#FFD4B8` (dark text)
- Stroke: `#333`, Text: `#333`/`#666`

### `ocean` — Ruhig/Professionell
- Background: `#EDF4F8` (Ice Blue)
- Containers: Navy `#2C3E6B`, Teal `#A8D5D8`, Seafoam `#C4E3CB`, Sand `#F0E4CC`, Coral `#E8927C`, Slate `#8B9DAF`
- Connectors: Navy `#2C3E6B`, Teal `#5BA4A4`, Coral `#D4735C`
- Badges: Navy `#2C3E6B` (white text), Teal `#5BA4A4` (white text), Sand `#D4C4A0` (dark text)
- Stroke: `#2C3E6B`, Text: `#2C3E6B`/`#5A6B7F`

### `neon` — Tech/Modern
- Background: `#1A1A2E` (Dark Navy)
- Containers: Electric `#0F3460`, Hot Pink `#E94560`, Lime `#53D769`, Orange `#FF8C42`, Cyan `#00D4FF`, Purple `#7B2FBE`
- Connectors: Cyan `#00D4FF`, Pink `#E94560`, Lime `#53D769`
- Badges: Pink `#E94560` (white text), Cyan `#00D4FF` (dark text), Lime `#53D769` (dark text)
- Stroke: `#4A4A6A`, Text: `#E0E0E0`/`#8888AA`

### `red-white` (Default) — Deutsche Bahn CI, weißer Hintergrund
- Background: `#FFFFFF` (Weiß)
- Containers: DB Red `#EC0016`, Dark Red `#8C0009`, Cool Gray `#282D37`, Warm Gray `#878C96`, White `#FFFFFF` (mit Stroke), Light Gray `#DBDFE3`
- Connectors: DB Red `#EC0016`, Dark `#282D37`, Warm Gray `#646973`
- Badges: DB Red `#EC0016` (white text), Dark `#282D37` (white text), Light Gray `#DBDFE3` (dark text)
- Stroke: `#282D37`, Text: `#282D37`/`#646973`

### `red` — Deutsche Bahn CI
- Background: `#F0F3F5` (Cool Gray Light)
- Containers: DB Red `#EC0016`, Dark Red `#8C0009`, Cool Gray `#282D37`, Warm Gray `#878C96`, White `#FFFFFF`, Light Gray `#DBDFE3`
- Connectors: DB Red `#EC0016`, Dark `#282D37`, Warm Gray `#646973`
- Badges: DB Red `#EC0016` (white text), Dark `#282D37` (white text), Light Gray `#DBDFE3` (dark text)
- Stroke: `#282D37`, Text: `#282D37`/`#646973`

## Styling
- Fonts: `Comic Neue, Segoe Print, Patrick Hand, cursive`
- Keine `<rect>` für Container — nur `<path>` mit leichtem Wobble (Q-Curves mit 1-3px Versatz)
- Farbpalette: Siehe gewähltes Schema oben (Default: `red-white`)
- Stroke/Text: Gemäß Schema
- Bezier Curves für alle Pfeile, Polygon-Heads

## IMAGE Placeholders
- Format: `<!-- IMAGE: kurze beschreibung -->`
- Max 6 pro Diagramm
- Werden via Tavily Image Search aufgelöst und als Referenzbilder an Kie.ai gesendet
- Platzierung: Innerhalb des zugehörigen Containers

## Layout-Patterns
- **Flow/Pipeline**: Links-nach-rechts oder oben-nach-unten
- **Fan-Out**: Ein Knoten → mehrere Ziele
- **Convergence**: Mehrere Quellen → ein Ziel
- **Panel Grid**: Gleichmäßig verteilte Boxen
- **Central Hub**: Zentraler Knoten mit Spokes
- **Before/After**: Zwei Hälften im Vergleich

## Typische Fehler (QA-Checkliste)
- Text-Overlaps: Mindestens 20px Abstand zwischen Textblöcken
- Container-Overlaps: Boxen dürfen sich nicht überlappen
- Pfeile ins Nichts: Jeder Connector muss Start- und Ziel-Element haben
- Unlesbarer Text: Mindestens font-size 10, Kontrast prüfen
- Zu viele Elemente: Max 8 Container, sonst wird es unübersichtlich
