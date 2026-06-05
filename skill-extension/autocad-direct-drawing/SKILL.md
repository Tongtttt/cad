---
name: "autocad-direct-drawing"
description: "Use when the user wants to work with AutoCAD on Windows: connect to an open drawing, drive AutoCAD via COM or MCP, load AutoLISP helpers, import vector/JSON linework, or troubleshoot why direct automation cannot see the active AutoCAD window."
---

# AutoCAD Direct Drawing

Use this skill for Windows AutoCAD work where Codex should operate on a real drawing instead of only describing steps.

## When to use

- User mentions `AutoCAD`, `CAD`, `DWG`, `LISP`, `APPLOAD`, or a currently open drawing
- User wants Codex to draw/import geometry into AutoCAD
- User wants to automate an existing AutoCAD session via COM or MCP
- User wants to convert local image/vector data into editable CAD linework
- User says AutoCAD automation cannot find the active window or drawing

## Core behavior

1. Prefer direct execution over teaching.
2. Prefer connecting to the user's active visible AutoCAD desktop session.
3. Assume the user may have opened AutoCAD and the target DWG in advance; prefer that visible instance over background automation instances.
4. If direct connection is blocked, diagnose the blocker before proposing fixes.
5. If direct drawing is not immediately possible, generate a usable fallback artifact such as `.lsp`, `.scr`, JSON linework, or a PowerShell bridge.

## Workflow

### 1. Establish the control path

Try these in order:

1. Existing MCP bridge for AutoCAD
2. Native AutoCAD COM automation on Windows
3. AutoLISP / script-file fallback loaded into AutoCAD

Choose the first path that can actually draw into the current DWG.

### 2. Confirm live AutoCAD state

Check:

- Is `acad.exe` running?
- Is there an open drawing, not just the welcome screen?
- Is AutoCAD running under a different privilege level or desktop session?
- Can COM see `AutoCAD.Application.*`?
- Does COM point to the same visible DWG the user opened on the desktop?
- Is COM accidentally attached to a hidden automation instance instead of the visible drawing window?

If AutoCAD is visible to the user but invisible to automation, suspect permission or session isolation first.
If COM resolves to a hidden automation instance, do not modify that document as if it were the user's visible drawing.

### 3. Prefer useful output over stalled debugging

If a direct bridge is flaky, do not stop at “connection failed”. Produce a fallback the user can run immediately:

- `AutoLISP` for `APPLOAD`
- `.scr` command script
- JSON/polyline export for later import
- PowerShell bridge that reads prepared geometry and writes into `ModelSpace`

### 4. Geometry strategy

- If the source is already vector or structured coordinates, keep it vector.
- If the source is raster, extract the minimum editable linework needed for the task.
- Preserve layers and closed polylines when possible.
- Name layers explicitly and keep output reusable.

### 5. Verification

Before claiming success, verify one of these:

- COM reports new entities in `ModelSpace`
- AutoCAD accepted and executed the generated script
- The generated fallback file exists and is ready for the user to load
- The document being modified matches the visible DWG the user opened

## Troubleshooting priorities

### AutoCAD cannot be found

Likely causes:

- AutoCAD launched as administrator while Codex is not
- AutoCAD is on a different Windows session/desktop
- No drawing is actually open
- The detected COM ProgID version is wrong

### COM found the wrong drawing

Likely causes:

- COM attached to a hidden automation instance
- Multiple `acad.exe` instances are running
- Hidden automation session exists alongside the visible desktop session

Recovery order:

1. Identify visible vs hidden instances
2. Prefer the visible desktop drawing the user opened manually
3. Avoid editing `Drawing1.dwg` in a hidden automation instance unless the user explicitly asked for it
4. If switching cannot be made reliable, fall back to a loadable artifact for the visible DWG

### Script sent but nothing appears

Check:

- Was the command terminated correctly?
- Did AutoCAD prompt for input mid-command?
- Did entities land far from origin?
- Is the drawing on the expected layer and viewport?

### Image-to-CAD quality is poor

Adjust in this order:

