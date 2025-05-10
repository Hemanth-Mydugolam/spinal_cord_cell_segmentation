#!/usr/bin/env python3
"""
Developed by Nikhil Nageshwar Inturi

Overlay original PNGs with their corresponding stitched masks,
then generate side-by-side comparison mosaics.
"""

# imports
from pathlib import Path
from typing import Union
from PIL import Image, ImageOps, ImageEnhance
import os


class OverlayGenerator:
    """
    For each image in original_dir, find matching mask in mask_dir,
    create an overlay with transparency, and a side-by-side composite.
    """
    def __init__(self, original_dir: Union[str, Path], mask_dir: Union[str, Path], output_dir: Union[str, Path], 
    mask_color: tuple = (255, 0, 0), alpha: float = 0.8) -> None:
        self.original_dir = Path(original_dir)
        self.mask_dir = Path(mask_dir)
        self.output_dir = Path(output_dir)
        self.mask_color = mask_color
        self.alpha = alpha
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        pngs = list(self.original_dir.glob("*.png"))
        for orig_path in pngs:
            stem = orig_path.stem
            mask_path = self.mask_dir / f"{stem}_mask_stitched.png"
            if not mask_path.exists():
                print(f"Warning: mask not found for {stem}")
                continue
            self._make_overlay(orig_path, mask_path)
            self._make_comparison(orig_path, mask_path)

    def _make_overlay(self, orig_path: Path, mask_path: Path) -> None:
        orig = Image.open(orig_path).convert("RGBA")
        mask = Image.open(mask_path).convert("L")
        # if mask.size != orig.size:
        #     mask = mask.resize(orig.size, resample=Image.NEAREST)
        color_mask = Image.new("RGBA", orig.size, self.mask_color + (0,))
        color_mask.putalpha(ImageEnhance.Brightness(mask).enhance(self.alpha))
        overlay = Image.alpha_composite(orig, color_mask)
        out_path = self.output_dir / f"{orig_path.stem}_overlay.png"
        overlay.save(out_path)

    def _make_comparison(self, orig_path: Path, mask_path: Path) -> None:
        orig = Image.open(orig_path).convert("RGB")
        mask = Image.open(mask_path).convert("RGB")
        if orig.size != mask.size:
            mask = mask.resize(orig.size, resample=Image.NEAREST)
        comp = Image.new("RGB", (orig.width * 2, orig.height))
        comp.paste(orig, (0, 0))
        comp.paste(mask, (orig.width, 0))
        out_path = self.output_dir / f"{orig_path.stem}_compare.png"
        comp.save(out_path)