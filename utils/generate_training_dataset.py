"""
Create a uint16 mask PNG from a GeoJSON file and write two down‑sampled
previews (black‑and‑white and random‑colour) for easy visual inspection.
"""

from pathlib import Path
import warnings, numpy as np, geopandas as gpd, rasterio, cv2
from shapely.geometry import Polygon, MultiPolygon
from PIL import Image
from tifffile import imread
from utils.constants import *
Image.MAX_IMAGE_PIXELS = None
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)

def geojson_to_mask_png(image_path: Path, geojson_path: Path, mask_out: Path) -> None:
    """
    Rasterize GeoJSON polygons into a uint16 label mask PNG.
    """
    with rasterio.open(image_path) as src:
        transform = src.transform
        height, width = src.height, src.width
        crs = src.crs

    mask = np.zeros((height, width), dtype=np.uint16)
    gdf = gpd.read_file(geojson_path)

    if crs is not None and gdf.crs is not None and gdf.crs != crs:
        gdf = gdf.to_crs(crs)

    def world_to_px(tx, x, y):
        c, r = ~tx * (x, y)
        return int(round(c)), int(round(r))

    for idx, geom in enumerate(gdf.geometry, start=1):
        polys = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
        for poly in polys:
            pts = np.array(
                [world_to_px(transform, x, y) for x, y in poly.exterior.coords],
                dtype=np.int32
            )
            cv2.fillPoly(mask, [pts], color=idx)

    cv2.imwrite(str(mask_out), mask)


def make_bw_preview(label_mask: np.ndarray, out_png: Path, downsample: int = 8):
    preview = (label_mask > 0).astype(np.uint8) * 255
    if downsample > 1:
        preview = preview[::downsample, ::downsample]
    Image.fromarray(preview, mode="L").save(out_png)
    print(f"saved B/W preview → {out_png}")


def make_colored_preview(label_mask: np.ndarray, out_png: Path, downsample: int = 8):
    rng = np.random.default_rng(42)
    lut = np.vstack(
        [np.zeros((1, 3), np.uint8),
         rng.integers(0, 256, size=(label_mask.max(), 3), dtype=np.uint8)]
    )
    rgb = lut[label_mask]
    if downsample > 1:
        rgb = rgb[::downsample, ::downsample]
    Image.fromarray(rgb, mode="RGB").save(out_png)
    print(f"saved colour preview → {out_png}")