#!/usr/bin/env python3
"""
Split every TIFF in IMG_DIR and its matching mask in MASK_DIR into 640×640 or 1024x1024 tiles.
Image tiles are saved as 8‑bit TIFFs: mask tiles are saved
as 16‑bit TIFFs with “_mask” suffix so Cellpose can pair them automatically.

Result:
    OUT_DIR/
        <stem>_0_0.tif
        <stem>_0_0_mask.tif
        <stem>_0_1.tif
        <stem>_0_1_mask.tif
        ...

Author : Nikhil Nageshwar Inturi  (modified to handle separate img/mask dirs)
"""

# imports
from pathlib import Path
import logging, numpy as np, tifffile, cv2
from utils.constants import setup_logging

setup_logging(logging.INFO)

# IMG_DIR = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/1_tif_images")
# MASK_DIR = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/7_mask_images")
# OUT_DIR = IMG_DIR.parent / "8_split_masks"

# TILE_H = TILE_W = 1024

def read_tif(path: Path) -> np.ndarray:
    arr = tifffile.imread(path)
    # (C,H,W) → (H,W,C) if few channels
    if arr.ndim == 3 and arr.shape[0] <= 4:
        arr = np.transpose(arr, (1, 2, 0))
    return arr


def pad(tile: np.ndarray, th: int, tw: int) -> np.ndarray:
    dh, dw = th - tile.shape[0], tw - tile.shape[1]
    if dh == 0 and dw == 0:
        return tile
    pads = ((0, dh), (0, dw)) + ((0, 0),) * (tile.ndim - 2)
    return np.pad(tile, pads, mode="constant", constant_values=0)


def tile_pair(img_path: Path, mask_path: Path, out_dir: Path, TILE_H: int, TILE_W: int):
    stem = img_path.stem
    img = read_tif(img_path)
    mask = read_tif(mask_path).astype(np.uint16)
    if img.shape[:2] != mask.shape[:2]:
        raise ValueError(f"Dimension mismatch {img_path.name} vs {mask_path.name}")

    H, W = img.shape[:2]
    nrows = (H + TILE_H - 1) // TILE_H
    ncols = (W + TILE_W - 1) // TILE_W

    for r in range(nrows):
        for c in range(ncols):
            y0, x0 = r * TILE_H, c * TILE_W
            y1, x1 = min(y0 + TILE_H, H), min(x0 + TILE_W, W)
            img_tile = pad(img[y0:y1, x0:x1], TILE_H, TILE_W)
            msk_tile = pad(mask[y0:y1, x0:x1], TILE_H, TILE_W)
            img_name = f"{stem}_{r}_{c}.tif"
            msk_name = f"{stem}_{r}_{c}_masks.tif"

            if img_tile.dtype != np.uint8:
                img_write = cv2.normalize(
                    img_tile, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            else:
                img_write = img_tile
            tifffile.imwrite(out_dir / img_name, img_write)
            tifffile.imwrite(out_dir / msk_name, msk_tile)
            logging.info("saved %s / %s", img_name, msk_name)


def split_folder(img_dir: Path, mask_dir: Path, out_dir: Path, TILE_H: int, TILE_W: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    for img_path in img_dir.glob("*.tif"):
        if img_path.name.endswith("_masks.tif"):
            continue
        mask_path = mask_dir / f"{img_path.stem}_masks.tif"
        if not mask_path.exists():
            logging.warning("no mask found for %s, skipping", img_path.name)
            continue
        tile_pair(img_path, mask_path, out_dir, TILE_H, TILE_W)