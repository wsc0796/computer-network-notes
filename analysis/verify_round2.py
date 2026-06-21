"""
Round 2 verification script.
Verifies exam scores, plan timing, file paths, question-answer correspondence.
"""
import os
import re
import sys

REPO = r"C:\Users\50469\Desktop\Shirakoko_Notes\...课程笔记_输出"
# Override with current directory logic
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

errors = []
warnings = []

def check(condition, msg, level="error"):
    if not condition:
        if level == "error":
            errors.append(msg)
        else:
            warnings.append(msg)

# ========== 1. Exam score verification ==========
print("=" * 60)
print("1. Exam score verification")

exam_path = os.path.join(REPO, "02_刷题模拟卷", "运输层网络层_6小时验收卷.md")
answer_path = os.path.join(REPO, "02_刷题模拟卷", "运输层网络层_6小时验收卷_答案.md")

check(os.path.exists(exam_path), f"Exam file missing: {exam_path}")
check(os.path.exists(answer_path), f"Answer file missing: {answer_path}")

with open(exam_path, 'r', encoding='utf-8') as f:
    exam_text = f.read()

transport_expected = [8, 8, 10, 6, 10, 8]
network_expected = [8, 8, 8, 8, 10, 8]

transport_total = 0
network_total = 0

for i, exp in enumerate(transport_expected):
    pattern = rf'### {i+1}\. .*?共(\d+)分'
    m = re.search(pattern, exam_text, re.DOTALL)
    if m:
        score = int(m.group(1))
        transport_total += score
        check(score == exp, f"Q{i+1} score={score}, expected={exp}")
    else:
        check(False, f"Q{i+1} score not found in exam")

for i, exp in enumerate(network_expected):
    pattern = rf'### {i+7}\. .*?共(\d+)分'
    m = re.search(pattern, exam_text, re.DOTALL)
    if m:
        score = int(m.group(1))
        network_total += score
        check(score == exp, f"Q{i+7} score={score}, expected={exp}")
    else:
        check(False, f"Q{i+7} score not found in exam")

total = transport_total + network_total
print(f"  Transport score: {transport_total}")
print(f"  Network score: {network_total}")
print(f"  Total score: {total}")

check(transport_total == 50, f"Transport total={transport_total}, expected=50")
check(network_total == 50, f"Network total={network_total}, expected=50")
check(total == 100, f"Total={total}, expected=100")

# Self-declaration check
if "50+50=100" in exam_text:
    print("  Self-declared total check: PASS")
else:
    warnings.append("Self-declared total '50+50=100' not found in exam text")

# ========== 2. Answer file score verification ==========
print("\n" + "=" * 60)
print("2. Answer file score verification")

with open(answer_path, 'r', encoding='utf-8') as f:
    answer_text = f.read()

if "50+50=100" in answer_text:
    print("  Answer self-declared total: PASS")
else:
    warnings.append("Answer self-declared total '50+50=100' not found")

# ========== 3. Question number correspondence ==========
print("\n" + "=" * 60)
print("3. Question number correspondence")

exam_q_nums = set()
answer_q_nums = set()

for m in re.finditer(r'### (\d+)\. ', exam_text):
    exam_q_nums.add(int(m.group(1)))
for m in re.finditer(r'### (\d+)\. ', answer_text):
    answer_q_nums.add(int(m.group(1)))

print(f"  Exam questions: {sorted(exam_q_nums)}")
print(f"  Answer questions: {sorted(answer_q_nums)}")

check(exam_q_nums == answer_q_nums,
      f"Question mismatch: exam extra={exam_q_nums-answer_q_nums}, answer extra={answer_q_nums-exam_q_nums}")
check(len(exam_q_nums) == 12, f"Expected 12 questions, got {len(exam_q_nums)}")
check(len(exam_q_nums) == len(set(exam_q_nums)), "Duplicate question numbers found")

# ========== 4. 6-hour plan time verification ==========
print("\n" + "=" * 60)
print("4. 6-hour plan time verification")

plan_path = os.path.join(REPO, "01_考前冲刺复习", "运输层与网络层_6小时完整复习计划.md")
check(os.path.exists(plan_path), f"Plan file missing: {plan_path}")

