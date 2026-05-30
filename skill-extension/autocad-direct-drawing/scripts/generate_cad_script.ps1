param(
  [Parameter(Mandatory=$true)][string]$CommandBody,
  [string]$OutputPath = "$env:USERPROFILE\Desktop\codex_cad_run.scr"
)

$lines = @(
  '; Codex generated AutoCAD script',
  $CommandBody,
  '._ZOOM _E'
)
Set-Content -LiteralPath $OutputPath -Value $lines -Encoding ASCII
Write-Output "Generated: $OutputPath"
