"""DIGITAL TWIN — mạng được nhìn qua telemetry có tuổi.

Trả lời: tại thời điểm quyết định t, twin tin rằng chi phí mỗi path là bao nhiêu,
khi nó chỉ thấy trạng thái ở t − z (age z) và dùng mô hình delay có thể sai?

Output: cost_twin[t, path] (cùng shape với cost_true) + age z của mỗi quyết định.
Phân biệt: simulator (sim/) = thế giới thật; twin (thư mục này) = cái nhìn của controller.
"""
