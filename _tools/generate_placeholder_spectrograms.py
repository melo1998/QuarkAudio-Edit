"""
Generate synthetic placeholder mel-spectrogram images for the complex demo
section of the QuarkAudio-Edit demo page.

Each image simulates a realistic mel-spectrogram appearance using numpy +
Pillow (no matplotlib/librosa dependency required). Source and edited images
have visually distinguishable patterns so reviewers can see the intended
before/after contrast.

Usage (from the demo_page/ directory):
    python _tools/generate_placeholder_spectrograms.py

Generates 8 PNG files into assets/images/spectrograms/.
Idempotent: only writes files that are currently missing (use --force to overwrite).
"""
from __future__ import annotations

import argparse
import hashlib
import math
import struct
import sys
import zlib
from pathlib import Path
from typing import Tuple

HERE = Path(__file__).resolve().parent
DEMO_ROOT = HERE.parent
OUTPUT_DIR = DEMO_ROOT / "assets" / "images" / "spectrograms"

# 4 complex scenarios × {src, edited} = 8 images
SCENARIOS = [
    "urban_countryside",
    "rainy_cafe",
    "chase_scene",
    "energetic_remix",
]

# Image dimensions (width × height) — wide and short like a real spectrogram
WIDTH = 640
HEIGHT = 160


def seeded_random(seed: int, count: int) -> list:
    """Simple deterministic pseudo-random float list [0,1) from a seed."""
    values = []
    state = seed & 0xFFFFFFFF
    for _ in range(count):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        values.append((state >> 16) / 32768.0)
    return values


def generate_spectrogram_data(width: int, height: int, seed: int,
                              energy_level: float = 0.6,
                              high_freq_suppress: float = 0.7) -> list:
    """
    Generate a 2D array (height x width) of float values [0, 1] that
    visually resembles a mel-spectrogram.

    Parameters:
        energy_level: overall brightness (higher = more energy)
        high_freq_suppress: how much to attenuate high frequency bins (top rows)
    """
    total_pixels = width * height
    noise = seeded_random(seed, total_pixels)

    data = []
    for y in range(height):
        row = []
        # Frequency weighting: lower rows (low freq) are brighter
        freq_weight = 1.0 - (y / height) * high_freq_suppress
        for x in range(width):
            idx = y * width + x
            base = noise[idx] * 0.5

            # Add some horizontal "formant" bands at certain frequencies
            band_factor = 0.0
            for band_center in [0.15, 0.30, 0.50, 0.72]:
                band_y = band_center * height
                dist = abs(y - band_y) / (height * 0.08)
                if dist < 1.0:
                    # Time-varying amplitude for the band
                    time_phase = (x / width) * 6.0 + seed * 0.1
                    band_amp = 0.3 * (0.5 + 0.5 * math.sin(time_phase))
                    band_factor += band_amp * (1.0 - dist)

            # Temporal envelope: slight fade in/out
            time_env = min(x / (width * 0.05), 1.0) * min((width - x) / (width * 0.05), 1.0)

            value = (base + band_factor) * freq_weight * energy_level * time_env
            value = max(0.0, min(1.0, value))
            row.append(value)
        data.append(row)
    return data


def value_to_rgb(value: float, colormap: str = "magma") -> Tuple[int, int, int]:
    """Map a float [0,1] to an RGB tuple using a simplified colormap."""
    value = max(0.0, min(1.0, value))

    if colormap == "magma":
        # Simplified magma-like colormap: black → purple → orange → yellow
        if value < 0.25:
            t = value / 0.25
            r = int(t * 30)
            g = int(t * 10)
            b = int(20 + t * 60)
        elif value < 0.5:
            t = (value - 0.25) / 0.25
            r = int(30 + t * 130)
            g = int(10 + t * 20)
            b = int(80 + t * 40)
        elif value < 0.75:
            t = (value - 0.5) / 0.25
            r = int(160 + t * 70)
            g = int(30 + t * 80)
            b = int(120 - t * 80)
        else:
            t = (value - 0.75) / 0.25
            r = int(230 + t * 25)
            g = int(110 + t * 140)
            b = int(40 - t * 30)
    else:
        # Viridis-like fallback
        r = int(value * 200)
        g = int(50 + value * 180)
        b = int(120 - value * 80)

    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def write_png(filepath: Path, width: int, height: int, pixels: list) -> None:
    """
    Write a minimal valid PNG file without external dependencies.
    pixels: list of height rows, each row is list of (r, g, b) tuples.
    """
    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk + struct.pack(">I", crc)

    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b"IHDR", ihdr_data)

    # IDAT (raw pixel data with filter byte 0 per row)
    raw_data = b""
    for row in pixels:
        raw_data += b"\x00"  # filter: None
        for r, g, b in row:
            raw_data += struct.pack("BBB", r, g, b)
    compressed = zlib.compress(raw_data, 9)
    idat = make_chunk(b"IDAT", compressed)

    # IEND
    iend = make_chunk(b"IEND", b"")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(signature + ihdr + idat + iend)


def generate_image(scenario: str, variant: str, force: bool = False) -> bool:
    """Generate a single spectrogram image. Returns True if created."""
    filename = f"{scenario}_{variant}.png"
    filepath = OUTPUT_DIR / filename

    if filepath.exists() and not force:
        print(f"[SKIP]    {filename}  (already exists)")
        return False

    # Use scenario + variant as seed for deterministic but distinct patterns
    seed_str = f"{scenario}_{variant}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)

    # Source images: moderate energy, standard suppression
    # Edited images: different energy profile to show audible change
    if variant == "src":
        energy = 0.55
        suppress = 0.65
    else:
        # Edited: higher energy, less suppression (brighter, more complex)
        energy = 0.72
        suppress = 0.50

    # Scenario-specific tweaks
    if "chase" in scenario and variant == "edited":
        energy = 0.85  # Chase scene: very energetic
    elif "countryside" in scenario and variant == "edited":
        energy = 0.40
        suppress = 0.80  # Countryside: quieter, more high-freq suppression

    spec_data = generate_spectrogram_data(WIDTH, HEIGHT, seed, energy, suppress)

    # Convert to RGB pixels
    pixels = []
    for row in spec_data:
        pixel_row = [value_to_rgb(v) for v in row]
        pixels.append(pixel_row)

    write_png(filepath, WIDTH, HEIGHT, pixels)
    size_kb = filepath.stat().st_size / 1024
    print(f"[CREATED] {filename}  ({size_kb:.1f} KB)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing PNG files.")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Image size: {WIDTH} × {HEIGHT}")
    print("-" * 60)

    created = 0
    skipped = 0
    for scenario in SCENARIOS:
        for variant in ("src", "edited"):
            if generate_image(scenario, variant, force=args.force):
                created += 1
            else:
                skipped += 1

    print("-" * 60)
    print(f"Summary: {created} created, {skipped} skipped, "
          f"{len(SCENARIOS) * 2} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
