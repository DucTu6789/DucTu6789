from flask import Flask, request, redirect, url_for, render_template_string
from markupsafe import escape
import datetime

app = Flask(__name__)

# Mock data
comments = [
    {
        "name": "Bảo mật hệ thống",
        "message": "Chào mừng bạn đến với cổng phản hồi người dùng của Nexus. Vui lòng để lại ý kiến đóng góp của bạn tại đây.",
        "time": "10:00 - 08/04/2026"
    }
]

@app.route('/', methods=['GET', 'POST'])
def index():
    global comments

    if request.method == 'POST':
        raw_name = request.form.get('name', 'Anonymous')
        raw_message = request.form.get('message', '')

        # 🔒 Chống XSS (Escape HTML) - SSTI vẫn hoạt động vì render_template_string chạy sau
        safe_name = escape(raw_name)
        safe_message = escape(raw_message)

        current_time = datetime.datetime.now().strftime("%H:%M - %d/%m/%Y")

        comments.append({
            "name": safe_name,
            "message": safe_message,
            "time": current_time
        })

        return redirect(url_for('index'))

    # Đọc template từ file
    try:
        with open('templates/index.html', encoding='utf-8') as f:
            base_template = f.read()
    except FileNotFoundError:
        return "Error: templates/index.html not found!"

    # 🛠️ Build comments HTML (⚠️ Trọng tâm lỗ hổng SSTI)
    # Chúng ta đưa input của người dùng trực tiếp vào chuỗi sẽ được render bởi Jinja2
    comments_html = ""
    for c in comments:
        comments_html += f"""
        <div class="comment-card p-3 mb-3 shadow-sm">
            <div class="d-flex align-items-center mb-2">
                <img class="avatar me-3" src="https://ui-avatars.com/api/?name={c['name']}&background=6366f1&color=fff" />
                <div>
                    <h6 class="fw-bold m-0 text-dark">{c['name']}</h6>
                    <small class="text-muted" style="font-size: 0.75rem;">{c['time']}</small>
                </div>
            </div>
            <div class="comment-content">
                <p class="m-0">{c['message']}</p>
            </div>
        </div>
        """

    # Thay thế placeholder trong file HTML bằng khối HTML vừa build
    final_template = base_template.replace("{{ comments_list }}", comments_html)

    # ⚠️ SSTI xảy ra tại đây vì Jinja2 sẽ parse toàn bộ final_template, bao gồm cả user input
    return render_template_string(final_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
