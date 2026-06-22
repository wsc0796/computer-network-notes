"""
Round 2 final verification script.

Checks:
- exam score totals and module totals
- exam question time total and declared answer/correction time
- question number uniqueness and exam-answer correspondence
- 6-hour plan blocks: total, no overlap, no gaps
- exact referenced file paths
- stage quiz files exist and prechecks do not point to formal exam answers
- key answer values for RTT/RTO, UDP parsing, route aggregation, and IP fragmentation
- VLSM required file existence when VLSM is in the plan
"""

import os
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

errors: list[str] = []
warnings: list[str] = []


def check(condition: bool, msg: str, level: str = "error") -> None:
    if condition:
        return
    if level == "error":
        errors.append(msg)
    else:
        warnings.append(msg)


def read_text(rel: str) -> str:
    path = REPO / rel
    check(path.exists(), f"File missing: {rel}")
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def time_to_minutes(value: str) -> int:
    h, m = value.split(":")
    return int(h) * 60 + int(m)


def section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)


exam_rel = "02_刷题模拟卷/运输层网络层_6小时验收卷.md"
answer_rel = "02_刷题模拟卷/运输层网络层_6小时验收卷_答案.md"
stage_rel = "02_刷题模拟卷/运输层网络层_阶段抽查题.md"
stage_answer_rel = "02_刷题模拟卷/运输层网络层_阶段抽查题_答案.md"
plan_rel = "01_考前冲刺复习/运输层与网络层_6小时完整复习计划.md"
checklist_rel = "01_考前冲刺复习/运输层与网络层_6小时执行清单.md"

exam_text = read_text(exam_rel)
answer_text = read_text(answer_rel)
stage_text = read_text(stage_rel)
stage_answer_text = read_text(stage_answer_rel)
plan_text = read_text(plan_rel)
checklist_text = read_text(checklist_rel)


# 1. Score verification
section("1. Exam score verification")

question_pattern = re.compile(
    r"^###\s+(\d+)\.\s+(.+?)（.+?共(\d+)分）【预计(\d+)分钟】",
    re.MULTILINE,
)
questions = [
    {
        "num": int(m.group(1)),
        "title": m.group(2),
        "score": int(m.group(3)),
        "time": int(m.group(4)),
    }
    for m in question_pattern.finditer(exam_text)
]

for q in questions:
    print(f"  Q{q['num']}: {q['score']}分, {q['time']}min, {q['title']}")

question_numbers = [q["num"] for q in questions]
check(len(question_numbers) == 15, f"Expected 15 questions, got {len(question_numbers)}")
check(
    len(question_numbers) == len(set(question_numbers)),
    f"Duplicate exam question numbers: {question_numbers}",
)
check(question_numbers == list(range(1, 16)), f"Question numbers must be 1-15, got {question_numbers}")

transport_total = sum(q["score"] for q in questions if 1 <= q["num"] <= 8)
network_total = sum(q["score"] for q in questions if 9 <= q["num"] <= 15)
score_total = transport_total + network_total

print(f"  Transport score: {transport_total}")
print(f"  Network score: {network_total}")
print(f"  Total score: {score_total}")

check(transport_total == 50, f"Transport total={transport_total}, expected=50")
check(network_total == 50, f"Network total={network_total}, expected=50")
check(score_total == 100, f"Total={score_total}, expected=100")


# 2. Exam timing
section("2. Exam timing verification")

declared_answer_time = re.search(r"答题时间：(\d+)分钟", exam_text)
declared_correction_time = re.search(r"订正时间：(\d+)分钟", exam_text)
answer_time = int(declared_answer_time.group(1)) if declared_answer_time else -1
correction_time = int(declared_correction_time.group(1)) if declared_correction_time else -1
question_time_total = sum(q["time"] for q in questions)

print(f"  Declared answer time: {answer_time}min")
print(f"  Declared correction time: {correction_time}min")
print(f"  Sum of question estimates: {question_time_total}min")

