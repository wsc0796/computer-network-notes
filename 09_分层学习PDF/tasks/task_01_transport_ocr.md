# Task 01: Transport Layer PDF OCR

## 目标

在 Y7000P 上完成《4-传输层.pdf》的 OCR 提取。轻薄本不承担重型 OCR、CUDA、MinerU 任务，只负责脚本生成、仓库管理和结果提炼。

## 执行设备

- Y7000P

## 处理文件

- 输入文件：`09_分层学习PDF/raw/4-传输层.pdf`
- 输出目录：`09_分层学习PDF/extracted/4-传输层_ocr`

## 执行命令

在 `computer-network-notes` 仓库根目录执行：

```powershell
.\scripts\run_ocr_y7000p.ps1 -PdfName "4-传输层.pdf"
```

如果当前已经在 `09_分层学习PDF` 目录，也可以执行：

```powershell
.\run_ocr_y7000p.ps1 -PdfName "4-传输层.pdf"
```

如 Y7000P 上需要指定虚拟环境 Python：

```powershell
.\scripts\run_ocr_y7000p.ps1 -PdfName "4-传输层.pdf" -PythonExe "D:\path\to\venv\Scripts\python.exe"
```

执行前确认 PDF 已在 `raw/` 子目录：

```powershell
Get-ChildItem ".\09_分层学习PDF\raw"
```

## 输出要求

OCR 结果必须先进入 `09_分层学习PDF/extracted/4-传输层_ocr/`，不得直接写入或覆盖 `07_考研预备_分层学习包`。

预期产物：

- `page_text/page_001.md`
- `page_text/page_002.md`
- `merged.md`
- `run_log.txt`
- `quality_report.md`

## 质量检查标准

- `run_log.txt` 末尾显示 OCR pipeline completed successfully，且没有 ERROR。
- `page_text/` 中的分页文件数量与 PDF 页数一致。
- `merged.md` 按页码顺序合并，页与页之间有分隔线。
- 抽查首页、中间页、末页，确认没有整页空白、明显乱码、大面积重复文字。
- 对公式、表格、协议字段、滑动窗口图、拥塞控制图等 OCR 易错内容，在 `quality_report.md` 中记录需人工复核的位置。
- 只有 `quality_report.md` 标记为通过后，才允许进入人工提炼阶段。

## GitHub 提交要求

建议一次提交只包含 OCR 流程与任务模板，不提交原始 PDF 和大体积图片缓存。

提交前检查：

```powershell
git status --short
git diff -- scripts/pdf_ocr_pipeline.py scripts/run_ocr_y7000p.ps1
```

建议提交信息：

```text
Add Y7000P PDF OCR workflow
```