1. Source quality / thresholding
2. Number of contours kept
3. Polyline simplification amount
4. Layer separation

## Deliverables

Return the smallest artifact that gets the user moving:

- direct AutoCAD changes when possible
- otherwise a clickable local file path to the generated `.lsp`, `.scr`, `.ps1`, or JSON artifact

## Local notes

- If local AutoCAD helper scripts or MCP servers already exist, reuse them before inventing a new bridge.
- Keep generated helper files inside the active workspace unless the user explicitly asks for a global install.
- For repeated local workflows, prefer saving a reusable bridge script instead of retyping commands each session.
- In this environment, expect the user to pre-open the target AutoCAD drawing on the desktop; treat that visible drawing as the primary target.

For diagnostic command patterns and fallback guidance, read `references/troubleshooting.md` when needed.

## Persistent local workflow

Read `references/persistent-workflow.md` for this machine's fixed AutoCAD connection policy and fallback paths.

## Local bridge scripts

Use these local scripts before blind COM edits on this machine:

- `scripts/detect_visible_autocad.ps1` to identify the visible AutoCAD desktop window and distinguish it from automation instances
- `scripts/generate_cad_script.ps1` to create a stable `.scr` fallback for the visible drawing

Read `references/local-bridge-notes.md` when future sessions need the fixed local bridge policy.

## Smoothing existing linework

When the user already traced a drawing in CAD and only wants cleaner, smoother lines:

1. Prefer operating on the existing CAD entities instead of re-vectorizing the reference image.
2. Generate a reusable `.lsp` helper if direct entity editing is not yet safely automated.
3. Optimize for portrait linework with hair strands, floral contours, sleeves, and hand outlines.
4. Keep the first pass conservative: improve flow without destroying silhouette intent.

## Connecting broken portrait segments

When portrait linework contains many short broken segments:

1. Do not only smooth; connect first where the contour is obviously meant to be continuous.
2. Prefer conservative join distance and smaller local selections for hair, eyelashes, petals, jewelry, and fingers.
3. Run a connect pass first, then a smoothing pass.
4. Avoid globally joining everything, because decorative detail can collapse if the fuzz distance is too large.

## Layer-first portrait cleanup

For portrait line art based on a reference image, separate major structures into layers before smoothing or joining.

Recommended logical groups (Chinese layer names, all white/color 7):
- 外轮廓
- 头发主块
- 头发细节
- 五官
- 手部
- 衣物
- 花朵主轮廓
- 花朵细节
- 饰品
- 其他细节

Reason: layer-first cleanup reduces accidental joins across unrelated features and makes local retries safer.

## Semi-automatic portrait layer assignment

When the user wants portrait linework grouped before cleanup:

1. Create the standard portrait layers first.
2. Prefer grouped user selection into predefined portrait layers over unreliable blind spatial guessing when entity assignment must be trustworthy.
3. Treat the result as a first pass only; require quick human review before connection and smoothing.
4. Prefer this over globally editing all entities in one layer.

## Portrait semantic segmentation

For complex portrait drawings where hands, flowers, hair, ornaments, and clothing overlap, pure LISP selection is not enough.

Treat semantic portrait segmentation as an optional pre-processing layer above CAD cleanup:

1. Try semantic region recognition when available
2. Map recognized regions into portrait layers
3. Use CAD cleanup tools only after regional grouping is in place
4. Fall back to grouped manual assignment when segmentation is unavailable

Read `references/portrait-segmentation-plan.md` when working on smarter portrait grouping or future GitHub/model integrations.

## Desktop command bridge

If COM attaches to the wrong AutoCAD document but the visible desktop window is correct, use the local desktop command bridge instead of pretending COM is safe.

Read `references/desktop-command-bridge.md` and prefer `scripts/send_visible_autocad_keys.ps1` when direct command injection into the visible AutoCAD session is needed.

## Portrait bridge module

Use `portrait-bridge/` as the local integration point for portrait recognition and CAD entity-selection assistance.

