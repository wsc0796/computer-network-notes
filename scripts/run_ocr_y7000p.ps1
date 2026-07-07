param(
    [Parameter(Mandatory = $true)]
    [string]$PdfName,

    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
$PdfPath = Join-Path $RepoRoot "09_分层学习PDF\raw\$PdfName"
$PdfStem = [System.IO.Path]::GetFileNameWithoutExtension($PdfName)
$OutputDir = Join-Path $RepoRoot "09_分层学习PDF\extracted\${PdfStem}_ocr"
$PipelineScript = Join-Path $RepoRoot "scripts\pdf_ocr_pipeline.py"
$QualityReport = Join-Path $OutputDir "quality_report.md"

if (-not (Test-Path $PipelineScript)) {
    throw "Cannot find OCR pipeline script: $PipelineScript"
}

if (-not (Test-Path $PdfPath)) {
    throw "Cannot find input PDF: $PdfPath"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host "Input PDF: $PdfPath"
Write-Host "Output directory: $OutputDir"
Write-Host "Running OCR pipeline on Y7000P..."

& $PythonExe $PipelineScript $PdfPath -o $OutputDir
$ExitCode = $LASTEXITCODE

$StatusText = if ($ExitCode -eq 0) { "completed" } else { "failed" }
$Now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

@"
# OCR Quality Report

- 执行设备：Y7000P
- PDF 文件：$PdfName
- 输入路径：09_分层学习PDF/raw/$PdfName
- 输出目录：09_分层学习PDF/extracted/${PdfStem}_ocr
- 执行时间：$Now
- 管线状态：$StatusText

## 1. 文件完整性检查

- [ ] 存在 merged.md
- [ ] 存在 run_log.txt
- [ ] page_text/page_001.md 等分页文件数量与 PDF 页数一致
- [ ] run_log.txt 末尾没有 ERROR

## 2. OCR 质量抽查

- [ ] 抽查首页：标题、段落、图表附近文字基本可读
- [ ] 抽查中间页：无大段空白、乱码、重复切块文本
- [ ] 抽查末页：页尾内容没有明显丢失
- [ ] 公式、表格、协议字段等难点已标注为需人工复核

## 3. 人工修订记录

| 页码 | 问题 | 处理方式 |
| --- | --- | --- |
| page_001 | 待检查 | 待填写 |

## 4. 审查结论

- [ ] 通过，可进入提炼阶段
- [ ] 暂不通过，需要重新 OCR 或人工补录

结论说明：

"@ | Set-Content -Encoding UTF8 $QualityReport

Write-Host "Quality report template written: $QualityReport"

if ($ExitCode -ne 0) {
    throw "OCR pipeline failed. Check run_log.txt in: $OutputDir"
}

Write-Host "OCR finished successfully."
