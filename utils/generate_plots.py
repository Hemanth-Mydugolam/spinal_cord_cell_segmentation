#!/usr/bin/env python3
"""
Developed by Nikhil Nageshwar Inturi

This module provides PlotGenerator to process all masks in a directory:
  - For each mask, find its image by matching name stem, then output:
      1) a binary mask PNG,
      2) an overlay PNG with colored mask + boundaries.
"""

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage.segmentation import find_boundaries
from pathlib import Path
import logging

class PlotGenerator:
    """
    Process every .npy mask in mask_dir and generate
    corresponding plots using images from image_dir.
    """

    def __init__(
        self,
        image_dir: Path,
        mask_dir: Path,
        output_dir: Path,
        overlay_color: tuple[int,int,int] = (238,144,144),
        boundary_color: tuple[int,int,int] = (100,100,255),
        alpha: float = 0.5
    ) -> None:
        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.output_dir = Path(output_dir)
        self.overlay_color = np.array(overlay_color, dtype=np.uint8)
        self.boundary_color = np.array(boundary_color, dtype=np.uint8)
        self.alpha = alpha
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        mask_paths = list(self.mask_dir.glob("*.npy"))
        if not mask_paths:
            self.logger.warning(f"No .npy masks found in {self.mask_dir}")
            return

        for mask_path in mask_paths:
            stem = mask_path.stem
            img_candidates = list(self.image_dir.glob(f"{stem}*.png"))
            if not img_candidates:
                self.logger.warning(f"No image found for mask '{stem}'")
                continue
            image_path = img_candidates[0]

            img = np.array(Image.open(image_path).convert("RGB"))
            mask = np.load(mask_path)

            # binary mask plot
            binary = (mask > 0).astype(np.uint8)
            plt.figure(figsize=(10,10))
            plt.imshow(binary, cmap='gray')
            plt.axis('off')
            plt.title(f"{stem} - Binary Mask")
            out_gray = self.output_dir / f"{stem}_binary.png"
            plt.savefig(out_gray, bbox_inches='tight', dpi=300)
            plt.close()
            self.logger.info(f"Saved binary mask plot: {out_gray.name}")

            # overlay with boundaries
            overlay = img.copy()
            mask_bool = mask > 0
            overlay[mask_bool] = (
                (1 - self.alpha) * img[mask_bool] + self.alpha * self.overlay_color
            ).astype(np.uint8)
            boundaries = find_boundaries(mask_bool, mode='outer')
            overlay[boundaries] = self.boundary_color

            plt.figure(figsize=(10,10))
            plt.imshow(overlay)
            plt.axis('off')
            plt.title(f"{stem} - Mask Overlay")
            out_overlay = self.output_dir / f"{stem}_overlay.png"
            plt.savefig(out_overlay, bbox_inches='tight', dpi=300)
            plt.close()
            self.logger.info(f"Saved overlay plot: {out_overlay.name}")


# # main.py snippet (to run plots for all masks)
# from utils.generate_plots import PlotGenerator

# plotter = PlotGenerator(
#     image_dir=PNG_IMAGES_DIR,
#     mask_dir=STITCHED_MASKS_DIR,
#     output_dir=OUTPUT_DIR,
#     overlay_color=(238,144,144),
#     boundary_color=(100,100,255),
#     alpha=0.5
# )
# plotter.run()




# import matplotlib.pyplot as plt
# import numpy as np

# # Create a binary mask (optional: if combined_mask contains labels like 1,2,3...)
# binary_mask = (combined_mask > 0).astype(np.uint8)

# plt.figure(figsize=(10, 10))
# plt.imshow(binary_mask, cmap='gray')  # all non-zero values will be gray
# plt.title('Combined Mask - Single Color')
# plt.axis('off')

# # Save the figure as PNG
# plt.savefig('combined_mask_grey_testing_model.png', bbox_inches='tight', dpi=300)

# # Show the plot
# plt.show()




# from PIL import Image
# import numpy as np

# image = Image.open("jayden_img.ome.png").convert("RGB")  # PNG_IMAGES_DIR = CONFIG_DIR / '2_png_images'
# image_np = np.array(image)
# mask = np.load("combined_full_mask_testing_model.npy")  # STITCHED_MASKS_DIR = CONFIG_DIR / '5_stitched_masks'





# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image
# from skimage.segmentation import find_boundaries

# # Define colors
# overlay_color = np.array([238, 144, 144])  # Light green
# boundary_color = np.array([100, 100, 255])     # Navy blue
# alpha = 0.5  # Transparency for overlay

# # Ensure mask is binary
# mask = (mask > 0).astype(np.uint8)

# # Create a copy for overlay
# overlay = image_np.copy()

# # Apply overlay color where mask is 1
# overlay[mask == 1] = ((1 - alpha) * image_np[mask == 1] + alpha * overlay_color).astype(np.uint8)

# # --- Add navy blue boundaries ---
# from skimage.segmentation import find_boundaries

# # Find boundaries in the mask
# boundaries = find_boundaries(mask, mode='outer')

# # Draw boundary color
# overlay[boundaries] = boundary_color

# # Show plot
# plt.figure(figsize=(10, 10))
# plt.imshow(overlay)
# plt.axis("off")
# plt.title("Image with Mask Overlay and Navy Blue Boundary")
# plt.show()

# # Save the image
# output = Image.fromarray(overlay)
# output.save("0_image_with_mask_overlay_with_white_boundary_model.png")

# # output dir where pltos needs to be saved: OUTPUT_DIR = CONFIG_DIR / '6_output_masks'
