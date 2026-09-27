"""L1.9 phần 2 — forward citation + truy vấn có mục tiêu qua OpenAlex (chạy trên máy có mạng; ~1–2 phút).

Ghi CSV cùng định dạng snowball_openalex_2026-09-23.csv, cộng cột `query` cho truy vấn có mục tiêu.
`title_filter_match` chỉ là lọc từ khoá trên tiêu đề, KHÔNG phải sàng lọc; `retained_for_next_read` để trống cho
bước sàng abstract. Đặt OPENALEX_MAILTO=email để vào "polite pool" của OpenAlex.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.openalex.org"
OUT = Path(__file__).resolve().parents[1] / "snowball_openalex_2026-09-27.csv"
SEEDS = {   # start_set: (DOI hoặc None, tiêu đề để tìm khi không có DOI / tìm thêm bản khác)
    "Fischer-Voecking": ("10.1016/j.tcs.2008.01.055", "Adaptive routing with stale information"),
    "Seshadri-Katz": (None, "Dynamics of simultaneous overlay network routing"),
}
TARGETED = [   # PHASE_1 L1.9 bước 3
    "stale path switching threshold",
    "hysteresis path selection uncertainty",
    "probabilistic digital twin network",
    "SD-WAN path selection prediction",
    "edge server selection hysteresis",
]
KEYWORDS = re.compile(r"stale|old information|hysteresis|oscillat|flapping|path (selection|switch)|route selection|"
                      r"server selection|handover|digital twin|overlay routing|adaptive routing|load balanc|"
                      r"uncertain|threshold", re.I)


def get(path, **params):
    mailto = os.environ.get("OPENALEX_MAILTO")
    if mailto:
        params["mailto"] = mailto
    url = f"{API}{path}?{urllib.parse.urlencode(params)}" if params else f"{API}{path}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                time.sleep(0.15)
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:            # mạng chập chờn: thử lại có giãn cách
            if attempt == 3:
                raise RuntimeError(f"OpenAlex lỗi tại {url}: {exc}") from exc
            time.sleep(2 ** attempt)


def row(work, start_set, direction, query=""):
    title = work.get("display_name") or work.get("title") or ""
    return dict(start_set=start_set, direction=direction, openalex_id=(work.get("id") or "").rsplit("/", 1)[-1],
                year=work.get("publication_year") or "", title=title, doi=work.get("doi") or "",
                title_filter_match=int(bool(KEYWORDS.search(title))), retained_for_next_read="", query=query)


def resolve(doi, title):
    """Trả mọi bản OpenAlex của một bài (bản journal theo DOI + các bản khác cùng tiêu đề, ví dụ PODC/TR)."""
    found = {}
    if doi:
        try:
            w = get(f"/works/doi:{doi}")
            found[w["id"]] = w
        except RuntimeError as exc:
            print(f"  ! không resolve được DOI {doi}: {exc}", file=sys.stderr)
    try:
        res = get("/works", filter=f"title.search:{title}", **{"per-page": 10})
        for w in res.get("results", []):
            if (w.get("display_name") or "").strip().lower().rstrip(".") == title.lower():
                found[w["id"]] = w
    except RuntimeError as exc:
        # Không làm mất bản đã resolve bằng DOI khi dịch vụ search tạm lỗi.
        print(f"  ! không tìm thêm bản theo tiêu đề {title!r}: {exc}", file=sys.stderr)
    return list(found.values())


def forward(work_id):
    """Mọi bài trích dẫn work_id (phân trang bằng cursor)."""
    short, cursor, out = work_id.rsplit("/", 1)[-1], "*", []
    while cursor:
        res = get("/works", filter=f"cites:{short}", cursor=cursor, **{"per-page": 200})
        out += res.get("results", [])
        cursor = res.get("meta", {}).get("next_cursor")
        if not res.get("results"):
            break
    return out


def main():
    rows, summary = [], []
    for name, (doi, title) in SEEDS.items():
        versions = resolve(doi, title)
        if not versions:
            summary.append(f"{name}: KHÔNG tìm thấy trong OpenAlex (ghi 'không lập chỉ mục', không suy ra 0 trích dẫn)")
            continue
        seen = {}
        for v in versions:
            for w in forward(v["id"]):
                seen[w["id"]] = w
        kept = [row(w, name, "forward") for w in seen.values()]
        rows += kept
        ids = ", ".join(v["id"].rsplit("/", 1)[-1] for v in versions)
        summary.append(f"{name}: {len(versions)} bản ({ids}); forward {len(kept)} bài, "
                       f"{sum(r['title_filter_match'] for r in kept)} qua lọc tiêu đề")
    for q in TARGETED:
        try:
            res = get("/works", search=q, **{"per-page": 50})
        except RuntimeError as exc:
            summary.append(f"'{q}': LỖI DỊCH VỤ — {exc}")
            continue
        kept = [row(w, "targeted", "search", q) for w in res.get("results", [])]
        rows += kept
        summary.append(f"'{q}': OpenAlex đếm {res.get('meta', {}).get('count', '?')} kết quả; "
                       f"lưu top {len(kept)}, {sum(r['title_filter_match'] for r in kept)} qua lọc tiêu đề")
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["start_set"])
        writer.writeheader()
        writer.writerows(rows)
    print("\n".join(summary))
    print(f"Đã ghi {len(rows)} dòng vào {OUT}")


if __name__ == "__main__":
    main()
