#!/usr/bin/env python3
"""
hwpx → Markdown 변환기

사용법:
    python -m app.hwpx_to_md 입력파일.hwpx [출력파일.md]

동작:
    1. hwpx(ZIP 컨테이너)를 임시 폴더에 압축 해제
    2. Contents/section*.xml 을 순서대로 파싱
    3. 문단(hp:p)과 표(hp:tbl)를 Markdown으로 변환
       - 표는 Markdown 표로 변환 (rowspan/colspan 병합 셀은 빈 칸으로 채움)
       - 셀 안에 여러 문단이 있으면 <br>로 연결
"""

import sys
import zipfile
import tempfile
import re
from pathlib import Path
import xml.etree.ElementTree as ET

# hwpx(OWPML) 네임스페이스
NS = {
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
}
HP = NS["hp"]


def q(tag: str) -> str:
    """'hp:t' → '{namespace}t' 형태의 정규화된 태그명으로 변환"""
    prefix, name = tag.split(":")
    return f"{{{NS[prefix]}}}{name}"


def cell_text(tc: ET.Element) -> str:
    """표 셀(hp:tc) 내부의 모든 문단 텍스트를 <br>로 연결해 반환"""
    lines = []
    for p in tc.iter(q("hp:p")):
        texts = [t.text or "" for t in p.iter(q("hp:t"))]
        line = "".join(texts).strip()
        if line:
            lines.append(line)
    text = "<br>".join(lines)
    # Markdown 표 안에서 파이프 문자는 이스케이프 필요
    return text.replace("|", "\\|")


def table_to_md(tbl: ET.Element) -> str:
    """hp:tbl 요소를 Markdown 표 문자열로 변환 (병합 셀은 그리드에 배치)"""
    row_cnt = int(tbl.get("rowCnt", "0"))
    col_cnt = int(tbl.get("colCnt", "0"))
    if row_cnt == 0 or col_cnt == 0:
        return ""

    # 병합(rowspan/colspan)을 반영하기 위해 2차원 그리드에 셀을 배치
    grid = [[None] * col_cnt for _ in range(row_cnt)]

    for tr_idx, tr in enumerate(tbl.findall(q("hp:tr"))):
        for tc in tr.findall(q("hp:tc")):
            addr = tc.find(q("hp:cellAddr"))
            span = tc.find(q("hp:cellSpan"))
            # cellAddr가 있으면 그 좌표를 사용, 없으면 순서대로 빈 칸에 배치
            if addr is not None:
                r, c = int(addr.get("rowAddr")), int(addr.get("colAddr"))
            else:
                r = tr_idx
                c = next((i for i, v in enumerate(grid[r]) if v is None), 0)
            rs = int(span.get("rowSpan", "1")) if span is not None else 1
            cs = int(span.get("colSpan", "1")) if span is not None else 1

            text = cell_text(tc)
            for dr in range(rs):
                for dc in range(cs):
                    rr, cc = r + dr, c + dc
                    if rr < row_cnt and cc < col_cnt and grid[rr][cc] is None:
                        # 병합 원점에만 텍스트, 나머지는 빈 문자열
                        grid[rr][cc] = text if (dr == 0 and dc == 0) else ""

    rows = [[cell if cell is not None else "" for cell in row] for row in grid]

    # Markdown 표 조립: 첫 행을 헤더로 사용
    md = []
    md.append("| " + " | ".join(rows[0]) + " |")
    md.append("|" + "---|" * col_cnt)
    for row in rows[1:]:
        md.append("| " + " | ".join(row) + " |")
    return "\n".join(md)


def para_to_md(p: ET.Element) -> str:
    """표 바깥의 일반 문단(hp:p)을 텍스트 한 줄로 변환"""
    parts = []
    for run in p.findall(q("hp:run")):
        for t in run.findall(q("hp:t")):
            parts.append(t.text or "")
    return "".join(parts).strip()


def section_to_md(xml_bytes: bytes) -> str:
    """section*.xml 하나를 Markdown 문자열로 변환"""
    root = ET.fromstring(xml_bytes)
    blocks = []

    # 최상위 문단만 순회 (표 안의 문단은 table_to_md에서 처리)
    for p in root.findall(q("hp:p")):
        # 문단 안의 run에 표가 포함되어 있으면 표로 변환
        tbls = p.findall(f'{q("hp:run")}/{q("hp:tbl")}')
        if tbls:
            # 표 앞뒤에 텍스트가 섞여 있을 수 있으므로 텍스트 먼저
            text = para_to_md(p)
            if text:
                blocks.append(text)
            for tbl in tbls:
                blocks.append(table_to_md(tbl))
        else:
            text = para_to_md(p)
            if text:
                blocks.append(text)

    return "\n\n".join(blocks)


def hwpx_to_md(hwpx_path: str) -> str:
    """hwpx 파일 → Markdown 전체 변환"""
    md_sections = []
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1단계: ZIP 압축 해제
        with zipfile.ZipFile("hwpx_files/" + hwpx_path) as zf:
            zf.extractall(tmpdir)

        # 2단계: section0.xml, section1.xml ... 순서대로 파싱
        contents = Path(tmpdir) / "Contents"
        sections = sorted(
            contents.glob("section*.xml"),
            key=lambda f: int(re.search(r"\d+", f.stem).group()),
        )
        if not sections:
            raise FileNotFoundError(
                "Contents/section*.xml을 찾을 수 없습니다. hwpx 파일이 맞는지 확인하세요."
            )

        # 3단계: 각 섹션을 Markdown으로 변환
        for sec in sections:
            md_sections.append(section_to_md(sec.read_bytes()))

    return "\n\n---\n\n".join(md_sections)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = sys.argv[1]
    dst = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "md_files/" + str(Path(src).with_suffix(".md"))
    )

    md = hwpx_to_md(src)
    Path(dst).write_text(md, encoding="utf-8")
    print(f"변환 완료: {dst} ({len(md):,}자)")


if __name__ == "__main__":
    main()
