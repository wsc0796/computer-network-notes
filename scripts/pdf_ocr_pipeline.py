#!/usr/bin/env python
"""PDF OCR pipeline for the Y7000P machine.

This script intentionally keeps the heavy work on the OCR machine:
PDF pages are rendered with PyMuPDF, optionally split into smaller image
tiles, recognized with PaddleOCR, and written to Markdown files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import shutil
import sys
import traceback
from collections.abc import Sequence
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a PDF, OCR each page/tile with PaddleOCR, and export Markdown text."
    )
    parser.add_argument("pdf_path", help="Input PDF path.")
    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Output directory. Existing generated images/text may be overwritten.",
    )
    parser.add_argument("--dpi", type=int, default=220, help="Render DPI. Default: 220.")
    parser.add_argument(
        "--max-tile-width",
        type=int,
        default=2600,
        help="Maximum image tile width in pixels before slicing. Default: 2600.",
    )
    parser.add_argument(
        "--max-tile-height",
        type=int,
        default=3200,
        help="Maximum image tile height in pixels before slicing. Default: 3200.",
    )
    parser.add_argument(
        "--lang",
        default="ch",
        help="PaddleOCR language code. Default: ch.",
    )
    parser.add_argument(
        "--keep-images",
        action="store_true",
        help="Keep rendered page and tile images after OCR.",
    )
    parser.add_argument(
        "--no-cls",
        action="store_true",
        help="Disable PaddleOCR angle classification.",
    )
    return parser.parse_args()


class RunLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("", encoding="utf-8")

    def write(self, message: str) -> None:
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")


def require_runtime() -> tuple[object, object, object]:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Missing dependency: PyMuPDF. Install with: pip install pymupdf") from exc

    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Missing dependency: Pillow. Install with: pip install pillow") from exc

    try:
        from paddleocr import PaddleOCR  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: paddleocr. Install PaddleOCR/PaddlePaddle on Y7000P first."
        ) from exc

    return fitz, Image, PaddleOCR


def reset_generated_dirs(output_dir: Path, keep_images: bool) -> tuple[Path, Path, Path]:
    page_text_dir = output_dir / "page_text"
    image_dir = output_dir / "images"
    tile_dir = output_dir / "tiles"

    for path in (page_text_dir, image_dir, tile_dir):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    if not keep_images:
        # Keep the directories during processing; cleanup happens after OCR.
        pass

    return page_text_dir, image_dir, tile_dir


def render_page(fitz: object, page: object, dpi: int, image_path: Path) -> tuple[int, int]:
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
    pixmap.save(str(image_path))
    return int(pixmap.width), int(pixmap.height)


def split_image_if_needed(
    Image: object,
    image_path: Path,
    tile_dir: Path,
    page_no: int,
    width: int,
    height: int,
    max_tile_width: int,
    max_tile_height: int,
) -> list[Path]:
    if width <= max_tile_width and height <= max_tile_height:
        return [image_path]

    cols = max(1, math.ceil(width / max_tile_width))
    rows = max(1, math.ceil(height / max_tile_height))
    tile_width = math.ceil(width / cols)
    tile_height = math.ceil(height / rows)
    tile_paths: list[Path] = []

    with Image.open(image_path) as image:
        for row in range(rows):
            for col in range(cols):
                left = col * tile_width
                upper = row * tile_height
                right = min(left + tile_width, width)
                lower = min(upper + tile_height, height)
                tile = image.crop((left, upper, right, lower))
                tile_path = tile_dir / f"page_{page_no:03d}_tile_{row + 1:02d}_{col + 1:02d}.png"
                tile.save(tile_path)
                tile_paths.append(tile_path)

    return tile_paths


def normalize_ocr_result(raw_result: object) -> list[tuple[str, float | None]]:
    """Handle common PaddleOCR v2/v3 result shapes without binding to one version."""
    lines: list[tuple[str, float | None]] = []

    if raw_result is None:
        return lines

    if isinstance(raw_result, dict):
        rec_texts = raw_result.get("rec_texts")
        rec_scores = raw_result.get("rec_scores") or []
        if isinstance(rec_texts, Sequence) and not isinstance(rec_texts, (str, bytes)):
            for index, text in enumerate(rec_texts):
                score = rec_scores[index] if index < len(rec_scores) else None
                lines.append((str(text), float(score) if isinstance(score, (int, float)) else None))
            return lines

    if isinstance(raw_result, list):
        # PaddleOCR often returns [page_lines] for one image. Unwrap one nesting level.
        if len(raw_result) == 1 and isinstance(raw_result[0], list):
            return normalize_ocr_result(raw_result[0])

        for item in raw_result:
            if isinstance(item, dict):
                lines.extend(normalize_ocr_result(item))
                continue

            if not isinstance(item, (list, tuple)):
                continue

            # Common v2 line shape: [box, ("text", score)]
            if len(item) >= 2 and isinstance(item[1], (list, tuple)) and item[1]:
                text = item[1][0]
                score = item[1][1] if len(item[1]) > 1 else None
                lines.append((str(text), float(score) if isinstance(score, (int, float)) else None))
                continue

            # Common lightweight shape: ["text", score]
            if item and isinstance(item[0], str):
                score = item[1] if len(item) > 1 else None
                lines.append((item[0], float(score) if isinstance(score, (int, float)) else None))

    return lines


def run_ocr_on_image(ocr: object, image_path: Path, use_cls: bool) -> list[tuple[str, float | None]]:
    # PaddleOCR v2 accepts cls=...; v3 may ignore or reject it depending on install.
    try:
        raw_result = ocr.ocr(str(image_path), cls=use_cls)
    except TypeError:
        raw_result = ocr.ocr(str(image_path))
    return normalize_ocr_result(raw_result)


def initialize_ocr(PaddleOCR: object, lang: str, use_cls: bool, logger: RunLogger) -> object:
    try:
        return PaddleOCR(use_angle_cls=use_cls, lang=lang)
    except (TypeError, ValueError) as exc:
        logger.write(f"PaddleOCR rejected angle-classifier args, retrying with lang only: {exc}")
        return PaddleOCR(lang=lang)


def markdown_for_page(
    page_no: int,
    page_image_size: tuple[int, int],
    tile_texts: Sequence[tuple[Path, list[tuple[str, float | None]]]],
) -> str:
    parts = [
        f"# Page {page_no:03d}",
        "",
        f"- Rendered image size: {page_image_size[0]} x {page_image_size[1]} px",
        f"- Tile count: {len(tile_texts)}",
        "",
    ]

    for index, (tile_path, lines) in enumerate(tile_texts, start=1):
        parts.append(f"## Tile {index:02d}: {tile_path.name}")
        parts.append("")
        if lines:
            parts.extend(text for text, _score in lines)
        else:
            parts.append("[NO_TEXT_RECOGNIZED]")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def write_merged(page_markdown_paths: Iterable[Path], merged_path: Path) -> None:
    with merged_path.open("w", encoding="utf-8", newline="\n") as merged:
        merged.write("# OCR Merged Text\n\n")
        for path in page_markdown_paths:
            merged.write(path.read_text(encoding="utf-8"))
            merged.write("\n---\n\n")


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf_path).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = RunLogger(output_dir / "run_log.txt")

    try:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Input must be a PDF file: {pdf_path}")

        logger.write(f"Input PDF: {pdf_path}")
        logger.write(f"Output directory: {output_dir}")
        logger.write("Loading OCR runtime dependencies.")
        fitz, Image, PaddleOCR = require_runtime()

        page_text_dir, image_dir, tile_dir = reset_generated_dirs(output_dir, args.keep_images)

        logger.write("Initializing PaddleOCR.")
        ocr = initialize_ocr(PaddleOCR, args.lang, use_cls=not args.no_cls, logger=logger)

        page_paths: list[Path] = []
        document = fitz.open(str(pdf_path))
        logger.write(f"PDF page count: {document.page_count}")

        for page_index in range(document.page_count):
            page_no = page_index + 1
            logger.write(f"Rendering page {page_no:03d}.")
            page = document.load_page(page_index)
            image_path = image_dir / f"page_{page_no:03d}.png"
            width, height = render_page(fitz, page, args.dpi, image_path)

            tile_paths = split_image_if_needed(
                Image,
                image_path,
                tile_dir,
                page_no,
                width,
                height,
                args.max_tile_width,
                args.max_tile_height,
            )
            logger.write(
                f"Page {page_no:03d}: rendered {width}x{height}px, OCR tile count {len(tile_paths)}."
            )

            tile_texts: list[tuple[Path, list[tuple[str, float | None]]]] = []
            for tile_index, tile_path in enumerate(tile_paths, start=1):
                logger.write(f"OCR page {page_no:03d}, tile {tile_index:02d}: {tile_path.name}")
                lines = run_ocr_on_image(ocr, tile_path, use_cls=not args.no_cls)
                logger.write(f"Recognized {len(lines)} text lines.")
                tile_texts.append((tile_path, lines))

            page_markdown = markdown_for_page(page_no, (width, height), tile_texts)
            page_path = page_text_dir / f"page_{page_no:03d}.md"
            page_path.write_text(page_markdown, encoding="utf-8", newline="\n")
            page_paths.append(page_path)

        document.close()
        write_merged(page_paths, output_dir / "merged.md")

        if not args.keep_images:
            shutil.rmtree(image_dir, ignore_errors=True)
            shutil.rmtree(tile_dir, ignore_errors=True)
            logger.write("Temporary images removed. Use --keep-images to retain them.")

        logger.write("OCR pipeline completed successfully.")
        return 0
    except Exception as exc:
        logger.write(f"ERROR: {exc}")
        logger.write(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
