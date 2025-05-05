# imports
import logging
from pathlib import Path
from model.run_cellpose import CellposeBatchProcessor
from utils.constants import *

# cellpose - masks
setup_logging(logging.INFO)
processor = CellposeBatchProcessor(input_dir=Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_test"), 
                                  output_dir=Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_outs"), 
                                  model_name="cyto3_restore", bsize=2048, overlap=0.15, batch_size=6, gpu=0, channels=(2,0), diameter=30)
processor.process_all()