# imports
import logging, os
from pathlib import Path
from utils.constants import *
from utils.generate_split_images import ImageSplitter
from utils.generate_masks import MaskStitcher
from utils.generate_pngs import TiffToPngConverter
from model.run_cellpose import CellposeBatchProcessor
from utils.generate_image_overlays import OverlayGenerator
from utils.generate_training_dataset import *
from utils.generate_training_split_img_masks import split_folder

# constants
TILE_H = TILE_W = 1024  # training tile size

# generate - pngs
setup_logging(logging.INFO)
converter = TiffToPngConverter(scaling_factor=SCALING_FACTOR, tif_dir=TIF_IMAGES_DIR, output_dir=PNG_IMAGES_DIR)
converter.convert_all()

# generate - splits
setup_logging(logging.INFO)
splitter = ImageSplitter(source_dir=PNG_IMAGES_DIR, output_dir=SPLIT_IMAGES_DIR, sub_image_width=IMG_WIDTH, sub_image_height=IMG_HEIGHT)
splitter.split_all()

# generate - masks for training
setup_logging(logging.INFO)
os.makedirs(TRAIN_MASKS_DIR, exist_ok=True)
for image in TIF_IMAGES_DIR.glob("*.tif"):
    img_path = Path(image)
    geojson_path = GEOJSON_DIR / (img_path.stem + ".geojson")
    mask_png = TRAIN_MASKS_DIR / (img_path.stem + "_masks.tif")
    geojson_to_mask_png(img_path, geojson_path, mask_png)
    label_mask = np.array(Image.open(mask_png), dtype=np.uint16)
    make_bw_preview(label_mask, mask_png.with_name(img_path.stem + "_mask_bw.png"))
    make_colored_preview(label_mask, mask_png.with_name(img_path.stem + "_mask_color.png"))

# generate - split images and masks for training
setup_logging(logging.INFO)
split_folder(TIF_IMAGES_DIR, TRAIN_MASKS_DIR, TRAIN_SPLIT_IMG_MASKS_DIR, TILE_H, TILE_W)



# img_path     = Path("/Users/discovery/Downloads/SP24_008_2.ome.tif")
# geojson_path = Path("/Users/discovery/Downloads/SP24_088_2.geojson")
# mask_png     = Path("/Users/discovery/Downloads/SP24_008_2_mask.tif")


