#  CTF Writeup: Path Traversal to Bypass Admin Authentication

##  1. Giai đoạn dò tìm (Reconnaissance)

Bước đầu tiên, mình tiến hành rà soát các endpoint nhạy cảm của ứng dụng. Sử dụng công cụ `dirsearch` (hoặc `ffuf`), mình phát hiện ra một đường dẫn đáng chú ý: `/browse`.

![image](https://github.com/user-attachments/assets/636451b0-c49b-4765-9165-e2503e216832)

Sau khi truy cập vào `/browse`, giao diện liệt kê danh sách các thư mục người dùng. Trong đó, thư mục **admin/** xuất hiện — đây chắc chắn là nơi cất giấu Flag.

![image](https://github.com/user-attachments/assets/b098d5ec-e2ba-4e48-8da6-b1f7532d6cbc)

Tiếp tục đi sâu vào thư mục này, mình thấy sự hiện diện của file `e017...-flag.gif`. Tuy nhiên, khi nhấn vào để xem nội dung, hệ thống yêu cầu xác thực **Username** và **Password** của Admin. 

![image](https://github.com/user-attachments/assets/7984a449-d8b6-45d3-9f6e-1c94ca0d986e)

Với mindset của một attacker, thay vì tốn thời gian tìm mật khẩu admin, mình sẽ tìm cách **Bypass** (vượt qua) lớp bảo vệ này.

![image](https://github.com/user-attachments/assets/15b24ee4-9b1a-48b3-a7c5-0ccff157fac6)

---

##  2. Phân tích lỗ hổng (Vulnerability Analysis)

Mình thử upload một file ảnh lên để quan sát cách server xử lý đường dẫn. 

![image](https://github.com/user-attachments/assets/7756c52a-3c86-4657-94d3-11874d1e7a55)

Dựa trên cấu trúc URL, có vẻ như Backend đang nối chuỗi theo dạng:  
`./browse/[user_id]/[view_parameter]`

**Lỗ hổng chí mạng:** Hệ thống không thực hiện lọc (filter) các ký tự điều hướng thư mục như `../`. Điều này cho phép mình thực hiện kỹ thuật **Path Traversal**.

---

##  3. Khai thác (Exploitation)

**Ý tưởng:** Mình sẽ lùi ra ngoài thư mục cá nhân hiện tại để đứng ở đường dẫn `/browse/`, sau đó "rẽ" vào thư mục của Admin.

**Payload:** `../admin/e017...-flag`

**Cơ chế thực thi:** Khi Backend ghép chuỗi, nó sẽ tạo ra đường dẫn:  
`/var/www/html/browse/9abc63e2.../../admin/e017...-flag`

Lúc này, hệ điều hành sẽ tự động rút gọn đoạn `9abc63e2.../../`, biến nó thành đường dẫn trực tiếp trỏ đến thư mục Admin. Vì đây là thao tác đọc file nội bộ của server, nó sẽ bỏ qua (bypass) hoàn toàn lớp xác thực tài khoản trên trình duyệt.

![image](https://github.com/user-attachments/assets/e10abdb8-285d-40a1-8127-fca7ce12c59d)

**Kết quả:** Yêu cầu thành công, file GIF chứa Flag hiện ra ngay trên màn hình, nhưng nên chỉnh speed chậm lại để quan sát cờ dễ hơn.

![image](https://github.com/user-attachments/assets/86a154eb-32d2-49ad-9e29-0462db38c84a)

** Flag thu được:** `gigem{3z_t0h0u_fl4g_r1t3}`

---