check(answer_time == 60, f"Answer time={answer_time}, expected=60")
check(correction_time >= 10, f"Correction time={correction_time}, expected >=10")
check(55 <= question_time_total <= 60, f"Question estimate total={question_time_total}, expected 55-60")


# 3. Answer correspondence
section("3. Question-answer correspondence")

answer_numbers = [int(m.group(1)) for m in re.finditer(r"^###\s+(\d+)\.\s+", answer_text, re.MULTILINE)]
print(f"  Exam questions: {question_numbers}")
print(f"  Answer questions: {answer_numbers}")

check(len(answer_numbers) == 15, f"Expected 15 answer sections, got {len(answer_numbers)}")
check(
    len(answer_numbers) == len(set(answer_numbers)),
    f"Duplicate answer question numbers: {answer_numbers}",
)
check(question_numbers == answer_numbers, f"Exam-answer mismatch: exam={question_numbers}, answer={answer_numbers}")


# 4. Plan time verification
section("4. 6-hour plan time verification")

block_pattern = re.compile(r"^##\s+(\d{2}:\d{2})[—-](\d{2}:\d{2})\s+.+?（(\d+)分钟）", re.MULTILINE)
blocks = []
for m in block_pattern.finditer(plan_text):
    start = time_to_minutes(m.group(1))
    end = time_to_minutes(m.group(2))
    declared = int(m.group(3))
    blocks.append((m.group(1), m.group(2), start, end, declared))
    actual = end - start
    print(f"  {m.group(1)}-{m.group(2)}: declared={declared}, actual={actual}")
    check(actual > 0, f"Non-positive block: {m.group(1)}-{m.group(2)}")
    check(actual == declared, f"Block duration mismatch {m.group(1)}-{m.group(2)}: declared={declared}, actual={actual}")

actual_total = sum(end - start for _, _, start, end, _ in blocks)
declared_total = sum(declared for *_, declared in blocks)
print(f"  Actual total: {actual_total}min")
print(f"  Declared total: {declared_total}min")

check(actual_total == 360, f"Plan actual total={actual_total}, expected=360")
check(declared_total == 360, f"Plan declared total={declared_total}, expected=360")

sorted_blocks = sorted(blocks, key=lambda x: x[2])
for prev, curr in zip(sorted_blocks, sorted_blocks[1:]):
    prev_end = prev[3]
    curr_start = curr[2]
    check(prev_end <= curr_start, f"Plan overlap: {prev[0]}-{prev[1]} and {curr[0]}-{curr[1]}")
    check(prev_end == curr_start, f"Plan gap: {prev[1]} to {curr[0]}")

check(sorted_blocks and sorted_blocks[0][2] == 0, "Plan must start at 00:00")
check(sorted_blocks and sorted_blocks[-1][3] == 360, "Plan must end at 06:00")

summary_expect = {
    "运输层复习": 125,
    "网络层复习": 140,
    "休息": 10,
    "自检缓冲": 10,
    "闭卷验收": 60,
    "订正复盘": 15,
}
for label, expected in summary_expect.items():
    m = re.search(rf"\|\s*{re.escape(label)}\s*\|\s*(\d+)\s*\|", plan_text)
    check(bool(m), f"Plan summary row missing: {label}")
    if m:
        value = int(m.group(1))
        print(f"  Table {label}: {value}min")
        check(value == expected, f"Plan summary {label}={value}, expected={expected}")


# 5. Exact path verification
section("5. Exact referenced path verification")

allowed_exts = (".md", ".jpg", ".jpeg", ".png", ".pdf")
texts_for_paths = [
    ("plan", plan_text),
    ("checklist", checklist_text),
    ("exam", exam_text),
    ("answer", answer_text),
    ("stage", stage_text),
    ("stage_answer", stage_answer_text),
]
referenced_paths: set[str] = set()

for source, text in texts_for_paths:
    for ref in re.findall(r"`([^`]+\.(?:md|jpg|jpeg|png|pdf))`", text, flags=re.IGNORECASE):
        referenced_paths.add(ref.replace("\\", "/"))
        print(f"  {source}: {ref}")