- `portrait-bridge/references/local-runtime-notes.md` tracks available local runtimes
- `portrait-bridge/references/portrait_regions.schema.json` defines the region output contract
- `portrait-bridge/scripts/run_comfyui_portrait_bridge.ps1` is the stable local entry point
- `portrait-bridge/scripts/portrait_region_extractor.py` generates semantic portrait regions through a local Python runtime
- Current first-choice backend: local `torchvision` Mask R-CNN person segmentation; fallback: deterministic line-art heuristic grouping

## Visible COM Recovery

On Windows, `New-Object -ComObject AutoCAD.Application.*` may attach to a hidden automation instance even when the visible DWG is already open.

Use this recovery order:

1. Detect the visible AutoCAD desktop window first
2. Prefer `[System.Runtime.InteropServices.Marshal]::GetActiveObject('AutoCAD.Application.*')` over `New-Object -ComObject` when the visible session is already open
3. **CRITICAL: After GetActiveObject succeeds, check `$acad.Visible` and set it to `$true` if needed. If the window was previously hidden (e.g. by a prior `New-Object -ComObject` session), COM calls will fail with "AutoCAD 主窗口不可见". Set `$acad.Visible = $true` and `$acad.WindowState = 3` before any ModelSpace operations.**
4. Once `ActiveDocument.Name`, `FullName`, and `ModelSpace.Count` are non-empty, prefer direct COM entity processing over SendKeys

**Working COM connection pattern (to visible AutoCAD):**
```powershell
$acad = [System.Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application.24")
if (-not $acad.Visible) {
    $acad.Visible = $true
    $acad.WindowState = 3  # acMax
    Start-Sleep -Milliseconds 200
}
$doc = $acad.ActiveDocument
# Now safe to call $doc.ModelSpace.AddCircle(...) etc.
```

## Current Practical Boundary

This skill can now do all of the following when the local bridge is configured:

- detect the visible DWG window
- attach COM to the real visible AutoCAD instance
- export entity geometry from the visible DWG
- run semantic portrait region grouping and map those regions into CAD layers
- recolor and reorganize entities through COM

This skill still does **not** have a fully reliable non-interactive bridge for AutoCAD's interactive `PEDIT/JOIN/SMOOTH` command chain.
When the user asks for fully automatic final smoothing, treat SendKeys-based command injection as best-effort only and document that risk explicitly.

## COM: Hidden Instance Cleanup

Multiple `acad.exe` processes are common on this machine. `GetActiveObject` may attach to a hidden/headless instance instead of the visible desktop window, causing `Documents.Count` to show an empty document with no open drawings.

**Before connecting, always kill hidden acad.exe instances:**

```powershell
$procs = Get-Process acad -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    if ([string]::IsNullOrEmpty($p.MainWindowTitle)) {
        $p.Kill()  # hidden instance — remove it
    }
}
# Then GetActiveObject will only find the visible desktop AutoCAD
```

After cleanup, `GetActiveObject("AutoCAD.Application.24")` should show the correct documents with non-empty `ModelSpace.Count`.

## Image-to-CAD: Closed Contours vs Open Segments

**This is the most important lesson for portrait tracing quality.**

### The problem

Canny edge detection + `findContours` produces **closed polygon contours** that wrap around detected regions. When imported as closed polylines (`AddLightWeightPolyline` with `Closed = $true`), each contour becomes a hard polygonal loop. This looks stiff and unnatural — not like hand-drawn line art.

### The reference quality target

A good hand-traced portrait drawing uses **open polyline segments** that follow edges like brush strokes. Key characteristics of a good reference:

| Metric | Good reference | Bad (closed contour) |
|--------|---------------|---------------------|
| Entities | ~2800+ open polylines | ~600 closed polylines |
| Vertices per segment | 3-20 (mostly 4-8) | 10-50+ |
| Closed | **All false** | All true |
| Visual feel | Soft, flowing line art | Hard, faceted polygons |

### The approach (incomplete — quality not solved)

Splitting closed contours into short open chunks (6 vertices each, 1-vertex overlap) can increase entity count to ~2900 and mimic the segment density, but **the visual result is still poor** because:

