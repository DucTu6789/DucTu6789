# CTF Writeup: Privilege Escalation via Mass Assignment

## 1. Phân tích mã nguồn (Recon)

Dựa trên mã nguồn Python (Flask) được cung cấp, chúng ta tập trung vào điểm yếu trong cách xử lý dữ liệu tại các endpoint `/api/register` và `/api/profile`.

* **Lỗ hổng:** Mass Assignment (Gán dữ liệu hàng loạt).

**Đoạn code lỗi:**
```python
record = {
    'username': username,
    'password': password,
    'role': 'standard',
    'full_name': full_name,
    'title': title,
    'team': team
}
record.update(incoming) # Vấn đề chí mạng nằm ở đây
```

**Nguyên nhân:** Hàm `record.update(incoming)` sẽ lấy toàn bộ dữ liệu từ JSON body mà người dùng gửi lên để ghi đè trực tiếp vào dictionary `record`. Nếu người dùng cố tình gửi kèm trường `"role": "admin"`, giá trị mặc định `"standard"` ban đầu sẽ bị ghi đè.

**Điều kiện lấy Flag:** Cần truy cập được route `/admin`. Tuy nhiên, route này yêu cầu session của người dùng phải có `role == 'admin'`.

---

## 2. Các bước khai thác (Exploitation)

### Bước 1: Vượt qua Password Policy
Server có hàm kiểm tra mật khẩu (`valid_password`). Nếu chỉ gửi mật khẩu đơn giản (ví dụ: `123`), server sẽ trả về lỗi `400 Bad Request`.
* **Yêu cầu:** Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt.
* **Mật khẩu hợp lệ sử dụng:** `Password123!`

### Bước 2: Đăng ký tài khoản với quyền Admin
Sử dụng công cụ **Burp Suite (Repeater)** để can thiệp và gửi request `POST` tới endpoint `/api/register`. Chúng ta sẽ chèn thêm trường `role` vào JSON Payload.

**Payload:**
```json
{
  "full_name": "tu ngo",
  "username": "ngo",
  "title": "abc",
  "team": "as",
  "password": "Password123!",
  "role": "admin" 
}
```

### Bước 3: Đăng nhập và kiểm tra
Sau khi gửi payload đăng ký thành công, thực hiện đăng nhập tại trang `/login` với thông tin vừa tạo:
* **Username:** `ngo`
* **Password:** `Password123!`

Kiểm tra tại trang `/dashboard`, chúng ta sẽ thấy phần Role đã được nâng cấp thành `admin` thành công.

<img width="1725" height="884" alt="image" src="https://github.com/user-attachments/assets/24a79de6-929e-4ae0-b7f0-4e2d5da1e8d7" />

### Bước 4: Lấy Flag
Vì Session hiện tại đã có quyền Admin hợp lệ, chúng ta chỉ cần truy cập trực tiếp vào đường dẫn quản trị: 
`http://23.179.17.92:5556/admin`

Kết quả: Hệ thống chấp nhận yêu cầu và Flag sẽ hiển thị ngay trên giao diện trang Admin.

**🚩 Flag:** `CIT{M@ss_@ssignm3nt_Pr1v3sc}`
