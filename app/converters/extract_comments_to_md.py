# -*- coding: utf-8 -*-
"""
엑셀 파일의 모든 시트에서 쪽지(메모/노트)를 추출해 Markdown 파일로 저장하는 스크립트.
openpyxl 로드에 실패하는 파일도 처리할 수 있도록 xlsx 내부 XML을 직접 파싱합니다.

사용법: python extract_comments_to_md.py 파일경로.xlsx [출력파일.md]
"""

import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def extract_comments(xlsx_path):
    """시트별 쪽지를 {시트명: [(셀주소, 작성자, 내용), ...]} 형태로 반환"""
    z = zipfile.ZipFile(xlsx_path)
    results = {}

    # 1) 시트 이름 -> 시트 XML 경로 매핑
    wb_root = ET.fromstring(z.read("xl/workbook.xml"))
    wb_rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {r.get("Id"): r.get("Target") for r in wb_rels}

    sheet_paths = {}
    for s in wb_root.iter(f"{NS_MAIN}sheet"):
        target = rid_to_target[s.get(f"{NS_REL}id")].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheet_paths[s.get("name")] = target

    # 2) 각 시트의 관계 파일에서 연결된 comments XML 찾기
    def comments_path_for(sheet_path):
        folder, fname = sheet_path.rsplit("/", 1)
        rels = f"{folder}/_rels/{fname}.rels"
        if rels not in z.namelist():
            return None
        for r in ET.fromstring(z.read(rels)):
            if r.get("Type").endswith("/comments"):
                t = r.get("Target")
                return (
                    re.sub(r"^\.\./", "xl/", t)
                    if t.startswith("..")
                    else f"{folder}/{t}"
                )
        return None

    # 3) 쪽지 내용 추출 (시트별로 그룹화)
    for sheet_name, sp in sheet_paths.items():
        cp = comments_path_for(sp)
        if not cp:
            continue
        root = ET.fromstring(z.read(cp))
        authors = [a.text or "" for a in root.iter(f"{NS_MAIN}author")]
        items = []
        for c in root.iter(f"{NS_MAIN}comment"):
            text = "".join(t.text or "" for t in c.iter(f"{NS_MAIN}t")).strip()
            author = authors[int(c.get("authorId", 0))] if authors else ""
            ref = c.get("ref").split(":")[0]  # "E18:E18" -> "E18"
            items.append((ref, author, text))
        if items:
            results[sheet_name] = items

    return results


def save_to_md(comments, xlsx_path, md_path):
    """추출한 쪽지를 Markdown 파일로 저장"""
    total = sum(len(v) for v in comments.values())
    lines = [
        f"# {Path(xlsx_path).name} 쪽지 모음",
        "",
        f"총 {total}개의 쪽지 (시트 {len(comments)}개)",
        "",
    ]
    for sheet_name, items in comments.items():
        lines.append(f"## {sheet_name}")
        lines.append("")
        for ref, author, text in items:
            lines.append(f"### {ref} (작성자: {author})")
            lines.append("")
            lines.append(text)
            lines.append("")

    Path(md_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"저장 완료: {md_path} (쪽지 {total}개)")


if __name__ == "__main__":
    default_file_name = "xlsx_files/조견표.xlsx"

    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else default_file_name
    md_path = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "md_files/" + Path(default_file_name).stem + "_추가설명.md"
    )

    comments = extract_comments(xlsx_path)
    save_to_md(comments, xlsx_path, md_path)
