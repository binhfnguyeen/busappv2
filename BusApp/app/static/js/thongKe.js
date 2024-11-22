function drawCharts() {
    // Vẽ biểu đồ Pie
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: ['An Giang - Sài Gòn', 'Cần Thơ - An Giang', 'Cần Thơ - Sài Gòn'],
            datasets: [{
                data: [14.3, 42.9, 42.9], // Tỉ lệ phần trăm
                backgroundColor: ['#007bff', '#ffc107', '#dc3545'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                },
            },
        },
    });

    // Vẽ biểu đồ Bar
    const barCtx = document.getElementById('barChart').getContext('2d');
    new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['lequangvinh13052004@gmail.com', 'tranthib@example.com', 'levanc@example.com', 'phamthid@example.com', 'nguyenquoce@example.com'],
            datasets: [{
                label: 'Doanh thu (nghìn đồng)',
                data: [160, 150, 145, 140, 135], // Doanh thu từng khách hàng
                backgroundColor: '#007bff',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Doanh thu (nghìn đồng)',
                    },
                },
            },
        },
    });
    const barCtx1 = document.getElementById('barChart1').getContext('2d');
    new Chart(barCtx1, {
        type: 'bar',
        data: {
            labels: ['lequangvinh13052004@gmail.com', 'tranthib@example.com', 'levanc@example.com', 'phamthid@example.com', 'nguyenquoce@example.com'],
            datasets: [{
                label: 'Doanh thu (nghìn đồng)',
                data: [160, 150, 145, 140, 135], // Doanh thu từng khách hàng
                backgroundColor: '#007bff',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Doanh thu (nghìn đồng)',
                    },
                },
            },
        },
    });
}

// Gọi hàm khi trang web đã tải
document.addEventListener('DOMContentLoaded', drawCharts);
