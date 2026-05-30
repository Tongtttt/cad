import csv, json, sys
from pathlib import Path

if len(sys.argv) < 4:
    raise SystemExit("Usage: build_entity_layer_assignment.py <entities_csv> <regions_json> <output_csv>")

entities_csv = Path(sys.argv[1])
regions_json = Path(sys.argv[2])
output_csv = Path(sys.argv[3])

region_to_layer = {
    'outer_silhouette': '???',
    'hair_main': '????',
    'hair_detail': '????',
    'face_features': '??',
    'hand': '??',
    'cloth': '??',
    'flower_main': '?????',
    'flower_detail': '????',
    'ornament': '??',
    'misc': '????',
}

def point_in_bbox(x, y, bbox):
    return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]

with entities_csv.open('r', encoding='utf-8', errors='replace', newline='') as f:
    reader = csv.DictReader(f)
    if reader.fieldnames:
        reader.fieldnames = [fn.lstrip('\ufeff').strip() for fn in reader.fieldnames]
    entities = list(reader)

if not entities:
    output_csv.write_text('handle,target_layer' + chr(10), encoding='utf-8')
    print(output_csv)
    raise SystemExit(0)

minx = min(float(r['minx']) for r in entities)
miny = min(float(r['miny']) for r in entities)
maxx = max(float(r['maxx']) for r in entities)
maxy = max(float(r['maxy']) for r in entities)

regions_payload = json.loads(regions_json.read_text(encoding='utf-8', errors='replace'))
img_w = float(regions_payload['image_size']['width'])
img_h = float(regions_payload['image_size']['height'])

clean_regions = []
for r in regions_payload.get('regions', []):
    bbox = r.get('bbox')
    if not bbox or len(bbox) != 4:
        continue
    rx0, ry0, rx1, ry1 = map(float, bbox)
    cx0 = minx + (rx0 / img_w) * (maxx - minx)
    cx1 = minx + (rx1 / img_w) * (maxx - minx)
    cy0 = maxy - (ry1 / img_h) * (maxy - miny)
    cy1 = maxy - (ry0 / img_h) * (maxy - miny)
    clean_regions.append((r['id'], [cx0, cy0, cx1, cy1], region_to_layer.get(r['id'], '????')))

rows = []
for row in entities:
    try:
        mx = float(row['midx'])
        my = float(row['midy'])
    except Exception:
        continue
    assigned = None
    for rid, bbox, layer in clean_regions:
        if point_in_bbox(mx, my, bbox):
            assigned = layer
            break
    if assigned:
        rows.append({'handle': row['handle'], 'target_layer': assigned})

with output_csv.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['handle','target_layer'])
    writer.writeheader()
    writer.writerows(rows)

print(output_csv)
