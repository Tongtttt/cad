import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageFilter, ImageOps

try:
    import torch
    from torchvision import transforms
    from torchvision.models.detection import (
        MaskRCNN_ResNet50_FPN_Weights,
        maskrcnn_resnet50_fpn,
    )
except Exception:
    torch = None
    transforms = None
    MaskRCNN_ResNet50_FPN_Weights = None
    maskrcnn_resnet50_fpn = None

Point = List[float]
Polygon = List[Point]
BBox = List[float]

SCHEMA_REGIONS = [
    ("outer_silhouette", "外轮廓"),
    ("hair_main", "头发主线"),
    ("hair_detail", "头发细节"),
    ("face_features", "五官"),
    ("hand", "手部"),
    ("cloth", "衣物"),
    ("flower_main", "花朵主轮廓"),
    ("flower_detail", "花朵细节"),
    ("ornament", "饰品"),
    ("misc", "其他细节"),
]

@dataclass
class Region:
    region_id: str
    label: str
    polygons: List[Polygon]
    bbox: Optional[BBox]
    area_ratio: float
    confidence: float
    source: str
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.region_id,
            "label": self.label,
            "type": "poly-region",
            "polygons": self.polygons,
            "bbox": self.bbox,
            "area_ratio": round(self.area_ratio, 6),
            "confidence": round(self.confidence, 4),
            "source": self.source,
            "notes": self.notes,
        }


