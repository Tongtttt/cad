param(
  [string]$OutputScriptPath = "$env:USERPROFILE\Desktop\codex_autocad_attach.scr"
)

$lines = @(
  '; Codex AutoCAD attach helper',
  '; Open the target DWG in the visible AutoCAD desktop window first.',
  '; Then run this script inside AutoCAD with SCRIPT if direct automation is unavailable.',
  '._ZOOM _E'
)

Set-Content -LiteralPath $OutputScriptPath -Value $lines -Encoding ASCII
Write-Output "Generated: $OutputScriptPath"
