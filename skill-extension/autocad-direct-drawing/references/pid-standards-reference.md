# P&ID Standards Quick Reference

Secondary reference for the `pid` MCP tool and CTO symbol library.
Load only when needed for specific tag formats, layer lookup, or symbol selection.

---

## ISA 5.1 Instrument Tag Letters

### First Letter — Measured / Initiating Variable

| Letter | Variable | Letter | Variable |
|--------|----------|--------|----------|
| A | Analysis | N | User's Choice |
| B | Burner / Combustion | O | User's Choice |
| C | User's Choice | P | Pressure |
| D | User's Choice | Q | Quantity |
| E | Voltage | R | Radiation |
| F | Flow | S | Speed / Frequency |
| G | User's Choice | T | Temperature |
| H | Hand | U | Multivariable |
| I | Current | V | Vibration / Mechanical |
| J | Power | W | Weight / Force |
| K | Time / Schedule | X | Unclassified |
| L | Level | Y | Event / State |
| M | User's Choice | Z | Position / Dimension |

### Succeeding Letters — Readout / Passive Functions

| Letter | Function | Letter | Function |
|--------|----------|--------|----------|
| A | Alarm | N | Not used |
| B | User's Choice | O | Orifice / Restriction |
| C | Controller | P | Point (test connection) |
| D | Differential | Q | Integrate / Totalize |
| E | Sensor / Primary Element | R | Record |
| F | Ratio (fraction) | S | Switch |
| G | Glass / Gauge | T | Transmit |
| H | High | U | Multifunction |
| I | Indicate | V | Valve / Damper |
| J | Scan | W | Well |
| K | Time / Schedule | X | Unclassified |
| L | Light (pilot) | Y | Relay / Compute / Convert |
| M | Middle / Intermediate | Z | Driver / Actuator |

**Examples:** FIC-045 (Flow Indicating Controller, loop 045), PT-101 (Pressure Transmitter), LAHH (Level Alarm High-High), TCV-201 (Temperature Control Valve)

### Instrument Location Modifiers

| Symbol | Meaning |
|--------|---------|
| Plain circle | Field-mounted |
| Circle + horizontal line | Panel-mounted / DCS display |
| Diamond | PLC / logic solver |
| Square | Shared display / control function |

---

## HG/T 20519 Pipe Line Number Format

```
PG  03  001  -  100  L1B  -  C
(1) (2) (3)    (4)  (5)    (6)
```

| Segment | Name | Description |
|---------|------|-------------|
| (1) PG | Service Code | Two-letter material abbreviation |
| (2) 03 | Unit Code | Two-digit project section (01-99) |
| (3) 001 | Serial Number | Three-digit sequential (001-999) |
| (4) 100 | Pipe Size | Nominal diameter in mm (DN) |
| (5) L1B | Pipe Class/SPEC | L=1.0MPa rating, 1=sequence, B=carbon steel |
| (6) C | Insulation Code | H/C/I/S |

### Common Service Codes

| Code | Service | Code | Service |
|------|---------|------|---------|
| PG | Process Gas | PL | Process Liquid |
| CW | Cooling Water (Supply) | CWR | Cooling Water (Return) |
| HS | High-Pressure Steam | MS | Medium-Pressure Steam |
| LS | Low-Pressure Steam | CD | Condensate |
| IA | Instrument Air | PA | Plant Air |
| N2 | Nitrogen | O2 | Oxygen |
| DR | Drain | VT | Vent |
| FO | Fuel Oil | BFW | Boiler Feed Water |
| H2 | Hydrogen | NG | Natural Gas |
| AG | Ammonia Gas | SW | Service Water |

### Pipe Class Pressure Rating Codes (ANSI)

| Code | Rating | Code | Rating |
|------|--------|------|--------|
| A | 150LB | D | 600LB |
| B | 300LB | E | 900LB |

### Insulation Codes

| Code | Type | Code | Type |
|------|------|------|------|
| H | Hot Insulation | C | Cold Insulation |
| I | Thermal Insulation | S | Acoustic |
| P | Personnel Protection | N | None |

---

## Equipment Numbering

Format: `[Type Code]-[Area]-[Serial][Suffix]`

