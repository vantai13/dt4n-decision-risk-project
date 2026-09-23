"""Khóa đúng phiên bản workbook dùng để bảo vệ novelty."""

import hashlib
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile


LITERATURE = Path(__file__).resolve().parents[1] / "notes" / "01_literature"
WORKBOOK = LITERATURE / "Paper_Breakdown_DT4N_One_Comparison_Table_updated.xlsx"
SHA256 = "2736294d1f04909d134042c9ac2f1d905e79853fa92d15f86a5f8d5c9eae2a73"
REQUIRED_SHEETS = {
    "Paper Breakdown",
    "OpenTwin 2026",
    "Novelty Matrix",
    "All Papers Comparison",
}


def test_only_canonical_workbook_is_present():
    assert [path.name for path in LITERATURE.glob("*.xlsx")] == [WORKBOOK.name]
    assert hashlib.sha256(WORKBOOK.read_bytes()).hexdigest() == SHA256


def test_novelty_matrix_and_key_prior_work_are_present():
    with ZipFile(WORKBOOK) as archive:
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        sheet_names = {node.attrib["name"] for node in workbook.iter() if node.tag.endswith("sheet")}
        assert REQUIRED_SHEETS <= sheet_names

        text = " ".join(
            node.text or ""
            for name in archive.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
            for node in ElementTree.fromstring(archive.read(name)).iter()
            if node.tag.endswith("t")
        )
        for prior_work in ("Guérin", "OpenTwin", "Zhu"):
            assert prior_work in text
