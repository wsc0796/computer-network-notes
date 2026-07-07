# PDF OCR Workflow Final Report

## 新增脚本

- `scripts/pdf_ocr_pipeline.py`
  - 输入 PDF 路径和输出目录。
  - 使用 PyMuPDF 将 PDF 页面渲染为图片。
  - 当页面图片超过阈值时，按行列自动切块。
  - 使用 PaddleOCR 按页码和切块顺序识别文字。
  - 输出 `page_text/page_001.md`、`merged.md` 和 `run_log.txt`。

- `scripts/run_ocr_y7000p.ps1`
  - 接收 `-PdfName` 参数。
  - 固定输入路径为 `09_分层学习PDF/raw/<PdfName>`。
  - 固定输出路径为 `09_分层学习PDF/extracted/<PdfName去扩展名>_ocr`。
  - 调用 `pdf_ocr_pipeline.py`。
  - 生成 `quality_report.md` 审查模板。

## Y7000P 怎么运行

1. 将待处理 PDF 放入：

```text
09_分层学习PDF/raw/
```

2. 在 `computer-network-notes` 仓库根目录执行：

```powershell
.\scripts\run_ocr_y7000p.ps1 -PdfName "4-传输层.pdf"
```

3. 如果需要指定虚拟环境：

```powershell
.\scripts\run_ocr_y7000p.ps1 -PdfName "4-传输层.pdf" -PythonExe "D:\path\to\venv\Scripts\python.exe"
```

4. 执行结束后检查：

```text
09_分层学习PDF/extracted/4-传输层_ocr/
```

## 轻薄本怎么审查

轻薄本不运行 OCR、CUDA 或 MinerU，只做结果审查和提炼：

1. 查看 `run_log.txt`，确认没有 ERROR。
2. 检查 `page_text/` 的分页数量是否与 PDF 页数一致。
3. 抽查 `merged.md` 的首页、中间页、末页。
4. 在 `quality_report.md` 中记录乱码、漏识别、表格和公式问题。
5. 只有 `quality_report.md` 审查通过后，才从 `extracted/` 提炼到正式学习笔记。

## 重要边界

本次流程不直接修改 `07_考研预备_分层学习包`。OCR 原始结果必须先进入：

```text
09_分层学习PDF/extracted/
```

通过人工质量审查后，再决定哪些内容进入正式分层学习包。

## 下一步：处理网络层 PDF

网络层 PDF 复用同一流程：

1. 将网络层 PDF 放入 `09_分层学习PDF/raw/`。
2. 新建对应任务文件，例如 `09_分层学习PDF/tasks/task_02_network_ocr.md`。
3. 在 Y7000P 执行：

```powershell
.\scripts\run_ocr_y7000p.ps1 -PdfName "网络层PDF文件名.pdf"
```

4. 审查 `extracted/<网络层PDF文件名>_ocr/quality_report.md`。
5. 审查通过后，再提炼网络层分层学习笔记。
