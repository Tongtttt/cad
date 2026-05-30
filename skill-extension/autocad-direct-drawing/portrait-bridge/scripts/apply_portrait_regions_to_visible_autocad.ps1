param(
  [string]$JsonPath = "$env:USERPROFILE\Desktop\portrait_regions_clean.json",
  [string]$OutputScr = "$env:USERPROFILE\Desktop\portrait_regions_bridge.scr",
  [string]$PythonExe = $env:COMFYUI_PYTHON,
  [string]$SendKeysScript = (Join-Path $PSScriptRoot '..\..\scripts\send_visible_autocad_keys.ps1')
)

$ErrorActionPreference = 'Stop'
$builder = Join-Path $PSScriptRoot 'build_portrait_region_bridge.py'

if(-not $PythonExe){
  throw "Set COMFYUI_PYTHON to your local ComfyUI Python runtime."
}
if(-not (Test-Path -LiteralPath $PythonExe)){
  throw "ComfyUI Python runtime not found: $PythonExe"
}
if(-not (Test-Path -LiteralPath $SendKeysScript)){
  throw "AutoCAD SendKeys script not found: $SendKeysScript"
}

& $PythonExe $builder $JsonPath $OutputScr
& $SendKeysScript -CadCommand ('_.SCRIPT ' + $OutputScr)
Write-Output "Portrait region SCR sent to visible AutoCAD: $OutputScr"
