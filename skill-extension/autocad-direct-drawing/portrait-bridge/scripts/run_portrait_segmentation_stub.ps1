param(
  [Parameter(Mandatory=$true)][string]$ImagePath,
  [string]$OutputJson = "$env:USERPROFILE\Desktop\portrait_regions.json"
)

$payload = @{
  status = 'stub'
  image = $ImagePath
  message = 'Portrait segmentation runtime not connected yet. This file reserves the output contract for future integration.'
  schema = 'portrait_regions.schema.json'
}
$payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputJson -Encoding UTF8
Write-Output "Stub output written: $OutputJson"