1. Canny edge topology fundamentally differs from artist-drawn strokes
2. Splitting a contour doesn't change where the edge pixels are
3. Polygon approximation removes organic hand-drawn curvature
4. No stroke-direction or line-weight variation

### Known limitations

- OpenCV Canny + contour extraction is **not sufficient** for production-quality portrait line art
- True curve vectorization (potrace-style centerline tracing, LSD line segments, or ML-based sketch extraction) would likely produce better results
- The current pipeline is acceptable for rough layout but not for finished portrait drawings
- `portrait-bridge/` with ComfyUI / ML models is the intended long-term path for quality improvement

### Do NOT blindly iterate parameters

When quality is poor, changing thresholds (Canny low/high, RDP epsilon, area cutoff, chunk size) produces marginal differences but never fundamentally fixes the closed-contour problem. **State clearly that the OpenCV approach has intrinsic limits** rather than silently iterating dozens of parameter combinations.

## Project Mode Split

Use two different working modes in this skill:

### 1. Portrait / character tracing mode

Use this mode only when the user clearly says they are drawing a person, anime character, portrait, or tracing a character image.

Rules:
- This mode is mainly for entertainment / visual likeness
- The goal is to trace or approximate the reference image according to the user's requested style
- Keep all existing portrait-related bridges, segmentation work, layer grouping logic, and AutoCAD helper workflows active
- Precision matters, but engineering manufacturing correctness is not the primary standard

### 2. Engineering / chemical drafting mode

Use this mode by default unless the user explicitly indicates portrait/character tracing.

Rules:
- This mode is the default for ambiguous CAD requests
- Treat the task as engineering drafting first, especially for mechanical / chemical / piping / valve / equipment drawings
- Prioritize dimensional logic, standards, structure, constraints, annotation meaning, and drawing correctness over visual similarity
- Do not rely on image-like approximation when the task is really an engineering drawing
- If the user does not explicitly say the target is a person or a character image, assume they want rigorous engineering drafting

#### 2a. Mode activation

This mode activates automatically when the user mentions any of: P&ID, process flow, piping, equipment layout, valve, pump, tank, instrument, BFD, PFD, isometric, plot plan, GA, chemical, plant, flange, pipe, DN, PN, exchanger, reactor, compressor, blower, steam, condensate, cooling water, nitrogen, relief, safety valve, control loop, DCS, PLC, ISA tag (e.g., FIC-101), line number with hyphens (e.g., 6-P-1001-B1A), HG/T or HG standard, ASME B31 or ASME B16, DEXPI.

Ambiguous CAD requests without explicit portrait reference default here.

#### 2b. Chemical drawing type hierarchy

Know which drawing type the user needs before inserting geometry:

| Level | Type | Content | MCP Tools |
|-------|------|---------|-----------|
| 1 | BFD (Block Flow Diagram) | Major blocks + flow arrows, no equipment detail | `draw_process_line`, `add_flow_arrow`, `add_equipment_tag` |
| 2 | PFD (Process Flow Diagram) | Major equipment, stream tables, operating conditions | `insert_symbol` (EQUIPMENT), `insert_pump`, `insert_tank` for major items |
| 3 | **P&ID** (Piping & Instrumentation Diagram) | All equipment/valves/instruments, line numbers, full ISA tags | **All 12 `pid` operations** — this is where the full toolchain shines |
| 4 | Plot Plan / GA | Equipment layout with coordinates, steel, civil | `entity` (rectangles, lines), `annotation` (dimensions) |
| 5 | Piping Isometrics | Single line, all dimensions, BOM, weld details | `entity` (polylines), `annotation` (dimensions, leaders) |

**BFD vs PFD vs P&ID distinction:**

| Feature | BFD | PFD | P&ID |
|---------|-----|-----|------|
| Equipment | None | Major only | All (including spares) |
| Pipe lines | Major flows | Main process lines | Every line with number, size, spec |
| Instruments | None | Major controllers only | All instruments with ISA tags |
| Valves | None | Key control valves | Every valve with type and tag |
| Line breaks | None | None | Cross-references between sheets |

