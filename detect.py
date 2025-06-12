# imports
import logging, numpy as np, matplotlib.pyplot as plt, os
from pathlib import Path
from model.run_cellpose import CellposeBatchProcessor
from utils.constants import *
from skimage.measure import label
from tifffile import imwrite
from utils.generate_masks import MaskStitcher
from PIL import Image

# # cellpose - masks
# setup_logging(logging.INFO)
# processor = CellposeBatchProcessor(input_dir=Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_test"), 
#                                   output_dir=Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_outs"), 
#                                   model_name="cyto3_restore", bsize=1024, overlap=0.15, batch_size=6, gpu=0, channels=(2,0), diameter=CELL_DIAMETER)
# processor.process_all()


setup_logging(logging.INFO)
processor = CellposeBatchProcessor(
    input_dir = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_test"),
    output_dir = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_outs"),
    # point to the folder that contains cellpose_model.pth + .yaml
    model_name = "/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/train/models/cellpose_1746568542.462492",
    bsize = 1024,
    overlap = 0.15,
    batch_size = 6,
    gpu = 0,          # set to –1 if you must run CPU
    channels = (2, 0),# or whatever channels you trained with
    diameter = CELL_DIAMETER   # or None to auto‑scale
)

processor.process_all()

## - x - x - x - x - x - x - x - x - x - x - x - x
RANGE_CELL_DIAMETER = list(range(20, 60, 5))
INPUT_DIR = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_test")
OUTPUT_DIR = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_outs")

# for CELL_DIAMETER in RANGE_CELL_DIAMETER:
#     processor = CellposeBatchProcessor(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR / f"{CELL_DIAMETER}", 
#                                   model_name="cyto3_restore", bsize=1024, overlap=0.15, batch_size=6, 
#                                   gpu=0, channels=(2,0), diameter=CELL_DIAMETER)
#     processor.process_all()

MASK_SUBDIR         = "masks"
STITCHED_DIR        = OUTPUT_DIR / "stitched"
STITCHED_DIR.mkdir(parents=True, exist_ok=True)
first_masks = sorted((OUTPUT_DIR / str(RANGE_CELL_DIAMETER[0]) / MASK_SUBDIR).glob("*.png"))

for mask_path in first_masks:
    name = mask_path.name
    union_mask = None
    for d in RANGE_CELL_DIAMETER:
        p = OUTPUT_DIR / str(d) / MASK_SUBDIR / name
        arr = np.array(Image.open(p)) > 0
        if union_mask is None:
            union_mask = arr
        else:
            union_mask |= arr

    union_lbl = label(union_mask)
    out_tif = STITCHED_DIR / name.replace(".png", "tif")
    imwrite(out_tif, union_lbl.astype(np.uint16))
    from skimage.io import imsave
    imsave(STITCHED_DIR / name, (union_mask * 255).astype(np.uint8))
    print(f"Stitched: {name} → {out_tif.name}")