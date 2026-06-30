# ⛏ Treasure Mining AI

Game mô phỏng các thuật toán Trí tuệ nhân tạo (AI) thông qua việc điều khiển nhân vật **Steve** đào đường đi tới **viên kim cương** trong môi trường lưới ô vuông (kiểu Minecraft). Game gồm **6 Level**, mỗi Level tương ứng với một **nhóm thuật toán tìm kiếm** khác nhau trong AI.

## 📋 Yêu cầu hệ thống

- Python 3.x
- Thư viện: `tkinter` (thường có sẵn trong Python), `Pillow`

Cài đặt thư viện còn thiếu (nếu cần):

```bash
pip install pillow
```

## 🚀 Cách chạy game

Mở terminal tại thư mục gốc của project (`my_game`) và chạy:

```bash
python main.py
```

Cửa sổ Menu chính sẽ hiện ra với 6 nút chọn Level tương ứng 6 nhóm thuật toán.

## 🎮 Cách chơi chung

Mỗi Level đều có giao diện gồm:

- **Bản đồ (bên trái):** lưới ô vuông gồm các loại địa hình — cỏ, đất, đá, dung nham, đá tảng (vật cản), Steve (điểm xuất phát), kim cương (đích đến).
- **Bảng điều khiển AI (bên phải):**
  - **Chọn thuật toán:** menu thả xuống để chọn thuật toán AI muốn xem hoạt động.
  - **Nút "Run AI":** cho AI tự động tìm đường và mô phỏng Steve di chuyển tới kim cương theo thuật toán đã chọn.
  - **Nút "Reset":** đưa Steve về vị trí ban đầu, xóa kết quả mô phỏng để chạy lại.
  - **Nút "Back To Menu":** quay lại Menu chính để chọn Level khác.
  - **Bảng "Statistics":** hiển thị kết quả sau khi AI chạy xong — số node đã mở rộng (Expanded), tổng chi phí đường đi (Total Cost) và thời gian thực thi.

👉 Cách chơi cơ bản ở mọi Level: **chọn thuật toán → bấm "Run AI" → quan sát Steve di chuyển và đọc số liệu thống kê → bấm "Reset" nếu muốn thử thuật toán khác.**

## 🗺️ Chi tiết từng Level

### Level 1 — Uninformed Search (Tìm kiếm không có thông tin)
**Thuật toán:** BFS, DFS, IDS
Steve không biết gì về vị trí kim cương, chỉ dò đường theo chiến lược duyệt mù (theo chiều rộng/chiều sâu). Hãy thử cả 3 thuật toán để so sánh độ dài đường đi và số node phải xét.

### Level 2 — Informed Search (Tìm kiếm có thông tin)
**Thuật toán:** Greedy Best-First, A*, IDA*
Steve sử dụng hàm heuristic (khoảng cách Manhattan tới kim cương) để định hướng tìm kiếm thông minh hơn, tránh dò mù toàn bản đồ. Bản đồ có nhiều loại địa hình với chi phí di chuyển khác nhau (đất, đá nặng hơn cỏ).

### Level 3 — Local Search (Tìm kiếm cục bộ)
**Thuật toán:** Hill Climbing, Simulated Annealing, Local Beam Search
Steve di chuyển dựa trên việc liên tục cải thiện vị trí hiện tại thay vì duyệt toàn bộ không gian trạng thái. Một số thuật toán (Hill Climbing) có thể bị "kẹt" giữa đường nếu gặp địa hình bất lợi — hãy thử Simulated Annealing để xem cách thoát kẹt.

### Level 4 — Complex Problems / Partial Observability (Môi trường không xác định / quan sát một phần)
**3 chế độ:** Mode 1 (Belief-state — không biết vị trí xuất phát chính xác), AND-OR Search (không biết đích, hành động không chắc kết quả), Mode 3 (quan sát cục bộ — bản đồ bị sương mù che, chỉ thấy phần đã khám phá xung quanh Steve).
Đây là Level khó nhất vì Steve phải suy luận và lập kế hoạch khi thông tin về môi trường bị thiếu hoặc không chắc chắn.

### Level 5 — CSP (Constraint Satisfaction Problem — Bài toán thỏa ràng buộc)
**Thuật toán:** Backtracking, Backtracking + AC-3, Min-Conflicts
Đường đi của Steve được mô hình hóa thành bài toán gán giá trị cho các biến (vị trí từng bước) sao cho thỏa các ràng buộc (liền kề, không đi vào vật cản, đúng số bước...).

### Level 6 — Adversarial Search (Tìm kiếm đối kháng)
**Thuật toán:** Minimax, Alpha-Beta Pruning, Expectimax
Xuất hiện **Zombie** — đối thủ chủ động truy đuổi Steve. Steve phải vừa tìm đường tới kim cương vừa né tránh Zombie. Đây là Level duy nhất có yếu tố đối kháng hai phía.

## 💡 Mẹo khi trải nghiệm

- Hãy thử **chạy lại cùng một thuật toán trên cùng bản đồ nhiều lần** ở Level 3 (Simulated Annealing) và Level 6 (Expectimax) để thấy rõ yếu tố ngẫu nhiên ảnh hưởng tới kết quả.
- So sánh **bảng Statistics** giữa các thuật toán trong cùng Level để thấy sự đánh đổi giữa tốc độ, bộ nhớ và chất lượng đường đi.
- Ở Level 4, hãy thử cả 3 mode để cảm nhận rõ sự khác biệt giữa "không biết điểm xuất phát", "không biết đích" và "bị giới hạn tầm nhìn".

## 📁 Cấu trúc thư mục chính

```
my_game/
├── main.py                  # Điểm khởi chạy game
├── game/                    # Giao diện 6 level + menu + renderer
├── algorithms/               # Cài đặt các nhóm thuật toán AI
│   ├── uninformed/           # BFS, DFS, IDS
│   ├── informed/             # Greedy, A*, IDA*
│   ├── local/                 # Hill Climbing, Simulated Annealing, Beam Search
│   ├── csp/                   # Backtracking, AC-3, Min-Conflicts
│   ├── complex/                # Partial Observability (Belief-state, AND-OR, Fog)
│   └── adversarial/            # Minimax, Alpha-Beta, Expectimax
└── assets/images/             # Hình ảnh: địa hình, nhân vật, zombie, kim cương...
```
