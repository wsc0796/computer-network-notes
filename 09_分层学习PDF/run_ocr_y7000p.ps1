param(
    [Parameter(Mandatory = $true)]
    [string]$PdfName,

    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$PdfDir = $PSScriptRoot
$RepoRoot = Resolve-Path (Join-Path $PdfDir "..")
$RootRunner = Join-Path $RepoRoot "scripts\run_ocr_y7000p.ps1"

if (-not (Test-Path $RootRunner)) {
    throw "Cannot find root OCR runner: $RootRunner. Run git pull in the repository root first."
}

& $RootRunner -PdfName $PdfName -PythonExe $PythonExe
exit $LASTEXITCODE
