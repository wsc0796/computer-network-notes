# Project Decisions

Use this file for durable decisions that both agents must remember.

## Template

```markdown
## YYYY-MM-DD - Decision title

- Decision:
- Reason:
- Alternatives considered:
- Affected files/modules:
- Revisit when:
```

## 2026-05-27 - Claude Code timebox for notes work

- Decision: Claude Code gets a 3-minute no-output timebox for Markdown note tasks. If it has not edited a file, written a report, or updated `AI_HANDOFF/BOARD.md` within that time, stop it and return the task to Codex.
- Reason: Claude Code spent over 15 minutes in `Tempering` with high token use and no visible handoff output, which blocks the student's study flow.
- Alternatives considered: waiting indefinitely; asking Claude Code to read the whole vault; using Claude Code for every task by default.
- Affected files/modules: `AI_HANDOFF/BOARD.md`, `AI_HANDOFF/tasks/`, `AI_HANDOFF/reports/`, and Markdown notes under `01_考前冲刺复习/`.
- Revisit when: Claude Code becomes consistently faster on small bounded tasks, or the project changes from note cleanup to larger code implementation.

## 2026-05-27 - FAST vs FULL handoff modes

- Decision: Split handoff into FAST and FULL modes. FAST is for Markdown notes and tiny mechanical edits; FULL is for multi-file code or architecture work.
- Reason: The original handoff required reading, editing, report writing, and board updates for every task, which made small note edits slower than direct implementation.
- Alternatives considered: removing handoff entirely; keeping only the heavy protocol; relying on Claude Code to self-limit without templates.
- Affected files/modules: `AI_HANDOFF/AGENT_ROLES.md`, `AI_HANDOFF/tasks/FAST_TASK-template.md`, `AI_HANDOFF/tasks/TASK-template.md`, `AI_HANDOFF/reports/REPORT-fast-template.md`, `AI_HANDOFF/reports/REPORT-template.md`.
- Revisit when: note tasks regularly need broad source synthesis instead of small edits.