for ref in sorted(referenced_paths):
    check(ref.lower().endswith(allowed_exts), f"Unsupported referenced extension: {ref}")
    check((REPO / ref).exists(), f"Referenced path missing: {ref}")


# 6. Stage quiz and anti-leak checks
section("6. Stage quiz and anti-leak checks")

for label, text in [("stage", stage_text), ("stage_answer", stage_answer_text)]:
    check(bool(text.strip()), f"{label} file must not be empty")

check("阶段抽查题.md" in plan_text, "Plan prechecks must reference stage quiz")
check("阶段抽查题_答案.md" in plan_text, "Plan prechecks must reference stage quiz answer for post-check")
transport_precheck = re.search(r"01:52[—-]02:05.*?(?=^##\s+02:05)", plan_text, re.S | re.M)
network_precheck = re.search(r"04:25[—-]04:35.*?(?=^##\s+04:35)", plan_text, re.S | re.M)
for name, match in [("transport precheck", transport_precheck), ("network precheck", network_precheck)]:
    check(bool(match), f"Missing {name} block")
    if match:
        block = match.group(0)
        check("6小时验收卷_答案.md" not in block, f"{name} must not reference formal answer")
        check("6小时验收卷.md" not in block, f"{name} must not reference formal exam")

check("正式验收前不得打开" in plan_text or "正式验收前不得查看" in plan_text,
      "Plan must explicitly forbid opening formal answer before final exam")
check("正式验收前不打开" in checklist_text or "正式验收前不得" in checklist_text,
      "Checklist must explicitly forbid opening formal answer before final exam")

for token in ["数据报", "虚电路", "转发", "路由", "直接", "间接", "IP", "MAC", "DHCP", "特殊IP"]:
    check(token in stage_text, f"Stage quiz missing required non-big-question token: {token}")


# 7. Key answer value checks
section("7. Key answer value checks")

check("RTO = 75 + 4*23.5 = 169 ms" in answer_text or "RTO=169 ms" in answer_text,
      "RTT/RTO answer must contain RTO=169 ms")
check("23.5 ms" in answer_text, "RTTVAR answer must be 23.5 ms")
check("75 ms" in answer_text, "SRTT answer must be 75 ms")

frag_lengths = [1480, 1480, 1120]
frag_offsets = [0, 185, 370]
check(sum(frag_lengths) == 4080, "IP fragmentation data lengths must sum to 4080")
for offset in frag_offsets:
    check(offset == int(offset) and offset >= 0, f"Fragment offset invalid: {offset}")
for value in frag_lengths + frag_offsets:
    check(str(value) in answer_text, f"Fragment answer missing value: {value}")

for token in ["8080", "53", "44 字节", "36 字节"]:
    check(token in answer_text, f"UDP parsing answer missing token: {token}")

for token in ["192.168.40.0/22", "00101000", "00101011"]:
    check(token in answer_text, f"Route aggregation answer missing token: {token}")


# 8. VLSM required file
section("8. VLSM status check")

vlsm_file = REPO / "01_考前冲刺复习/网络层_VLSM完整例题.md"
if "VLSM" in plan_text:
    check(vlsm_file.exists(), "Plan contains VLSM but network VLSM example file is missing")
    if vlsm_file.exists():
        vlsm_text = vlsm_file.read_text(encoding="utf-8")
        for token in ["192.168.10.0/24", "100", "50", "20", "10", "不重叠"]:
            check(token in vlsm_text, f"VLSM example missing token: {token}")


# Summary
section("VERIFICATION SUMMARY")

if errors:
    print(f"FAIL: {len(errors)} error(s)")
    for err in errors:
        print(f"  - {err}")
else:
    print("PASS: All hard checks passed")

if warnings:
    print(f"WARN: {len(warnings)} warning(s)")
    for warn in warnings:
        print(f"  - {warn}")

print(f"Errors: {len(errors)}, Warnings: {len(warnings)}")
sys.exit(1 if errors else 0)
