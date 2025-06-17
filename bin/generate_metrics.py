# imports
from pathlib import Path
import geopandas as gpd, pandas as pd, numpy as np

class MetricsCalculator:
    def __init__(self, gt_dir: Path, pred_dir: Path, output_csv: Path, iou_threshold: float = 0.5):
        """
        Calculate metrics between ground truth and predicted GeoJSONs.
        gt_dir : Directory containing ground-truth GeoJSON files.
        pred_dir : Directory containing predicted GeoJSON files (same basenames).
        output_csv : Path to write the metrics CSV.
        iou_threshold : float
        Minimum IoU to count a match as a true positive.
        """
        self.gt_dir = Path(gt_dir)
        self.pred_dir = Path(pred_dir)
        self.output_csv = Path(output_csv)
        self.iou_threshold = iou_threshold

    @staticmethod
    def compute_iou_matrix(gt_polys, pred_polys) -> np.ndarray:
        """
        Compute IoU matrix between two lists of Shapely geometries.
        """
        n_gt, n_pred = len(gt_polys), len(pred_polys)
        iou = np.zeros((n_gt, n_pred), dtype=float)
        for i, g in enumerate(gt_polys):
            for j, p in enumerate(pred_polys):
                inter = g.intersection(p).area
                union = g.union(p).area
                iou[i, j] = inter / union if union > 0 else 0.0
        return iou

    def match_and_metrics(self, iou_mat: np.ndarray):
        """
        Greedy matching on IoU matrix.
        Returns TP, FP, FN, and mean IoU over matched pairs.
        """
        matches, gt_used, pred_used = list(), set(), set()
        flat = [(i, j, iou_mat[i, j])
                for i in range(iou_mat.shape[0])
                for j in range(iou_mat.shape[1])]
        flat.sort(key=lambda x: x[2], reverse=True)

        for i, j, val in flat:
            # if val < self.iou_threshold:
            #     break
            if i not in gt_used and j not in pred_used:
                matches.append(val)
                gt_used.add(i)
                pred_used.add(j)

        tp = len(matches)
        fn = iou_mat.shape[0] - tp
        fp = iou_mat.shape[1] - tp
        mean_iou = float(np.mean(matches)) if matches else 0.0
        return tp, fp, fn, mean_iou

    def compute_image_metrics(self, gt_file: Path, pred_file: Path) -> dict:
        """
        Load GeoJSONs and compute metrics for a single image.
        """
        gt_gdf = gpd.read_file(gt_file)
        pred_gdf = gpd.read_file(pred_file)
        iou_mat = self.compute_iou_matrix(gt_gdf.geometry, pred_gdf.geometry)
        tp, fp, fn, mean_iou = self.match_and_metrics(iou_mat)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall    = tp / (tp + fn) if (tp + fn) else 0.0
        f1_score  = (2 * precision * recall / (precision + recall)
                     if (precision + recall) else 0.0)

        return {"image": gt_file.name, "n_gt": len(gt_gdf), "n_pred": len(pred_gdf),
                "TP": tp, "FP": fp, "FN": fn, "precision": precision, "recall": recall, 
                "f1_score": f1_score, "mean_iou": mean_iou}

    def run(self):
        """Iterate over all GeoJSONs in gt_dir, compute metrics, and save CSV."""
        records = []
        print(sorted(self.gt_dir.glob("*.geojson")))
        print(self.gt_dir)
        for gt_path in sorted(self.gt_dir.glob("*.geojson")):
            print(gt_path)
            pred_path = self.pred_dir / gt_path.name
            print(pred_path)
            if not pred_path.exists():
                print(f"[WARN] Prediction missing for {gt_path.name}, skipping.")
                continue
            print(gt_path, pred_path)
            rec = self.compute_image_metrics(gt_path, pred_path)
            records.append(rec)

        df = pd.DataFrame(records)
        df.to_csv(self.output_csv, index=False)
        print(f"[INFO] Metrics written to {self.output_csv}")


# # testing
# if __name__ == "__main__":
#     GT_DIR        = Path("/mnt/WorkingDos/cellpose_sam/manual_labels")
#     PRED_DIR      = Path("/mnt/WorkingDos/cellpose_sam/model_labels")
#     OUTPUT_CSV    = Path("/mnt/WorkingDos/cellpose_sam/metrics.csv")
#     IOU_THRESHOLD = 0.5
#     calc = MetricsCalculator(gt_dir=GT_DIR, pred_dir=PRED_DIR, output_csv=OUTPUT_CSV, iou_threshold=IOU_THRESHOLD)
#     calc.run()