import io
from flask import url_for, render_template, redirect, request, flash, make_response, session, jsonify
from BusApp.app.main import login_blueprint
from BusApp.app.datve import datve_blueprints
import sqlite3
import os
import json
from BusApp.app import dao
from BusApp.app import app, db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from sqlalchemy.sql import text

app.register_blueprint(datve_blueprints)
app.register_blueprint(login_blueprint)

@app.route('/thanhtoan')
def thanh_toan():
    return render_template("thanhtoan.html")

name = ''
@app.route('/')
def trang_chu():
    with sqlite3.connect('data/database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM provinces ")
        provinces = c.fetchall()
    conn.close()
    return render_template("home.html", provinces=provinces)

@app.route('/ThongKe')
def thongKe_admin():
    with db.session() as session:
        # Biểu đồ tròn - Trạng thái hóa đơn
        trang_thai_data = session.execute(text("""
               SELECT TrangThaiHoaDon.tenTrangThai, COUNT(*) as soLuong
               FROM HoaDon
               JOIN TrangThaiHoaDon ON HoaDon.trangThai = TrangThaiHoaDon.idTrangThai
               GROUP BY TrangThaiHoaDon.tenTrangThai;
           """)).fetchall()

        # Biểu đồ cột 1 - Doanh thu theo tháng
        doanh_thu_data = session.execute(text("""
               SELECT strftime('%Y-%m', ngayLap) as thang, SUM(tongTien) as doanhThu
               FROM HoaDon
               GROUP BY thang
               ORDER BY thang;
           """)).fetchall()


        # Định dạng lại dữ liệu thành JSON để truyền qua template
    trang_thai_chart = {
        "labels": [row[0] for row in trang_thai_data],
        "data": [row[1] for row in trang_thai_data],
    }
    doanh_thu_chart = {
        "labels": [row[0] for row in doanh_thu_data],
        "data": [row[1] for row in doanh_thu_data],
    }
    return render_template('thongke.html',
                           trang_thai_chart=trang_thai_chart,
                           doanh_thu_chart=doanh_thu_chart)

@app.route('/HoaDon')
def hoaDon_admin():
    kw = request.args.get('kw')
    hd = dao.load_hoaDon(kw=kw)
    total = dao.total_hoaDon()
    return render_template("hoaDon.html", HoaDon=hd, sum=total)

@app.route('/xoa_HoaDon/<int:idHoaDon>', methods=['DELETE'])
def delete_receipt(idHoaDon):
    try:
        # Giả sử bạn có một hàm để kết nối và xóa dữ liệu từ database
        dao.delete_receipt_from_db(idHoaDon)  # X óa nhan vien theo ID
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500

@app.route('/ChuyenXe')
def chuyenXe_admin():
    tinhs = dao.load_tinh()
    cx = dao.load_ChuyenXe()
    total = dao.total_ChuyenXe()
    return render_template("chuyenXe.html", chuyenXe=cx, sum=total, tinhs=tinhs)

@app.route('/ChuyenXe/<int:chuyen_xe_id>')
def chi_tiet_chuyen_xe(chuyen_xe_id):
    # Lấy thông tin chuyến xe
    chuyen_xe = dao.chiTietChuyenXe(chuyen_xe_id)
    danh_sach_ghe = dao.load_Ghe(chuyen_xe)

    return render_template(
        'chiTietChuyenXe.html',
        chuyen_xe=chuyen_xe,
        danh_sach_ghe=danh_sach_ghe
    )

@app.route('/ThemChuyenXe', methods=['GET', 'POST'])
def add_trip():
    if request.method == 'POST':
        # Xử lý dữ liệu từ form
        idTuyenDuong = request.form['idTuyenDuong']
        thoiGianDi = request.form['thoiGianDi']
        thoiGianDen = request.form['thoiGianDen']
        idXe = request.form['idXe']

        # Kết nối và thêm dữ liệu vào database
        connection = sqlite3.connect('data/database.db')
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO LichTrinh (idTuyenDuong, thoiGianDi, thoiGianDen, idXe) 
            VALUES (?, ?, ?, ?)
        """, (idTuyenDuong, thoiGianDi, thoiGianDen, idXe))
        connection.commit()
        connection.close()

        # Chuyển hướng về trang chính sau khi thêm thành công
        return redirect('/HomeAdmin')

    vehicles = dao.load_TenXe()
    routes = dao.load_IDTuyenXe()
    return render_template('them_chuyenXe.html', vehicles=vehicles, routes=routes)

@app.route('/xoa_ChuyenXe/<int:idChuyenXe>', methods=['DELETE'])
def delete_trip(idChuyenXe):
    try:
        # Giả sử bạn có một hàm để kết nối và xóa dữ liệu từ database
        dao.delete_trip_from_db(idChuyenXe)  # X óa nhan vien theo ID
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500

@app.route('/chinhSua_ChuyenXe/<int:id>')
def edit_trip(id):
    conn = dao.get_db_connection()
    trip = conn.execute('SELECT * FROM LichTrinh WHERE idLichTrinh = ?', (id,)).fetchone()
    conn.close()
    routes = dao.load_IDTuyenXe()
    vehicles = dao.load_TenXe()
    if trip:
        return render_template('capNhat_ChuyenXe.html', trip=trip, routes=routes, vehicles=vehicles)
    return "Không tìm thấy tuyến đương", 404

# Route để cập nhật thông tin khách hàng
@app.route('/capNhat_ChuyenXe/<int:id>', methods=['GET', 'POST'])
def update_trip(id):
    if request.method == 'POST':
        idTuyenDuong = request.form['idTuyenDuong']
        thoiGianDi = request.form['thoiGianDi']
        thoiGianDen = request.form['thoiGianDen']
        idXe = request.form['idXe']

        conn = dao.get_db_connection()
        conn.execute('''UPDATE LichTrinh SET idTuyenDuong = ?, thoiGianDi = ?, thoiGianDen = ?, idXe = ? WHERE idLichTrinh = ?''',
                     (idTuyenDuong, thoiGianDi, thoiGianDen, idXe, id))
        conn.commit()
        conn.close()
        return redirect(url_for('home_admin'))  # Chuyển hướng về trang chủ sau khi cập nhật thành công

    return render_template('capNhat_ChuyenXe.html')

@app.route('/TuyenXe')
def tuyenXe_admin():
    tinhs = dao.load_tinh()
    tx = dao.tuyenXe_load()
    total = dao.total_tuyenXe()
    return render_template("tuyenXe.html", tuyenXe=tx, sum=total, tinhs=tinhs)

@app.route('/ThemTuyenXe', methods=['GET', 'POST'])
def add_route():
    if request.method == 'POST':
        # Xử lý dữ liệu từ form
        diemDi = request.form['diemDi']
        diemDen = request.form['diemDen']
        khoangCach = request.form['khoangCach']
        soNgayTrongTuanChay = request.form['soNgayTrongTuanChay']
        soChuyenTrongTuan = request.form['soChuyenTrongTuan']
        gia = request.form['gia']

        # Kết nối và thêm dữ liệu vào database
        connection = sqlite3.connect('data/database.db')
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO TuyenDuong (diemDi, diemDen, khoangCach, soNgayTrongTuanChay, soChuyenTrongTuan, gia) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (diemDi, diemDen, khoangCach, soNgayTrongTuanChay, soChuyenTrongTuan, gia))
        connection.commit()
        connection.close()

        # Chuyển hướng về trang chính sau khi thêm thành công
        return redirect('/HomeAdmin')

    # Nếu là GET, hiển thị trang thêm khách hàng
    stations = dao.load_benXe()
    return render_template('them_tuyenXe.html', stations=stations)

@app.route('/xoa_TuyenXe/<int:idTuyenXe>', methods=['DELETE'])
def delete_route(idTuyenXe):
    try:
        # Giả sử bạn có một hàm để kết nối và xóa dữ liệu từ database
        dao.delete_route_from_db(idTuyenXe)  # X óa nhan vien theo ID
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500

@app.route('/chinhSua_TuyenXe/<int:id>')
def edit_route(id):
    conn = dao.get_db_connection()
    route = conn.execute('SELECT * FROM TuyenDuong WHERE idTuyenDuong = ?', (id,)).fetchone()
    conn.close()
    stations = dao.load_benXe()
    if route:
        return render_template('capNhat_TuyenXe.html', route=route, stations=stations)
    return "Không tìm thấy tuyến đương", 404

# Route để cập nhật thông tin khách hàng
@app.route('/capNhat_TuyenXe/<int:id>', methods=['GET', 'POST'])
def update_route(id):
    if request.method == 'POST':
        diemDi = request.form['diemDi']
        diemDen = request.form['diemDen']
        khoangCach = request.form['khoangCach']
        soNgayTrongTuanChay = request.form['soNgayTrongTuanChay']
        soChuyenTrongTuan = request.form['soChuyenTrongTuan']
        gia = request.form['gia']

        conn = dao.get_db_connection()
        conn.execute('''UPDATE TuyenDuong SET diemDi = ?, diemDen = ?, khoangCach = ?, soNgayTrongTuanChay = ?, soChuyenTrongTuan = ?
            , gia = ? WHERE idTuyenDuong = ?''',
                     (diemDi, diemDen, khoangCach, soNgayTrongTuanChay, soChuyenTrongTuan, gia, id))
        conn.commit()
        conn.close()
        return redirect(url_for('home_admin'))  # Chuyển hướng về trang chủ sau khi cập nhật thành công

    return render_template('capNhat_TuyenXe.html')

@app.route('/Xe')
def xe_admin():
    kw = request.args.get('kw')
    x = dao.load_Xe(kw=kw)
    total = dao.total_Xe()
    return render_template("xe.html", Xe=x, sum=total)

@app.route('/ThemXe', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        # Xử lý dữ liệu từ form
        bienSo = request.form['bienSo']
        sucChua = request.form['sucChua']
        tinhTrangXe = request.form['tinhTrangXe']
        idTaiXe = request.form['idTaiXe']

        # Kết nối và thêm dữ liệu vào database
        connection = sqlite3.connect('data/database.db')
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Xe (bienSo, sucChua, tinhTrangXe, idTaiXe) 
            VALUES (?, ?, ?, ?)
        """, (bienSo, sucChua, tinhTrangXe, idTaiXe))
        connection.commit()
        connection.close()

        # Chuyển hướng về trang chính sau khi thêm thành công
        return redirect('/HomeAdmin')

    # Nếu là GET, hiển thị trang thêm khách hàng
    drivers = dao.load_taiXe()
    return render_template('them_Xe.html', drivers=drivers)

