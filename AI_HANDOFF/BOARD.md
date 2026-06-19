# AI Handoff Board

## Active Task

- Task ID: TASK-20260527-001
- Status: IMPLEMENTED
- Owner: CODEX_TAKEOVER
- Next action: Codex review complete; user can stop Claude Code if it is still running.
- Task file: AI_HANDOFF/tasks/TASK-20260527-001-整理 TCP 拥塞控制考前大题小节.md
- Latest report: AI_HANDOFF/reports/REPORT-20260527-001.md
- Latest review: Codex took over because Claude Code had no report/state update after waiting; Markdown validation completed.

## Queue

| Task ID | Status | Owner | File | Notes |
| --- | --- | --- | --- | --- |
| TASK-20260527-001 | IMPLEMENTED | CODEX_TAKEOVER | AI_HANDOFF/tasks/TASK-20260527-001-整理 TCP 拥塞控制考前大题小节.md | 整理 TCP 拥塞控制考前大题小节 |

## Blocked Questions

- none

## Protocol

Statuses:

- DRAFT
- READY_FOR_DS
- IN_PROGRESS
- IMPLEMENTED
- REVIEW_REQUESTED
- CHANGES_REQUESTED
- ACCEPTED
- NEEDS_CLARIFICATION

Rules:

- Codex/GPT writes tasks and reviews.
- Claude Code + DeepSeek implements active tasks and writes reports.
- Do not run two implementation tasks at the same time.
- If execution requires touching forbidden scope, stop and write NEEDS_CLARIFICATION.
- Keep durable decisions in AI_HANDOFF/decisions/DECISIONS.md.
- Claude Code must use narrow context only: read BOARD.md, the active task file, and the specific target files listed in the task. Do not scan the whole vault unless the task explicitly asks for it.
- If Claude Code runs longer than 3 minutes without editing a file, writing a report, or updating BOARD.md, stop it and hand the task back to Codex.
- For Markdown exam-note tasks, prefer Codex direct implementation when the task affects 1-2 files; use Claude Code only for isolated mechanical edits.
- Use FAST mode for Markdown note tasks and tiny mechanical edits. FAST reports must be 5 lines or fewer.
- Use FULL mode only for multi-file code work, architecture changes, data/interface changes, or tasks with real test commands.
