# CTF Writeup: Command Injection via MD5 Endpoint

## 1. Giai đoạn dò tìm (Reconnaissance)

Sau khi truy cập vào thử thách, mình tiến hành kiểm tra toàn bộ các chức năng hiện có trên trang web.

<img width="693" height="587" alt="image" src="https://github.com/user-attachments/assets/2e9dec9f-a2e6-4035-bce9-f3acb9626f61" />
<img width="691" height="315" alt="image" src="https://github.com/user-attachments/assets/cbfde90e-e5bd-4cb5-9867-ce126f73f5c7" />
<img width="691" height="316" alt="image" src="https://github.com/user-attachments/assets/b7206e3e-9fda-46af-a0e0-64a76c2c434e" />

Sau khi xem xét, cờ (flag) có thể bị ẩn ở 1 trong 3 chức năng này. Tuy nhiên, tính năng khả nghi nhất chính là phần **Network** (Ping hệ thống). 

---

## 2. Phân tích lỗ hổng (Vulnerability Analysis)

Khi quan sát URL của chức năng này, mình nhận thấy một endpoint có cấu trúc khá đặc biệt: `/_sys_/c4ca4238a0b923820dcc509a6f75849b`.

Tiến hành crack chuỗi MD5 `c4ca4238a0b923820dcc509a6f75849b`, kết quả thu được đây chính là mã băm của giá trị `1`.

<img width="690" height="333" alt="image" src="https://github.com/user-attachments/assets/da473f9f-5a09-4eae-978a-8d728e7aef98" />

Để kiểm tra xem server có xử lý logic dựa trên tham số băm này không, mình thử thay thế nó bằng chuỗi MD5 của `0` (là `cfcd208495d565ef66e7dff9f98764da`). 

Kết quả thu được: Server trả về kết quả của lệnh ping. Điều này chứng tỏ chúng ta có thể tương tác với hệ thống thông qua tham số này.

<img width="691" height="316" alt="image" src="https://github.com/user-attachments/assets/328eb013-ae97-41ee-9283-fa9415204703" />

---

## 3. Khai thác (Exploitation)

Vì ứng dụng gọi lệnh `ping` ở bên dưới hệ điều hành (OS), đây là mục tiêu hoàn hảo cho lỗ hổng **Command Injection** (Tiêm lệnh hệ thống).

Mình sử dụng **Burp Suite** để bắt và chỉnh sửa request HTTP. Thay vì truyền giá trị IP/Domain thông thường, mình chèn thêm các ký tự đặc biệt (như `|` hoặc `;`) để nối lệnh. Bắt đầu với lệnh `ls` để liệt kê các thư mục hiện tại:

<img width="692" height="587" alt="image" src="https://github.com/user-attachments/assets/dc164d8b-ca28-4ccd-8b21-89e28611685f" />

Thành công! Trong danh sách trả về, mình phát hiện ra một file có tên rất khả nghi chứa nội dung của cờ.

---

## 4. Kết quả (Results)

Tiếp tục thay đổi payload trong Burp Suite, sử dụng lệnh `cat` để đọc nội dung file flag vừa tìm thấy.

<img width="692" height="582" alt="image" src="https://github.com/user-attachments/assets/3eac9a74-5d89-4ea3-b8fe-07fab0ad0291" />

Kết quả cờ đã hiện ra trên màn hình phản hồi.

**🚩 Flag:** `RS{1_br0k3_17_e6ebced80740d006889f26ceeeee666b}`