with open(plan_path, 'r', encoding='utf-8') as f:
    plan_text = f.read()

time_pattern = r'## (\d+:\d+)[—-](\d+:\d+) .+?（(\d+)分钟）'
matches = re.findall(time_pattern, plan_text)

total_minutes = 0
for m in matches:
    start, end, minutes = m
    mins = int(minutes)
    total_minutes += mins
    print(f"  {start}-{end}: {mins}min")

print(f"  Sum of time blocks: {total_minutes}min")
check(total_minutes == 360, f"Plan total={total_minutes}, expected=360")

# Check the summary table
for label, key in [("Transport", "运输层"), ("Network", "网络层"), ("Rest", "休息"), ("Exam+Review", "闭卷验收")]:
    pattern = rf'\|\s*{key}.*?\|\s*(\d+)\s*\|'
    m = re.search(pattern, plan_text)
    if m:
        print(f"  Table {label}: {m.group(1)}min")
    else:
        warnings.append(f"Table {label} not found in plan")

# ========== 5. File path existence ==========
print("\n" + "=" * 60)
print("5. Key file path existence check")

# Find files referenced in the plan
ref_pattern = r'`([^`]+\.md)`'
refs = set(re.findall(ref_pattern, plan_text))
# Also check analysis files
analysis_files = [
    "analysis/资料审计_读取状态.md",
    "analysis/覆盖矩阵与证据评估_第二轮.md",
]

missing = []
for f in sorted(refs):
    # Try as relative path
    full = os.path.join(REPO, f)
    if not os.path.exists(full):
        # Try without leading directories
        found = False
        for root, dirs, files in os.walk(REPO):
            for fn in files:
                if fn == os.path.basename(f) or f.endswith(fn):
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(f)

for f in analysis_files:
    full = os.path.join(REPO, f)
    if not os.path.exists(full):
        missing.append(f)

if missing:
    for f in missing:
        errors.append(f"File not found: {f}")
else:
    print(f"  All referenced files present")

# ========== 6. Required content checks ==========
print("\n" + "=" * 60)
print("6. Required exam content checks")

content_checks = [
    ("SYN clarified", r'不携带.*数据.*SYN|SYN.*不携带', exam_text),
    ("Model notation", r'简化模型|课程常用简化', exam_text),
    ("GBN timer wording", r'最早未确认.*计时器|为最早未确认', exam_text),
    ("Total 100 declared", r'100分', exam_text),
    ("Pass line 80", r'80分', exam_text),
    ("Closed book rule", r'闭卷', exam_text),
    ("Time estimate", r'预计\d+分钟|预计\d+min', exam_text),
]

for name, pattern, text in content_checks:
    if re.search(pattern, text, re.MULTILINE | re.DOTALL):
        print(f"  PASS: {name}")
    else:
        warnings.append(f"Exam missing: {name}")
        print(f"  WARN: {name} - not found")

# Answer content checks
print("\n7. Required answer content checks")
answer_checks = [
    ("Calculation steps", r'步骤', answer_text),
    ("Scoring points", r'评分点|得\d分', answer_text),
    ("Common mistakes", r'常见错误|易错', answer_text),
    ("Verification", r'验证', answer_text),
    ("Score verification", r'50\+50=100', answer_text),
]

for name, pattern, text in answer_checks:
    if re.search(pattern, text, re.MULTILINE | re.DOTALL):
        print(f"  PASS: {name}")
    else:
        warnings.append(f"Answer missing: {name}")
        print(f"  WARN: {name} - not found")

# ========== Summary ==========
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)

if errors:
    print(f"\nFAIL: {len(errors)} error(s):")
    for e in errors:
        print(f"  - {e}")
else:
    print("\nPASS: All hard checks passed")

if warnings:
    print(f"\nWARN: {len(warnings)} warning(s):")
    for w in warnings:
        print(f"  - {w}")

print(f"\nErrors: {len(errors)}, Warnings: {len(warnings)}")

if errors:
    sys.exit(1)
else:
    sys.exit(0)
