import sqlite3

import stripe
from flask import Blueprint, Flask, render_template, request
from flask import jsonify
import os
app = Flask(__name__)
datve_blueprints = Blueprint("datve", __name__)

stripe.api_key = "sk_test_51QKFWxHwA2xtXgiVV3nkxS8tuCsiDbIVbpOfLPtnoa82UGwlwyYRdlw9I2SnO3Ix6PtaReYomTMr6AhGUPCEW5kI00bovmtMxJ"
def get_data_from_db(query, params):
    try:
        with sqlite3.connect(os.path.join(os.path.dirname(__file__), 'data/database.db')) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
    except sqlite3.Error as e:
        print("Lỗi cơ sở dữ liệu:", e)
        return None
    finally:
        conn.close()


@datve_blueprints.route('/save_order', methods=['POST'])
def save_order():
    try:
        data = request.json
        idKhachHang = data.get("idKhachHang")
        idXe = data.get("idXe")
        gia = data.get("gia")
        trangThai = data.get("trangThai")
        ngayDat = data.get("ngayDat")
        idLichTrinh = data.get("idLichTrinh")
        soGhe = data.get("soGhe")

        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        idDonHang = cursor.lastrowid

        query = """
        INSERT INTO DonHang (idDonHang, idKhachHang, idXe, ngayDat, idLichTrinh, soGhe, gia, trangThai)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (idDonHang, idKhachHang, idXe, ngayDat, idLichTrinh, soGhe, gia, trangThai))
        conn.commit()


        conn.close()

        return jsonify({"success": True, "message": "Order saved successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@datve_blueprints.route("/api/chuyenxe", methods=["GET"])
def get_chuyenxe():
    diem_di = request.args.get('diem_di')
    diem_den = request.args.get('diem_den')
    ben_di = request.args.get('ben_di')
    ben_den = request.args.get('ben_den')
    query = """
    SELECT * FROM Chuyen_Xe
    WHERE DiemDi = ? AND DiemDen = ? AND BenDi = ? AND BenDen = ?
    """
    result = get_data_from_db(query, (diem_di, diem_den, ben_di, ben_den))

    if result:
        return jsonify({"status": "found", "data": result})
    else:
        return jsonify({"status": "not_found"})


@datve_blueprints.route("/api/bienso")
def get_bienso():
    bien_so = get_data_from_db("SELECT DISTINCT bienSo FROM Xe")
    data = {
        "bien_so": [row[0] for row in bien_so]
    }
    return jsonify(data)


@datve_blueprints.route('/charge', methods=['POST'])
def charge():
    try:
        # Tạo session thanh toán Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Vé xe',
                        },
                        'unit_amount': 1000,  # Số tiền là 10.00 USD (1000 cent)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )

        return render_template("thanhtoan.html")
    except Exception as e:
        return str(e), 500


@datve_blueprints.route('/success')
def success():
    return 'Thanh toán thành công!'


@datve_blueprints.route('/cancel')
def cancel():
    return 'Thanh toán bị hủy.'


@datve_blueprints.route('/checkout')
def checkout():
    return render_template('checkout.html')


@datve_blueprints.route('/datve')
def index():
    return render_template("datve.html")


if __name__ == "main":
    app.run(debug=True)