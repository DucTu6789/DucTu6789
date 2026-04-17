from flask import Flask, render_template, request, make_response, redirect

app = Flask(__name__)
app.secret_key = "super_secret_key_for_flask_sessions"

# Middleware để set fake cookie cho tất cả response (dùng để test XSS lấy cookie)
@app.after_request
def add_fake_cookie(response):
    response.set_cookie('admin_session', 'token_xyz_987654321_secret_admin_cookie')
    return response

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # Trả về query trực tiếp cho template. XSS sẽ được trigger ở phía Jinja2 template.
    return render_template('search.html', query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Giả lập logic login luôn sai để hiển thị thông báo lỗi chứa username
        if username == 'admin' and password == '123456':
             return redirect('/') # Tạm thời giả lập thành công
        
        # Trả về username trực tiếp. XSS trigger trên template.
        return render_template('login.html', error_user=username)
        
    return render_template('login.html')

@app.route('/redirect', methods=['GET'])
def redirect_page():
    url = request.args.get('url', '')
    # Trả về URL. XSS trigger trên template.
    return render_template('redirect.html', url=url)

if __name__ == '__main__':
    # Chạy trên port 5000, bật debug để dễ dàng theo dõi
    app.run(host='0.0.0.0', port=5000, debug=True)
