

## Step-by-Step Process

### 1. Generate .tiff Images

* Export whole-slide images (WSI) from QuPath in TIFF format.
* Note down slide intersections or regions of interest for later reference.

### 2. Convert to .png Images

* Create scaled-down PNG versions of the TIFF files for faster processing.

### 3. Split Images

* Divide each PNG into smaller tiles to feed into the detection model.

### 4. Ellipse Detection

* Apply the trained ellipse detection model to each tile.
* Output annotated PNG files with detected ellipses overlaid.

### 5. Generate Plots

* Aggregate detection results and visualize metrics or distributions.

### 6. Export GeoJSON

* Convert detected ellipse coordinates into GeoJSON format for spatial analysis.

### 7. Use in QuPath

* Import original .tiff files back into QuPath.
* Import the generated GeoJSON files to overlay detected regions.
* Manually review and correct annotations as needed.
* Export the final corrected GeoJSONs from QuPath for downstream analysis in Xenium Ranger.

## Notes

* TIFF files are exported from QuPath at the start of the pipeline.
* The pipeline produces GeoJSONs which are then refined in QuPath.
* Final GeoJSONs reflect both automated detections and manual corrections.