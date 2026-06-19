# 提取计划

## 1. 输入文件

`downloads/` 中共有 7 个 PDF 文件，均为百度网盘 PPTX 在线预览接口生成的 PDF 版本。

| 文件 | 处理方式 |
|---|---|
| 计算题专项突破.pptx.preview.pdf | 用 `pdfplumber` 提取文本 |
| 第1章 计算机网络体系结构.pptx.preview.pdf | 用 `pdfplumber` 提取文本 |
| 第2章 物理层.pptx.preview.pdf | 用 `pdfplumber` 提取文本 |
| 第3章 数据链路层.pptx.preview.pdf | 用 `pdfplumber` 提取文本 |
| 第4章 网络层.pptx.preview.pdf | 用 `pdfplumber` 提取文本 |
| 第5章 传输层.pptx.preview.pdf | 用 `pdfplumber` 提取文本 |
| 第6章 应用层.pptx.preview.pdf | 用 `pdfplumber` 提取文本 |

## 2. 注意事项

- 这些不是原始 PPTX，而是 PPTX 的在线预览 PDF。
- 若某些公式、图形、箭头或表格没有文字层，可能提取不完整。
- 原始文件保留在 `downloads/`，提取结果写入 `extracted/`。

## 3. 后续输出

提取完成后生成：

```text
notes/00-资料索引.md
notes/01-物理层.md
notes/02-数据链路层.md
notes/03-网络层.md
notes/04-运输层.md
notes/05-应用层.md
notes/06-选择判断题高频考点.md
notes/07-简答题模板.md
notes/08-大题题型与解题步骤.md
notes/09-易错题与冲突答案.md
notes/10-考前一页速记.md
```

