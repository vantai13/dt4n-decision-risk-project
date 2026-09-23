"""THẾ GIỚI THẬT (ground truth) — cấu trúc mạng.

Trả lời: mạng có những link nào, mỗi cặp nguồn–đích có những path ứng viên nào?

Input : tên topology ("butterfly" trước; sau đó Topology Zoo / SNDlib), K path.
Output: danh sách link (capacity, base delay, queue), ma trận path × link.
Không làm: không biết gì về tải, về twin, hay về quyết định.
"""
