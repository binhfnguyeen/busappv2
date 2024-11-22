const provinces = [  
    { value: 'ha_noi', text: 'Hà Nội' },  
    { value: 'ha_tinh', text: 'Hà Tĩnh' },  
    { value: 'da_nang', text: 'Đà Nẵng' },  
    { value: 'ho_chi_minh', text: 'Hồ Chí Minh' },  
    { value: 'hai_phong', text: 'Hải Phòng' },  
    { value: 'vinh', text: 'Vinh' },  
    { value: 'nha_trang', text: 'Nha Trang' },  
    { value: 'can_tho', text: 'Cần Thơ' },  
    { value: 'quang_ngai', text: 'Quảng Ngãi' },  
    { value: 'binh_thuan', text: 'Bình Thuận' },  
    { value: 'thua_thien_hue', text: 'Thừa Thiên Huế' },  
    { value: 'dak_lak', text: 'Đắk Lắk' },  
    { value: 'ba_ria_vung_tau', text: 'Bà Rịa - Vũng Tàu' },  
    { value: 'phu_tho', text: 'Phú Thọ' },  
    { value: 'ba_ninh', text: 'Bắc Ninh' },  
    { value: 'long_an', text: 'Long An' },  
    { value: 'tien_giang', text: 'Tiền Giang' },  
    { value: 'thanh_hoa', text: 'Thanh Hóa' },  
    { value: 'nam_dinh', text: 'Nam Định' },  
    { value: 'quang_ninh', text: 'Quảng Ninh' },  
    { value: 'ha_giang', text: 'Hà Giang' },  
    { value: 'lang_son', text: 'Lạng Sơn' },  
    { value: 'tam_dao', text: 'Tam Đảo' },  
    { value: 'hoa_binh', text: 'Hòa Bình' },  
    { value: 'soc_trang', text: 'Sóc Trăng' },  
    { value: 'hau_giang', text: 'Hậu Giang' },  
    { value: 'bac_lieu', text: 'Bạc Liêu' },  
    { value: 'tra_vinh', text: 'Trà Vinh' },  
    { value: 'thai_nguyen', text: 'Thái Nguyên' },  
    { value: 'tuyen_quang', text: 'Tuyên Quang' },  
    { value: 'bac_kan', text: 'Bắc Kạn' },  
    { value: 'ca_mau', text: 'Cà Mau' }  
];  

function loadOption() {  
    const departureSelect = document.getElementById('departure');  
    const destinationSelect = document.getElementById('destination');  

    provinces.forEach(province => {  
        const optionElementDeparture = document.createElement('option');  
        optionElementDeparture.value = province.value; // Gán giá trị cho option  
        optionElementDeparture.textContent = province.text; // Gán văn bản hiển thị cho option  
        departureSelect.appendChild(optionElementDeparture);  

        const optionElementDestination = document.createElement('option');  
        optionElementDestination.value = province.value; // Gán giá trị cho option  
        optionElementDestination.textContent = province.text; // Gán văn bản hiển thị cho option  
        destinationSelect.appendChild(optionElementDestination);  
    });  
}  

window.onload = loadOption; 