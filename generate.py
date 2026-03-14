#!/usr/bin/env python3
"""PrettyDiagrams — Rendert SVG Blueprints als handgezeichnete Illustrationen.

Pipeline:
1. SVG Blueprint lesen (oder via --prompt generieren lassen)
2. IMAGE Placeholders parsen und via Tavily auflösen
3. Rendering via Kie.ai (nano-banana-pro) oder Google Gemini
4. PNG speichern

Backends: kie (async polling), gemini (synchron).
Basiert auf Tyler Germain's Graphics-Diagram Konzept.
"""

import argparse
import base64
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Config ---
KIE_API_URL = "https://api.kie.ai/api/v1/jobs/createTask"
KIE_POLL_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
KIE_API_KEY = os.environ.get("KIE_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-pro-image-preview")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
PRETTYDIAGRAMS_BACKEND = os.environ.get("PRETTYDIAGRAMS_BACKEND", "kie")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

POLL_INTERVAL = 3  # Sekunden
POLL_TIMEOUT = 600  # 10 Minuten max

IMAGE_PLACEHOLDER_RE = re.compile(r"<!--\s*IMAGE:\s*(.+?)\s*-->")

SYSTEM_PROMPT = """\
You are a world-class illustrator specializing in hand-drawn, \
sketchy editorial diagrams. Render the following SVG blueprint as a \
beautiful hand-drawn illustration. \
IMPORTANT: Preserve the EXACT colors from the SVG — use the fill and stroke \
colors as specified in the markup. Do not substitute or shift colors. \
If the background is white (#FFFFFF), keep it pure white. \
If a color is red (#EC0016), render it as true red, not orange or coral. \
Use a playful but professional aesthetic with Comic Neue-style lettering. \
Keep all text readable. Add small decorative elements like stars, \
confetti, and squiggles where appropriate."""


def parse_image_placeholders(svg_content: str) -> list[str]:
    """Extrahiert IMAGE Placeholder-Beschreibungen aus dem SVG."""
    placeholders = IMAGE_PLACEHOLDER_RE.findall(svg_content)
    if placeholders:
        logger.info("Gefunden: %d IMAGE Placeholders", len(placeholders))
        for i, p in enumerate(placeholders, 1):
            logger.info("  [%d] %s", i, p)
    return placeholders[:6]  # Max 6