@app.route('/xoa_Xe/<int:idXe>', methods=['DELETE'])
def delete_vehicle(idXe):
    try:
        # Giả sử bạn có một hàm để kết nối và xóa dữ liệu từ database
        dao.delete_vehicle_from_db(idXe)  # X óa nhan vien theo ID
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500

@app.route('/chinhSua_Xe/<int:id>')
def edit_vehicle(id):
    conn = dao.get_db_connection()
    vehicle = conn.execute('SELECT * FROM Xe WHERE idXe = ?', (id,)).fetchone()
    conn.close()
    if vehicle:
        return render_template('capNhat_Xe.html', vehicle=vehicle)
    return "Khong tìm thấy xe", 404

# Route để cập nhật thông tin khách hàng
@app.route('/capNhat_Xe/<int:id>', methods=['POST'])
def update_vehicle(id):
    bienSo = request.form['bienSo']
    sucChua = request.form['sucChua']
    tinhTrangXe = request.form['tinhTrangXe']

    conn = dao.get_db_connection()
    conn.execute('''UPDATE Xe SET bienSo = ?, sucChua = ?, tinhTrangXe = ? WHERE idXe = ?''',
                     (bienSo, sucChua, tinhTrangXe, id))
    conn.commit()
    conn.close()
    return redirect(url_for('home_admin'))  # Chuyển hướng về trang chủ sau khi cập nhật thành công


