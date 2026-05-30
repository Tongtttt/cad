param(
  [string]$JsonPath = "$env:USERPROFILE\Desktop\portrait_regions.json",
  [string]$OutputScr = "$env:USERPROFILE\Desktop\portrait_regions_bridge.scr",
  [double]$Scale = 1.0
)

$ErrorActionPreference = 'Stop'
if(-not (Test-Path -LiteralPath $JsonPath)){ throw "portrait_regions.json not found: $JsonPath" }
if((Split-Path -Parent $OutputScr) -and -not (Test-Path -LiteralPath (Split-Path -Parent $OutputScr))){
  New-Item -ItemType Directory -Path (Split-Path -Parent $OutputScr) -Force | Out-Null
}
$data = Get-Content -LiteralPath $JsonPath -Raw | ConvertFrom-Json
if(-not $data.regions){ throw "No regions found in portrait JSON." }
$layerMap = @{
  'outer_silhouette' = 'P_OUTLINE'
  'hair_main' = 'P_HAIR_MAIN'
  'hair_detail' = 'P_HAIR_DETAIL'
  'face_features' = 'P_FACE'
  'hand' = 'P_HAND'
  'cloth' = 'P_CLOTH'
  'flower_main' = 'P_FLOWER_MAIN'
  'flower_detail' = 'P_FLOWER_DETAIL'
  'ornament' = 'P_ORNAMENT'
  'misc' = 'P_MISC'
}
$sb = New-Object System.Text.StringBuilder
function Add-Line([string]$line){ [void]$sb.AppendLine($line) }
Add-Line '_.UNDO _BEGIN'
Add-Line '_.CMDECHO 0'
foreach($name in $layerMap.Values){
  Add-Line '_.-LAYER'
  Add-Line '_M'
  Add-Line $name
  Add-Line '_C'
  Add-Line '8'
  Add-Line $name
  Add-Line ''
}
foreach($region in $data.regions){
  $layer = $layerMap[$region.id]
  if(-not $layer){ continue }
  foreach($poly in $region.polygons){
    if(-not $poly -or $poly.Count -lt 4){ continue }
    Add-Line '_.-LAYER'
    Add-Line '_S'
    Add-Line $layer
    Add-Line ''
    Add-Line '_.PLINE'
    foreach($pt in $poly){
      $x = [math]::Round(([double]$pt[0] * $Scale), 3)
      $y = [math]::Round((-1.0 * [double]$pt[1] * $Scale), 3)
      Add-Line ("{0},{1}" -f $x, $y)
    }
    $first = $poly[0]
    $fx = [math]::Round(([double]$first[0] * $Scale), 3)
    $fy = [math]::Round((-1.0 * [double]$first[1] * $Scale), 3)
    Add-Line ("{0},{1}" -f $fx, $fy)
    Add-Line ''
  }
}
Add-Line '_.-LAYER'
Add-Line '_S'
Add-Line '0'
Add-Line ''
Add-Line '_.UNDO _END'
[System.IO.File]::WriteAllText($OutputScr, $sb.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Output "Bridge script written: $OutputScr"
