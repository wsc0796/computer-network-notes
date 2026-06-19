# Skill 候选工作流梳理

扫描对象：

`C:\Users\50469\Desktop\Shirakoko_Notes\计算机网络（自顶向下方法）课程笔记_输出`

## 证据摘要

- 项目包含 90 个文件。
- 主要内容是 PDF/OCR 转换出来的课程资料：Markdown、PDF、JSON 布局文件和图片。
- Markdown 文件 3 个，图片 75 个，PDF 4 个，JSON 8 个。
- 原始主笔记位于 `auto/计算机网络（自顶向下方法）课程笔记.md`，约 2228 行，包含 233 个标题、66 张图片、6 个 HTML 表格。
- 当前对话中反复出现的需求是：回答课程概念、说明考察重要性、把大段课程笔记整理成分重点的复习材料。
- 已存在两份人工整理结果：`TCP-IP分层模型及基础协议-梳理.md` 和 `计算机网络全课程重点梳理.md`，说明“从原始课程笔记提炼复习稿”是可复用工作流。

## 候选 1：course-note-distiller

Trigger: Use when Codex needs to scan lecture/course notes, PDF/OCR-converted Markdown, Obsidian note folders, or screenshots and turn them into prioritized study guides, topic summaries, answer templates, and "必会/重点/了解" review plans.

Evidence:

- 当前项目有典型的 OCR/PDF 转换结构：`auto/` 原始笔记、图片、PDF、JSON 布局文件。
- 原始笔记标题很多、图片多、表格混杂，不适合直接复习。
- 用户连续要求“回答问题并说明考察重要性”“梳理 TCP/IP”“梳理计算机网络全部内容并划分重点”。
- 已生成的两份整理笔记采用稳定格式：知识地图、必会/重点/了解、常见考法、答题模板。

Workflow:

1. 扫描课程项目，识别原始笔记、图片、PDF、已有整理稿。
2. 抽取章节结构、表格、图片、关键词和已有重点标签。
3. 按课程模块建立知识地图。
4. 将内容划分为 `必会`、`重点`、`了解`。
5. 生成 Obsidian 友好的复习笔记或概念答题稿。
6. 验证输出文件存在、标题结构清晰、原始笔记未被覆盖。

Resources:

- `scripts/scan_course_notes.py`：扫描课程笔记目录，输出 Markdown、标题、图片、表格、重点关键词等 JSON 摘要。
- `references/study-guide-patterns.md`：定义全课程梳理、专题梳理、截图问答、重点划分和验证模板。

Validation:

- 在本项目上运行扫描脚本，成功识别 3 个 Markdown、75 张图片、4 个 PDF、8 个 JSON。
- `quick_validate.py` 校验通过。
- `py_compile` 脚本语法检查通过。

Scoring:

| 维度 | 分数 |
|---|---:|
| Frequency | 3 |
| Friction | 3 |
| Repeatability | 3 |
| Resource fit | 3 |
| Validation | 3 |
| Total | 15 |

Recommendation: Create. 这是最高价值候选，已经实现为 `C:\Users\50469\.codex\skills\course-note-distiller`。

## 候选 2：ocr-markdown-cleaner

Trigger: Use when Codex needs to clean PDF/OCR-converted Markdown by normalizing headings, replacing HTML tables with Markdown tables, fixing image links, and reducing OCR artifacts.

Evidence:

- 原始笔记包含 HTML 表格、图片链接、PDF/OCR 产生的异常字符。
- 自动导出的 `auto/` 内容适合保留为源，但阅读体验较重。

Workflow:

1. 备份或保留原始 Markdown。
2. 检测 HTML 表格、图片链接、异常空格、标题层级。
3. 生成清理版 Markdown。
4. 检查图片链接和表格渲染。

Resources:

- scripts/: HTML 表格到 Markdown 表格转换、图片链接检查。
- references/: OCR 清理规则。

Validation: 统计 HTML 表格数量、坏链数量、标题层级变化。

Scoring:

| 维度 | 分数 |
|---|---:|
| Frequency | 2 |
| Friction | 3 |
| Repeatability | 2 |
| Resource fit | 2 |
| Validation | 2 |
| Total | 11 |

Recommendation: Defer. 有价值，但当前用户的主要痛点是“复习重点提炼”，不是清理原始 OCR。

## 候选 3：concept-answer-coach

Trigger: Use when Codex needs to answer a course concept question or screenshot and explain what the question is testing.

Evidence:

- 用户多次给出截图或短主题列表，要求“回答这个内容，并说明这些问题在考察的重要性”。
- 输出模式稳定：直接解释、表格对比、机制原因、考察重要性、常见追问。

Workflow:

1. 识别截图/题目中的关键词。
2. 给出直接答案。
3. 补充机制解释和类比。
4. 单独说明“考察重要性”。
5. 给出可背诵版答题模板。

Resources:

- references/: 问答结构模板和常见追问模式。

Validation: 回答是否包含定义、原因、机制、重要性和答题模板。

Scoring:

| 维度 | 分数 |
|---|---:|
| Frequency | 3 |
| Friction | 2 |
| Repeatability | 3 |
| Resource fit | 2 |
| Validation | 2 |
| Total | 12 |

Recommendation: Defer as standalone. 这个模式已经并入 `course-note-distiller` 的截图/概念问答流程。

## 候选 4：obsidian-course-indexer

Trigger: Use when Codex needs to create Obsidian-ready indexes, backlinks, course maps, or review navigation pages for a course note vault.

Evidence:

- 项目包含 `.obsidian`。
- 用户希望在笔记项目中持续整理课程内容。

Workflow:

1. 扫描笔记文件。
2. 生成课程主页、章节索引、专题索引。
3. 添加 Obsidian 链接和复习路径。

Resources:

- scripts/: Markdown 文件索引器。
- references/: Obsidian 链接和命名规范。

Validation: 检查链接目标存在、索引覆盖所有笔记。

Scoring:

| 维度 | 分数 |
|---|---:|
| Frequency | 1 |
| Friction | 2 |
| Repeatability | 2 |
| Resource fit | 2 |
| Validation | 2 |
| Total | 9 |

Recommendation: Defer. 目前证据不足，等笔记数量更多时再做更划算。