@app.route('/HomeAdmin')
def home_admin():
    # Tổng số khách hàng
    total_customers = dao.total_customers()

    # Tổng số chuyến xe
    total_trips = dao.total_ChuyenXe()

    # Tổng doanh thu
    total_revenue = dao.total_revenue()

    # Tổng số tuyến xe
    total_routes = dao.total_tuyenXe()

    # Tổng số nhân viên
    total_employees = dao.total_employees()

    # Tổng số xe
    total_vehicles = dao.total_Xe()

    # Tổng doanh thu
    total_provinces = dao.total_provinces()

    # Tổng số tuyến xe
    total_stations = dao.total_stations()


    return render_template('homeAd_new.html',
                           total_customers=total_customers,
                           total_trips=total_trips,
                           total_revenue=total_revenue,
                           total_routes=total_routes,
                           total_employees=total_employees,
                           total_vehicles=total_vehicles,
                           total_provinces=total_provinces,
                           total_stations=total_stations,)


@app.route('/UserAdmin/NhanVien')
def user_admin_NV():
    kw = request.args.get('kw')
    em = dao.load_employees(kw=kw)
    total = dao.total_employees()
    return render_template("userAd_NV.html", employees=em, sum=total)

@app.route('/ThemNhanVien', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Xử lý dữ liệu từ form
        hoNV = request.form['hoNV']
        tenNV = request.form['tenNV']
        soDienThoai = request.form['soDienThoai']
        gioiTinh = request.form['gioiTinh']
        email = request.form['email']
        ngaySinh = request.form['ngaySinh']
        nganHang = request.form['nganHang']
        soTaiKhoan = request.form['soTaiKhoan']

        # Kết nối và thêm dữ liệu vào database
        connection = sqlite3.connect('data/database.db')
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO NhanVien (hoNV, tenNV, soDienThoai, gioiTinh, email, ngaySinh, nganHang, soTaiKhoan) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (hoNV, tenNV, soDienThoai, gioiTinh, email, ngaySinh, nganHang, soTaiKhoan))
        connection.commit()
        connection.close()

        # Chuyển hướng về trang chính sau khi thêm thành công
        return redirect('/HomeAdmin')

    # Nếu là GET, hiển thị trang thêm khách hàng
    return render_template('them_NV.html')

