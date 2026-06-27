from pathlib import Path
import re, sys
root = Path(__file__).resolve().parents[1]
main = (root / "output/pdf/计算机网络_平板精简速记笔记.md").read_text(encoding="utf-8")
exam = (root / "02_刷题模拟卷/物理层数据链路层_90分验收卷.md").read_text(encoding="utf-8")
ans = (root / "02_刷题模拟卷/物理层数据链路层_90分验收卷_答案.md").read_text(encoding="utf-8")
checks = []
def check(name, ok):
    checks.append((name, ok))

for kw in ["连续 5 个 1", "6 Byte", "46-1500", "64 Byte", "1518 Byte", "72 Byte", "Lmin = 2dR/v", "ARP 请求广播", "客户端 UDP 68", "服务器 UDP 67", "DORA"]:
    check(f"主笔记包含 {kw}", kw in main)
points = [int(x) for x in re.findall(r"【(\d+)分", exam)]
check("验收卷总分为100", sum(points) == 100)
check("验收卷题号1-14存在", all(f"{i}." in exam for i in range(1, 15)))
check("答案题号1-14存在", all(f"{i}." in ans for i in range(1, 15)))
minutes = [int(x) for x in re.findall(r"，(\d+)分钟", exam)]
check("预计时间不超过75分钟", sum(minutes) <= 75)
failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(("PASS" if ok else "FAIL"), name)
print("points", sum(points), "minutes", sum(minutes))
if failed:
    sys.exit(1)
