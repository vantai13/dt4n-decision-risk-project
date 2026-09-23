"""Novelty matrix là TÀI LIỆU SỐNG (sẽ sửa suốt Phase 1).

Vì vậy test này kiểm CẤU TRÚC và NỘI DUNG TỐI THIỂU, không khóa checksum.
Muốn đóng băng một phiên bản cho một mốc (ví dụ DP1), hãy gắn git tag,
đừng khóa hash ở đây.
"""

from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

LITERATURE = Path(__file__).resolve().parents[1] / "notes" / "01_literature"
WORKBOOK = LITERATURE / "novelty_matrix.xlsx"

REQUIRED_SHEETS = {
    "Paper Breakdown",
    "OpenTwin 2026",
    "Novelty Matrix",
    "All Papers Comparison",
}
# Các prior work mà lập luận novelty dựa vào; mất một cái là lập luận hổng.
KEY_PRIOR_WORK = ("Guérin", "OpenTwin", "Zhu")


def _local(tag: str) -> str:
    """'{namespace}t' -> 't': bỏ phần namespace XML để so tên thẻ chính xác."""
    return tag.rsplit("}", 1)[-1]


def _sheet_names(archive: ZipFile) -> set[str]:
    root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    return {node.attrib["name"] for node in root.iter() if _local(node.tag) == "sheet"}


def _all_cell_text(archive: ZipFile) -> str:
    """Gom chữ từ CẢ HAI nơi một file .xlsx có thể cất chữ:

    - xl/sharedStrings.xml : Excel/LibreOffice lưu kiểu này khi bạn mở file và bấm Save;
    - xl/worksheets/sheetN.xml (inlineStr) : thư viện Python thường ghi kiểu này.
    """
    parts = [
        name
        for name in archive.namelist()
        if name == "xl/sharedStrings.xml"
        or (name.startswith("xl/worksheets/sheet") and name.endswith(".xml"))
    ]
    return " ".join(
        node.text or ""
        for name in parts
        for node in ElementTree.fromstring(archive.read(name)).iter()
        if _local(node.tag) == "t"
    )


def test_only_one_workbook():
    """Chỉ một workbook chính thức, để không bao giờ dùng nhầm bản cũ."""
    assert [p.name for p in LITERATURE.glob("*.xlsx")] == [WORKBOOK.name]


def test_novelty_matrix_structure_and_key_prior_work():
    with ZipFile(WORKBOOK) as archive:
        missing = REQUIRED_SHEETS - _sheet_names(archive)
        assert not missing, f"Thiếu sheet: {missing}"
        text = _all_cell_text(archive)
    for prior in KEY_PRIOR_WORK:
        assert prior in text, f"Novelty matrix không còn nhắc tới {prior}"
