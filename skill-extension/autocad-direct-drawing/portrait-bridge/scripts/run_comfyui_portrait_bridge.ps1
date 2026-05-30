param(
  [Parameter(Mandatory=$true)][string]$ImagePath,
  [string]$OutputJson = "$env:USERPROFILE\Desktop\portrait_regions.json",
  [string]$PythonExe = $env:COMFYUI_PYTHON,
  [string]$ExtractorScript = (Join-Path $PSScriptRoot 'portrait_region_extractor.py')
)

if(-not $PythonExe){
  throw "Set COMFYUI_PYTHON to your local ComfyUI Python runtime."
}
if(-not (Test-Path -LiteralPath $PythonExe)){
  throw "ComfyUI Python runtime not found: $PythonExe"
}
if(-not (Test-Path -LiteralPath $ExtractorScript)){
  throw "Portrait extractor script not found: $ExtractorScript"
}
if(-not (Test-Path -LiteralPath $ImagePath)){
  throw "Input image not found: $ImagePath"
}

& $PythonExe $ExtractorScript $ImagePath $OutputJson
