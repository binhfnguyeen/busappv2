from flask import request
import os
import json
import hashlib

from sqlalchemy import or_

from BusApp.app.models import KhachHang, NhanVien, TuyenXe, Xe, Ben_Xe, Tinh, ChuyenXe, Ghe, HoaDon, TrangThaiHoaDon, DonHang
import sqlite3
from BusApp.app import db
from sqlalchemy.orm import aliased


def read_user():
    try:
        with open(os.path.join(BusApp.app.root_path, "./data/user.json"), encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and 'users' in data and isinstance(data['users'], list):
                return data['users']
            else:
                raise ValueError("The user data should be a list of dictionaries under the 'users' key")
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        raise ValueError("The user.json file is not a valid JSON format")

def write_user(data):
    with open(os.path.join(BusApp.app.root_path, "./data/user.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def validate_user(username=None, password=None):
    users = read_user()
    if not users:
        return None  # No users found or error reading users

    password_hash = hashlib.md5(password.strip().encode("utf-8")).hexdigest()
    for user in users:
        if user.get('username') == username and user.get('password') == password_hash:
            return user
    return None  # If no matching user is found

def load_customers(kw=None):
    page = request.args.get('page', 1, type=int)
    query = KhachHang.query

    # Nếu `kw` không trống, lọc theo từ khóa trong tên khách hàng
    if kw:
        query = query.filter(KhachHang.tenKhach.contains(kw) | KhachHang.hoKhach.contains(kw))

    return query.paginate(page=page, per_page=6)

def total_customers():
    return KhachHang.query.count()

def load_employees(kw=None):
    page = request.args.get('page', 1, type=int)
    query = NhanVien.query

    # Nếu `kw` không trống, lọc theo từ khóa trong tên nhân viên
    if kw:
        query = query.filter(NhanVien.tenNV.contains(kw) | NhanVien.hoNV.contains(kw))

    return query.paginate(page=page, per_page=6)

def total_employees():
    return NhanVien.query.count()

def tuyenXe_load():
    # Khai báo alias cho bảng Ben_Xe và Tinh
    ben_xe_diem_di = aliased(Ben_Xe)
    ben_xe_diem_den = aliased(Ben_Xe)
    tinh_diem_di = aliased(Tinh)  # Alias cho bảng Tinh (điểm đi)
    tinh_diem_den = aliased(Tinh)  # Alias cho bảng Tinh (điểm đến)

    # Lấy tham số từ query string
    diemDi = request.args.get('diemDi')  # Lấy tỉnh điểm đi
    diemDen = request.args.get('diemDen')  # Lấy tỉnh điểm đến
    page = request.args.get('page', 1, type=int)  # Số trang

    # Truy vấn cơ bản
    query = db.session.query(
        TuyenXe,
        ben_xe_diem_di.ten_ben_xe.label('diem_di_name'),
        ben_xe_diem_den.ten_ben_xe.label('diem_den_name'),
        tinh_diem_di.name.label('diem_di_tinh_name'),
        tinh_diem_den.name.label('diem_den_tinh_name'),
        ben_xe_diem_di.tinh_code.label('diem_di_tinh_code'),
        ben_xe_diem_den.tinh_code.label('diem_den_tinh_code')
    ) \
        .join(ben_xe_diem_di, TuyenXe.diemDi == ben_xe_diem_di.ben_xe_id) \
        .join(ben_xe_diem_den, TuyenXe.diemDen == ben_xe_diem_den.ben_xe_id) \
        .join(tinh_diem_di, ben_xe_diem_di.tinh_code == tinh_diem_di.code) \
        .join(tinh_diem_den, ben_xe_diem_den.tinh_code == tinh_diem_den.code)

    # Lọc theo điểm Đi và điểm Đến nếu có
    if diemDi:
        query = query.filter(tinh_diem_di.name == diemDi)
    if diemDen:
        query = query.filter(tinh_diem_den.name == diemDen)

    # Phân trang kết quả
    tuyen_xe = query.paginate(page=page, per_page=6)

    return tuyen_xe


def total_tuyenXe():
    return TuyenXe.query.count()

def load_IDTuyenXe():
    return db.session.query(TuyenXe.idTuyenDuong).all()

def load_tuyenXe():
    return TuyenXe.query.all()

def load_tinh():
    return db.session.query(Tinh).all()

def load_ChuyenXe():
    # Aliases cho các bảng liên quan
    ben_xe_diem_di = aliased(Ben_Xe)
    ben_xe_diem_den = aliased(Ben_Xe)
    tinh_diem_di = aliased(Tinh)
    tinh_diem_den = aliased(Tinh)

    # Lấy tham số từ query string
    diemDi = request.args.get('diemDi')
    diemDen = request.args.get('diemDen')

    # Lấy số trang từ query string
    page = request.args.get('page', 1, type=int)

    # Truy vấn dữ liệu
    query = db.session.query(
        ChuyenXe.idLichTrinh,
        Xe.bienSo.label('bienSo'),
        ChuyenXe.thoiGianDi,
        ChuyenXe.thoiGianDen,
        TuyenXe.idTuyenDuong,
        tinh_diem_di.name.label('diem_di_tinh_name'),
        tinh_diem_den.name.label('diem_den_tinh_name')
    ) \
        .join(Xe, ChuyenXe.idXe == Xe.idXe) \
        .join(TuyenXe, ChuyenXe.idTuyenDuong == TuyenXe.idTuyenDuong) \
        .join(ben_xe_diem_di, TuyenXe.diemDi == ben_xe_diem_di.ben_xe_id) \
        .join(ben_xe_diem_den, TuyenXe.diemDen == ben_xe_diem_den.ben_xe_id) \
        .join(tinh_diem_di, ben_xe_diem_di.tinh_code == tinh_diem_di.code) \
        .join(tinh_diem_den, ben_xe_diem_den.tinh_code == tinh_diem_den.code)

    # Lọc theo điểm Đi và điểm Đến nếu có
    if diemDi:
        query = query.filter(tinh_diem_di.name == diemDi)
    if diemDen:
        query = query.filter(tinh_diem_den.name == diemDen)

    return query.paginate(page=page, per_page=6)


def total_ChuyenXe():
    return ChuyenXe.query.count()

def chiTietChuyenXe(chuyen_xe_id):
    chuyen_xe = db.session.query(
        ChuyenXe,
        TuyenXe,
        Xe.bienSo,
        Ben_Xe.ten_ben_xe.label('diem_di_name'),
        Ben_Xe.ten_ben_xe.label('diem_den_name')
    ) \
        .join(TuyenXe, ChuyenXe.idTuyenDuong == TuyenXe.idTuyenDuong) \
        .join(Xe, ChuyenXe.idXe == Xe.idXe) \
        .join(Ben_Xe, TuyenXe.diemDi == Ben_Xe.ben_xe_id) \
        .filter(ChuyenXe.idLichTrinh == chuyen_xe_id).first()
    return chuyen_xe

def load_Ghe(chuyen_xe):
    return Ghe.query.filter_by(idXe=chuyen_xe.ChuyenXe.idXe).all()

def load_Xe(kw=None):
    page = request.args.get('page', 1, type=int)
    query = Xe.query

    # Nếu `kw` không trống, lọc theo từ khóa trong tên nhân viên
    if kw:
        query = query.filter(Xe.bienSo.contains(kw) | Xe.tinhTrangXe.contains(kw))

    return query.paginate(page=page, per_page=6)

def total_Xe():
    return Xe.query.count()

def load_taiXe():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT idNhanVien, hoNV || ' ' || tenNV AS hoTen FROM NhanVien")
    drivers = cursor.fetchall()  # Lấy dữ liệu trước khi đóng kết nối
    conn.close()
    return drivers

def load_TenXe():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT idXe, bienSo FROM Xe")
    vehicles = cursor.fetchall()  # Lấy dữ liệu trước khi đóng kết nối
    conn.close()
    return vehicles

def load_benXe():
    connection = sqlite3.connect('data/database.db')
    cursor = connection.cursor()

    # Truy vấn tất cả các bến xe
    cursor.execute("SELECT ben_xe_id, ten_ben_xe FROM Ben_Xe")
    stations = cursor.fetchall()

    connection.close()
    return stations

def load_hoaDon(kw=None):
    page = request.args.get('page', 1, type=int)
    query = db.session.query(
        HoaDon.idHoaDon,
        KhachHang.email,
        HoaDon.ngayLap,
        HoaDon.tongTien,
        TrangThaiHoaDon.tenTrangThai
    ).join(DonHang, HoaDon.idDonHang == DonHang.idDonHang) \
     .join(KhachHang, DonHang.idKhachHang == KhachHang.idKhachHang) \
     .join(TrangThaiHoaDon, HoaDon.trangThai == TrangThaiHoaDon.idTrangThai)

    # Nếu có từ khóa `kw`, áp dụng bộ lọc
    if kw:
        query = query.filter(or_(
            KhachHang.email.contains(kw),
            TrangThaiHoaDon.tenTrangThai.contains(kw)
        ))

    # Thực hiện phân trang
    return query.paginate(page=page, per_page=6)

def delete_customer_from_db(customer_id):
    connection = sqlite3.connect('D:/PycharmProject/BusTicketSales/BusApp/data/database.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM KhachHang WHERE idKhachHang = ?", (customer_id,))
    connection.commit()
    connection.close()

def delete_employee_from_db(employee_id):
    connection = sqlite3.connect('D:/PycharmProject/BusTicketSales/BusApp/data/database.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM NhanVien WHERE idNhanVien = ?", (employee_id,))
    connection.commit()
    connection.close()

def delete_vehicle_from_db(vehicle_id):
    connection = sqlite3.connect('D:/PycharmProject/BusTicketSales/BusApp/data/database.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Xe WHERE idXe = ?", (vehicle_id,))
    connection.commit()
    connection.close()

def delete_route_from_db(route_id):
    connection = sqlite3.connect('D:/PycharmProject/BusTicketSales/BusApp/data/database.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM TuyenDuong WHERE idTuyenDuong = ?", (route_id,))
    connection.commit()
    connection.close()

def delete_trip_from_db(trip_id):
    connection = sqlite3.connect('D:/PycharmProject/BusTicketSales/BusApp/data/database.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM LichTrinh WHERE idLichTrinh = ?", (trip_id,))
    connection.commit()
    connection.close()

def delete_receipt_from_db(receipt_id):
    connection = sqlite3.connect('D:/PycharmProject/BusTicketSales/BusApp/data/database.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM HoaDon WHERE idHoaDon = ?", (receipt_id,))
    connection.commit()
    connection.close()

def get_db_connection():
    conn = sqlite3.connect('data/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def thongKeTuyenXe():
    # Aliases cho các bảng
    tinh_diem_di = aliased(Tinh)
    tinh_diem_den = aliased(Tinh)
    ben_xe_diem_di = aliased(Ben_Xe)
    ben_xe_diem_den = aliased(Ben_Xe)

    # Truy vấn lấy thông tin cần thiết
    query = (
        db.session.query(
            TuyenXe.soNgayTrongTuanChay,
            tinh_diem_di.name.label('tinh_diem_di_name'),
            tinh_diem_den.name.label('tinh_diem_den_name')
        )
        .join(ben_xe_diem_di, TuyenXe.diemDi == ben_xe_diem_di.ben_xe_id)
        .join(ben_xe_diem_den, TuyenXe.diemDen == ben_xe_diem_den.ben_xe_id)
        .join(tinh_diem_di, ben_xe_diem_di.tinh_code == tinh_diem_di.code)
        .join(tinh_diem_den, ben_xe_diem_den.tinh_code == tinh_diem_den.code)
        .order_by(TuyenXe.soNgayTrongTuanChay.desc())
        .limit(5)
        .all()
    )

    return query

def total_revenue():
    return db.session.query(db.func.coalesce(db.func.sum(HoaDon.tongTien), 0)).scalar()

def total_provinces():
    return Tinh.query.count()

def total_stations():
    return Ben_Xe.query.count()

def total_hoaDon():
    return HoaDon.query.count()