# Import ehealth-full-model.xml (Open Exchange) vao Archi, luu .archimate va xuat anh PNG moi view bang chinh Archi.
# Can Archi 5.x (archimatetool.com). Chay: powershell -File export_archi.ps1 [-Archi "duong\dan\Archi.exe"]
param([string]$Archi = "$env:LOCALAPPDATA\Programs\Archi\Archi.exe")
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$tmp = Join-Path $env:TEMP "archi-html-report"
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
Remove-Item "$here\ehealth-full-model.archimate" -ErrorAction SilentlyContinue
& $Archi -application com.archimatetool.commandline.app -consoleLog -nosplash `
  --xmlexchange.import "$here\ehealth-full-model.xml" `
  --saveModel "$here\ehealth-full-model.archimate" `
  --html.createReport $tmp
Copy-Item "$tmp\id-ehealth-full\images\V-*.png" "$here\..\exports\" -Force
Write-Host "Da luu ehealth-full-model.archimate va anh view vao 02-models/exports"