@app.route('/xoa_NV/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        # Giả sử bạn có một hàm để kết nối và xóa dữ liệu từ database
        dao.delete_employee_from_db(employee_id)  # Xóa nhan vien theo ID
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500

@app.route('/chinhSua_NV/<int:id>')
def edit_employee(id):
    conn = dao.get_db_connection()
    employee = conn.execute('SELECT * FROM NhanVien WHERE idNhanVien = ?', (id,)).fetchone()
    conn.close()
    if employee:
        return render_template('capNhat_NV.html', employee=employee)
    return "Không tìm thấy nhân viên", 404

# Route để cập nhật thông tin khách hàng
@app.route('/capNhat_NV/<int:id>', methods=['POST'])
def update_employee(id):
    hoNV = request.form['hoNV']
    tenNV = request.form['tenNV']
    soDienThoai = request.form['soDienThoai']
    gioiTinh = request.form['gioiTinh']
    email = request.form['email']
    ngaySinh = request.form['ngaySinh']
    nganHang = request.form['nganHang']
    soTaiKhoan = request.form['soTaiKhoan']

    conn = dao.get_db_connection()
    conn.execute('''UPDATE NhanVien SET hoNV = ?, tenNV = ?, soDienThoai = ?, gioiTinh = ?, 
                    email = ?, ngaySinh = ?, nganHang = ?, soTaiKhoan = ? WHERE idNhanVien = ?''',
                 (hoNV, tenNV, soDienThoai, gioiTinh, email, ngaySinh, nganHang, soTaiKhoan, id))
    conn.commit()
    conn.close()
    return redirect(url_for('home_admin'))  # Chuyển hướng về trang chủ sau khi cập nhật thành công

@app.route('/UserAdmin/KhachHang')
def user_admin_KH():
    kw = request.args.get('kw')
    cus = dao.load_customers(kw=kw)
    total = dao.total_customers()
    return render_template("userAd_KH.html", customers=cus, sum=total)

@app.route('/ThemKhachHang', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        # Xử lý dữ liệu từ form
        hoKhach = request.form['hoKhach']
        tenKhach = request.form['tenKhach']
        soDienThoai = request.form['soDienThoai']
        gioiTinh = request.form['gioiTinh']
        email = request.form['email']
        ngaySinh = request.form['ngaySinh']
        nganHang = request.form['nganHang']
        soTaiKhoan = request.form['soTaiKhoan']

        # Kết nối và thêm dữ liệu vào database
        connection = sqlite3.connect('data/database.db')
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO KhachHang (hoKhach, tenKhach, soDienThoai, gioiTinh, email, ngaySinh, nganHang, soTaiKhoan) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (hoKhach, tenKhach, soDienThoai, gioiTinh, email, ngaySinh, nganHang, soTaiKhoan))
        connection.commit()
        connection.close()

        # Chuyển hướng về trang chính sau khi thêm thành công
        return redirect('/HomeAdmin')

    # Nếu là GET, hiển thị trang thêm khách hàng
    return render_template('them_KH.html')

@app.route('/xoa_KH/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        # Giả sử bạn có một hàm để kết nối và xóa dữ liệu từ database
        dao.delete_customer_from_db(customer_id)  # X óa khách hàng theo ID
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500


# Route để hiển thị trang chỉnh sửa
@app.route('/chinhSua_KH/<int:id>')
def edit_customer(id):
    conn = dao.get_db_connection()
    customer = conn.execute('SELECT * FROM KhachHang WHERE idKhachHang = ?', (id,)).fetchone()
    conn.close()
    if customer:
        return render_template('capNhat_KH.html', customer=customer)
    return "Không tìm thấy khách hàng", 404

# Route để cập nhật thông tin khách hàng
@app.route('/capNhat_KH/<int:id>', methods=['POST'])
def update_customer(id):
    hoKhach = request.form['hoKhach']
    tenKhach = request.form['tenKhach']
    soDienThoai = request.form['soDienThoai']
    gioiTinh = request.form['gioiTinh']
    email = request.form['email']
    ngaySinh = request.form['ngaySinh']
    nganHang = request.form['nganHang']
    soTaiKhoan = request.form['soTaiKhoan']

    conn = dao.get_db_connection()
    conn.execute('''UPDATE KhachHang SET hoKhach = ?, tenKhach = ?, soDienThoai = ?, gioiTinh = ?, 
                    email = ?, ngaySinh = ?, nganHang = ?, soTaiKhoan = ? WHERE idKhachHang = ?''',
                 (hoKhach, tenKhach, soDienThoai, gioiTinh, email, ngaySinh, nganHang, soTaiKhoan, id))
    conn.commit()
    conn.close()
    return redirect(url_for('home_admin'))  # Chuyển hướng về trang chủ sau khi cập nhật thành công


@app.route('/loginAd', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Kiểm tra xem email và password có được nhập không
        if not email or not password:
            flash("Vui lòng nhập email và mật khẩu!", "danger")
        elif email == "admin@example.com" and password == "password":
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('home_admin'))  # Chuyển hướng đến route 'home_admin'
        else:
            flash("Email hoặc mật khẩu không đúng!", "danger")

    return render_template('login_new.html')


@app.route('/verify_Save', methods=['get', 'post'])
def verify():
    app.secret_key = 'aiughiakjf'
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    if request.method == 'GET':
        otp = generate_otp()
        session['otp'] = otp
        nhanOTP(session.get('otp'), session.get('email'))
        print(session.get('otp'))
    if request.method == 'POST':
        otpcheck = request.form['otp']
        print(session.get('otp'))
        if session.get('otp') == otpcheck:
            query = "UPDATE KhachHang SET soDienThoai = ?, diaChi = ?, email = ? WHERE idKhachHang = 1"
            cursor.execute(query, (session.get('soDienThoai'), session.get('diaChi'), session.get('email')))
            conn.commit()
            conn.close()
            return redirect(url_for('tt_ca_nhan'))
        if session.get('otp') != otpcheck:
            print("SAI OTP")
            return redirect(url_for('tt_ca_nhan'))
    return render_template("verify.html")


def send_email(to_email, subject, message):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'lequangvinhkanghaneul@gmail.com'
    sender_password = 'vorv rxwe giey jpmq'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


def generate_otp():
    return str(random.randint(100000, 999999))


def nhanOTP(otp, usermail):
    send_email(usermail, "Password Reset Code", f"Your password reset code is: {otp}")


@app.route('/ttcanhan', methods=['get', 'post'])
def tt_ca_nhan():
    thongTin = getThongTin()
    if request.method == 'POST':
        session['soDienThoai'] = request.form['sdt']
        session['diaChi'] = request.form['diaChi']
        session['email'] = request.form['email']
        return redirect(url_for('verify'))
    return render_template("ThongTinCaNhan.html", tt=thongTin)


@app.route('/vecuatoi')
def ve_cua_toi():
    data = getVe()

    return render_template("VeCuaToi.html", data=data)


def getVe():
    db_path = os.path.join(os.path.dirname(__file__), 'data/database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'SELECT Ben_Xe_Di.ten_ben_xe, Ben_Xe_Den.ten_ben_xe, TuyenDuong.khoangCach, LichTrinh.thoiGianDi, Ve.trangThaiVe FROM Ve JOIN  DonHang ON Ve.idDonHang  = DonHang.idDonHang JOIN LichTrinh ON LichTrinh.idLichTrinh = DonHang.idLichTrinh JOIN TuyenDuong ON TuyenDuong.idTuyenDuong = LichTrinh.idTuyenDuong JOIN Ben_Xe AS Ben_Xe_Di ON TuyenDuong.diemDi = Ben_Xe_Di.ben_xe_id JOIN Ben_Xe AS Ben_Xe_Den ON TuyenDuong.diemDen = Ben_Xe_Den.ben_xe_id; '
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data


def searchLichTrinh(diemDi=None, diemDen=None):
    with sqlite3.connect('data/database.db') as conn:
        c = conn.cursor()
        c.execute(
            "SELECT  BenXeDi.ten_ben_xe AS ten_diem_di, BenXeDen.ten_ben_xe AS ten_diem_den, TuyenDuong.khoangCach, LichTrinh.thoiGianDi, Ben_xe.tinh_code FROM LichTrinh, Ben_xe JOIN  TuyenDuong ON LichTrinh.idTuyenDuong = TuyenDuong.idTuyenDuong  JOIN Ben_Xe AS BenXeDi ON TuyenDuong.diemDi = BenXeDi.ben_xe_id  JOIN Ben_Xe AS BenXeDen ON TuyenDuong.diemDen = BenXeDen.ben_xe_id GROUP BY BenXeDi.ten_ben_xe, BenXeDen.ten_ben_xe, TuyenDuong.khoangCach, LichTrinh.thoiGianDi ")
        data = c.fetchall()
    if diemDi != None:
        data = [p for p in data if str(p[4]) == str(diemDi)]
    if diemDen != None:
        data = [p for p in data if str(p[4]) == str(diemDen)]
    conn.close()
    return data


def getThongTin():
    db_path = os.path.join(os.path.dirname(__file__), 'data/database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'select hoKhach, tenKhach, email, soDienThoai, nganHang, diaChi, soTaiKhoan, ngaySinh, gioiTinh from KhachHang where idKhachHang = 1;'
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data


@app.route('/search')
def search():
    diemdi = request.args.get("departure")
    diemden = request.args.get("destination")
    data = searchLichTrinh(diemdi, diemden)
    with sqlite3.connect('data/database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM provinces ")
        provinces = c.fetchall()
    conn.close()
    return render_template('home.html', data=data, provinces=provinces)


@app.route('/ttlienhe')
def tt_lien_he():
    return render_template("ThongTinLienHe.html")


@app.route('/lichtrinh', methods=["GET", "POST"])
def lich_trinh():
    diemDi = request.form.get("diemDi")
    diemDen = request.form.get("diemDen")
    data = getLichTrinh(diemDi, diemDen)
    return render_template("lichtrinh.html", data=data)


def getLichTrinh(diemDi=None, diemDen=None):
    db_path = os.path.join(os.path.dirname(__file__), 'data/database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'SELECT * FROM Chuyen_Xe'
    if diemDi:
        query += f' WHERE diemDi = "{diemDi}"'
    if diemDen:
        query += f' WHERE diemDen = "{diemDen}"'
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data


app.secret_key = 'your_secret_key'


# Đọc dữ liệu từ file JSON
def load_users():
    user_path = os.path.join(os.path.dirname(__file__), 'data/user.json')
    with open(user_path, 'r') as file:
        data = json.load(file)
    return data['users']


# Lưu dữ liệu vào file JSON
def save_users(users):
    user_path = os.path.join(os.path.dirname(__file__), 'data/user.json')
    with open(user_path, 'w') as file:
        json.dump({"users": users}, file, indent=4)


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


invoice_data = {
    "invoices": [
        {
            "ticket_id": "P392",
            "seat": "160",
            "route": "Vũng Tàu - TP.Hồ Chí Minh",
            "date": "2024-10-21",
            "created_date": "2024-10-19",
            "amount": "160000 VNĐ",
            "status": "Đã thanh toán"
        },
        {
            "ticket_id": "P772",
            "seat": "150",
            "route": "Cần Thơ - Bến Tre",
            "date": "2024-10-22",
            "created_date": "2024-10-19",
            "amount": "150000 VNĐ",
            "status": "Chờ thanh toán"
        }
    ],
    "total_amount": "310000 VNĐ"
}


@app.route('/lshoadon')
def invoice_history():
    return render_template('lshoadon.html', data=invoice_data)


@app.route('/generate_pdf')
def generate_pdf():
    buffer = io.BytesIO()
    buffer.seek(0)
    return make_response(buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="HoaDon.pdf"'
    })


@app.route('/delete_invoice/<ticket_id>', methods=['POST'])
def delete_invoice(ticket_id):
    # Gọi hàm xóa hóa đơn từ cơ sở dữ liệu theo ticket_id
    # Ví dụ: db.delete_invoice(ticket_id)
    # Nếu thành công:
    return '', 200
    # Nếu không thành công:
    # return '', 400


if __name__ == '__main__':
    app.run(debug=True)
