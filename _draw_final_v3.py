"""全新绘制 - 先设置环境再画图"""
import asyncio, math
from autocad_mcp.backends.file_ipc import FileIPCBackend

async def main():
    b = FileIPCBackend()
    await b.initialize()

    # ==================== 环境设置 ====================
    print("设置环境...")
    setups = [
        '(setvar "OSMODE" 0)',       # 关闭捕捉(防乱连)
        '(setvar "AUTOSNAP" 0)',
        '(setvar "GRIDMODE" 0)',
        '(setvar "LUNITS" 2)',
        '(setvar "LTSCALE" 0.5)',
        '(setvar "LWDISPLAY" 0)',
        '(setvar "TILEMODE" 1)',
        '(if (not (tblsearch "LTYPE" "CENTER")) (command "_.-LINETYPE" "_L" "CENTER" "acadiso.lin" ""))',
        '(if (not (tblsearch "LTYPE" "DASHED")) (command "_.-LINETYPE" "_L" "DASHED" "acadiso.lin" ""))',
        '(command "_.-STYLE" "CHINESE" "宋体" "" "" "" "" "" "")',
    ]
    for s in setups:
        r = await b.execute_lisp(s)
        if not r.ok:
            print(f"  警告: {s[:50]} -> {r.error}")

    # ==================== 清空 ====================
    print("清空旧图...")
    await b.drawing_create()

    # ==================== 图层 ====================
    print("创建图层...")
    layers = [
        ("A4_FRAME", 7, 30),
        ("A4_OUTLINE", 7, 50),
        ("A4_CENTER", 1, 13),
        ("A4_THIN", 7, 13),
        ("A4_TEXT", 7, 13),
        ("A4_HATCH", 8, 13),
    ]
    for ln, c, lw in layers:
        await b.execute_lisp(
            f'(command "_.-LAYER" "_M" "{ln}" "_C" "{c}" "" "_LW" "{lw/100:.2f}" "" "")')

    # 给CENTER图层指定线型
    await b.execute_lisp('(command "_.-LAYER" "_LT" "CENTER" "" "A4_CENTER" "")')

    # ==================== A4 图框 ====================
    print("A4图框...")
    await b.create_rectangle(0, 0, 297, 210, layer="A4_FRAME")
    await b.create_rectangle(20, 5, 292, 205, layer="A4_FRAME")

    # ==================== 主视图 (全剖视) ====================
    print("主视图(全剖视)...")
    X0, YC = 50.0, 140.0
    def lx(x): return X0 + x
    def ly(y): return YC + y

    # X分段 (总长96mm)
    X = [0, 20, 23, 24, 31, 66, 80, 88, 96]
    R_ext = [18, 18, 17.5, 17.5, 25, 25, 25, 40, 40]

    # === 上半外部 ===
    await b.create_line(lx(0), YC, lx(0), YC+R_ext[0], layer="A4_OUTLINE")
    for i in range(len(X)-1):
        await b.create_line(lx(X[i]), YC+R_ext[i], lx(X[i+1]), YC+R_ext[i+1], layer="A4_OUTLINE")
    await b.create_line(lx(96), YC, lx(96), YC+R_ext[-1], layer="A4_OUTLINE")

    # === 上半内部型腔 ===
    # 左端口φ25
    await b.create_line(lx(0), YC, lx(0), YC+12.5, layer="A4_OUTLINE")
    await b.create_line(lx(0), YC+12.5, lx(20), YC+12.5, layer="A4_OUTLINE")
    # 倒角1x45
    await b.create_line(lx(0), YC+12.5, lx(1), YC+13.5, layer="A4_OUTLINE")
    # φ25→φ64过渡
    await b.create_line(lx(20), YC+12.5, lx(30), YC+32, layer="A4_OUTLINE")
    # φ64大腔
    await b.create_line(lx(30), YC+32, lx(60), YC+32, layer="A4_OUTLINE")
    # φ64→φ44过渡
    await b.create_line(lx(60), YC+32, lx(72), YC+22, layer="A4_OUTLINE")
    # φ44孔
    await b.create_line(lx(72), YC+22, lx(82), YC+22, layer="A4_OUTLINE")
    # 台阶→φ30 (R1.5)
    await b.create_line(lx(82), YC+22, lx(82), YC+15, layer="A4_OUTLINE")
    await b.create_arc(lx(82+1.5), YC+15+1.5, 1.5, 180, 270, layer="A4_OUTLINE")
    # φ30孔 深28
    await b.create_line(lx(82+1.5), YC+15, lx(96-28), YC+15, layer="A4_OUTLINE")
    await b.create_line(lx(96-28), YC+15, lx(96-28), YC, layer="A4_OUTLINE")

    # === 顶部端口 ===
    tcx = lx(48.5)
    tby = YC + 25
    tey = YC + 22.5
    # 外部
    await b.create_line(tcx-20, tby, tcx-20, tey, layer="A4_OUTLINE")
    await b.create_line(tcx+20, tby, tcx+20, tey, layer="A4_OUTLINE")
    await b.create_line(tcx-20, tey, tcx+20, tey, layer="A4_OUTLINE")
    # R3圆角
    await b.create_arc(tcx-17, tby+3, 3, 180, 270, layer="A4_OUTLINE")
    await b.create_arc(tcx+17, tby+3, 3, 270, 360, layer="A4_OUTLINE")
    # 内孔
    tte = tey - 14
    await b.create_line(tcx-12, tby, tcx-12, tte, layer="A4_OUTLINE")
    await b.create_line(tcx+12, tby, tcx+12, tte, layer="A4_OUTLINE")
    await b.create_line(tcx-12, tte, tcx+12, tte, layer="A4_OUTLINE")
    # 倒角
    await b.create_line(tcx-12, tey, tcx-11, tey-1, layer="A4_OUTLINE")
    await b.create_line(tcx+12, tey, tcx+11, tey-1, layer="A4_OUTLINE")

    # === 下半外部 ===
    await b.create_line(lx(0), YC, lx(0), YC-R_ext[0], layer="A4_OUTLINE")
    for i in range(len(X)-1):
        await b.create_line(lx(X[i]), YC-R_ext[i], lx(X[i+1]), YC-R_ext[i+1], layer="A4_OUTLINE")
    await b.create_line(lx(96), YC, lx(96), YC-R_ext[-1], layer="A4_OUTLINE")

    # === 下半内部 ===
    await b.create_line(lx(0), YC-12.5, lx(20), YC-12.5, layer="A4_OUTLINE")
    await b.create_line(lx(20), YC-12.5, lx(30), YC-32, layer="A4_OUTLINE")
    await b.create_line(lx(30), YC-32, lx(60), YC-32, layer="A4_OUTLINE")
    await b.create_line(lx(60), YC-32, lx(72), YC-22, layer="A4_OUTLINE")
    await b.create_line(lx(72), YC-22, lx(82), YC-22, layer="A4_OUTLINE")
    await b.create_line(lx(82), YC-22, lx(82), YC-15, layer="A4_OUTLINE")
    await b.create_line(lx(82+1.5), YC-15, lx(96-28), YC-15, layer="A4_OUTLINE")
    await b.create_line(lx(96-28), YC-15, lx(96-28), YC, layer="A4_OUTLINE")

    # === 底部基准面 ===
    by = YC - 22.5
    await b.create_line(lx(18), by, lx(85), by, layer="A4_OUTLINE")
    await b.create_line(lx(23), YC-17.5, lx(18), by, layer="A4_OUTLINE")
    await b.create_line(lx(60), YC-25, lx(85), by, layer="A4_OUTLINE")
    await b.create_line(lx(88), YC-40, lx(88), by, layer="A4_OUTLINE")
    await b.create_line(lx(85), by, lx(88), by, layer="A4_OUTLINE")

    # === 中心线 ===
    await b.create_line(lx(-8), YC, lx(104), YC, layer="A4_CENTER")
    await b.create_line(tcx, YC-30, tcx, YC+28, layer="A4_CENTER")

    # ==================== A-A剖视 ====================
    print("A-A剖视...")
    aax, aay = 225.0, 135.0

    await b.create_circle(aax, aay, 40, layer="A4_OUTLINE")
    await b.create_circle(aax, aay, 22, layer="A4_OUTLINE")
    await b.create_circle(aax, aay, 30, layer="A4_CENTER")

    for ang in [45, 135, 225, 315]:
        rad = math.radians(ang)
        bx, by = aax+30*math.cos(rad), aay+30*math.sin(rad)
        await b.create_circle(bx, by, 4.5, layer="A4_OUTLINE")
        await b.create_line(bx-6, by, bx+6, by, layer="A4_CENTER")
        await b.create_line(bx, by-6, bx, by+6, layer="A4_CENTER")

    await b.create_line(aax-50, aay, aax+50, aay, layer="A4_CENTER")
    await b.create_line(aax, aay-50, aax, aay+50, layer="A4_CENTER")

    # 定位槽
    sl_y = aay - 40
    await b.create_polyline(
        [(aax-3.5, sl_y), (aax+3.5, sl_y),
         (aax+3.5, sl_y-8), (aax-3.5, sl_y-8)],
        closed=True, layer="A4_OUTLINE")

    # 标签 (使用CHINESE样式)
    await b.create_mtext(aax-10, aay-58, 30, "A-A", height=4, layer="A4_TEXT")
    await b.create_mtext(aax-20, aay-65, 60, "A-A 剖视", height=3, layer="A4_TEXT")

    # ==================== 标题栏 ====================
    print("标题栏...")
    tl, tb = 180.0, 5.0
    tr, tt = 292.0, 48.0

    await b.create_rectangle(tl, tb, tr, tt, layer="A4_OUTLINE")
    for y in [tb+8, tb+16, tb+24, tb+32, tb+40]:
        await b.create_line(tl, y, tr, y, layer="A4_THIN")
    for x in [tl+25, tl+60, tl+85]:
        await b.create_line(x, tb, x, tt, layer="A4_THIN")

    texts = [
        (tl+2, tb+2, "标记 处数 分区 更改文件号 签名 年月日", 1.6),
        (tl+2, tb+10, "设计", 2.0),
        (tl+27, tb+10, "审核", 2.0),
        (tl+62, tb+10, "工艺", 2.0),
        (tl+62, tb+18, "比例 1:1.5   材料 HT200", 3.0),
        (tl+62, tb+26, "阀体", 4.0),
        (tl+62, tb+34, "三通式法兰连接阀体", 3.0),
        (tl+27, tb+38, "标准化", 2.0),
        (tl+62, tb+38, "阶段标记 重量 比例", 2.0),
    ]
    for x, y, t, h in texts:
        await b.create_mtext(x, y, 100, t, height=h, layer="A4_TEXT")

    # ==================== 技术要求 ====================
    print("技术要求...")
    for i, n in enumerate([
        "技术要求:",
        "1. 未注铸造圆角R2~R3",
        "2. 未注表面粗糙度为铸造毛坯面",
        "3. 材料 HT200 (灰铸铁)",
        "4. 管螺纹G1/2、G3/4为55度非密封管螺纹",
        "5. 4X 直径9螺栓孔均布于直径60中心圆",
        "6. 直径44H7公差: +0.039/0",
    ]):
        await b.create_mtext(25, 68-i*5, 150, n, height=2.5, layer="A4_TEXT")

    # 视图标签
    await b.create_mtext(X0, YC+48, 60, "主视图（全剖视）", height=4, layer="A4_TEXT")

    # 剖切标记
    await b.create_line(lx(80), YC+46, lx(100), YC+46, layer="A4_THIN")
    await b.create_mtext(lx(77), YC+49, 10, "A", height=3.5, layer="A4_TEXT")

    # ==================== 保存 ====================
    await b.zoom_extents()
    await b.execute_lisp('(progn (command "_.ZOOM" "_W" "-10,-10" "310,220") (princ))')
    await b.drawing_save(r"C:/Users/ASUS/Desktop/valve_body_A4_v2.dwg")
    print("\n=== 完成! 桌面: valve_body_A4_v2.dwg ===")

if __name__ == "__main__":
    asyncio.run(main())
