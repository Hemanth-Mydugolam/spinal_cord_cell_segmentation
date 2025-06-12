# imports
import logging, numpy as np, matplotlib.pyplot as plt, os
from pathlib import Path
from model.run_cellpose import CellposeBatchProcessor
from utils.constants import *
from skimage.measure import label
from tifffile import imwrite
from utils.generate_masks import MaskStitcher
from PIL import Image
from cellpose.io import imread
from cellpose import models, core, io, plot
from tqdm import trange
from natsort import natsorted

image_ext = ".tif"
masks_ext = ".png" if image_ext == ".png" else ".tif"
flow_threshold = 0.8
cellprob_threshold = 0.0
tile_norm_blocksize = 0

if core.use_gpu()==False:
  raise ImportError("No GPU access, change your runtime")

model = models.CellposeModel(pretrained_model="/Users/discovery/Desktop/spinal_cord_segmentation/model/cellpose_sam_neun", gpu=True)

# print(models.model_path("/Users/discovery/Desktop/spinal_cord_segmentation/model/cellpose_sam_neun"))

input_dir = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_imgs/data")
output_dir = Path("/Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/cellpose_outs")
output_dir.mkdir(parents=True, exist_ok=True)

files = natsorted([f for f in input_dir.glob("*"+image_ext) if "_masks" not in f.name and "_flows" not in f.name])

if(len(files)==0):
  raise FileNotFoundError("no image files found, did you specify the correct folder and extension?")
else:
  print(f"{len(files)} images in folder:")

# for f in files:
#   print(f)

imgs = [io.imread(files[i]) for i in trange(len(files))]

masks, flows, styles = model.eval(imgs, batch_size=32, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold, normalize={"tile_norm_blocksize": tile_norm_blocksize})

print("saving masks")
for i in trange(len(files)):
    f = files[i]
    io.imsave(output_dir / (f.stem + "_pred_masks" + masks_ext), masks[i])