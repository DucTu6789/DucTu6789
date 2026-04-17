# CTF Writeup

## 1. Phân tích mã nguồn (Source Code Analysis)

Dựa vào đoạn code được cung cấp từ đề bài, dễ dàng quan sát thấy hàm xử lý tìm kiếm có vấn đề nghiêm trọng:

```go
func searchHandler(w http.ResponseWriter, r *http.Request) {
	q := r.URL.Query().Get("q")
	var recipes []Recipe
	db.Where("title LIKE '%" + q + "%'").Find(&recipes)
	searchTmpl.Execute(w, recipes)
}
```

**Lỗ hổng:** Lập trình viên đã dùng phép cộng chuỗi `+ q +` để ghép trực tiếp input của người dùng vào câu lệnh SQL. Vì input không được xử lý (escape), bất cứ ký tự đặc biệt nào bạn nhập vào (như dấu nháy đơn `'`) đều sẽ được Database hiểu là một phần của câu lệnh SQL chứ không phải là dữ liệu văn bản bình thường. Đây chính là lỗ hổng **SQL Injection**.

Đáng lẽ ra, họ phải dùng **Tham số hóa (Parameterized Query)** như thế này thì mới an toàn:
```go
db.Where("title LIKE ?", "%"+q+"%").Find(&recipes)
```

---

## 2. Khai thác (Exploitation)

Dựa vào lỗ hổng trên, chúng ta có thể dễ dàng thao túng truy vấn bằng cách truyền vào một payload đặc biệt. 

**Payload:** ```text
%' OR 1=1
```

**Cơ chế thực thi:** Khi nhập payload này vào ô tìm kiếm, Backend (BE) sẽ tiến hành ghép chuỗi. Câu lệnh SQL thực tế được thực thi dưới Database sẽ trở thành dạng như sau:

```sql
SELECT * FROM recipes WHERE recipes.deleted_at IS NULL AND (title LIKE '%%') OR 1=1 -- %')
```

Biểu thức `OR 1=1` là một mệnh đề luôn luôn đúng (True). Nhờ đó, câu lệnh này sẽ bỏ qua điều kiện lọc theo tiêu đề (`title LIKE...`) và lập tức trả về toàn bộ dữ liệu có trong bảng `recipes`.

---

## 3. Kết quả (Results)

Sau khi gửi payload, toàn bộ danh sách công thức bị rò rỉ, trong đó chứa luôn cả Flag mà chúng ta cần tìm.

<img width="1717" height="881" alt="image" src="https://github.com/user-attachments/assets/75db8e52-b01b-4b93-adbc-cbf6ae0772a8" />

**🚩 Flag:** `CPCTF{k!MChI_FR!ed_RiC3_w1th_MaY0nnA1s3}`
