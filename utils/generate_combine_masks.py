#!/usr/bin/env python3
"""
Developed by Nikhil Nageshwar Inturi

This module provides MaskStitcher for stitching tiled .npy masks
back into full-size masks, one per original image stem.
"""

import re
from pathlib import Path
import numpy as np
import logging

class NPYMaskStitcher:
    """
    Scans an input directory for files matching
    <stem>_<row>_<col>.npy, groups them by stem, and
    stitches each group into a single full-size mask.
    """

    TILE_PATTERN = re.compile(r'^(?P<stem>.+)_(?P<row>\d+)_(?P<col>\d+)\.npy$')

    def __init__(self, input_dir: Path, output_dir: Path) -> None:
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_output_directory()

    def _setup_output_directory(self) -> None:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Output directory ready: {self.output_dir}")
        except Exception as e:
            self.logger.error(f"Could not create output directory {self.output_dir}: {e}")
            raise

    def stitch_all(self) -> None:
        """
        Find all .npy tiles, group by stem, and stitch each group.
        """
        all_files = list(self.input_dir.glob("*.npy"))
        if not all_files:
            self.logger.warning(f"No .npy files found in {self.input_dir}")
            return

        # group files by stem
        stems = {}
        for p in all_files:
            m = self.TILE_PATTERN.match(p.name)
            if not m:
                self.logger.warning(f"Skipping unrecognized file name: {p.name}")
                continue
            stem = m.group("stem")
            stems.setdefault(stem, []).append(p)

        for stem, paths in stems.items():
            try:
                self._stitch_stem(stem, paths)
                self.logger.info(f"Stitched mask for '{stem}' → {stem}.npy")
            except Exception:
                self.logger.exception(f"Failed to stitch tiles for '{stem}'")

    def _stitch_stem(self, stem: str, paths: list[Path]) -> None:
        """
        Given all tile paths for a single stem, reconstruct the full mask.
        """
        # load each tile into a dict keyed by (row, col)
        mask_map = {}
        rows = set()
        cols = set()

        for p in paths:
            m = self.TILE_PATTERN.match(p.name)
            row, col = int(m.group("row")), int(m.group("col"))
            tile = np.load(p)
            mask_map[(row, col)] = tile
            rows.add(row)
            cols.add(col)

        all_rows = sorted(rows)
        all_cols = sorted(cols)

        # determine max height per row, max width per col
        row_heights = {r: max(mask_map[(r, c)].shape[0]
                              for c in all_cols if (r, c) in mask_map)
                       for r in all_rows}
        col_widths = {c: max(mask_map[(r, c)].shape[1]
                             for r in all_rows if (r, c) in mask_map)
                      for c in all_cols}

        # compute offsets
        row_offsets = {r: sum(row_heights[rr] for rr in all_rows if rr < r)
                       for r in all_rows}
        col_offsets = {c: sum(col_widths[cc] for cc in all_cols if cc < c)
                       for c in all_cols}

        # total dims
        total_h = sum(row_heights.values())
        total_w = sum(col_widths.values())

        # create canvas
        full_mask = np.zeros((total_h, total_w), dtype=np.uint16)

        # place tiles
        for (r, c), tile in mask_map.items():
            y0, x0 = row_offsets[r], col_offsets[c]
            h, w = tile.shape
            full_mask[y0:y0+h, x0:x0+w] = tile

        # save combined mask
        out_path = self.output_dir / f"{stem}.npy"
        np.save(out_path, full_mask)




# # Path to mask files
# mask_folder = image_dir  # update this
# mask_files = [f for f in os.listdir(mask_folder) if f.endswith('.npy')]

# # Pattern to extract row and column
# pattern = re.compile(r'_(\d+)_(\d+)\.npy')

# # Map to hold each mask and its (row, col)
# mask_map = {}
# row_col_set = set()

# # Organize masks by (row, col)
# for f in mask_files:
#     match = pattern.search(f)
#     if match:
#         row = int(match.group(1))  # y
#         col = int(match.group(2))  # x
#         mask = np.load(os.path.join(mask_folder, f))
#         mask_map[(row, col)] = mask
#         row_col_set.add((row, col))

# # Determine row and column counts
# all_rows = sorted({r for r, _ in row_col_set})
# all_cols = sorted({c for _, c in row_col_set})

# # Build a lookup for tile dimensions per row/col
# row_heights = {}
# col_widths = {}

# for row in all_rows:
#     for col in all_cols:
#         if (row, col) in mask_map:
#             h, w = mask_map[(row, col)].shape
#             row_heights[row] = max(row_heights.get(row, 0), h)
#             col_widths[col] = max(col_widths.get(col, 0), w)

# # Compute cumulative row/column positions
# row_offsets = {r: sum(row_heights[rr] for rr in all_rows if rr < r) for r in all_rows}
# col_offsets = {c: sum(col_widths[cc] for cc in all_cols if cc < c) for c in all_cols}

# # Total dimensions
# total_height = sum(row_heights[r] for r in all_rows)
# total_width = sum(col_widths[c] for c in all_cols)

# # Create blank canvas
# combined_mask = np.zeros((total_height, total_width), dtype=np.uint16)

# # Stitch masks into the full canvas
# for (row, col), mask in mask_map.items():
#     y = row_offsets[row]
#     x = col_offsets[col]
#     h, w = mask.shape
#     combined_mask[y:y+h, x:x+w] = mask

# # Save result
# np.save('combined_full_mask_testing_model.npy', combined_mask)