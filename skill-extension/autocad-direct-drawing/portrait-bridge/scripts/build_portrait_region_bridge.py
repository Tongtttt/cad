import json
import sys
from pathlib import Path

if len(sys.argv) < 3:
    raise SystemExit("Usage: build_portrait_region_bridge.py <input_json> <output_scr>")

input_json = Path(sys.argv[1])
output_scr = Path(sys.argv[2])
raw = input_json.read_text(encoding="utf-8", errors="replace")
data = json.loads(raw)

layer_map = {
    "outer_silhouette": "GUIDE_OUTER_SILHOUETTE",
    "hair_main": "GUIDE_HAIR_MAIN",
    "hair_detail": "GUIDE_HAIR_DETAIL",
    "face_features": "GUIDE_FACE_FEATURES",
    "hand": "GUIDE_HAND",
    "cloth": "GUIDE_CLOTH",
    "flower_main": "GUIDE_FLOWER_MAIN",
    "flower_detail": "GUIDE_FLOWER_DETAIL",
    "ornament": "GUIDE_ORNAMENT",
    "misc": "GUIDE_MISC",
}

lines = ["_.UNDO _BEGIN", "_.CMDECHO 0"]
for name in layer_map.values():
    lines += ["_.-LAYER", "_M", name, "_C", "8", name, ""]

for region in data.get("regions", []):
    layer = layer_map.get(region.get("id"))
    if not layer:
        continue
    for poly in region.get("polygons", []):
        if not poly or len(poly) < 4:
            continue
        lines += ["_.-LAYER", "_S", layer, "", "_.PLINE"]
        for pt in poly:
            x = round(float(pt[0]), 3)
            y = round(-float(pt[1]), 3)
            lines.append(f"{x},{y}")
        fx = round(float(poly[0][0]), 3)
        fy = round(-float(poly[0][1]), 3)
        lines += [f"{fx},{fy}", ""]

lines += ["_.-LAYER", "_S", "0", "", "_.UNDO _END"]
output_scr.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
print(output_scr)
