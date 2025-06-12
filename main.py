# imports
import logging
from pathlib import Path
from utils.constants import *
from utils.generate_plots import PlotGenerator
from utils.generate_split_images import ImageSplitter
from utils.generate_masks import MaskStitcher
from utils.generate_combine_masks import NPYMaskStitcher
from utils.generate_pngs import TiffToPngConverter
from model.run_cellpose import CellposeBatchProcessor
from utils.generate_image_overlays import OverlayGenerator
from model.run_cellpose_sam import cellpose_sam_detect_images_eval
from utils.generate_geojson_qp_mask import MaskToGeoJSONConverter

# generate - pngs
setup_logging(logging.INFO)
converter = TiffToPngConverter(scaling_factor=SCALING_FACTOR, tif_dir=TIF_IMAGES_DIR, output_dir=PNG_IMAGES_DIR)
converter.convert_all()

# generate - splits
setup_logging(logging.INFO)
splitter = ImageSplitter(source_dir=PNG_IMAGES_DIR, output_dir=SPLIT_IMAGES_DIR, sub_image_width=IMG_WIDTH, sub_image_height=IMG_HEIGHT)
splitter.split_all()

# generate - cellpose masks (detect step using a pre-trained model)
setup_logging(logging.INFO)
cellpose_sam_detect_images_eval(model_path=MODEL, image_input_dir=SPLIT_IMAGES_DIR, image_output_dir=CELLPOSE_MASKS_DIR)

# generate - stitched masks (.npy files)
setup_logging(logging.INFO)
stitcher = NPYMaskStitcher(input_dir=CELLPOSE_MASKS_DIR, output_dir=STITCHED_MASKS_DIR)
stitcher.stitch_all()

# generate - plots
setup_logging(logging.INFO)
plotter = PlotGenerator(image_dir=PNG_IMAGES_DIR, mask_dir=STITCHED_MASKS_DIR, output_dir=OUTPUT_DIR, overlay_color=(238,144,144), boundary_color=(100,100,255), alpha=0.5)
plotter.run()

# generate - geojsons
setup_logging(logging.INFO)
converter = MaskToGeoJSONConverter(mask_dir=STITCHED_MASKS_DIR, output_dir=GEOJSON_OUTS_DIR, upscale_factor=SCALING_FACTOR)
converter.convert_all()



########## archived code ##########
# # cellpose - masks
# setup_logging(logging.INFO)
# processor = CellposeBatchProcessor(input_dir=SPLIT_IMAGES_DIR, output_dir=CELLPOSE_MASKS_DIR, model_name="",
#                                    bsize=640, overlap=0.15, batch_size=6, gpu=0, channels=(2,0), diameter=CELL_DIAMETER)
# processor.process_all()

# # stitch - masks
# setup_logging(logging.INFO)
# stitcher = MaskStitcher(input_dir=CELLPOSE_MASKS_DIR, output_dir=STITCHED_MASKS_DIR)
# stitcher.stitch_all()

# # img-mask overlay & comparison
# overlay_gen = OverlayGenerator(original_dir = PNG_IMAGES_DIR, mask_dir = STITCHED_MASKS_DIR, output_dir = OUTPUT_DIR, mask_color = (255, 0, 0), alpha = 0.5)
# overlay_gen.run()