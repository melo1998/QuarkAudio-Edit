"""
Generate small, valid placeholder .wav files for every audio path referenced
in ``assets/js/data.js``.

This script is intentionally *not* a silent-no-op: it writes real, playable
WAV files (2-second mono 22.05 kHz silence, ~88 KB each) so that the demo
page's <audio> elements never produce a 404 during review. Replace these
placeholders with your real generations when ready.

Usage (from the demo_page/ directory):
    python _tools/generate_placeholder_audio.py

The script is idempotent: it only writes files that are currently missing.
Pass --force to overwrite existing files.
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import sys
import wave
from pathlib import Path
from typing import List


HERE = Path(__file__).resolve().parent
DEMO_ROOT = HERE.parent
DATA_JS = DEMO_ROOT / "assets" / "js" / "data.js"


def extract_audio_paths(data_js_text: str) -> List[str]:
    """Pull out every ``assets/audio/...`` path from data.js."""
    # Matches both single- and double-quoted string literals that begin with
    # ``assets/audio/`` and end with a common audio extension.
    pattern = re.compile(
        r"""['"](assets/audio/[^'"]+\.(?:wav|mp3|ogg|flac|m4a))['"]""",
        re.IGNORECASE,
    )
    # Preserve order, deduplicate.
    seen: set[str] = set()
    ordered: List[str] = []
    for match in pattern.finditer(data_js_text):
        path = match.group(1)
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered


def write_silent_wav(target: Path, duration_s: float = 2.0,
                     sample_rate: int = 22050) -> None:
    """Write a mono 16-bit PCM WAV file filled with silence."""
    target.parent.mkdir(parents=True, exist_ok=True)
    num_frames = int(duration_s * sample_rate)
    silence_frame = struct.pack("<h", 0)  # int16 little-endian zero
    with wave.open(str(target), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(silence_frame * num_frames)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing WAV files (default: skip existing).",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=2.0,
        help="Placeholder duration in seconds (default: 2.0).",
    )
    args = parser.parse_args()

    if not DATA_JS.is_file():
        print(f"[ERROR] data.js not found at: {DATA_JS}", file=sys.stderr)
        return 1

    paths = extract_audio_paths(DATA_JS.read_text(encoding="utf-8"))
    if not paths:
        print("[ERROR] No audio paths found in data.js", file=sys.stderr)
        return 1

    print(f"Discovered {len(paths)} audio path(s) in data.js")
    print("-" * 70)

    created = 0
    skipped = 0
    for rel_path in paths:
        abs_path = DEMO_ROOT / rel_path
        if abs_path.exists() and not args.force:
            print(f"[SKIP]    {rel_path}  (already exists)")
            skipped += 1
            continue

        # Only generate for .wav; other extensions require an encoder
        # (ffmpeg/lame) which is out of scope for this bootstrap script.
        if abs_path.suffix.lower() != ".wav":
            print(f"[WARN]    {rel_path}  (non-wav extension, skipping)")
            skipped += 1
            continue

        write_silent_wav(abs_path, duration_s=args.duration)
        size_kb = abs_path.stat().st_size / 1024
        print(f"[CREATED] {rel_path}  ({size_kb:.1f} KB)")
        created += 1

    print("-" * 70)
    print(f"Summary: {created} created, {skipped} skipped, {len(paths)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