| Type Code | Equipment |
|-----------|-----------|
| P | Pump |
| T | Tank / Vessel |
| E | Heat Exchanger |
| C | Compressor |
| F | Furnace / Fired Heater |
| V | Valve |
| R | Reactor |
| D | Distillation Column |
| B | Blower / Fan |
| S | Separator |
| Y | Relief Device |

**Example:** P-101A = Pump in Area 100, first of two parallel pumps (A/B)

---

## P&ID Layer Names

### MCP Layers ↔ DEXPI / ISO Map

| MCP Layer | Color | Line | DEXPI / ISO Equivalent | Usage |
|-----------|-------|------|------------------------|-------|
| PID-EQUIPMENT | 6 (Magenta) | Continuous | D-EQUIP-* | Equipment symbols |
| PID-PROCESS-PIPING | 4 (Cyan) | Continuous | D-PIPE-MAJOR | Major process lines |
| PID-UTILITY-PIPING | 3 (Green) | Dashed | D-PIPE-MINOR | Utility / service lines |
| PID-INSTRUMENTS | 5 (Blue) | Dash-dot | D-INST-* | Instrument bubbles, loops |
| PID-ELECTRICAL | 1 (Red) | Dotted | E-INST-SIGNL | Signal / electrical lines |
| PID-ANNOTATION | 7 (White/Black) | Continuous | D-TEXT-* | Tags, line numbers, notes |
| PID-VALVES | 2 (Yellow) | Continuous | D-VALV-* | Valve symbols |

Invoke `pid(operation="setup_layers")` as the **first step** for any new P&ID drawing.

---

## Line Type Conventions by Service

| Line Type | AutoCAD Linetype | Usage |
|-----------|-----------------|-------|
| Solid | CONTINUOUS | Main process piping |
| Dashed | DASHED | Utility piping, future equipment |
| Dash-dot | DASHDOT | Instrument impulse tubing |
| Dash-dot-dot | DASHDOT2 | Electrical signal lines |
| Dotted | DOTTED | Existing / underground piping |
| Phantom | PHANTOM | Alternate position / demolition |

Drawing break priority (highest to lowest): electrical signal → instrument → minor/utility → major process.

---

## CTO Symbol Library Quick Lookup

600+ ISA 5.1-2009 symbols at `C:/PIDv4-CTO/`. Use `pid(operation="list_symbols", data={"category": "..."})` to browse.

### Categories and Key Symbols

**ACTUATORS** (prefix: `ACT-`)
`ACT-BELLOWS_SPRING`, `ACT-MOTOR`, `ACT-SOLENOID`, `ACT-SPRING_DIAPHRAGM`

**ANNOTATION** (prefix: `ANNOT-`)
`ANNOT-EQUIP_TAG`, `ANNOT-EQUIP_DESCR`, `ANNOT-FLOWARROW`, `ANNOT-LINE_NUMBER`

**EQUIPMENT** (prefix: `EQUIP-`)
`EQUIP-CLARIFIER`, `EQUIP-FILTER`, `EQUIP-FILTER_PRESS`, `EQUIP-HEAT_EXCH-GENERIC`, `EQUIP-MOTOR`, `EQUIP-SCREENBAR`

**PUMPS-BLOWERS** (prefix: `PUMP-`)
`PUMP-CENTRIF1`, `PUMP-CENTRIF2`, `PUMP-DIAPHRAGM`, `PUMP-METERING`, `PUMP-PROGRESSIVE_CAVITY`, `PUMP-SUBMERSIBLE`

**TANKS** (prefix: `TANK-`)
`TANK-VERTICAL_OPEN`, `TANK-VERTICAL_DOME`, `TANK-HORIZONTAL`, `TANK-CONE_BOTTOM_DOME`

**VALVES** (prefix: `VA-`)
`VA-GATE`, `VA-GLOBE`, `VA-CHECK`, `VA-BALL`, `VA-BUTTERFLY`, `VA-KNIFEGATE`

### CTO Block Attributes

Key attributes on CTO symbol blocks (varies by category):

