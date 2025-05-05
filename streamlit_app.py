#!/usr/bin/env python3
"""
Streamlit front-end for the Cellpose automation pipeline.
Allows uploading a TIF, runs conversion → split → cellpose → stitching → overlay/comparison,
then displays results and provides download links.
"""

# imports
import streamlit as st
from pathlib import Path
from bin.constants import *
from bin.generate_masks import MaskStitcher
from bin.generate_pngs import TiffToPngConverter
from model.run_cellpose import CellposeBatchProcessor
from bin.generate_image_overlays import OverlayGenerator

# ensure directories
for d in [TIF_IMAGES_DIR, PNG_IMAGES_DIR, SPLIT_IMAGES_DIR, CELLPOSE_MASKS_DIR, STITCHED_MASKS_DIR, OUTPUT_DIR]:
    Path(d).mkdir(parents=True, exist_ok=True)

st.title("Cellpose Automation Pipeline")

uploaded = st.file_uploader("Upload a TIFF image", type=["tif", "tiff"])
if uploaded:
    # save TIFF
    tif_path = TIF_IMAGES_DIR / uploaded.name
    with open(tif_path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success(f"Saved input to {tif_path}")
    stem = tif_path.stem

    # 1) TIFF → PNG
    with st.spinner("Converting TIFF to PNG..."):
        TiffToPngConverter(
            scaling_factor=0.2125,
            tif_dir=TIF_IMAGES_DIR,
            output_dir=PNG_IMAGES_DIR
        ).convert_all()

    # 2) Split
    with st.spinner("Splitting PNG into tiles..."):
        ImageSplitter(
            source_dir=PNG_IMAGES_DIR,
            output_dir=SPLIT_IMAGES_DIR,
            sub_image_width=640,
            sub_image_height=640
        ).split_all()

    # 3) Segment
    with st.spinner("Running Cellpose segmentation..."):
        CellposeBatchProcessor(
            input_dir=SPLIT_IMAGES_DIR,
            output_dir=CELLPOSE_MASKS_DIR,
            model_name="cyto3_restore",
            bsize=2048,
            overlap=0.15,
            batch_size=6,
            gpu=0,
            channels=(1,0)
        ).process_all()

    # 4) Stitch masks
    with st.spinner("Stitching masks..."):
        MaskStitcher(root_dir=CELLPOSE_MASKS_DIR, out_dir=STITCHED_MASKS_DIR).stitch_all()

    # 5) Generate overlays & comparisons
    overlay_dir = CONFIG_DIR / '6_overlays'
    compare_dir = CONFIG_DIR / '7_comparisons'
    with st.spinner("Generating overlays and comparisons..."):
        OverlayGenerator(
            original_dir=PNG_IMAGES_DIR,
            mask_dir=STITCHED_MASKS_DIR,
            output_dir=overlay_dir,
            mask_color=(255,0,0),
            alpha=0.5
        ).run()
        OverlayGenerator(
            original_dir=PNG_IMAGES_DIR,
            mask_dir=STITCHED_MASKS_DIR,
            output_dir=compare_dir,
            mask_color=(255,0,0),
            alpha=0.0  # pure side-by-side; overlay not used
        ).run()

    st.success("Pipeline complete!")

    # display overlay and comparison
    st.header("Overlay")
    st.image(str(overlay_dir / f"{stem}_overlay.png"), caption="Overlay", use_column_width=True)
    st.header("Comparison")
    st.image(str(compare_dir / f"{stem}_compare.png"), caption="Comparison", use_column_width=True)

    # downloads
    st.header("Downloads")
    npy = STITCHED_DIR / f"{stem}_stitched.npy"
    tif = STITCHED_DIR / f"{stem}_stitched.tif"
    if npy.exists():
        st.download_button("Download segmentation (.npy)", open(npy,'rb'), file_name=npy.name)
    if tif.exists():
        st.download_button("Download mask TIFF (.tif)", open(tif,'rb'), file_name=tif.name)

else:
    st.info("Please upload a TIFF image to begin.")