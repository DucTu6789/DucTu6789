# HƯỚNG DẪN TRIỂN KHAI DNS TRÊN LINUX VÀ TÍCH HỢP ACTIVE DIRECTORY

Báo cáo chi tiết các bước triển khai hệ thống phân giải tên miền (DNS BIND9) trên Ubuntu Server, kết hợp cấu hình DHCP và gia nhập Domain thông qua Active Directory trên Windows Server.

---

##  PHẦN I: CẤU HÌNH DNS TRÊN UBUNTU SERVER

### 1. Cấu hình IP tĩnh bằng netplan
Mở file cấu hình netplan để đặt IP tĩnh `192.168.19.20/24`, gateway `192.168.19.1` và DNS `127.0.0.1` cho card mạng.

```bash
sudo nano /etc/netplan/00-installer-config.yaml
```

![image](https://github.com/user-attachments/assets/5a8a1a22-3b2a-474a-ac80-dfecc80836b0)

### 2. Kiểm tra bảng định tuyến (Routing Table)
Xem máy đang đi ra ngoài bằng gateway nào và các mạng nội bộ được gắn với interface nào.

- `default`: Tuyến mặc định – mọi gói tin đi ra ngoài mạng `192.168.19.0/24` sẽ đi theo đường này.
- `via 192.168.19.1`: Địa chỉ gateway (thường là router hoặc “cửa ra” mạng).
- `dev ens33`: Đi qua card mạng `ens33`.
- `proto static`: Tuyến này được cấu hình tĩnh (do đã set trong netplan), không phải do DHCP tự cấp.

![image](https://github.com/user-attachments/assets/12c22f8f-da49-48f6-8f9e-d65c44163d22)

### 3. Cấu hình file `/etc/bind/named.conf.options`
DNS server bật recursion và cho phép mọi client gửi truy vấn. Khi gặp các tên miền ngoài nội bộ, BIND9 sẽ forward truy vấn ra internet qua các DNS công cộng `8.8.8.8` và `1.1.1.1`.

- `directory "/var/cache/bind";`: Thư mục BIND dùng để lưu cache và file runtime.
- `recursion yes;`: Cho phép truy vấn đệ quy (hỏi thay client nếu không biết).
- `allow-query { any; };`: Cho phép mọi IP được gửi truy vấn DNS đến server.
- `forwarders { 8.8.8.8; 1.1.1.1; };`: Chuyển tiếp câu hỏi lên DNS của Google và Cloudflare nếu tên miền không thuộc zone nội bộ.
- `dnssec-validation no;`: Tắt kiểm tra DNSSEC để tránh lỗi khi forward trong môi trường lab.
- `listen-on-v6 { any; };`: Cho phép BIND lắng nghe trên mọi địa chỉ IPv6.

![image](https://github.com/user-attachments/assets/2bf27579-cf0b-43ab-b2d3-4b9246684088)

### 4. Cấu hình file `/etc/bind/named.conf.local`
Khai báo hai zone `nhom19.local` (forward) và `19.168.192.in-addr.arpa` (reverse), với Ubuntu đóng vai trò DNS master.

- `type master;`: Ubuntu là DNS chủ (Primary) cho zone.
- `file "/etc/bind/db.nhom19.local";`: File chứa các bản ghi chi tiết.
- `allow-update { 192.168.19.10; };`: Cho phép Domain Controller (192.168.19.10) gửi dynamic update để tự động đăng ký các bản ghi dịch vụ (SRV), A, PTR.

![image](https://github.com/user-attachments/assets/6fed0cec-77d0-439c-957c-4bbbf7e204f0)

### 5. File zone forward `db.nhom19.local`
Bản ghi SOA và NS xác định `ubuntu19` là DNS server chính. Các bản ghi A ánh xạ tên máy tới IP tương ứng. Các bản ghi SRV giúp client tìm DC và join domain thành công.

- `$TTL 86400`: Thời gian cache mặc định (1 ngày).
- `SOA`: Khai báo DNS server chính và email quản trị.
- `NS`: Khai báo nameserver phục vụ domain.
- **A records:** Ánh xạ tên ra IP (VD: `ubuntu19` -> `192.168.19.20`).
- **SRV records:** Báo cho client biết dịch vụ LDAP (cổng `389/TCP`) và Kerberos (cổng `88/TCP`) đang chạy trên máy DC `hcserver01`.

![image](https://github.com/user-attachments/assets/2b7fc49f-ca56-4fa8-ad45-2e41b5d3d3fe)

### 6. Cấu hình DNS Resolver trên Ubuntu (`/etc/resolv.conf`)
Cấu hình cho hệ thống sử dụng chính BIND9 chạy trên localhost làm DNS resolver. 

- `nameserver 127.0.0.1`: Báo hệ thống gửi truy vấn DNS đến chính máy localhost.
- `search nhom19.local local`: Tự động bổ sung hậu tố domain khi phân giải tên, giúp truy cập nhanh bằng short name.

![image](https://github.com/user-attachments/assets/b17db747-5432-4479-83ff-ffe3791232ea)

### 7. Kiểm tra cấu hình và khởi động lại dịch vụ
Kiểm tra cú pháp file cấu hình, kết quả `OK` cho thấy zone hợp lệ.

![image](https://github.com/user-attachments/assets/a6a39588-fec2-4bc6-a940-aa594715a87a)

Restart dịch vụ BIND9 và kiểm tra trạng thái (`systemctl status bind9`). Trạng thái `active (running)` và log báo `all zones loaded` xác nhận DNS server đã nạp đầy đủ.

![image](https://github.com/user-attachments/assets/f012ebdc-ecae-4b08-b4d4-4557278457bd)

Dùng lệnh `dig nhom19.local` để kiểm tra thực tế. BIND9 trả về đúng IP `192.168.19.10` của Domain Controller.

![image](https://github.com/user-attachments/assets/727c0fa2-41d0-4d80-965c-e42373c6a799)

---

##  PHẦN II: DHCP VÀ ACTIVE DIRECTORY TRÊN WINDOWS SERVER

### 1. Cấu hình IPv4 tĩnh cho hcserver01
Gán IP `192.168.19.10/24`, gateway `192.168.19.1`. Phần DNS được trỏ duy nhất về máy Ubuntu (`192.168.19.20`).

![image](https://github.com/user-attachments/assets/37cbdff1-3da4-496b-b726-73a27ac0753c)

### 2. Cài đặt Active Directory Domain Services (AD DS)
Cài đặt role AD DS để quản lý user, group và máy tính. Sau đó tiến hành promote server thành Domain Controller.

![image](https://github.com/user-attachments/assets/4acf991b-33b5-463a-a966-2f9f18d8cfc5)

![image](https://github.com/user-attachments/assets/3773764b-ae12-4941-b779-a53e3e58a325)

Chọn **Add a new forest** và khai báo tên root domain là `nhom19.local`. HCServer01 sẽ trở thành DC đầu tiên.

![image](https://github.com/user-attachments/assets/368e88f0-09e4-46a3-b7a6-6a9877b04d1d)

Thiết lập mật khẩu khôi phục và hoàn tất quá trình khởi động lại.

![image](https://github.com/user-attachments/assets/fa9caba9-94b5-494c-924f-0751310a2dd7)
![image](https://github.com/user-attachments/assets/c17249ce-f267-4b8a-ab38-eb116ceea631)

### 3. Cài đặt DHCP Server và Web Server
Sau khi đăng nhập lại, tiến hành cài thêm role DHCP Server và Web Server (IIS).

![image](https://github.com/user-attachments/assets/207ca97b-6fbe-4ae8-a3f4-cd36cd25df35)

### 4. Kiểm tra phân giải tên miền
Sử dụng lệnh `nslookup` để kiểm tra việc phân giải tên từ Windows sang DNS BIND9 trên Ubuntu.

```cmd
nslookup ubuntu19.nhom19.local 192.168.19.20
```

![image](https://github.com/user-attachments/assets/a0ac5717-fc4a-41e9-b750-23592ecec823)

---

##  PHẦN III: WINDOWS 10 CLIENT VÀ GIA NHẬP DOMAIN

### 1. Cấu hình nhận IP động (DHCP)
Thiết lập card mạng sang chế độ "Obtain automatically" để nhận cấu hình mạng từ DHCP Server.

![image](https://github.com/user-attachments/assets/c7d83d3c-49c8-4f81-96c2-eaf7e24b4541)

### 2. Kiểm tra IP nhận được
Mở Command Prompt và kiểm tra thông số mạng:
```cmd
ipconfig /all
```
> Máy trạm nhận IP động `192.168.19.25` từ DHCP Server `192.168.19.10`, và trỏ DNS về Ubuntu `192.168.19.20`.

![image](https://github.com/user-attachments/assets/d800befc-ccbe-43b4-929e-de9b3436f968)

### 3. Kiểm tra bản ghi dịch vụ SRV
Kiểm tra xem Active Directory đã đăng ký dịch vụ LDAP lên BIND9 thành công hay chưa:
```cmd
nslookup -type=SRV _ldap._tcp.nhom19.local
```
> Kết quả trả về trỏ tới `hcserver01.nhom19.local`, chứng tỏ AD đã đăng ký bản ghi thành công.

![image](https://github.com/user-attachments/assets/2b00b14f-23aa-4453-a8dd-afd3099ff892)

### 4. Kiểm tra truy cập Web Server (IIS)
Truy cập vào URL `http://hcserver01.nhom19.local`. Trang mặc định của IIS hiển thị thành công, xác nhận BIND9 đã phân giải đúng tên máy chủ web.

![image](https://github.com/user-attachments/assets/b87337ef-15bd-4c3e-b6e4-51d9c1cdc9e2)

### 5. Gia nhập Domain (Join Domain)
Mở System Properties, chuyển máy từ Workgroup sang domain `nhom19.local`. Sử dụng tài khoản có quyền admin (VD: `NHOM19\Administrator`) để xác thực.

![image](https://github.com/user-attachments/assets/e8639bb6-a84b-40bd-aa44-1696554e201e)

Thông báo **"Welcome to the nhom19.local domain"** xác nhận máy trạm đã join thành công. Lúc này có thể đăng nhập bằng tài khoản domain để sử dụng.

![image](https://github.com/user-attachments/assets/3cde9cf8-09ce-4525-bd30-c182eb3dca24)

---
