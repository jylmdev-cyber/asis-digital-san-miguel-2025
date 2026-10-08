param([string]$SourceDirectory = (Split-Path -Parent $PSScriptRoot | Split-Path -Parent))
$taskSource = (Resolve-Path -LiteralPath $SourceDirectory).Path
$taskWordPath = Join-Path $taskSource 'ASIS_RED_SAN_MIGUEL_2026_FINAL.doc'
$taskAuditPath = Join-Path $taskSource 'audit'
New-Item -ItemType Directory -Path $taskAuditPath -Force | Out-Null
$taskExport = Join-Path $taskAuditPath 'word-export-unicode.txt'
$taskUtf8 = Join-Path $taskAuditPath 'word-2026-utf8.txt'
$taskWordApp = $null
$taskWordDoc = $null
try {
    $taskWordApp = New-Object -ComObject Word.Application
    $taskWordApp.Visible = $false
    $taskWordApp.DisplayAlerts = 0
    $taskWordDoc = $taskWordApp.Documents.Open($taskWordPath, $false, $true, $false)
    $taskWordDoc.SaveAs2($taskExport, 7)
    $taskText = [System.IO.File]::ReadAllText($taskExport, [System.Text.Encoding]::Unicode)
    [System.IO.File]::WriteAllText($taskUtf8, $taskText, [System.Text.UTF8Encoding]::new($false))
    Write-Output 'Word exported read-only to private local audit; original preserved.'
} finally {
    if ($taskWordDoc) { $taskWordDoc.Close(0) }
    if ($taskWordApp) { $taskWordApp.Quit() }
}