class PortraitRegionExtractor:
    def __init__(self, image_path: Path):
        self.image_path = image_path
        self.image = Image.open(image_path).convert("RGB")
        self.gray = ImageOps.grayscale(self.image)
        self.width, self.height = self.image.size

    def run(self) -> Dict[str, object]:
        maskrcnn_result = self._try_maskrcnn_person_mask()
        if maskrcnn_result is not None:
            person_mask, runtime_notes = maskrcnn_result
            regions = self._build_semantic_regions(person_mask, source="torchvision-maskrcnn")
            available = True
            reason = "Used torchvision Mask R-CNN person segmentation from the local ComfyUI runtime."
            method = "torchvision-maskrcnn"
        else:
            person_mask = self._build_lineart_subject_mask()
            regions = self._build_semantic_regions(person_mask, source="lineart-heuristic")
            available = True
            reason = "Used local line-art heuristic portrait segmentation because no ready portrait workflow/custom node was installed."
            method = "lineart-heuristic"
            runtime_notes = [
                "Mask R-CNN weights/model were not available locally, so the extractor fell back to a deterministic heuristic segmenter.",
            ]

        return {
            "status": "ok",
            "image": str(self.image_path),
            "image_size": {"width": self.width, "height": self.height},
            "segmentation": {
                "available": available,
                "reason": reason,
                "method": method,
                "runtime_notes": runtime_notes,
            },
            "regions": [region.to_dict() for region in regions],
            "schema": "portrait_regions.schema.json",
        }

    def _try_maskrcnn_person_mask(self) -> Optional[Tuple[np.ndarray, List[str]]]:
        if torch is None or transforms is None or maskrcnn_resnet50_fpn is None:
            return None

        notes: List[str] = []
        try:
            weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT
            model = maskrcnn_resnet50_fpn(weights=weights)
            model.eval()
            preprocess = weights.transforms()
            tensor = preprocess(self.image).unsqueeze(0)
            with torch.no_grad():
                output = model(tensor)[0]
        except Exception as exc:
            notes.append(f"Mask R-CNN unavailable: {exc}")
            return None

        labels = output.get("labels")
        scores = output.get("scores")
        masks = output.get("masks")
        if labels is None or scores is None or masks is None:
            notes.append("Mask R-CNN returned incomplete outputs.")
            return None

        best_score = -1.0
        best_mask = None
        for idx, label in enumerate(labels.tolist()):
            if label != 1:
                continue
            score = float(scores[idx].item())
            if score > best_score:
                best_score = score
                best_mask = masks[idx, 0].detach().cpu().numpy()

        if best_mask is None or best_score < 0.4:
            notes.append("No person instance above confidence threshold.")
            return None

        notes.append(f"Detected person mask with confidence {best_score:.3f}.")
        return (best_mask > 0.45).astype(np.uint8), notes

    def _build_lineart_subject_mask(self) -> np.ndarray:
        gray = np.asarray(self.gray, dtype=np.uint8)
        binary = (gray < 235).astype(np.uint8)
        cleaned = self._dilate(binary, iterations=max(1, min(self.width, self.height) // 300))
        cleaned = self._erode(cleaned, iterations=max(1, min(self.width, self.height) // 500))
        components = self._connected_components(cleaned)
        if not components:
            return np.ones((self.height, self.width), dtype=np.uint8)

        center = np.array([self.width / 2.0, self.height / 2.0])
        best_mask = None
        best_score = -10**9
        for comp in components:
            ys, xs = np.where(comp)
            area = len(xs)
            if area < (self.width * self.height) * 0.002:
                continue
            cx = float(xs.mean())
            cy = float(ys.mean())
            dist = np.linalg.norm(np.array([cx, cy]) - center)
            bbox_w = xs.max() - xs.min() + 1
            bbox_h = ys.max() - ys.min() + 1
            compact_bonus = bbox_w * bbox_h
            score = area * 1.0 - dist * 2.0 + compact_bonus * 0.05
            if score > best_score:
                best_score = score
                best_mask = comp

        if best_mask is None:
            best_mask = max(components, key=lambda m: int(m.sum()))
        return best_mask.astype(np.uint8)

    def _build_semantic_regions(self, person_mask: np.ndarray, source: str) -> List[Region]:
        person_mask = (person_mask > 0).astype(np.uint8)
        if person_mask.sum() == 0:
            person_mask = np.ones((self.height, self.width), dtype=np.uint8)

        bbox = self._bbox_from_mask(person_mask)
        if bbox is None:
            bbox = [0.0, 0.0, float(self.width), float(self.height)]
        x0, y0, x1, y1 = [int(v) for v in bbox]
        bw = max(1, x1 - x0)
        bh = max(1, y1 - y0)

        regions: List[Region] = []
        base_polygons = self._mask_to_polygons(person_mask)
        regions.append(self._make_region(
            "outer_silhouette", "???", base_polygons, person_mask, 0.88, source, "\u4e3b\u4f53\u6574\u4f53\u8f6e\u5ed3"
        ))

        hair_mask = np.zeros_like(person_mask)
        hair_y_end = y0 + int(bh * 0.36)
        hair_mask[y0:hair_y_end, x0:x1] = person_mask[y0:hair_y_end, x0:x1]
        hair_mask = self._dilate(hair_mask, iterations=max(1, bw // 220))
        regions.append(self._make_region(
            "hair_main", "????", self._mask_to_polygons(hair_mask), hair_mask, 0.66, source, "\u6309\u4e3b\u4f53\u4e0a\u90e8\u533a\u57df\u4f30\u8ba1\u5934\u53d1\u4e3b\u8f6e\u5ed3"
        ))

        hair_detail_mask = np.zeros_like(person_mask)
        detail_y0 = y0 + int(bh * 0.08)
        detail_y1 = y0 + int(bh * 0.48)
        detail_x0 = x0 + int(bw * 0.08)
        detail_x1 = x1 - int(bw * 0.08)
        hair_detail_mask[detail_y0:detail_y1, detail_x0:detail_x1] = person_mask[detail_y0:detail_y1, detail_x0:detail_x1]
        hair_detail_mask = self._erode(hair_detail_mask, iterations=max(1, bw // 280))
        regions.append(self._make_region(
            "hair_detail", "????", self._mask_to_polygons(hair_detail_mask), hair_detail_mask, 0.52, source, "\u82b1\u6735\u5185\u90e8\u7ec6\u8282\u5019\u9009\u533a"
        ))

        face_mask = np.zeros_like(person_mask)
        fx0 = x0 + int(bw * 0.25)
        fx1 = x1 - int(bw * 0.25)
        fy0 = y0 + int(bh * 0.16)
        fy1 = y0 + int(bh * 0.42)
        face_mask[fy0:fy1, fx0:fx1] = person_mask[fy0:fy1, fx0:fx1]
        regions.append(self._make_region(
            "face_features", "??", self._mask_to_polygons(face_mask), face_mask, 0.58, source, "\u5934\u90e8\u53f3\u4e0a\u9644\u4ef6\u4f5c\u4e3a\u9970\u54c1\u5019\u9009\u533a"
        ))

        hand_mask = np.zeros_like(person_mask)
        arm_y0 = y0 + int(bh * 0.36)
        arm_y1 = y0 + int(bh * 0.72)
        left_x1 = x0 + int(bw * 0.22)
        right_x0 = x1 - int(bw * 0.22)
        hand_mask[arm_y0:arm_y1, x0:left_x1] = person_mask[arm_y0:arm_y1, x0:left_x1]
        hand_mask[arm_y0:arm_y1, right_x0:x1] = person_mask[arm_y0:arm_y1, right_x0:x1]
        regions.append(self._make_region(
            "hand", "??", self._mask_to_polygons(hand_mask), hand_mask, 0.42, source, "\u5934\u90e8\u53f3\u4e0a\u9644\u4ef6\u4f5c\u4e3a\u9970\u54c1\u5019\u9009\u533a"
        ))

        cloth_mask = np.zeros_like(person_mask)
        cy0 = y0 + int(bh * 0.42)
        cy1 = y1
        cx0 = x0 + int(bw * 0.14)
        cx1 = x1 - int(bw * 0.14)
        cloth_mask[cy0:cy1, cx0:cx1] = person_mask[cy0:cy1, cx0:cx1]
        regions.append(self._make_region(
            "cloth", "??", self._mask_to_polygons(cloth_mask), cloth_mask, 0.61, source, "\u4e3b\u4f53\u4e0b\u534a\u533a\u4f5c\u4e3a\u8863\u7269\u5de5\u4f5c\u533a"
        ))

        flower_main_mask = np.zeros_like(person_mask)
        flower_y0 = y0 + int(bh * 0.34)
        flower_y1 = y0 + int(bh * 0.72)
        flower_x0 = x0 + int(bw * 0.55)
        flower_x1 = x1
        flower_main_mask[flower_y0:flower_y1, flower_x0:flower_x1] = person_mask[flower_y0:flower_y1, flower_x0:flower_x1]
        regions.append(self._make_region(
            "flower_main", "?????", self._mask_to_polygons(flower_main_mask), flower_main_mask, 0.46, source, "\u672a\u5f52\u5165\u4e3b\u8981\u8bed\u4e49\u533a\u7684\u5269\u4f59\u4e3b\u4f53\u7ebf\u6761"
        ))

        flower_detail_mask = self._erode(flower_main_mask, iterations=max(1, bw // 260))
        regions.append(self._make_region(
            "flower_detail", "????", self._mask_to_polygons(flower_detail_mask), flower_detail_mask, 0.36, source, "\u82b1\u6735\u5185\u90e8\u7ec6\u8282\u5019\u9009\u533a"
        ))

        ornament_mask = np.zeros_like(person_mask)
        oy0 = y0
        oy1 = y0 + int(bh * 0.28)
        ox0 = x0 + int(bw * 0.62)
        ox1 = x1
        ornament_mask[oy0:oy1, ox0:ox1] = person_mask[oy0:oy1, ox0:ox1]
        regions.append(self._make_region(
            "ornament", "??", self._mask_to_polygons(ornament_mask), ornament_mask, 0.34, source, "\u5934\u90e8\u53f3\u4e0a\u9644\u4ef6\u4f5c\u4e3a\u9970\u54c1\u5019\u9009\u533a"
        ))

        misc_mask = person_mask.copy()
        for used in [hair_mask, face_mask, hand_mask, cloth_mask, flower_main_mask, ornament_mask]:
            misc_mask = np.where(used > 0, 0, misc_mask)
        regions.append(self._make_region(
            "misc", "????", self._mask_to_polygons(misc_mask), misc_mask, 0.31, source, "\u672a\u5f52\u5165\u4e3b\u8981\u8bed\u4e49\u533a\u7684\u5269\u4f59\u4e3b\u4f53\u7ebf\u6761"
        ))

        return [region for region in regions if region.polygons]

    def _make_region(
        self,
        region_id: str,
        label: str,
        polygons: List[Polygon],
        mask: np.ndarray,
        confidence: float,
        source: str,
        notes: str,
    ) -> Region:
        return Region(
            region_id=region_id,
            label=label,
            polygons=polygons,
            bbox=self._bbox_from_mask(mask),
            area_ratio=float(mask.sum()) / float(self.width * self.height),
            confidence=confidence,
            source=source,
            notes=notes,
        )

    def _bbox_from_mask(self, mask: np.ndarray) -> Optional[BBox]:
        ys, xs = np.where(mask > 0)
        if len(xs) == 0:
            return None
        return [float(xs.min()), float(ys.min()), float(xs.max() + 1), float(ys.max() + 1)]

    def _mask_to_polygons(self, mask: np.ndarray) -> List[Polygon]:
        polygons: List[Polygon] = []
        for comp in self._connected_components(mask):
            ys, xs = np.where(comp > 0)
            if len(xs) == 0:
                continue
            if len(xs) < max(20, (self.width * self.height) // 3000):
                continue
            x0 = int(xs.min())
            x1 = int(xs.max()) + 1
            y0 = int(ys.min())
            y1 = int(ys.max()) + 1
            polygons.append([
                [float(x0), float(y0)],
                [float(x1), float(y0)],
                [float(x1), float(y1)],
                [float(x0), float(y1)],
            ])
        return polygons

    def _connected_components(self, mask: np.ndarray) -> List[np.ndarray]:
        h, w = mask.shape
        visited = np.zeros_like(mask, dtype=np.uint8)
        components: List[np.ndarray] = []
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for y in range(h):
            for x in range(w):
                if mask[y, x] == 0 or visited[y, x]:
                    continue
                stack = [(y, x)]
                visited[y, x] = 1
                coords = []
                while stack:
                    cy, cx = stack.pop()
                    coords.append((cy, cx))
                    for dy, dx in neighbors:
                        ny = cy + dy
                        nx = cx + dx
                        if ny < 0 or ny >= h or nx < 0 or nx >= w:
                            continue
                        if mask[ny, nx] == 0 or visited[ny, nx]:
                            continue
                        visited[ny, nx] = 1
                        stack.append((ny, nx))
                comp = np.zeros_like(mask, dtype=np.uint8)
                ys, xs = zip(*coords)
                comp[np.array(ys), np.array(xs)] = 1
                components.append(comp)
        return components

    def _dilate(self, mask: np.ndarray, iterations: int = 1) -> np.ndarray:
        result = mask.astype(np.uint8)
        for _ in range(iterations):
            padded = np.pad(result, 1, mode="constant")
            out = np.zeros_like(result)
            for dy in range(3):
                for dx in range(3):
                    out = np.maximum(out, padded[dy:dy + result.shape[0], dx:dx + result.shape[1]])
            result = out
        return result

    def _erode(self, mask: np.ndarray, iterations: int = 1) -> np.ndarray:
        result = mask.astype(np.uint8)
        for _ in range(iterations):
            padded = np.pad(result, 1, mode="constant", constant_values=1)
            out = np.ones_like(result)
            for dy in range(3):
                for dx in range(3):
                    out = np.minimum(out, padded[dy:dy + result.shape[0], dx:dx + result.shape[1]])
            result = out
        return result


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("Usage: portrait_region_extractor.py <image_path> <output_json>")

    image_path = Path(sys.argv[1])
    output_json = Path(sys.argv[2])
    extractor = PortraitRegionExtractor(image_path)
    payload = extractor.run()
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Portrait extractor output written: {output_json}")


if __name__ == "__main__":
    main()
