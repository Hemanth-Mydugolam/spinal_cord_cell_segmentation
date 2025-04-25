# usage
import logging
from bin.constants import *
from bin.generate_masks import MaskStitcher
from bin.generate_pngs import TiffToPngConverter
from bin.generate_split_images import ImageSplitter
from model.run_cellpose import CellposeBatchProcessor

# # generate - pngs
setup_logging(logging.INFO)
converter = TiffToPngConverter(scaling_factor=SCALING_FACTOR, tif_dir=TIF_IMAGES_DIR, output_dir=PNG_IMAGES_DIR)
converter.convert_all()

# # generate - splits
setup_logging(logging.INFO)
splitter = ImageSplitter(source_dir=PNG_IMAGES_DIR, output_dir=SPLIT_IMAGES_DIR, sub_image_width=IMG_WIDTH, sub_image_height=IMG_HEIGHT)
splitter.split_all()

# cellpose - masks
setup_logging(logging.INFO)
processor = CellposeBatchProcessor(input_dir=SPLIT_IMAGES_DIR, output_dir=CELLPOSE_MASKS_DIR, model_name="cyto3_restore",
                                   bsize=2048, overlap=0.15, batch_size=6, gpu=0, channels=(1,0))
processor.process_all()

# stitch - masks
setup_logging(logging.INFO)
stitcher = MaskStitcher(input_dir=CELLPOSE_MASKS_DIR, output_dir=STITCHED_MASKS_DIR)
stitcher.stitch_all()