#### 2c. MCP Server integration

**P&ID tooling is available via the AutoCAD MCP Server** at `C:\Users\ASUS\cad\`.

The `pid` tool provides 12 operations:

```
pid(operation="setup_layers")                                → Create all 7 P&ID layers
pid(operation="list_symbols",     data={"category": "VALVES"})  → List available symbols
pid(operation="insert_symbol",    data={"category":"VALVES","symbol":"VA-GATE","x":100,"y":200,"scale":1.0,"rotation":0})
pid(operation="draw_process_line",  data={"x1":0,"y1":0,"x2":100,"y2":50})
pid(operation="connect_equipment",  data={"x1":0,"y1":0,"x2":100,"y2":50})
pid(operation="add_flow_arrow",    data={"x":80,"y":40,"rotation":45})
pid(operation="add_equipment_tag", data={"x":50,"y":120,"tag":"P-101A","description":"Feed Pump"})
pid(operation="add_line_number",   data={"x":30,"y":10,"line_num":"PG-03-001-100","spec":"L1B-C"})
pid(operation="insert_valve",     data={"x":60,"y":30,"valve_type":"GATE","rotation":0})
pid(operation="insert_instrument", data={"x":80,"y":50,"instrument_type":"FLOW","tag_id":"FIC-101","range_value":"0-100 GPM"})
pid(operation="insert_pump",      data={"x":20,"y":40,"pump_type":"CENTRIF1","rotation":0})
pid(operation="insert_tank",      data={"x":20,"y":100,"tank_type":"VERTICAL_DOME","scale":1.5})
```

**Dual backend architecture:**

| Backend | When Active | Symbol Quality |
|---------|------------|----------------|
| `file_ipc` | Live AutoCAD visible on desktop | Full ISA 5.1 CTO symbol blocks with attributes |
| `ezdxf` headless | No AutoCAD running | Simplified geometric placeholders (rectangles, circles, diamonds) with labels |

- Verify backend health with `system(operation="health")`.
- For production P&IDs, always prefer the `file_ipc` backend with live AutoCAD.
- The `.mcp.json` at `C:\Users\ASUS\cad\.mcp.json` defines the current bridge configuration.
- When MCP is unavailable entirely, fall back to LISP helpers (see 2h).

**Other MCP tools used in engineering drafting:**

| Tool | Operations |
|------|-----------|
| `entity` | create_line, create_polyline, create_circle, create_rectangle, create_arc |
| `layer` | list, create, set_current, freeze/thaw |
| `annotation` | create_text, create_dimension_horizontal, create_dimension_vertical, create_dimension_aligned, create_leader |
| `block` | list, insert, get_attributes, update_attribute |
| `view` | zoom_extents, zoom_window, get_screenshot |
| `drawing` | info |

#### 2d. P&ID layer naming

Always start a new P&ID with `pid(operation="setup_layers")`. This creates:

| Layer | Color | Usage |
|-------|-------|-------|
| `PID-EQUIPMENT` | 6 (Magenta) | Equipment symbols — vessels, exchangers, tanks |
| `PID-PROCESS-PIPING` | 4 (Cyan) | Major process lines — solid |
| `PID-UTILITY-PIPING` | 3 (Green) | Utility / service lines — dashed |
| `PID-INSTRUMENTS` | 5 (Blue) | Instrument bubbles, loops |
| `PID-ELECTRICAL` | 1 (Red) | Signal / electrical lines — dotted |
| `PID-ANNOTATION` | 7 (White/Black) | Tags, line numbers, notes |
| `PID-VALVES` | 2 (Yellow) | Valve symbols |

These map to the DEXPI / ISO discipline-prefix convention (`D-EQUIP-*`, `D-PIPE-MAJOR`, `D-INST-*`, etc.). See `references/pid-standards-reference.md` for the full mapping.

**Line break priority** when lines cross: electrical signal > instrument > minor/utility > major process.
Break gap: 3 mm.

#### 2e. CTO symbol library

The CAD Tools Online (CTO) library at `C:/PIDv4-CTO/` contains **600+ ISA 5.1-2009 standard P&ID symbols** as `.dwg` block files.

**Six built-in categories** from `cto_library.py`:

| Category | Key Symbols |
|----------|------------|
| **ACTUATORS** | Bellows Spring, Motor, Solenoid, Spring Diaphragm |
| **ANNOTATION** | Equipment Tag, Equipment Description, Flow Arrow, Line Number |
| **EQUIPMENT** | Clarifier, Filter, Filter Press, Heat Exchanger, Motor, Screen Bar |
| **PUMPS-BLOWERS** | Centrifugal 1/2, Diaphragm, Metering, Progressive Cavity, Submersible |
| **TANKS** | Vertical Open, Vertical Dome, Horizontal, Cone Bottom |
| **VALVES** | Gate, Globe, Check, Ball, Butterfly, Knife Gate |

**Discovery workflow:**

1. Browse symbols: `pid(operation="list_symbols", data={"category": "VALVES"})`
2. Place a symbol: `pid(operation="insert_symbol", data={"category":"VALVES","symbol":"VA-GATE","x":10,"y":20})`
3. Populate attributes after insertion: `block(operation="update_attribute", data={"entity_id":"...","tag":"LINE-NO","value":"6-P-1001-B1A"})`

CTO symbol blocks carry standard attributes (EQUIPMENT-TYPE, EQUIPMENT-NO, MANUFACTURER, MODEL-NO, LINE-NO, TAG, RANGE, SERVICE, MATERIAL, etc.). Valid P&IDs must have these populated. See `references/pid-standards-reference.md` for the full attribute table.

#### 2f. Canonical P&ID workflow

Follow this order for any new P&ID:

**Step 1 — Initialize**
- `pid(operation="setup_layers")`
- `drawing(operation="info")` to verify the active document

**Step 2 — Place major equipment**
- Determine category/symbol from CTO library
- `pid(operation="insert_pump", ...)`, `pid(operation="insert_tank", ...)`, or `pid(operation="insert_symbol", ...)` for specialty equipment
- Use reasonable spacing: 80-150 mm between equipment centers in model space
- Populate equipment number attributes (e.g., `P-101A`, `T-201`)

**Step 3 — Draw process pipe runs**
- `pid(operation="draw_process_line", data={"x1":...,"y1":...,"x2":...,"y2":...})` for straight segments
- `pid(operation="connect_equipment", ...)` for orthogonal routes between equipment
- Place on `PID-PROCESS-PIPING` (major lines) or `PID-UTILITY-PIPING` (utility)

**Step 4 — Insert in-line components**
- `pid(operation="insert_valve", data={"x":...,"y":...,"valve_type":"GATE","rotation":...})`
- `pid(operation="insert_instrument", data={"x":...,"y":...,"instrument_type":"FLOW","tag_id":"FIC-101","range_value":"0-100 GPM"})`
- Valves go on `PID-VALVES`, instruments on `PID-INSTRUMENTS`

**Step 5 — Add flow arrows**
- `pid(operation="add_flow_arrow", data={"x":...,"y":...,"rotation":...})`
- One arrow per line direction; batch where needed

**Step 6 — Annotate**
- Equipment tags: `pid(operation="add_equipment_tag", data={"x":...,"y":...,"tag":"P-101A","description":"Centrifugal Feed Pump"})`
- Line numbers: `pid(operation="add_line_number", data={"x":...,"y":...,"line_num":"PG-03-001-100","spec":"L1B-C"})`
- Annotation text height: 2.5-3.0 mm for equipment tags, 2.0 mm for line numbers

**Step 7 — Verify**
- `entity(operation="count")` or per-layer counts
- `view(operation="zoom_extents")` and `view(operation="get_screenshot")` for visual review

#### 2g. Line numbering and annotation standards

**HG/T 20519 domestic format** (primary reference for Chinese projects):

```
PG-03-001-100-L1B-C
│  │  │   │   │  │
│  │  │   │   │  └─ Insulation: C=Cold, H=Hot, I=Thermal, S=Acoustic
│  │  │   │   └──── Pipe Class: L=1.0MPa, 1=seq, B=Carbon Steel
│  │  │   └──────── Pipe Size: DN in mm
│  │  └──────────── Serial: 001-999
│  └─────────────── Unit/Area: 01-99
└────────────────── Service Code: PG=Process Gas, PL=Process Liquid, CW=Cooling Water, etc.
```

**International EPC format:**

```
6-P-1001-B1A-H-ST  = 6" NPS, Process, line 1001, class B1A, Hot insulated, Steam Traced
```

**ISA 5.1 instrument tag format:**

```
FIC-101  = Flow Indicating Controller, loop 101
PT-201   = Pressure Transmitter, loop 201
LAHH     = Level Alarm High-High
TCV-301  = Temperature Control Valve, loop 301
```

First letter = measured variable (F=Flow, P=Pressure, T=Temperature, L=Level, A=Analysis, S=Speed, W=Weight).
Succeeding letters = function (I=Indicate, C=Control, T=Transmit, A=Alarm, S=Switch, R=Record, V=Valve, H=High).

**Equipment numbering:** `[Type]-[Area][Serial][Suffix]` — e.g., `P-101A` = Pump, Area 100, first of two (A/B).

Full tag letter tables and service codes are in `references/pid-standards-reference.md`.

#### 2h. LISP fallback bridge

When MCP is unavailable but COM connects to live AutoCAD, generate a `.lsp` file using `attribute_tools.lsp` commands.

Key fallback commands from `C:\Users\ASUS\cad\lisp-code\attribute_tools.lsp`:

| Command | Purpose |
|---------|---------|
| `insert-pid-equipment` | Full equipment block with CTO attributes |
| `insert-valve-with-attributes` | Valve block + CTO metadata |
| `insert-equipment-tag` | Equipment tag on ANNOT-EQUIP_TAG block |
| `insert-equipment-description` | Multi-line description on ANNOT-EQUIP_DESCR block |
| `insert-line-number` | Line number on ANNOT-LINE_NUMBER block |
| `insert-instrument-with-tag` | Instrument block + TAG + RANGE |
| `update-block-attribute` | Edit single attribute on any block entity |
| `insert-block-simple` | Insert any CTO block without attribute dialog |
| `insert-block-with-attribs` | Insert + batch attribute set from list |
| `list-block-attributes` | Debug: dump all attributes from a block |

Workflow: write the LISP commands to a `.lsp` file, instruct the user to `APPLOAD` it in AutoCAD, then run the generated commands.

#### 2i. Headless / offline fallback (ezdxf)

When no AutoCAD instance is running, the MCP server uses the ezdxf headless backend:

- `pid` operations work but produce simplified geometry (rectangles for equipment, diamonds for valves, circles for instruments).
- Layer assignments, labels, and tags are preserved correctly.
- Generated `.dxf` files can be opened in AutoCAD later — re-insert CTO blocks to replace simplified placeholders with true ISA symbols.
- For layout/coordination work, headless `.dxf` is sufficient. For production P&IDs, always require the final pass in live AutoCAD with the `file_ipc` backend.

#### 2j. Standards quick reference

Key standards governing chemical drafting — use these as design authority, not the skill itself:

- **ISA 5.1-2009** — Instrumentation symbols and identification (basis of CTO library)
- **ISO 10628 / ISO 14617** — Process equipment and diagram symbols
- **HG/T 20519** — Chinese chemical process design documentation depth (line numbering basis)
- **HG/T 20559.5** — Chinese standard for material codes on P&IDs
- **ASME B31.3** — Process piping code (routing clearances, isometric annotation)
- **ASME B16.5 / B16.47** — Pipe flanges and flanged fittings dimensions
- **DEXPI 2.0** — Vendor-neutral P&ID/PFD data exchange (Proteus XML / OPC UA)
- **PIP PIC001** — P&ID documentation criteria
- **IEC 62424** — P&ID representation for process control

Full symbol tables, service codes, tag letter matrices, and layer mappings are in `references/pid-standards-reference.md`.