| Attribute | Applies To | Example |
|-----------|------------|---------|
| EQUIPMENT-TYPE | Equipment | CENTRIFUGAL PUMP |
| EQUIPMENT-NO | Equipment, Tanks, Pumps | P-101A |
| MANUFACTURER | Equipment, Pumps | Sulzer |
| MODEL-NO | Equipment, Pumps | CP-50-200 |
| LINE-NO | Valves | PG-03-001-100 |
| LINE_NUMBER | Line annotations | PG-03-001-100 |
| TAG | Instruments | FIC-101 |
| RANGE | Instruments | 0-100 GPM |
| SERVICE | Pumps, Tanks | FEED |
| MATERIAL | All | CS / SS304 / SS316 |

---

## MCP `pid` Tool Operations Summary

| Operation | Required Fields | Optional Fields |
|-----------|----------------|-----------------|
| `setup_layers` | — | — |
| `list_symbols` | `category` | — |
| `insert_symbol` | `category`, `symbol`, `x`, `y` | `scale`, `rotation` |
| `draw_process_line` | `x1`, `y1`, `x2`, `y2` | — |
| `connect_equipment` | `x1`, `y1`, `x2`, `y2` | — |
| `add_flow_arrow` | `x`, `y` | `rotation` |
| `add_equipment_tag` | `x`, `y`, `tag` | `description` |
| `add_line_number` | `x`, `y`, `line_num`, `spec` | — |
| `insert_valve` | `x`, `y`, `valve_type` | `rotation`, `attributes` |
| `insert_instrument` | `x`, `y`, `instrument_type` | `rotation`, `tag_id`, `range_value` |
| `insert_pump` | `x`, `y`, `pump_type` | `rotation`, `attributes` |
| `insert_tank` | `x`, `y`, `tank_type` | `scale`, `attributes` |

---

## Attribute Tools (LISP Fallback)

`C:\Users\ASUS\cad\lisp-code\attribute_tools.lsp` provides 14+ AutoLISP commands for direct P&ID work when MCP is unavailable:

| Command | Purpose |
|---------|---------|
| `insert-block-simple` | Insert block without attribute dialog |
| `update-block-attribute` | Set single attribute on block entity |
| `insert-pid-equipment` | Full equipment + CTO attributes |
| `insert-valve-with-attributes` | Valve + CTO metadata |
| `insert-equipment-tag` | Equipment tag block (ANNOT-EQUIP_TAG) |
| `insert-equipment-description` | Description block (ANNOT-EQUIP_DESCR) |
| `insert-line-number` | Line number block (ANNOT-LINE_NUMBER) |
| `insert-instrument-with-tag` | Instrument + TAG + RANGE |
| `insert-block-with-attribs` | Insert + batch attribute set |
| `update-block-attribs-at-point` | Edit nearest block's attribute |
| `list-block-attributes` | Debug: dump all attributes |
| `edit-last-block-attrib` | Quick edit on last inserted block |

Usage: `appload` the `.lsp` file, then call commands in the form `(c:insert-pid-equipment)` or `(command "insert-pid-equipment")`.

---

## Key Standards

| Standard | Scope |
|----------|-------|
| ISA 5.1-2009 | Instrumentation symbols and identification |
| ISO 10628 | Flow diagrams for process plants (equipment symbols) |
| ISO 14617 | Graphical symbols for diagrams |
| HG/T 20519 | Chinese standard — chemical process design documentation |
| HG/T 20559.5 | Chinese standard — material codes on P&IDs |
| ASME B31.3 | Process piping code |
| ASME B31.1 | Power piping code |
| DEXPI 2.0 | Vendor-neutral P&ID/PFD data exchange |
| IEC 62424 | P&ID representation for process control |
| ISO 6412 | Simplified isometric pipeline representation |
| PIP PIC001 | P&ID documentation criteria |

## Drawing Type Hierarchy

```
BFD → PFD → P&ID → Plot Plan/GA → Piping Isometrics
```

| Type | Content | Scale |
|------|---------|-------|
| BFD | Major blocks + flow arrows | Not to scale |
| PFD | Major equipment, stream tables, operating conditions | Not to scale |
| P&ID | All equipment/valves/instruments with tags, line numbers | Not to scale |
| Plot Plan / GA | Equipment layout with coordinates, steel, civil | 1:100–1:500 |
| Piping Isometrics | Single line, all dimensions, BOM, weld details | To scale (dimensioned) |
