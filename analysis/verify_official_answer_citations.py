"""Mechanical audit for claims that cite the local 20-paper answer corpus.

This script intentionally does not call an LLM.  It proves only two things:

1. A claim that names a local paper/question still agrees with that paper's
   answer record or answer text.
2. A small set of calculations transcribed from the primary true-question PDFs
   still agrees with the stated formula and rendered source page.

The 408 true-question chapters are OCR-derived and do not have a one-to-one
mapping to the local 20-paper corpus.  They are therefore reported as
out-of-scope for answer-key equivalence rather than silently marked correct.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DEFAULT_EXAM_ROOT = Path(r"D:\计算机网络试卷\converted_utf8")
PACKAGE_REL = Path("07_考研预备_分层学习包")
DEFAULT_REPORT = REPO / "analysis" / "本地试卷引用机械验收报告.md"
EXPECTED_PAPER_NAMES = tuple(f"计算机网络试卷_{number}.md" for number in range(1, 21))


@dataclass(frozen=True)
class CitationCheck:
    label: str
    material_rel: Path
    paper: int
    question: int
    source_evidence: str
    material_evidence: str


@dataclass(frozen=True)
class ContentCheck:
    label: str
    material_rel: Path
    required: tuple[str, ...]
    forbidden: tuple[str, ...] = ()
    source_note: str = ""


SUBNET = Path("03_网络层/08_子网专题.md")
RIP = Path("03_网络层/09_RIP路由更新专题.md")
ROUTING = Path("03_网络层/10_路由表构建与聚合专题.md")
PHYSICAL = Path("05_物理层/01_零基础学习版.md")
PHYSICAL_QUICK = Path("05_物理层/07_考研强化速查.md")
PHYSICAL_RECALL = Path("05_物理层/06_空白默写.md")
DATALINK = Path("04_数据链路层/01_零基础学习版.md")
NETWORK = Path("03_网络层/04_题型训练.md")
APPLICATION = Path("01_应用层/04_题型训练.md")


# Each item is a direct, human-readable citation that already exists in the
# material.  The script never guesses a paper/question mapping from wording.
CITATION_CHECKS = (
    CitationCheck("子网专题：试卷1第44题", SUBNET, 1, 44, "44.答案：D", "官方答案 D=130"),
    CitationCheck("子网专题：试卷1第46题", SUBNET, 1, 46, "46.答案：B", "官方答案 B=14,14"),
    CitationCheck("子网专题：试卷12第32题", SUBNET, 12, 32, "32.答案：D", "官方答案 D=256,254"),
    CitationCheck("子网专题：试卷12第43题", SUBNET, 12, 43, "43.答案：A", "官方答案 A=16,14"),
    CitationCheck("子网专题：试卷14第44题", SUBNET, 14, 44, "44.答案：C", "官方答案 C=2"),
    CitationCheck("RIP专题：试卷12第24题", RIP, 12, 24, "24．（√）RIP2协议使用运输层UDP的端口520进行传送。", "RIP 使用 UDP 端口 520 | ✅"),
    CitationCheck("RIP专题：试卷10第53题N2更新", RIP, 10, 53, "N2 5 C", "N2  5  C"),
    CitationCheck("RIP专题：试卷10第53题N3新增", RIP, 10, 53, "N3 9 C", "N3  9  C"),
    CitationCheck("RIP专题：试卷10第53题N6更新", RIP, 10, 53, "N6 5 C", "N6  5  C"),
)


CONTENT_CHECKS = (
    ContentCheck(
        "子网专题：试卷12第35题答案键冲突已披露",
        SUBNET,
        (
            "试卷12 第35题（⚠️ 答案键与选项文本不符，已注明）",
            "试卷答案键写 D，但试卷文件里 D 项实际是 255.255.255.192",
            "正确答案按数学应为 /28 = 255.255.255.240，不能声称与答案文件 D 项原文一致。",
        ),
        ("官方答案 D=255.255.255.240",),
        "试卷12第35题的答案键只可验证为 D；选项文本与 /28 计算结果冲突，资料必须同时保留两项事实。",
    ),
    ContentCheck(
        "物理层2022 ASK奈奎斯特计算",
        PHYSICAL,
        ("答案：**800kbps（C）**", "C = 2W·log₂(V) = 2×200k×log₂(4) = 800kbps"),
        ("答案：**400kbps**", "官方答案 400kbps"),
        "原题图：真题题目/…pdf 02.pdf，第5页；4个幅值、200kHz无噪声信道。",
    ),
    ContentCheck(
        "物理层2013分组交换流水线",
        PHYSICAL,
        ("答案：**1600ms 和 801ms**", "T=(N+h-1)×1ms=(800+2-1)×1ms=801ms"),
        ("答案：**1600ms 和 800ms**", "800 个分组流水线转发 ≈ 800ms"),
        "OCR 原题明确为一个路由器、两条 10Mbps 链路、800 个 10kb 分组。",
    ),
    ContentCheck(
        "物理层2025三种交换时延比较",
        PHYSICAL,
        (
            "**T分组 < T电路 < T报文**",
            "Tps=(N+h-1)×3.2ms=(500+3-1)×3.2ms=1.6064s",
            "Tc=32ms+2MB×8/10Mbps=1.632s",
        ),
        ("**T分组 < T报文 < T电路**",),
        "OCR 原题图含 R1、R2 两台存储转发路由器，h=3。",
    ),
    ContentCheck(
        "数据链路层2023二进制指数退避",
        DATALINK,
        ("连续 4 次冲突", "答案：**768μs（C）**", "15×51.2μs = 768μs"),
        ("连续 3 次冲突", "716.8μs", "358.4μs？"),
        "原题图：真题题目/…pdf 03.pdf，第14页。",
    ),
    ContentCheck(
        "数据链路层2025二进制指数退避",
        DATALINK,
        ("答案：**52.3776ms（C）**", "1023×51.2μs = 52.3776ms"),
        ("答案：**104.8064ms**", "2047×51.2"),
        "原题图：真题题目/…pdf 03.pdf，第15页；k=min(11,10)=10。",
    ),
    ContentCheck(
        "网络层2021分片8B对齐",
        NETWORK,
        ("最大数据长度 = floor((800-20)/8)×8 = 776B", "首片总长度 = 776+20 = 796B"),
        ("实际 780B 数据",),
        "由MTU=800B、首部20B及片偏移量8B单位直接计算。",
    ),
    ContentCheck(
        "物理层速查：10BASE-T与100BASE-TX编码区分",
        PHYSICAL_QUICK,
        ("10Base-T 用曼彻斯特", "100BASE-TX 使用 4B/5B + MLT-3"),
        ("100Base-T 用曼彻斯特",),
        "避免把100BASE-T系列泛化为曼彻斯特编码。",
    ),
    ContentCheck(
        "物理层默写：10BASE-T与100BASE-TX编码区分",
        PHYSICAL_RECALL,
        ("10Base-T 用______编码", "100BASE-TX 使用______编码"),
        ("100Base-T 用______编码",),
        "与速查表保持同一术语口径。",
    ),
    ContentCheck(
        "物理层默写：分组交换通用公式",
        PHYSICAL_RECALL,
        (
            "总时延（h 条等速链路） = (______ + ______ - 1) × ______",
            "分组数 N = ⌈文件大小 / (分组大小 - ______开销)⌉",
            "不背固定排序",
        ),
        (
            "总时延 ≈ ______ + 中间节点转发一个分组的时延",
            "三种交换时延大小：______ < ______ < ______（通常）",
        ),
        "用 N、h、分组总长度和链路速率建模，避免把单中间节点特例当作通式。",
    ),
    ContentCheck(
        "应用层2020 DNS与HTTP时延",
        APPLICATION,
        (
            "往返时间（RTT）均为 **10ms**",
            "答案：**20ms 与 50ms（D）**",
            "本地 DNS 分别查询根、`.com` 顶级域和 `abc.com` 权威服务器",
        ),
        ("答案：**10ms 与 30ms**", "主机→本地 DNS（1 次递归，占 1 个 RTT）"),
        "原题图：真题题目/…pdf 06.pdf，第3页；H与本地DNS同在局域网，Internet RTT=10ms，选项D为20ms/50ms。",
    ),
    ContentCheck(
        "应用层2010递归DNS请求次数",
        APPLICATION,
        (
            "用户主机、本地域名服务器发送的域名请求消息数分别为",
            "答案：**B，一条、多条**",
        ),
        ("答案：**1 条**。递归查询",),
        "原题图：真题题目/…pdf 06.pdf，第2页；题目同时询问用户主机和本地域名服务器的请求数。",
    ),
    ContentCheck(
        "应用层2022 HTTP与TCP慢开始",
        APPLICATION,
        (
            "同目录下的 **1 幅图像**",
            "答案：**40ms（B）**",
            "第 4 个 RTT：服务器发送图像剩余 1 MSS",
        ),
        ("同目录下的 3 个图像文件", "共 3 RTT = 30ms"),
        "原题图：真题题目/…pdf 06.pdf，第10页；2022年第40题，选项B=40ms。",
    ),
    ContentCheck(
        "应用层2015 HTTP Connection Close",
        APPLICATION,
        (
            "Connection: Close",
            "答案：**C**。`Connection: Close` 明确要求响应后关闭连接",
        ),
        (
            "该浏览器请求使用持续连接\"：请求行 HTTP/1.1 **默认就是持久连接**",
            "原题四个选项 OCR 不完整",
        ),
        "原题图：真题题目/…pdf 06.pdf，第9页；Connection: Close使选项C错误。",
    ),
    ContentCheck(
        "应用层2024非持久HTTP RTT题干",
        APPLICATION,
        (
            "同一网站上 7 个小图像文件",
            "答案：**16 个 RTT**",
        ),
        ("4 个不同域下的 7 个小图像文件",),
        "原题图：真题题目/…pdf 06.pdf，第9页；题干为同一网站上的7个小图像文件。",
    ),
    ContentCheck(
        "应用层2021 DNS封装、交换机自学习与ARP广播",
        APPLICATION,
        (
            "DNS 报文依次封装在 **UDP -> IP -> 以太网** 中",
            "<00-11-22-33-44-cc, 4>",
            "<00-11-22-33-44-bb, 1>",
            "<00-11-22-33-44-aa, 2>",
            "至少 **2 个帧**，都是 H1 发出的 **ARP 请求广播帧**",
            "FF-FF-FF-FF-FF-FF",
        ),
        (
            "**DNS 解析**（域名→IP，应用层）+ **ARP**",
            "1 个 ARP 应答帧 + 1 个 HTTP 响应帧",
        ),
        "原题图：真题题目/…pdf 06.pdf，第4页；2021年第47题，t0时H1的ARP表和DNS缓存均为空，t1时S首次收到HTTP请求帧。",
    ),
    ContentCheck(
        "应用层408真题证据边界",
        APPLICATION,
        (
            "不能证明 408 真题答案已逐题核对",
            "统一标记为“未建立官方答案键映射”",
        ),
        ("所有真题的题干、选项与官方答案已通过机械验收", "10/10 PASS"),
        "本地20套教材配套卷不能替代408统考答案键。",
    ),
)


def normalized(value: str) -> str:
    """Make spacing and full-width punctuation irrelevant for copied answers."""

    return re.sub(r"[\W_]+", "", value, flags=re.UNICODE).casefold()


def contains(text: str, fragment: str) -> bool:
    return normalized(fragment) in normalized(text)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def answer_line(text: str, question: int) -> str:
    """Return the first answer-record line for reporting, when present."""

    answer_start = text.find("参考答案和试题分析")
    block = text[answer_start:] if answer_start >= 0 else text
    patterns = (
        rf"^\s*{question}[.．]\s*答案\s*[：:]\s*(.+)$",
        rf"^\s*{question}[.．]\s*[（(][√×][）)]\s*(.+)$",
    )
    for pattern in patterns:
        match = re.search(pattern, block, flags=re.MULTILINE)
        if match:
            return match.group(0).strip()
    return "未解析到标准答案行"


def count_true_question_chapters(package_root: Path) -> tuple[int, list[Path]]:
    paths: list[Path] = []
    total = 0
    for path in package_root.rglob("*.md"):
        text = read_text(path)
        count = len(re.findall(r"^#{1,6}\s+.*408\s+真题专章", text, flags=re.MULTILINE))
        if count:
            paths.append(path)
            total += count
    return total, paths


def audit_citations(package_root: Path, exam_root: Path) -> tuple[list[tuple[CitationCheck, bool, str]], list[str]]:
    material_cache: dict[Path, str] = {}
    results: list[tuple[CitationCheck, bool, str]] = []
    errors: list[str] = []

    for check in CITATION_CHECKS:
        material_path = package_root / check.material_rel
        paper_path = exam_root / f"计算机网络试卷_{check.paper}.md"
        if material_path not in material_cache:
            material_cache[material_path] = read_text(material_path) if material_path.exists() else ""
        material = material_cache[material_path]
        paper = read_text(paper_path) if paper_path.exists() else ""

        source_ok = bool(paper) and contains(paper, check.source_evidence)
        material_ok = bool(material) and contains(material, check.material_evidence)
        ok = source_ok and material_ok
        evidence = answer_line(paper, check.question) if paper else "试卷文件缺失"
        results.append((check, ok, evidence))
        if not ok:
            missing = []
            if not source_ok:
                missing.append(f"试卷证据缺失：{check.source_evidence}")
            if not material_ok:
                missing.append(f"资料证据缺失：{check.material_evidence}")
            errors.append(f"{check.label}（{'；'.join(missing)}）")
    return results, errors


def audit_content(package_root: Path) -> tuple[list[tuple[ContentCheck, bool, list[str]]], list[str]]:
    results: list[tuple[ContentCheck, bool, list[str]]] = []
    errors: list[str] = []
    for check in CONTENT_CHECKS:
        path = package_root / check.material_rel
        text = read_text(path) if path.exists() else ""
        problems = [f"缺少：{value}" for value in check.required if value not in text]
        problems.extend(f"仍存在旧表述：{value}" for value in check.forbidden if value in text)
        ok = not problems
        results.append((check, ok, problems))
        if not ok:
            errors.append(f"{check.label}（{'；'.join(problems)}）")
    return results, errors


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_report(
    output: Path,
    exam_root: Path,
    paper_files: list[Path],
    missing_papers: list[str],
    unexpected_papers: list[str],
    paper_answer_sections: int,
    chapter_count: int,
    chapter_paths: list[Path],
    citation_results: list[tuple[CitationCheck, bool, str]],
    content_results: list[tuple[ContentCheck, bool, list[str]]],
    errors: list[str],
) -> None:
    status = "通过（受限范围）" if not errors else "不通过"
    lines = [
        "# 本地试卷引用机械验收报告",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"结论：**{status}**",
        "",
        "## 证据边界",
        "",
        "- 本报告不调用 Codex，也不依赖模型额度。",
        f"- 对照库为 `{exam_root}` 的本地 20 套带答案试卷；它可验证资料中**明确引用同卷同题号**的内容。",
        "- 2009-2025 408 真题专章来自 PDF 的 OCR 转录，当前没有“真题条目 -> 一手答案键”的映射；因此不能用这 20 套配套试卷替代 408 统考答案键。",
        "- 未建立映射的 408 真题被标记为“未验证”，不是“正确”。",
        "- 本脚本不自动阅读原题图或 PDF；原题页码仅用于定位此前人工复核的证据，表中的自动检查是资料文字和确定性公式的回归检查。",
        "",
        "## 对照库完整性",
        "",
        f"- 符合预期文件名的试卷：`{len(paper_files)}` / 20",
        f"- 含“参考答案和试题分析”分隔符：`{paper_answer_sections}` / {len(paper_files)}",
        f"- 分层学习包中的 408 真题专章：`{chapter_count}` 个，位于 `{len(chapter_paths)}` 个文件。",
        "",
        "## 直接引用核对",
        "",
        "| 状态 | 引用 | 本地答案记录 | 资料断言 |",
        "|---|---|---|---|",
    ]
    for check, ok, evidence in citation_results:
        source_record = f"{evidence}；核对片段：{check.source_evidence}"
        material_assertion = check.material_evidence.replace("官方答案", "资料标注")
        lines.append(
            f"| {'PASS' if ok else 'FAIL'} | {markdown_cell(check.label)} | "
            f"{markdown_cell(source_record)} | {markdown_cell(material_assertion)} |"
        )

    lines.extend([
        "",
        "## 人工复核结论的回归检查",
        "",
        "| 状态 | 项目 | 证据 |",
        "|---|---|---|",
    ])
    for check, ok, problems in content_results:
        evidence = "；".join(problems) if problems else (check.source_note or "资料表述符合已核对公式")
        lines.append(f"| {'PASS' if ok else 'FAIL'} | {markdown_cell(check.label)} | {markdown_cell(evidence)} |")

    if missing_papers or unexpected_papers:
        lines.extend(["", "## 对照库异常", ""])
        lines.extend(f"- 缺少预期试卷：`{name}`" for name in missing_papers)
        lines.extend(f"- 发现非预期试卷：`{name}`" for name in unexpected_papers)

    lines.extend([
        "",
        "## 未覆盖项",
        "",
        "1. 408 真题专章的全部答案一致性：缺少可追溯的一手答案键和题号映射，不能机械判定。",
        "2. 本地 20 套试卷的来源被资料称为教材配套卷，不能在没有原始出版/校方出处的情况下改称“408 官方答案”。",
        "3. Codex 语义审核仍可作为第二层验收，但应在额度恢复后运行，并将结果与本报告分开保存。",
        "",
        "## 复跑命令",
        "",
        "```powershell",
        "python analysis/verify_official_answer_citations.py",
        "```",
        "",
    ])
    if errors:
        lines.extend(["## 阻断项", ""])
        lines.extend(f"- {item}" for item in errors)
        lines.append("")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify local-paper citations in the study package.")
    parser.add_argument("--exam-root", type=Path, default=DEFAULT_EXAM_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    package_root = REPO / PACKAGE_REL
    expected_paths = [args.exam_root / name for name in EXPECTED_PAPER_NAMES]
    paper_files = [path for path in expected_paths if path.is_file()]
    missing_papers = [path.name for path in expected_paths if not path.is_file()]
    unexpected_papers = (
        sorted(path.name for path in args.exam_root.glob("计算机网络试卷_*.md") if path.name not in EXPECTED_PAPER_NAMES)
        if args.exam_root.exists()
        else []
    )
    paper_answer_sections = sum("参考答案和试题分析" in read_text(path) for path in paper_files)
    chapter_count, chapter_paths = count_true_question_chapters(package_root)
    citation_results, citation_errors = audit_citations(package_root, args.exam_root)
    content_results, content_errors = audit_content(package_root)
    corpus_errors = [f"缺少预期试卷：{name}" for name in missing_papers]
    corpus_errors.extend(f"发现非预期试卷：{name}" for name in unexpected_papers)
    corpus_errors.extend(
        f"答案分隔符缺失：{path.name}"
        for path in paper_files
        if "参考答案和试题分析" not in read_text(path)
    )
    errors = corpus_errors + citation_errors + content_errors
    write_report(
        args.output,
        args.exam_root,
        paper_files,
        missing_papers,
        unexpected_papers,
        paper_answer_sections,
        chapter_count,
        chapter_paths,
        citation_results,
        content_results,
        errors,
    )

    print(f"Report: {args.output}")
    print(f"Citation checks: {sum(ok for _, ok, _ in citation_results)}/{len(citation_results)}")
    print(f"Content checks: {sum(ok for _, ok, _ in content_results)}/{len(content_results)}")
    if errors:
        print("FAIL")
        for item in errors:
            print(f"- {item}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
