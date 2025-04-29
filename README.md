# Spinal Cord Segmentation Pipeline

Automated, end‑to‑end processing and segmentation of spinal‑cord microscopy images with [Cellpose](https://cellpose.readthedocs.io/).

## Overview

This repository provides a **turn‑key workflow** for turning raw histological slides of the spinal cord (TIFF) into high‑quality, full‑resolution segmentation masks—in a *single command*.

## Key Features

| Stage | Purpose |
|-------|---------|
| **TIFF → PNG conversion** | Converts raw `.tiff` slides to compressed `.png`, with optional down‑scaling to speed up processing. |
| **Smart tiling** | Splits very large images into manageable tiles that fit comfortably in GPU/CPU memory. |
| **Cellpose inference** | Runs the *cyto3* (default) or any other Cellpose model on every tile. |
| **Mask stitching** | Re‑assembles the individual tile masks into a single, full‑resolution segmentation mask. |

## Requirements

* Python **3.9+**
* GPU‑enabled PyTorch build (optional but recommended)
* Dependencies (installed automatically via `requirements.txt`):
  * `cellpose==3.1.1.1`
  * `opencv‑python`
  * `numpy`
  * `pillow`
  * `tifffile`

## Installation

```bash
# Clone the repository
git clone https://github.com/your‑username/spinal‑cord‑segmentation.git
cd spinal‑cord‑segmentation

# Create / activate a virtualenv (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

## Quick Start

1. **Place** your raw `.tiff` images in `data/input/` (or adjust the paths in `bin/constants.py`).
2. **Run** the pipeline:

   ```bash
   python main.py
   ```
3. **Collect** your results:
   * PNG conversions → `data/png/`
   * Split tiles → `data/tiles/`
   * Cellpose masks → `data/masks/`
   * Stitched masks → `data/output/`

## Detailed Workflow

```mermaid
flowchart LR
    A[TIFF images] --> B[generate_pngs.py]:::step
    classDef step fill:#fafafa,stroke:#333,stroke-width:1px;
    B --> C[generate_split_images.py]:::step
    C --> D[run_cellpose.py]:::step
    D --> E[generate_masks.py]:::step
    E --> F[Final segmentation]:::step
```

*All paths, tile overlap, and Cellpose parameters are configurable in* **`bin/constants.py`**.

## Project Layout

```
.
├── main.py              # Orchestrates the full pipeline
├── bin/
│   ├── constants.py     # Centralised paths & tunables
│   ├── generate_pngs.py # TIFF → PNG converter
│   ├── generate_split_images.py
│   └── generate_masks.py
├── model/
│   └── run_cellpose.py  # Wrapper around Cellpose API
├── requirements.txt
└── LICENSE
```

## License

Distributed under the terms of the **MIT License**.  See `LICENSE` for full text.

## Contributing

Contributions, issues and feature requests are welcome!  Please open an issue or submit a pull request — and ensure your code passes `flake8`/`black` checks and includes appropriate tests.

## Citation

If you use this pipeline in your research, please cite *Cellpose* **and** this repository:

```text
@article{stringer_cellpose_2021,
  title   = {Cellpose: a generalist algorithm for cellular segmentation},
  author  = {Stringer, Carsen and Pachitariu, Marius},
  journal = {Nature Methods},
  year    = {2021}
}
```