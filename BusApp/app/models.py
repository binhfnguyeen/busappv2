from sqlalchemy import Column, Integer, String, Date, ForeignKey, REAL, CheckConstraint
from sqlalchemy.orm import relationship
from BusApp.app import db, app
from datetime import datetime

class KhachHang(db.Model):
    __tablename__ = 'KhachHang'
    idKhachHang = Column(Integer, primary_key=True, autoincrement=True)
    hoKhach = Column(String(50), nullable=False)
    tenKhach = Column(String(20), nullable=False)
    soDienThoai = Column(String(255), nullable=False)
    gioiTinh = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    ngaySinh = Column(Date, nullable=False)
    nganHang = Column(String(100), nullable=True)
    soTaiKhoan = Column(String(20), nullable=True)

class NhanVien(db.Model):
    __tablename__ = 'NhanVien'
    idNhanVien = Column(Integer, primary_key=True, autoincrement=True)
    hoNV = Column(String(50), nullable=False)
    tenNV = Column(String(20), nullable=False)
    soDienThoai = Column(String(255), nullable=False)
    gioiTinh = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    ngaySinh = Column(Date, nullable=False)
    nganHang = Column(String(100), nullable=True)
    soTaiKhoan = Column(String(20), nullable=True)

class TuyenXe(db.Model):
    __tablename__ = 'TuyenDuong'
    idTuyenDuong = Column(Integer, primary_key=True, autoincrement=True)
    diemDi = Column(Integer, db.ForeignKey('Ben_Xe.ben_xe_id'), nullable=False)
    diemDen = Column(Integer, db.ForeignKey('Ben_Xe.ben_xe_id'), nullable=False)
    khoangCach = Column(REAL, nullable=False)
    soNgayTrongTuanChay = Column(Integer, nullable=True)
    soChuyenTrongTuan = Column(Integer, nullable=True)
    gia = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint('soNgayTrongTuanChay BETWEEN 1 AND 7', name='check_soNgayTrongTuanChay'),
    )

    # Mối quan hệ với bảng Ben_Xe
    diem_di_ben_xe = db.relationship('Ben_Xe', foreign_keys=[diemDi])
    diem_den_ben_xe = db.relationship('Ben_Xe', foreign_keys=[diemDen])

class ChuyenXe(db.Model):
    __tablename__ = 'LichTrinh'
    idLichTrinh = Column(Integer, primary_key=True, autoincrement=True)
    idTuyenDuong = Column(Integer, ForeignKey('TuyenXe.idTuyenDuong'), nullable=False)
    thoiGianDi = Column(String(50), nullable=False)
    thoiGianDen = Column(String(50), nullable=False)
    idXe = Column(Integer, ForeignKey('Xe.idXe'), nullable=False)
    # Mối quan hệ với bảng TuyenXe và Xe

class Ben_Xe(db.Model):
    __tablename__ = 'Ben_Xe'
    ben_xe_id = Column(Integer, primary_key=True, autoincrement=True)
    ten_ben_xe = Column(String(50), nullable=False)
    tinh_code = Column(String(50), nullable=False)
    quan_huyen_code = Column(String(50), nullable=False)

class Xe(db.Model):
    __tablename__ = 'Xe'
    idXe = Column(Integer, primary_key=True, autoincrement=True)
    bienSo = Column(String(50), nullable=False)
    sucChua = Column(Integer, nullable=False)
    tinhTrangXe = Column(String(20), nullable=False)

class Ghe(db.Model):
    __tablename__ = 'gheNgoi'
    maGhe=Column(Integer, primary_key=True, autoincrement=True)
    soGhe = Column(String(20), nullable=False)
    idXe = Column(Integer, ForeignKey('Xe.idXe'), nullable=False)
    tinhTrang = Column(String(30), nullable=False)

    xe = db.relationship('Xe', backref='danh_sach_ghe')

class Tinh(db.Model):
    __tablename__ = 'provinces'
    code = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)

class HoaDon(db.Model):
    __tablename__ = 'HoaDon'
    idHoaDon = Column(Integer, primary_key=True, autoincrement=True)
    idDonHang = Column(Integer, ForeignKey('DonHang.idDonHang'), nullable=False)
    ngayLap = Column(String(20), nullable=False)
    tongTien = Column(REAL, nullable=False)
    trangThai = Column(Integer, ForeignKey('TrangThaiHoaDon.idTrangThai'), nullable=False)

class TrangThaiHoaDon(db.Model):
    __tablename__ = 'TrangThaiHoaDon'
    idTrangThai = Column(Integer, primary_key=True, autoincrement=True)
    tenTrangThai = Column(String(20), nullable=False)

class DonHang(db.Model):
    __tablename__ = 'DonHang'
    idDonHang = Column(Integer, primary_key=True, autoincrement=True)
    idKhachHang = Column(Integer, ForeignKey('KhachHang.idKhachHang'), nullable=False)
    idXe = Column(Integer, ForeignKey('Xe.idXe'), nullable=False)
    ngayDat = Column(String(20), nullable=False)
    idLichTrinh = Column(Integer, ForeignKey('ChuyenXe.idLichTrinh'), nullable=False)
    soGhe = Column(Integer, nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()