function showResult() {
    var diemDi = document.querySelector('[name="diem_di"]').value;
    var diemDen = document.querySelector('[name="diem_den"]').value;
    var benDi = document.querySelector('[name="ben_di"]').value;
    var benDen = document.querySelector('[name="ben_den"]').value;
    var ngayDi = document.getElementById('ngaydi').value;
    var ngayVe = document.getElementById('ngayve').value;
    let TTchoNgoi = localStorage.getItem('selectedSeat');
    localStorage.setItem('ngayDi', ngayDi);
    localStorage.setItem('ngayVe', ngayVe);
    fetch(`/api/chuyenxe?diem_di=${diemDi}&diem_den=${diemDen}&ben_di=${benDi}&ben_den=${benDen}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === "found") {
                console.log("Tìm thấy chuyến xe:", data.data);
                var resultContainer = document.getElementById('resultContainer');
                resultContainer.innerHTML = '';
                data.data.forEach(chuyenxe => {
                    localStorage.setItem('diemDi', diemDi);
                    localStorage.setItem('diemDen', diemDen);
                    localStorage.setItem('benDi', benDi);
                    localStorage.setItem('benDen', benDen);
                    localStorage.setItem('giaVe', chuyenxe[6]);
                    localStorage.setItem('xeDi', chuyenxe[7]);
                    var htmlContent = `
                    <div class="card mb-3" style="width: 30%;">
                        <div class="card-body">
                            <table class="table table-bordered table-striped table-sm">
                                <tbody>
                                    <tr><td><strong>Bến đi</strong></td><td>${chuyenxe[3]}</td></tr>
                                    <tr><td><strong>Bến đến</strong></td><td>${chuyenxe[4]}</td></tr>
                                    <tr><td><strong>Điểm đi</strong></td><td>${chuyenxe[1]}</td></tr>
                                    <tr><td><strong>Điểm đến</strong></td><td>${chuyenxe[2]}</td></tr>
                                    <tr><td><strong>Ngày đi</strong></td><td>${ngayDi}</td></tr>
                                    <tr><td><strong>Ngày về</strong></td><td>${ngayVe}</td></tr>
                                    <tr><td><strong>Xe đi</strong></td><td>Xe số ${chuyenxe[7]} </td></tr>
                                    <tr><td><strong>Chỗ ngồi</strong></td><td> Ghế ${TTchoNgoi} </td></tr>
                                    <tr><td><strong>Khoảng cách</strong></td><td>${chuyenxe[5]} km</td></tr>
                                    <tr><td><strong>Giá vé</strong></td><td>${chuyenxe[6]} VND</td></tr>
                                </tbody>
                            </table>
                            <a href="/thanhtoan" class="btn btn-primary btn-sm">Đặt vé</a>
                        </div>
                    </div>
                    `;
                    resultContainer.innerHTML += htmlContent;
                });
            } else {
                console.log("Không tìm thấy chuyến xe.");
                var resultContainer = document.getElementById('resultContainer');
                resultContainer.innerHTML = '<p>Không tìm thấy chuyến xe với các thông tin đã nhập.</p>';
            }
        })
        .catch(error => {
            console.error("Lỗi khi gọi API:", error);
            var resultContainer = document.getElementById('resultContainer');
            resultContainer.innerHTML = '<p>Đã xảy ra lỗi khi truy xuất dữ liệu.</p>';
        });
}

function getValueButton(button) {
    var seatValue = button.value;
    var seats = document.querySelectorAll('.seat');
    seats.forEach(function(seat) {
        seat.classList.remove('selected');
    });
    button.classList.add('selected');
    localStorage.setItem('selectedSeat', seatValue);
}

function thanhToanDonHang() {
    let i=3;
    const idKhachHang = 1;
    const idXe = document.getElementById('xeDi').textContent;
    const ngayDat = new Date().toISOString().slice(0, 10);
    const gia = (document.getElementById('giaVe').textContent);
    const trangThai = "Đã xác nhận";
    const idLichTrinh = 1;
    const soGhe = 1;

    // Tạo đối tượng dữ liệu để gửi đến server
    const data = {
        idKhachHang: idKhachHang,
        idXe: idXe,
        ngayDat: ngayDat,
        gia: gia,
        trangThai: trangThai,
        idLichTrinh: idLichTrinh,
        soGhe: soGhe
    };

    // Gửi yêu cầu POST tới server để lưu thông tin
    fetch('/save_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (!result.success) {
            alert('Có lỗi xảy ra: ' + result.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Lỗi kết nối đến server.');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    let TTdiemDi = localStorage.getItem('diemDi');
    let TTdiemDen = localStorage.getItem('diemDen');
    let TTbenDi = localStorage.getItem('benDi');
    let TTbenDen = localStorage.getItem('benDen');
    let TTngayDi = localStorage.getItem('ngayDi');
    let TTngayVe = localStorage.getItem('ngayVe');
    let TTgiaVe = localStorage.getItem('giaVe');
    let TTxeDi = localStorage.getItem('xeDi');
    let TTchoNgoi = localStorage.getItem('selectedSeat');

    TTdiemDi = TTdiemDi ? TTdiemDi : 'Chưa có thông tin';
    TTdiemDen = TTdiemDen ? TTdiemDen : 'Chưa có thông tin';
    TTbenDi = TTbenDi ? TTbenDi : 'Chưa có thông tin';
    TTbenDen = TTbenDen ? TTbenDen : 'Chưa có thông tin';
    TTngayDi = TTngayDi ? TTngayDi : 'Chưa có thông tin';
    TTngayVe = TTngayVe ? TTngayVe : 'Chưa có thông tin';
    TTgiaVe = TTgiaVe ? TTgiaVe : 'Chưa có thông tin';
    TTxeDi = TTxeDi ? TTxeDi : 'Chưa có thông tin';
    TTchoNgoi = TTchoNgoi ? TTchoNgoi : 'Chưa có thông tin';

    if (document.getElementById('diemDi')) document.getElementById('diemDi').textContent = TTdiemDi;
    if (document.getElementById('diemDen')) document.getElementById('diemDen').textContent = TTdiemDen;
    if (document.getElementById('benDi')) document.getElementById('benDi').textContent = TTbenDi;
    if (document.getElementById('benDen')) document.getElementById('benDen').textContent = TTbenDen;
    if (document.getElementById('ngayDi')) document.getElementById('ngayDi').textContent = TTngayDi;
    if (document.getElementById('ngayVe')) document.getElementById('ngayVe').textContent = TTngayVe;
    if (document.getElementById('giaVe')) document.getElementById('giaVe').textContent = TTgiaVe;
    if (document.getElementById('xeDi')) document.getElementById('xeDi').textContent = "Xe số " + TTxeDi;
    if (document.getElementById('choNgoi')) document.getElementById('choNgoi').textContent = "Ghế " + TTchoNgoi;
});

