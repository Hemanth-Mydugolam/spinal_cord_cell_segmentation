# utils/mask_to_geojson.py
#!/usr/bin/env python3
"""
Developed by Nikhil Nageshwar Inturi

This module converts full-size .npy mask files into GeoJSON polygon files,
scaling coordinates back to the original image resolution using a scale factor.
"""

import json
from pathlib import Path
import numpy as np
import cv2
import logging

class MaskToGeoJSONConverter:
    """
    Scans a directory of .npy masks, finds contours for each labeled region,
    scales coordinates by upscale_factor, and writes out a GeoJSON file per mask.
    """

    def __init__(self, mask_dir: Path, output_dir: Path, upscale_factor: float = 1.0):
        self.mask_dir = Path(mask_dir)
        self.output_dir = Path(output_dir)
        self.upscale = 1/(upscale_factor)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert_all(self) -> None:
        mask_files = list(self.mask_dir.glob("*.npy"))
        if not mask_files:
            self.logger.warning(f"No .npy mask files found in {self.mask_dir}")
            return

        for mask_fp in mask_files:
            try:
                self._convert_file(mask_fp)
                self.logger.info(f"Converted {mask_fp.name} to GeoJSON")
            except Exception:
                self.logger.exception(f"Failed to convert {mask_fp.name}")

    def _convert_file(self, mask_fp: Path) -> None:
        mask = np.load(mask_fp)
        labels = np.unique(mask)
        labels = labels[labels != 0]
        features = []

        for label in labels:
            binary = (mask == label).astype(np.uint8)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                coords = cnt.squeeze().tolist()
                if len(coords) < 3:
                    continue
                # scale coordinates back to original resolution
                scaled = [[int(x * self.upscale), int(y * self.upscale)] for [x, y] in coords]
                if scaled[0] != scaled[-1]:
                    scaled.append(scaled[0])

                feature = {
                    "type": "Feature",
                    "properties": {"label": int(label)},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [scaled]
                    }
                }
                features.append(feature)

        geojson = {"type": "FeatureCollection", "features": features}
        out_fp = self.output_dir / f"{mask_fp.stem}.geojson"
        with open(out_fp, "w") as f:
            json.dump(geojson, f)