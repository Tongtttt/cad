# CLAUDE.md

AutoCAD MCP server — bridges Claude AI with AutoCAD LT via the Model Context Protocol (Python).

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                          # Install dependencies
uv run pytest tests/ -v          # Run all tests
uv run pytest tests/test_ezdxf_backend.py -v  # Run ezdxf backend tests
uv run pytest tests/test_ipc_protocol.py -v   # Run IPC protocol tests
uv run python -m autocad_mcp     # Run MCP server manually
```

## Architecture

```
MCP Client (Claude)
    │  stdio (JSON-RPC)
    ▼
autocad_mcp/server.py          — FastMCP server, 8 tools with operation dispatch
    │
    ├── backends/file_ipc.py   — File IPC: PostMessageW(WM_CHAR) → mcp_dispatch.lsp in AutoCAD LT
    │   Reads/writes JSON via C:/temp/*.json, no focus steal
    │
    └── backends/ezdxf_backend.py — Headless DXF generation, no AutoCAD required
        Uses ezdxf + matplotlib for rendering
```

- **`src/autocad_mcp/server.py`** — All 8 MCP tools (`drawing`, `entity`, `layer`, `block`, `annotation`, `pid`, `view`, `system`). Each tool dispatches operations to the active backend. Tools return `str | list` (list for ImageContent + TextContent).
- **`src/autocad_mcp/client.py`** — Backend auto-detection (`auto` → try file_ipc, fallback ezdxf), error wrapping (`_safe`, `_error`, `_json`), screenshot helper.
- **`src/autocad_mcp/config.py`** — Environment variable parsing (`AUTOCAD_MCP_BACKEND`, `AUTOCAD_MCP_IPC_DIR`, etc.).
- **`src/autocad_mcp/screenshot.py`** — Win32 PrintWindow for File IPC, matplotlib render for ezdxf.
- **`src/autocad_mcp/pid/cto_library.py`** — CTO P&ID symbol library mapping.
- **`lisp-code/mcp_dispatch.lsp`** — AutoLISP dispatcher loaded in AutoCAD LT 2024+. Reads IPC JSON, executes commands, writes results back.
- **`tests/`** — Pytest with `asyncio_mode = "auto"`. Tests cover ezdxf backend and IPC protocol.

## Backend Selection

Set `AUTOCAD_MCP_BACKEND` env var: `auto` (default, tries File IPC first), `file_ipc` (requires AutoCAD LT 2024+ Windows), `ezdxf` (headless, cross-platform).

## Key Constraints

- File IPC backend requires Windows native Python (not WSL) — uses `pywin32` for `PostMessageW`.
- When running from WSL, launch via `cmd.exe /d /s /c` so Python runs as native Windows process.
- LISP files use Windows-1252 encoding; Python side has UTF-8/cp1252 fallback for result parsing.

## MCP Client Configuration (Claude Code)

项目根目录 `.mcp.json` 和 `~/.claude/.mcp.json` 中配置了 autocad-mcp 服务器入口。
由于 Git Bash/MSYS2 环境，必须通过 `cmd.exe` 启动：

```json
{
  "mcpServers": {
    "autocad-mcp": {
      "type": "stdio",
      "command": "cmd.exe",
      "args": ["/d", "/s", "/c", "cd /d <project> && .venv\\Scripts\\python.exe -m autocad_mcp"],
      "env": { "AUTOCAD_MCP_BACKEND": "auto" }
    }
  }
}
```

## 绘图前置设置（AutoCAD 环境）

通过 File IPC 绘图前必须设置以下系统变量，否则线条会乱连、中文乱码：

1. **OSMODE=0** — 关闭对象捕捉（最关键的设置！否则 line 端点会跳到附近的捕捉点）
2. **字体样式** — `_.-STYLE` 命令创建使用宋体的 CHINESE 文字样式
3. **LTSCALE=0.5** — 线型比例，让中心线/虚线正常显示
4. **LUNITS=2** — 十进制单位
5. **加载线型** — CENTER、DASHED 等需要从 acadiso.lin 加载

参考实现：`_cad_setup2.py`

## 三通法兰阀体工程图项目 (2026-05-19)

### 项目概述
绘制三通式法兰连接阀体的 A4 工程图，包含全剖主视图和 A-A 剖视图。

### 关键文件
- `D:\新建文件夹\零件特征.txt` — 零件全部尺寸/公差/技术要求
- `C:\Users\ASUS\Pictures\Camera Roll\屏幕截图 2026-05-19 170234.png` — 参考图
- `_draw_final_v3.py` — 最终绘图脚本（File IPC 直接绘制）
- `_cad_setup2.py` — AutoCAD 环境配置脚本
- `C:\Users\ASUS\Desktop\valve_body_A4_v2.dwg` — 最终 DWG 输出

### 技术要点
- 通过 FileIPCBackend 直接调用 `create_line`/`create_circle`/`create_mtext` 等方法在 AutoCAD 中逐条创建实体
- ezdxf 生成 DXF 导入方案被放弃：DXF 打开后实体无法正确加载到 AutoCAD
- OCR 方案（easyocr + OpenCV）尝试识别参考图：文字提取成功但耗时过长（CPU），仅用 OpenCV 边缘检测辅助理解视图布局
- DeepSeek 模型无视觉能力，无法直接查看截图，依赖尺寸数据+边缘分析拼凑图面

### 视图布局
- 左上区：主视图（全剖视），水平中心轴 paper Y=140，左端 paper X=50
- 右上区：A-A 剖视（右法兰），中心 paper (225, 135)
- 底部：标题栏 + 技术要求

### 零件关键尺寸
- 总长 96mm × 总高 45mm，材料 HT200，比例 1:1.5
- 左端口 G1/2 管螺纹，φ25 内孔，1×45° 倒角
- 中间主体 φ50 外圆，内腔 φ64/φ50
- 顶部端口 G3/4，φ40 外圆，高 46mm，螺纹深 14mm
- 右法兰 φ80×8mm，内孔 φ44H7(+0.039/0)→φ30，深 28mm
- 4×φ9 螺栓孔，φ60 PCD，45° 均布
