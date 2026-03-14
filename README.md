# PrettyDiagrams

Generate hand-drawn sketchnote-style diagrams from text descriptions. Uses SVG blueprints as input and renders them as beautiful hand-drawn illustrations via [Kie.ai](https://kie.ai) or Google Gemini.

![How to create a PrettyDiagram](examples/prettydiagrams-workflow.png)

## How it works

```
Text description → SVG Blueprint (6 layers) → Kie.ai / Gemini → Hand-drawn PNG
```

1. Describe what you want (architecture, workflow, concept)
2. An SVG blueprint is generated following strict layout rules
3. The SVG is sent to an image generation model (Nano Banana Pro)
4. You get a hand-drawn illustration back as PNG

## Quick start

### As Claude Code plugin

```bash
/plugin marketplace add Jadefalkner/jadefalkner-plugins
/plugin install prettydiagrams@jadefalkner-plugins
```

Then use `/prettydiagrams:prettydiagram` to create diagrams.

### Standalone

```bash
git clone https://github.com/Jadefalkner/prettydiagrams.git
cd prettydiagrams
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```bash
# Option A: Google Gemini (recommended, free tier available)
PRETTYDIAGRAMS_BACKEND=gemini
GEMINI_API_KEY=your-key-here

# Option B: Kie.ai (~$0.09/image)
PRETTYDIAGRAMS_BACKEND=kie
KIE_API_KEY=your-key-here

# Optional: reference image search
TAVILY_API_KEY=your-key-here
```

Render a diagram:

```bash
python generate.py --svg examples/prettydiagrams-workflow.svg -o output.png
python generate.py --prompt "How Kubernetes networking works" -o output.png
```

### Options

```
--svg PATH          SVG blueprint file
--prompt TEXT       Additional prompt text
-o, --output PATH  Output path (default: output/diagram.png)
--backend kie|gemini  Override backend
--resolution 1K|2K|4K  Resolution (default: 2K)
--aspect-ratio      Aspect ratio (default: 16:9)
--no-images         Skip Tavily image search
```

## Color schemes

| Scheme | Background | Style |
|--------|-----------|-------|
| `red-white` (default) | White | Bold red, dark gray, clean and modern |
| `red` | Light gray | Same red palette, light gray background |
| `warm` | Cream | Whiteboard/sketchnote — coral, blue, green |
| `ocean` | Ice blue | Professional — navy, teal, seafoam |
| `neon` | Dark navy | Tech/modern — hot pink, cyan, lime |

## SVG blueprint rules

Blueprints follow a strict 6-layer structure:

1. **Background** — base color with wobbly border
2. **Containers** — colored boxes as `<path>` (not `<rect>`!) with 1-3px wobble
3. **Connectors** — bezier curves, dashed/solid, polygon arrow heads
4. **Icons/Figures** — inline SVG or `<!-- IMAGE: description -->` placeholders
5. **Text/Badges** — labels, pill badges
6. **Decorations** — emoji, stars, confetti (max 4-5)

ViewBox is always `0 0 900 550`. Max 8 containers. See [svg-rules.md](skills/prettydiagram/references/svg-rules.md) for full spec.

## Backends

Both backends use the same underlying model (Nano Banana Pro / gemini-3-pro-image-preview). If both API keys are configured, the primary backend is tried first. On failure, the other is used as fallback.

| | Google Gemini (default) | Kie.ai |
|---|---|---|
| API Key | `GEMINI_API_KEY` | `KIE_API_KEY` |
| Pricing | Google AI free tier / pay-as-you-go | 18 credits (~$0.09) / image |
| Model | `gemini-3-pro-image-preview` | `nano-banana-pro` |
| Model override | `GEMINI_MODEL` env var | — |

## Integration

PrettyDiagrams can be integrated into any tool that can call Python scripts. The `generate.py` CLI is the main entry point — pass it an SVG file and get a PNG back.

## License

[MIT](LICENSE)
