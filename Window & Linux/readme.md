#  Triển khai DNS trên Linux và Tích hợp với Active Directory

##  Mục tiêu bài Lab
Triển khai hệ thống mạng kết hợp giữa Windows Server và Ubuntu Linux, tập trung vào:
1. Cấu hình **DNS BIND9** trên Ubuntu làm DNS Server chính.
2. Tích hợp DNS Linux với **Active Directory (AD)** trên Windows Server 2022.
3. Cấu hình **DHCP Server** trên Windows Server để cấp phát IP động và trỏ DNS về Ubuntu.
4. Kiểm tra phân giải tên miền và truy cập dịch vụ web (IIS) qua tên miền nội bộ.

---

##  Mô hình triển khai
| Thành phần | Hệ điều hành | Địa chỉ IP | Vai trò |
| :--- | :--- | :--- | :--- |
| **Ubuntu Server** | Ubuntu 22.04 | `192.168.19.20` | DNS Server (BIND9) |
| **Windows Server** | Windows Server 2022 | `192.168.19.10` | AD DC, DHCP Server |
| **Windows Client** | Windows 10 | DHCP (Dynamic) | Máy trạm kiểm thử |

---

##  Các bước thực hiện chính

### 1. Cấu hình Ubuntu DNS (BIND9)
- Thiết lập IP tĩnh bằng `netplan`.
- Cấu hình file `named.conf.options` để cho phép truy vấn và forwarder.
- Tạo các Zone thuận (`nhom19.local`) và Zone nghịch để phân giải tên miền.



### 2. Tích hợp Active Directory
- Cấu hình Windows Server gia nhập và quản lý domain `nhom19.local`.
- Thực hiện cập nhật bản ghi SRV từ AD lên BIND9 để đảm bảo các dịch vụ của Windows (LDAP, Kerberos) hoạt động bình thường.

### 3. Cấu hình DHCP Server
- Tạo Scope cấp phát IP từ `192.168.19.25` đến `192.168.19.100`.
- Thiết lập Option 006 (DNS Server) trỏ về IP của máy Ubuntu (`192.168.19.20`).

---

##  Kết quả nghiệm thu
1. **Phân giải tên miền:** Lệnh `nslookup` trên Client trả về đúng IP của máy chủ.
2. **Bản ghi SRV:** Kiểm tra `_ldap._tcp.nhom19.local` thành công, chứng tỏ AD đã đăng ký dịch vụ lên BIND9.
3. **Truy cập Web:** Client truy cập thành công trang mặc định của IIS thông qua địa chỉ `http://hcserver01.nhom19.local`.

---
