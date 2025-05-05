#!/usr/bin/env python3
"""
Developed by Nikhil Nageshwar Inturi

This module provides TiffToPngConverter for converting TIFF images to PNG format,
applying a scaling factor to resize the images.
"""

# imports
import logging, tifffile
from pathlib import Path
from typing import Union
from PIL import Image
# local imports
from utils.constants import *


class TiffToPngConverter:
    """
    Converts all TIFF images in a source directory to PNG format,
    applying a scaling factor to resize the images.
    """

    def __init__(self, scaling_factor: float, tif_dir: Union[str, Path], output_dir: Union[str, Path]) -> None:
        self.scaling_factor = scaling_factor
        self.tif_dir = Path(tif_dir)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_output_directory()

    def _setup_output_directory(self) -> None:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Output directory ready: {self.output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create output directory {self.output_dir}: {e}")
            raise

    def convert_all(self) -> None:
        """
        Convert all .tif files in the source directory.
        """
        tif_files = list(self.tif_dir.glob("*.tif"))
        if not tif_files:
            self.logger.warning(f"No .tif files found in {self.tif_dir}")
            return

        for tif_path in tif_files:
            try:
                self.convert_file(tif_path)
            except Exception:
                self.logger.exception(f"Error converting file: {tif_path}")

    def convert_file(self, tif_path: Path) -> None:
        """
        Convert a single TIFF file to PNG, resizing by the scaling factor.

        Args:
            tif_path: Path to the input .tif file.
        """
        img_array = tifffile.imread(str(tif_path), level=0)
        self.logger.debug(f"Read {tif_path.name} with shape {img_array.shape}")
        img = Image.fromarray(img_array)
        new_size = (int(img_array.shape[1] * self.scaling_factor), int(img_array.shape[0] * self.scaling_factor))
        img_resized = img.resize(new_size, resample=Image.LANCZOS)
        output_path = self.output_dir / tif_path.with_suffix(".png").name
        img_resized.save(output_path, format="PNG")
        self.logger.info(f"Converted {tif_path.name} to {output_path}")


# testing
# setup_logging(logging.INFO)
# converter = TiffToPngConverter(0.2125, 'path/to/tifs', 'path/to/output')
# converter.convert_all()