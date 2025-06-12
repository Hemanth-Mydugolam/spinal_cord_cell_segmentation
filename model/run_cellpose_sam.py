# imports
from pathlib import Path
import os, re, numpy as np
from cellpose import models
from skimage import io as skio
from tqdm import tqdm


def cellpose_sam_detect_images_eval(model_path, image_input_dir, image_output_dir, image_ext=".png", flow_threshold=0.9, cellprob_threshold=-6, min_size=1):
    """
    Detect images using Cellpose SAM.
    
    Args:
        model_path (str): Path to the Cellpose SAM model.
        image_input_dir (Path): Directory containing the images.
        image_output_dir (Path): Directory to save the masks.
        image_ext (str): Image file extension.
        flow_threshold (float): Flow threshold for Cellpose SAM.
        cellprob_threshold (float): Cell probability threshold for Cellpose SAM.
        min_size (int): Minimum size for Cellpose SAM.
    """
    print(image_output_dir)
    image_files = [f for f in image_input_dir.glob("*"+image_ext) if "_masks" not in f.name and "_flows" not in f.name]
    model = models.CellposeModel(gpu=True, pretrained_model=model_path)
    os.makedirs(image_output_dir, exist_ok=True)

    for image_file in tqdm(image_files, desc="Segmenting images"):
        image_path = os.path.join(image_input_dir, image_file)
        img = skio.imread(image_path)
        masks, flows, styles = model.eval([img], batch_size = 16, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold, augment=True, resample=True, min_size=min_size)
        mask = masks[0]
        base_name = Path(image_file).stem
        mask_path = os.path.join(image_output_dir, f"{base_name}.npy")
        np.save(mask_path, mask)