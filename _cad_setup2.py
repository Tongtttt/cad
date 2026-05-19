"""AutoCAD绘图环境配置 - 分步执行"""
import asyncio
from autocad_mcp.backends.file_ipc import FileIPCBackend

async def run_cmd(b, desc, lisp):
    r = await b.execute_lisp(lisp)
    status = "OK" if r.ok else f"FAIL: {r.error}"
    print(f"  {desc}: {status}")

async def main():
    b = FileIPCBackend()
    await b.initialize()
    print("配置AutoCAD绘图环境...\n")

    # 1. 基础变量
    await run_cmd(b, "关闭对象捕捉(防止线乱连)", '(setvar "OSMODE" 0)')
    await run_cmd(b, "关闭极轴追踪", '(setvar "AUTOSNAP" 0)')
    await run_cmd(b, "关闭栅格", '(setvar "GRIDMODE" 0)')
    await run_cmd(b, "设置毫米单位", '(setvar "LUNITS" 2)')
    await run_cmd(b, "设置线型比例", '(setvar "LTSCALE" 0.5)')
    await run_cmd(b, "关闭线宽显示", '(setvar "LWDISPLAY" 0)')
    await run_cmd(b, "确保模型空间", '(setvar "TILEMODE" 1)')

    # 2. 加载线型
    await run_cmd(b, "加载CENTER线型",
        '(if (not (tblsearch "LTYPE" "CENTER")) (command "_.-LINETYPE" "_L" "CENTER" "acadiso.lin" ""))')
    await run_cmd(b, "加载DASHED线型",
        '(if (not (tblsearch "LTYPE" "DASHED")) (command "_.-LINETYPE" "_L" "DASHED" "acadiso.lin" ""))')

    # 3. 中文字体 - 尝试几个常见字体
    for font in ['宋体', 'SimSun', 'Microsoft YaHei', '微软雅黑', '仿宋', 'arial.ttf']:
        r = await b.execute_lisp(
            f'(command "_.-STYLE" "CHINESE" "{font}" "" "" "" "" "" "")')
        if r.ok:
            print(f"  中文字体 '{font}': OK")
            break
        else:
            print(f"  中文字体 '{font}': 不可用")

    # 4. 验收
    r = await b.execute_lisp(
        '(progn (princ "\\nOSMODE=")(princ (getvar "OSMODE"))'
        '(princ " LUNITS=")(princ (getvar "LUNITS"))'
        '(princ " LTSCALE=")(princ (getvar "LTSCALE"))'
        '(princ))')
    print(f"\n验收: {r.payload}")

    print("\n环境配置完成!")

asyncio.run(main())
