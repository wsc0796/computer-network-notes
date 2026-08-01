# Codex 分层验收协议（GPT-5.6 独立语义审查）

> 用途：用 Codex CLI（`gpt-5.6-sol`）对分层学习包做独立的语义审核，发现整理资料中的事实、计算、覆盖和结构问题。
>
> 前提：先显式选择认证通道。Plus 订阅额度、卷几网关 API 和 OpenAI Platform API 是三套独立计费/认证路径；不要让自动化继承不确定的桌面登录状态。

## 证据边界

- `D:\计算机网络试卷\converted_utf8\` 的 20 份文件是本地带参考答案试卷。它们只可用于核对资料里明确写出“试卷 X 第 Y 题”的同卷同题号引用，不能称为 408 统考官方答案。
- 2009-2025 的 408 真题专章来自 PDF OCR。当前没有“真题条目 -> 一手答案键”的映射，因此未建立映射的真题只能审查题干转录、计算和表述，不能自动判为答案正确。
- 不依赖模型的现有基线见 [本地试卷引用机械验收报告](../../analysis/本地试卷引用机械验收报告.md)。它已经检查 20 份本地试卷完整性、10 条明确引用和 6 条人工复核结论的文字/公式回归。

## Codex 认证通道

本机的 PowerShell 交互别名和非交互启动器不是同一件事。后台 Agent 不应调用裸 `codex`，因为它会读取启动进程继承的 `CODEX_HOME`，可能落到桌面 Plus 登录。

| `-AuthBackend` | 实际隔离启动器 | 用途 |
|---|---|---|
| `juanji-api`（默认） | `C:\Users\50469\codex-launchers\codex-api.cmd` / `codex-juanji.ps1` | 对应交互终端的 `codex-api`，使用卷几网关 API。 |
| `openai-api` | `C:\Users\50469\codex-launchers\codex-api.ps1` | 使用独立保存的 OpenAI Platform API 凭据。 |
| `plus` | `codex-plus.ps1` | 仅在明确要消耗 ChatGPT Plus 额度时使用。 |
| `direct` | PATH 中的 `codex.cmd` | 仅用于故障排查；不用于后台自动化。 |

启动器各自设置 `CODEX_HOME` 和强制登录方式。不要把 API Key 写进命令、提示词、报告或环境变量回显中。

## 验收对象

```text
07_考研预备_分层学习包/
├── 01_应用层/      01 04 05 06 07
├── 02_运输层/      01 04 05 06 07
├── 03_网络层/      01 04 05 06 07 08_子网专题 09_RIP 10_路由表
├── 04_数据链路层/  01 04 05 06 07
├── 05_物理层/      01 04 05 06 07
├── 06_网络安全/    01 04 05 06 07
└── 00_总览/        考纲矩阵、外部资源清单和本协议
```

## 验收标准

1. 知识点正确性：事实错误、公式/计算错误、互相矛盾或会误导学习的表述。
2. 408 考纲覆盖：核心考点遗漏、重点失衡和不合理的组织顺序。
3. 引用与答案边界：对明确的同卷同题号引用，核对本地带答案试卷；无映射的 OCR 真题必须标为“未建立映射”。
4. 结构完整性：零基础版、题型训练、错题本、默写和速查之间的缺口或冲突。

Codex 的结论是独立审核意见，不会把 OCR 或本地配套试卷升级为一手官方答案证据。

## 执行步骤

先在资料根目录运行不调用模型的基线检查：

```powershell
python analysis\verify_official_answer_citations.py
```

先确认卷几 API 通道的登录状态。这个命令只显示认证类型，不会调用模型：

```powershell
& "$env:USERPROFILE\codex-launchers\codex-api.cmd" login status
```

然后生成六层输入并确认文件清单。默认后端就是交互终端 `codex-api` 对应的卷几 API，而不是 Plus：

```powershell
.\scripts\run_codex_layer_audit.ps1 -AuthBackend juanji-api -DryRun -ThrottleLimit 2
```

确认后运行实际审核。默认每层最多 30 分钟，同时运行 2 层；不要一开始就启动 6 个进程。已测物理层单层约 310 秒、约 2.7 万 tokens，因此先以 2 路观察网关稳定性和成本，再决定是否升到 3。`SUMMARY.md` 会记录认证后端、实际启动器和每层耗时。

```powershell
.\scripts\run_codex_layer_audit.ps1 -AuthBackend juanji-api -ThrottleLimit 2 -TimeoutMinutes 30
```

若明确需要官方 OpenAI Platform API，使用同一脚本的独立后端：

```powershell
.\scripts\run_codex_layer_audit.ps1 -AuthBackend openai-api -ThrottleLimit 2 -TimeoutMinutes 30
```

单层复核示例：

```powershell
.\scripts\run_codex_layer_audit.ps1 -AuthBackend juanji-api -Layer '05_物理层' -ThrottleLimit 1
```

## 运行产物与进度

每次执行会创建 `analysis/codex-audit/YYYYMMDD-HHmmssfff/`：

```text
<运行目录>/
├── <层>/input.md      # 送入 Codex 的固定输入
├── <层>/stdout.md     # 最终审核结论
├── <层>/stderr.log    # CLI 进度、错误、限额或网络信息
└── SUMMARY.md         # 状态、退出码、每层耗时及日志路径
```

终端会打印每层 `Starting`、每 15 秒的耗时/日志字节数和 `Finished` 状态。执行中优先查看某层的 `stderr.log`；`stdout.md` 可能在模型生成最终答案前保持为空。不要依赖单个后台任务界面判断是否仍在工作。

- 任一层失败或超时，脚本返回退出码 `1`，并保留所有输入和日志用于定位。
- 失败原因是额度、认证或网络时，先读同层 `stderr.log`；Plus 的 `usage limit` 不代表 API 余额也不可用，反之亦然。
- 完成后应人工汇总各层 `stdout.md`，将“严重”问题与机械报告中的已验证项分开记录。

## 使用频率

- 大规模更新资料后：先跑机械基线，再做全层 Codex 审核。
- 单层小更新：只运行对应层。
- 考研复习开始前：重跑机械基线和全层审核，并保留当次 `SUMMARY.md`。
