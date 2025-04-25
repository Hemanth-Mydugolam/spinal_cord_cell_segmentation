# Spinal Cord Segmentation

An automated pipeline for segmenting spinal cord images using Cellpose.

## Overview

This project provides a complete workflow for processing and segmenting spinal cord images. It includes tools for converting TIFF images to PNG, splitting large images into manageable pieces, performing segmentation using Cellpose, and stitching the results back together.

## Features

- TIFF to PNG conversion with customizable scaling
- Automatic image splitting for large images
- Cellpose-based segmentation using the cyto3 model
- Mask stitching for reconstructing full segmentation results

## Requirements

The project requires Python and several dependencies listed in `requirements.txt`. Key dependencies include:

- cellpose==3.1.1.1
- opencv-python
- numpy
- pillow
- tifffile

## Usage

1. Place your TIFF images in the designated input directory
2. Run the main pipeline:

```bash
python main.py
```

The pipeline will:
1. Convert TIFF images to PNG format
2. Split the images into smaller sections
3. Process the sections using Cellpose
4. Stitch the resulting masks back together

## Project Structure

- `main.py`: Main pipeline script
- `bin/`
  - `constants.py`: Configuration and path constants
  - `generate_pngs.py`: TIFF to PNG conversion
  - `generate_split_images.py`: Image splitting functionality
  - `generate_masks.py`: Mask stitching utilities
- `model/`
  - `run_cellpose.py`: Cellpose model implementation

## License

See the LICENSE file for details.