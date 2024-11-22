import json
from flask import Flask, render_template, request, redirect, url_for, flash

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình khóa bí mật để sử dụng với Flask session (để lưu thông báo lỗi hoặc thành công)
app.secret_key = 'your_secret_key'

# Đọc dữ liệu từ file JSON
def load_users():
    with open('users.json', 'r') as file:
        data = json.load(file)
    return data['users']

# Lưu dữ liệu vào file JSON
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump({"users": users}, file, indent=4)

# Trang đổi mật khẩu
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Kiểm tra người dùng trong file JSON
        users = load_users()
        user_found = False

        for user in users:
            if user['username'] == username and user['password'] == old_password:
                user_found = True
                # Kiểm tra mật khẩu mới và xác nhận mật khẩu có giống nhau không
                if new_password == confirm_password:
                    # Cập nhật mật khẩu mới
                    user['password'] = new_password
                    save_users(users)  # Lưu lại dữ liệu
                    flash('Password changed successfully!', 'success')
                else:
                    flash('New password and confirm password do not match!', 'danger')
                break
        
        if not user_found:
            flash('Incorrect username or old password!', 'danger')

        return redirect(url_for('change_password'))
    
    # Render trang HTML với form
    return render_template('change_password.html')

# Trang chủ
@app.route('/')
def home():
    return "Welcome to the password change example. Go to /change-password to change your password."

if __name__ == '__main__':
    app.run(debug=True)
