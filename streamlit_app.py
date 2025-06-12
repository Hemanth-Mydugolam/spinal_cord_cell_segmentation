#!/usr/bin/env python3
"""
Streamlit front-end for the Cellpose automation pipeline.
Allows uploading a TIF, runs conversion → split → cellpose → stitching → overlay/comparison → geojson,
then displays results and provides download links.
"""

# imports
import streamlit as st, logging, shutil
from PIL import Image
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

dirs = [TIF_IMAGES_DIR, PNG_IMAGES_DIR, SPLIT_IMAGES_DIR, CELLPOSE_MASKS_DIR, STITCHED_MASKS_DIR, OUTPUT_DIR, GEOJSON_OUTS_DIR]

st.title("Cellpose-sam for DRGs - Automated Pipeline")

uploaded = st.file_uploader("Upload a TIFF image", type=["tif"])
if uploaded:

    for d in dirs:
        p = Path(d)
        if p.exists() and p.is_dir():
            shutil.rmtree(p) # to refresh the directory
        p.mkdir(parents=True, exist_ok=True)

    tif_path = TIF_IMAGES_DIR / uploaded.name
    with open(tif_path, "wb") as f:
        f.write(uploaded.getbuffer())  # save TIFF
    st.success(f"Saved input to {tif_path}")
    stem = tif_path.stem

    # generate - pngs
    with st.spinner("Converting TIFF to PNG..."):
        TiffToPngConverter(scaling_factor=SCALING_FACTOR, tif_dir=TIF_IMAGES_DIR, output_dir=PNG_IMAGES_DIR).convert_all()
    # generate - splits
    with st.spinner("Splitting PNG into tiles..."):
        ImageSplitter(source_dir=PNG_IMAGES_DIR, output_dir=SPLIT_IMAGES_DIR, sub_image_width=IMG_WIDTH, sub_image_height=IMG_HEIGHT).split_all()
    # generate - cellpose masks (detect step using a pre-trained model)
    with st.spinner("Running Cellpose segmentation..."):
        cellpose_sam_detect_images_eval(model_path=MODEL, image_input_dir=SPLIT_IMAGES_DIR, image_output_dir=CELLPOSE_MASKS_DIR)
    # generate - stitched masks (.npy files)
    with st.spinner("Stitching masks..."):
        NPYMaskStitcher(input_dir=CELLPOSE_MASKS_DIR, output_dir=STITCHED_MASKS_DIR).stitch_all()
    # generate - plots
    with st.spinner("Generating overlays and comparisons..."):
        PlotGenerator(image_dir=PNG_IMAGES_DIR, mask_dir=STITCHED_MASKS_DIR, output_dir=OUTPUT_DIR, overlay_color=(238,144,144), boundary_color=(100,100,255), alpha=0.5).run()
    # generate - geojsons
    with st.spinner("Generating GeoJSON files..."):
        MaskToGeoJSONConverter(mask_dir=STITCHED_MASKS_DIR, output_dir=GEOJSON_OUTS_DIR, upscale_factor=SCALING_FACTOR).convert_all()

    st.success("Pipeline complete!")

    # download buttons
    st.header("Download segmentation masks")
    geojson_file = GEOJSON_OUTS_DIR / f"{stem}.geojson"

    if geojson_file.exists():
        st.download_button(label="Download .geojson mask", data=open(geojson_file, "rb"), file_name=geojson_file.name)
    
    overlay_file = OUTPUT_DIR / f"{stem}_overlay.png"
    if overlay_file.exists():
        st.image(Image.open(overlay_file), caption="{stem} - overlay", use_column_width=True)
else:
    st.info("Please upload a TIFF image to begin.")