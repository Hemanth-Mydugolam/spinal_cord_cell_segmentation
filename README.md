# Xenium Cell Segmentation Pipeline

![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/github/license/unikill066/xenium_cell_segmentation)


**End‑to‑end pipeline for segmenting spinal‑cord microscopy images using [Cellpose](https://github.com/MouseLand/cellpose).**

> Drag‑and‑drop GUI (Streamlit) • Headless CLI • Custom training workflow

## Table of Contents

* [Why this repo?](#why-this-repo)
* [Quick Start (TL;DR)](#quick-start-tldr)
* [Installation](#installation)
* [Downloading Pre‑trained Weights](#downloading-pre-trained-weights)
* [Configuring Paths & Parameters](#configuring-paths--parameters)
* [Running the Pipeline](#running-the-pipeline)

  * [Command‑line](#command-line)
  * [Streamlit App](#streamlit-app)
* [Training on Your Own Data](#training-on-your-own-data)
* [Directory Structure](#directory-structure)
* [Troubleshooting & FAQ](#troubleshooting--faq)
* [Citing](#citing)
* [License](#license)

## Why this repo?

- This repository provides a turn‑key workflow for turning raw histological slides of the Xenium Data (TIFF) into high‑quality, full‑resolution segmentation masks. 

- Huge TIFF slides (>40k × 40k px) do not fit into GPU memory. This repo scaled down, breaks them into tiles, runs a pre-trained Cellpose-SAM model in parallel, then stitches the probability masks back together.

- The same code powers a drag‑and‑drop Streamlit interface for bench scientists and a fully scriptable CLI for batch jobs.

## Quick Start (TL;DR)

```bash
# 1. Clone & install
git clone https://github.com/unikill066/xenium_cell_segmentation.git
cd xenium_cell_segmentation
pip install -r requirements.txt

# 2. Put your slide(s) in ./data/input
# 3. Download the model weights from huggingface/box and copy it to ./model/ model directory (see below)
# 4. Edit utils/constants.py, with model path and config path 
# 5. Run the pipeline
python main.py
```


## Installation

### Python environment

* Python ≥ 3.8
* (Optional) CUDA‑enabled PyTorch for GPU speed‑ups
  *Tested on CUDA 12.1 + RTX A5000.*

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### System packages

| Dependency | Debian / Ubuntu                       | macOS (brew)           |
| ---------- | ------------------------------------- | ---------------------- |
| OpenCV     | `sudo apt-get install python3-opencv` | `brew install opencv`  |
| Tiff       | `sudo apt-get install libtiff-dev`    | `brew install libtiff` |

Override any parameter at the CLI with `--param=value`. See `python main.py --help`.

## Running the Pipeline

### Command‑line

```bash
python main.py
```

### Streamlit App

```bash
streamlit run streamlit_app.py
```

1. Drag a `.tif` (or folder) onto the **Upload** panel.
2. Tune tile size & model on the sidebar.
3. Click **Run segmentation** – outputs stream to `data/output/`.

The app supports one upload at a time; progress bars updates live. More on the steps that go into the pipeline can be found here: <p align="left">
  <a href="docs/step_process.md">
    <img src="https://img.shields.io/badge/Step–by–Step-Docs-blue?style=for-the-badge" alt="Step-by-Step Docs">
  </a>
</p>


## Training on Your Own Data

1. **Annotate** nuclei or whole cells in **QuPath**

   * Export objects as **GeoJSON** (`File › Object data › Export as GeoJSON`).
   * Export the corresponding raw slide as an **OME‑TIFF**.

2. **Generate training patches**

   ```bash
   python generate_training_data.py
   ```

3. **Fine‑tune Cellpose** (`cellpose/train.py`). Example:

   ```python
   python -m bin/train_cellpose_sam.py
   ```

   > Note: Make sure to update the constants in `train_dir` and `model_name` in`bin/train_cellpose_sam.py`.

4. Update `MODEL_PATH` and re‑run inference.
   For hyper‑parameter suggestions see the [Cellpose docs](https://cellpose.readthedocs.io).

   > Note: Download and copy this model to models directory.
   > 
   > Model weights are uploaded to Hugging Face: [DRG Cellpose-SAM Model](https://huggingface.co/unikill066/drg_cellpose_sam_model)

## Directory Structure

```
xenium_cell_segmentation/
├── bin/           # one‑shot utility scripts for training a new cellpose / cellpose-sam models
├── model/         # pre‑trained & fine‑tuned weights
├── utils/         # reusable helpers (tiling, stitching, viz, etc.)
├── notebooks/     # jupyter demos and exploratory analysis
├── docs/          # extra figures & extended docs
├── data/          # auto‑generated at runtime
│   ├── input/     # raw slides (.tif)
│   ├── tiles/     # png tiles fed to cellpose
│   ├── masks/     # per‑tile masks
│   └── output/    # stitched full‑res masks
└── streamlit_app.py
```

Additional Documentation:
<p align="left">
  <a href="docs/xenium_cell_segmentation.md">
    <img src="https://img.shields.io/badge/Xenium–Cell–Segmentation-Docs-blue?style=for-the-badge" alt="Xenium Cell Segmentation Docs">
  </a>
</p>


## Troubleshooting & FAQ

| Symptom                                | Fix                                                              |
| -------------------------------------- | ---------------------------------------------------------------- |
| **OOM on GPU**                         | Lower `--tile_px`, increase overlap.                             |
| **No masks produced**                  | Check contrast / staining; try `--net_avg=False` with Cellpose.  |
| **Streamlit app upload fails >200 MB** | Increase `server.maxUploadSize` in `~/.streamlit/config.toml`.   |
| **GeoJSON mis‑aligned with slide**     | Verify that QuPath export uses *Entire Image* coordinate system. |

## Citing

If you use this code, please cite:

```
@article{Stringer_2025_Cellpose-SAM,
  title={Cellpose-SAM: how to train your own model},
  author={Stringer, Carsen and Pachitariu, Marius},
  journal={Nat. Methods},
  year={2025}
}
```
[Cellpose-SAM paper](https://www.biorxiv.org/content/10.1101/2025.04.28.651001v1): Pachitariu, M., Rariden, M., & Stringer, C. (2025). Cellpose-SAM: superhuman generalization for cellular segmentation. bioRxiv.

## License

This project is licensed under the MIT License – see `LICENSE` for details.