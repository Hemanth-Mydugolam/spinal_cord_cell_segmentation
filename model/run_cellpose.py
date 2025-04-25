#!/usr/bin/env python3
"""
Developed by Nikhil Nageshwar Inturi

Batch-process .png or .tif slides with Cellpose, saving masks, previews, and segmentation arrays
into designated directories.
"""

# imports
from PIL import Image
from pathlib import Path
from cellpose import models, io
from typing import Tuple, Union
from cellpose import plot as cplt
import os, numpy as np, logging, matplotlib.pyplot as plt

# local imports
from bin.constants import *


class CellposeBatchProcessor:
    """
    Batch-process a directory of images with Cellpose,
    saving outputs in MASKS_DIR, PREVIEW_DIR, and SEGMENTATION_DIR.
    """

    def __init__(self, input_dir: Union[str, Path], output_dir: Union[str, Path], model_name: str = "cyto3_restore",
                 bsize: int = 2048, overlap: float = 0.15, batch_size: int = 6, gpu: int = 0, channels: Tuple[int, int] = (1, 0),) -> None:
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.model_name = model_name
        self.bsize = bsize
        self.overlap = overlap
        self.batch_size = batch_size
        self.gpu = gpu
        self.channels = list(channels)

        if self.gpu >= 0:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(self.gpu)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = models.CellposeModel(gpu=(self.gpu >= 0), pretrained_model=self.model_name)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for sub in (MASKS_DIR, PREVIEW_DIR, SEGMENTATION_DIR):
            dir_path = self.output_dir / sub
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created output directory: {dir_path}")

    def process_all(self) -> None:
        """
        Find all .png/.tif images in input_dir and process each.
        """
        img_paths = sorted(
            list(self.input_dir.glob("*.png")) + list(self.input_dir.glob("*.tif"))
        )
        if not img_paths:
            self.logger.warning(f"No images found in {self.input_dir}")
            return

        self.logger.info(f"Found {len(img_paths)} images in {self.input_dir}")
        for img_path in img_paths:
            try:
                self._process_image(img_path)
            except Exception:
                self.logger.exception(f"Failed processing {img_path.name}")

    def _process_image(self, img_path: Path) -> None:
        """
        Process a single image: segment, save masks, preview, and numpy array.
        """
        stem = img_path.stem
        self.logger.info(f"Processing: {img_path.name}")

        img = io.imread(str(img_path))
        if img.ndim == 3 and img[:, :, self.channels[0]].max() == 0:
            self.logger.warning(f"Channel {self.channels[0]} empty — skipping {img_path.name}")
            return

        masks, flows, styles = self.model.eval(
            img,
            channels=self.channels,
            diameter=None,
            bsize=self.bsize,
            tile_overlap=self.overlap,
            batch_size=self.batch_size,
            resample=False
        )

        fig = plt.figure(figsize=(12, 5))
        cplt.show_segmentation(fig, img, masks, flows[0], channels=self.channels)
        plt.tight_layout()

        preview_path = self.output_dir / PREVIEW_DIR / f"{stem}.png"
        fig.savefig(preview_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        self.logger.info(f"Saved preview: {preview_path}")

        mask_path = self.output_dir / MASKS_DIR / f"{stem}.png"
        Image.fromarray(masks.astype("uint16")).save(mask_path)
        self.logger.info(f"Saved mask: {mask_path}")

        seg_path = self.output_dir / SEGMENTATION_DIR / f"{stem}.npy"
        np.save(seg_path, masks)
        self.logger.info(f"Saved segmentation array: {seg_path}")