def search_images_tavily(queries: list[str]) -> list[dict]:
    """Sucht Referenzbilder via Tavily Image Search API.

    Returns: Liste von {query, url} Dicts.
    """
    if not TAVILY_API_KEY:
        logger.info("Kein TAVILY_API_KEY — überspringe Bildersuche")
        return []

    results = []
    with httpx.Client(timeout=15) as client:
        for query in queries:
            try:
                resp = client.post(
                    TAVILY_SEARCH_URL,
                    json={
                        "api_key": TAVILY_API_KEY,
                        "query": query,
                        "include_images": True,
                        "max_results": 1,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                images = data.get("images", [])
                if images:
                    img_url = images[0] if isinstance(images[0], str) else images[0].get("url", "")
                    results.append({
                        "query": query,
                        "url": img_url,
                    })
                    logger.info("Tavily: '%s' → %s", query, img_url[:80])
                else:
                    logger.info("Tavily: '%s' → keine Bilder gefunden", query)
            except Exception as e:
                logger.warning("Tavily-Suche fehlgeschlagen für '%s': %s", query, e)

    return results


def download_image(url: str) -> bytes | None:
    """Lädt ein Bild herunter und gibt die Bytes zurück."""
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.content
    except Exception as e:
        logger.warning("Bild-Download fehlgeschlagen: %s — %s", url[:80], e)
        return None


def build_prompt(svg_content: str, extra_prompt: str | None = None) -> str:
    """Baut den vollständigen Prompt."""
    parts = [SYSTEM_PROMPT]
    if extra_prompt:
        parts.append(f"\nAdditional context: {extra_prompt}")
    parts.append(f"\n\n--- SVG BLUEPRINT ---\n{svg_content}")
    return "\n".join(parts)


def submit_to_kie(
    prompt: str,
    reference_images: list[bytes] | None = None,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
) -> str | None:
    """Sendet den Rendering-Auftrag an Kie.ai. Gibt taskId zurück."""
    if not KIE_API_KEY:
        logger.error("KIE_API_KEY nicht gesetzt!")
        return None

    # Referenzbilder als base64-encoded input images
    image_inputs = []
    if reference_images:
        for img_bytes in reference_images:
            b64 = base64.b64encode(img_bytes).decode()
            image_inputs.append(f"data:image/png;base64,{b64}")

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": "png",
        },
    }

    if image_inputs:
        payload["input"]["image_input"] = image_inputs

    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(KIE_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") == 200:
                task_id = data["data"]["taskId"]
                logger.info("Kie.ai Task erstellt: %s", task_id)
                return task_id
            else:
                logger.error("Kie.ai Fehler: %s", data)
                return None
    except Exception as e:
        logger.error("Kie.ai Request fehlgeschlagen: %s", e)
        return None


def submit_to_gemini(
    prompt: str,
    reference_images: list[bytes] | None = None,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
) -> bytes | None:
    """Sendet den Rendering-Auftrag an Google Gemini. Synchron — gibt PNG-Bytes zurück."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY nicht gesetzt!")
        return None

    # Prompt als Text-Part
    parts: list[dict] = [{"text": prompt}]

    # Referenzbilder als inline_data Parts
    if reference_images:
        for img_bytes in reference_images:
            b64 = base64.b64encode(img_bytes).decode()
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": b64,
                },
            })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution,
            },
        },
    }

    url = f"{GEMINI_API_URL}/{GEMINI_MODEL}:generateContent"

    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                url,
                params={"key": GEMINI_API_KEY},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            # Bild aus Response extrahieren
            candidates = data.get("candidates", [])
            if not candidates:
                logger.error("Gemini: Keine Candidates in Response")
                return None

            for part in candidates[0].get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    img_bytes = base64.b64decode(inline["data"])
                    logger.info("Gemini: Bild erhalten (%.1f KB)", len(img_bytes) / 1024)
                    return img_bytes

            logger.error("Gemini: Kein Bild in Response gefunden")
            return None

    except httpx.HTTPStatusError as e:
        logger.error("Gemini API Fehler %d: %s", e.response.status_code, e.response.text[:500])
        return None
    except Exception as e:
        logger.error("Gemini Request fehlgeschlagen: %s", e)
        return None


def poll_result(task_id: str) -> str | None:
    """Pollt das Ergebnis bis es fertig ist. Gibt die Bild-URL zurück."""
    headers = {"Authorization": f"Bearer {KIE_API_KEY}"}
    start = time.time()

    with httpx.Client(timeout=15) as client:
        while time.time() - start < POLL_TIMEOUT:
            try:
                resp = client.get(
                    KIE_POLL_URL,
                    params={"taskId": task_id},
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                state = data.get("state", "unknown")

                if state == "success":
                    result_json = json.loads(data.get("resultJson", "{}"))
                    urls = result_json.get("resultUrls", [])
                    if urls:
                        elapsed = time.time() - start
                        logger.info("Rendering fertig in %.1fs: %s", elapsed, urls[0][:80])
                        return urls[0]
                    logger.error("Task erfolgreich aber keine resultUrls: %s", data)
                    return None

                elif state == "fail":
                    logger.error("Rendering fehlgeschlagen: %s — %s",
                                 data.get("failCode"), data.get("failMsg"))
                    return None

                else:
                    elapsed = int(time.time() - start)
                    logger.info("Status: %s (%ds)", state, elapsed)

            except Exception as e:
                logger.warning("Poll-Fehler: %s", e)

            time.sleep(POLL_INTERVAL)

    logger.error("Timeout nach %ds", POLL_TIMEOUT)
    return None


def download_result(url: str, output_path: Path) -> bool:
    """Lädt das fertige Bild herunter."""
    img_bytes = download_image(url)
    if img_bytes:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(img_bytes)
        logger.info("Gespeichert: %s (%.1f KB)", output_path, len(img_bytes) / 1024)
        return True
    return False


def generate(
    svg_content: str,
    output_path: Path,
    extra_prompt: str | None = None,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
    no_images: bool = False,
    backend: str | None = None,
) -> bool:
    """Komplette Pipeline: SVG → Tavily → Kie.ai/Gemini → PNG."""
    backend = backend or PRETTYDIAGRAMS_BACKEND
    logger.info("Backend: %s", backend)

    # 1. Image Placeholders auflösen
    reference_images = []
    if not no_images:
        placeholders = parse_image_placeholders(svg_content)
        if placeholders:
            tavily_results = search_images_tavily(placeholders)
            for result in tavily_results:
                img_bytes = download_image(result["url"])
                if img_bytes:
                    reference_images.append(img_bytes)
                    logger.info("Referenzbild geladen: %s", result["query"])

    # 2. Prompt bauen
    prompt = build_prompt(svg_content, extra_prompt)
    logger.info("Prompt: %d Zeichen, %d Referenzbilder", len(prompt), len(reference_images))

    # 3. Rendering (primary backend with fallback)
    backends = [backend]
    fallback = "kie" if backend == "gemini" else "gemini"
    fallback_key = KIE_API_KEY if fallback == "kie" else GEMINI_API_KEY
    if fallback_key:
        backends.append(fallback)

    for attempt_backend in backends:
        logger.info("Versuche Backend: %s", attempt_backend)

        if attempt_backend == "gemini":
            img_bytes = submit_to_gemini(
                prompt=prompt,
                reference_images=reference_images,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
            )
            if img_bytes:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(img_bytes)
                logger.info("Gespeichert: %s (%.1f KB)", output_path, len(img_bytes) / 1024)
                return True
            logger.warning("Gemini fehlgeschlagen")

        elif attempt_backend == "kie":
            task_id = submit_to_kie(
                prompt=prompt,
                reference_images=reference_images,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
            )
            if task_id:
                result_url = poll_result(task_id)
                if result_url and download_result(result_url, output_path):
                    return True
            logger.warning("Kie.ai fehlgeschlagen")

        else:
            logger.error("Unbekanntes Backend: %s (erlaubt: kie, gemini)", attempt_backend)

        if attempt_backend != backends[-1]:
            logger.info("Fallback auf %s...", backends[backends.index(attempt_backend) + 1])

    logger.error("Alle Backends fehlgeschlagen")
    return False


def main():
    parser = argparse.ArgumentParser(description="PrettyDiagrams — SVG zu handgezeichneter Illustration")
    parser.add_argument("--svg", type=str, help="Pfad zur SVG Blueprint-Datei")
    parser.add_argument("--prompt", type=str, help="Zusätzlicher Prompt-Text")
    parser.add_argument("-o", "--output", type=str, default="output/diagram.png", help="Output-Pfad (default: output/diagram.png)")
    parser.add_argument("--aspect-ratio", type=str, default="16:9", help="Seitenverhältnis (default: 16:9)")
    parser.add_argument("--resolution", type=str, default="2K", choices=["1K", "2K", "4K"], help="Auflösung (default: 2K)")
    parser.add_argument("--backend", type=str, choices=["kie", "gemini"], help="Rendering-Backend (default: PRETTYDIAGRAMS_BACKEND oder kie)")
    parser.add_argument("--no-images", action="store_true", help="Keine Tavily-Bildersuche")
    args = parser.parse_args()

    if not args.svg and not args.prompt:
        parser.error("--svg oder --prompt ist erforderlich")

    if args.svg:
        svg_path = Path(args.svg)
        if not svg_path.exists():
            logger.error("SVG-Datei nicht gefunden: %s", svg_path)
            sys.exit(1)
        svg_content = svg_path.read_text()
    else:
        # Wenn nur --prompt gegeben: minimales SVG als Wrapper
        svg_content = f"""\
<svg viewBox="0 0 900 550" xmlns="http://www.w3.org/2000/svg">
  <!-- Placeholder SVG — Nano Banana Pro will generate from prompt -->
  <text x="450" y="275" text-anchor="middle" font-size="24">{xml_escape(args.prompt)}</text>
</svg>"""

    output_path = Path(args.output)

    success = generate(
        svg_content=svg_content,
        output_path=output_path,
        extra_prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        no_images=args.no_images,
        backend=args.backend,
    )

    if success:
        logger.info("Fertig!")
    else:
        logger.error("Generierung fehlgeschlagen")
        sys.exit(1)


if __name__ == "__main__":
    main()
