#!/usr/bin/env python3
"""
Developed by Nikhil Nageshwar Inturi

Stitch tiled mask .npy files and mask PNGs into mosaics,
based on a Cellpose output root (4_cellpose_masks) containing
 'segmentation' and 'masks' subfolders, ignoring 'preview'.
"""

# imports
from PIL import Image
from pathlib import Path
import logging, numpy as np, tifffile
# local imports
from bin.constants import *


class MaskStitcher:
    """
    Stitch both .npy masks and mask PNGs from a Cellpose output root:
    - Expects root with subfolders SEGMENTATION_DIR (.npy) and MASKS_DIR (.png)
    - Outputs mosaics in STITCHED_MASKS_DIR
    """

    def __init__(self, input_dir: Path, output_dir: Path = None) -> None:
        self.input_dir = Path(input_dir)
        self.seg_dir = self.input_dir / SEGMENTATION_DIR
        self.png_dir = self.input_dir / MASKS_DIR
        self.output_dir = Path(output_dir) if output_dir is not None else Path(STITCHED_MASKS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _parse(fname: str):
        stem = Path(fname).stem
        base, row, col = stem.rsplit("_", 2)
        return base, int(row), int(col)

    def _read_npy(self, fp: Path) -> np.ndarray:
        data = np.load(fp, allow_pickle=True)
        if data.dtype == object:
            data = data.item().get('masks')
        return data.astype(np.int32, copy=False)

    def _read_png(self, fp: Path) -> np.ndarray:
        arr = np.array(Image.open(fp))
        return arr.astype(np.int32, copy=False)

    def _groups(self, directory: Path, pattern: str):
        groups = {}
        for fp in directory.glob(pattern):
            base, _, _ = self._parse(fp.name)
            groups.setdefault(base, []).append(fp)
        return groups

    def _layout(self, files, read_func):
        row_h = {}
        col_w = {}
        for fp in files:
            _, r, c = self._parse(fp.name)
            h, w = read_func(fp).shape
            row_h[r] = max(row_h.get(r, 0), h)
            col_w[c] = max(col_w.get(c, 0), w)
        y_off = {}
        x_off = {}
        y = x = 0
        for r in sorted(row_h):
            y_off[r] = y
            y += row_h[r]
        for c in sorted(col_w):
            x_off[c] = x
            x += col_w[c]
        return y_off, x_off, y, x

    def _stitch(self, files, read_func):
        y_off, x_off, H, W = self._layout(files, read_func)
        mosaic = np.zeros((H, W), dtype=np.int32)
        next_lbl = 1
        for fp in files:
            _, r, c = self._parse(fp.name)
            tile = read_func(fp)
            for lbl in np.unique(tile)[1:]:
                mask_region = (tile == lbl)
                yy = y_off[r]
                xx = x_off[c]
                region = mosaic[yy:yy+tile.shape[0], xx:xx+tile.shape[1]]
                region[mask_region] = next_lbl
                next_lbl += 1
        return mosaic

    def stitch_all(self) -> None:
        seg_groups = self._groups(self.seg_dir, "*.npy")
        for base, files in seg_groups.items():
            self.logger.info(f"Stitching segmentation for '{base}' ")
            mosaic = self._stitch(files, self._read_npy)
            out_npy = self.output_dir / f"{base}_stitched.npy"
            np.save(out_npy, mosaic)
            self.logger.info(f"Saved stitched .npy: {out_npy}")
            out_tif = self.output_dir / f"{base}_stitched.tif"
            tifffile.imwrite(out_tif, (mosaic>0).astype(np.uint8)*255, photometric="minisblack")
            self.logger.info(f"Saved stitched TIFF: {out_tif}")

        png_groups = self._groups(self.png_dir, "*.png")
        for base, files in png_groups.items():
            self.logger.info(f"Stitching mask PNGs for '{base}' ")
            mosaic = self._stitch(files, self._read_png)
            out_png = self.output_dir / f"{base}_mask_stitched.png"
            Image.fromarray(mosaic.astype(np.uint16)).save(out_png)
            self.logger.info(f"Saved stitched mask PNG: {out_png}")