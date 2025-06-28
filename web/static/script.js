document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN ---
    const predictForm = document.getElementById('predict-form');
    const indexForms = document.querySelectorAll('.index-form'); 
    
    const resultBox = document.getElementById('result-box');
    const resultTitle = document.getElementById('result-title');
    const resultContent = document.getElementById('result-content');

    // <<<<<<<<<<<<<<<< THAY ĐỔI LOGIC MỚI Ở ĐÂY >>>>>>>>>>>>>>>>

    // 1. Tạo một đối tượng để lưu trữ kết quả cho từng tab
    const tabResults = {};

    // 2. Lấy tất cả các nút bấm chuyển tab
    const tabTriggers = document.querySelectorAll('#mainTab button[data-bs-toggle="tab"]');

    // Hàm để ẩn và xóa nội dung hộp kết quả
    function hideResultBox() {
        if (resultBox) {
            resultBox.style.display = 'none';
            resultTitle.innerText = '';
            resultContent.innerHTML = '';
        }
    }

    // 3. Gán sự kiện cho mỗi nút tab
    tabTriggers.forEach(triggerEl => {
        // Lắng nghe sự kiện 'shown.bs.tab' của Bootstrap
        triggerEl.addEventListener('shown.bs.tab', function (event) {
            // event.target là nút tab vừa được kích hoạt
            // Lấy ID của pane nội dung tương ứng (ví dụ: 'predict-pane')
            const newTabId = event.target.getAttribute('data-bs-target').substring(1);
            
            // Kiểm tra xem có kết quả nào được lưu cho tab này không
            const storedResult = tabResults[newTabId];

            if (storedResult) {
                // Nếu có, hiển thị lại kết quả đã lưu
                resultBox.style.display = 'block';
                resultBox.className = storedResult.className;
                resultTitle.innerHTML = storedResult.title;
                resultContent.innerHTML = storedResult.content;
            } else {
                // Nếu không có, ẩn hộp kết quả đi
                hideResultBox();
            }
        });
    });

    // --- XỬ LÝ SỰ KIỆN FORM (Giữ nguyên) ---
    if (predictForm) {
        predictForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const data = Object.fromEntries(new FormData(predictForm).entries());
            handleRequest('/predict', data, 'Đang dự đoán...', displayPredictionResult);
        });
    }

    if (indexForms) {
        indexForms.forEach(form => {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                const category = form.dataset.category;
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                data.category = category;
                
                handleRequest('/calculate_index', data, 'Đang tính toán...', displayIndexResult);
            });
        });
    }

    // --- CÁC HÀM TIỆN ÍCH ---
    function handleRequest(url, data, loadingMessage, callback) {
        showLoading(loadingMessage);
        // Xác định tab nào đang active để lưu kết quả đúng chỗ
        const activeTabPaneId = document.querySelector('.tab-pane.active').id;

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                displayError(result.error);
            } else {
                // Truyền ID của tab active vào hàm callback
                callback(result, activeTabPaneId);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayError('Có lỗi xảy ra khi kết nối đến máy chủ.');
        });
    }

    function showLoading(message) {
        resultBox.style.display = 'block';
        resultBox.className = 'result-box alert alert-info';
        resultTitle.innerText = message;
        resultContent.innerHTML = 'Vui lòng chờ trong giây lát.';
    }

    function displayError(errorMessage) {
        resultBox.style.display = 'block';
        resultBox.className = 'result-box alert alert-warning';
        resultTitle.innerText = 'Lỗi';
        resultContent.innerText = errorMessage;
    }

    function displayPredictionResult(result, tabId) {
        let className, title, adviceHtml = '';

        if (result.prediction === 1) {
            className = 'result-box alert alert-danger';
            title = '⚠️ Có dấu hiệu TRẦM CẢM!';
        } else {
            className = 'result-box alert alert-success';
            title = '✅ Không có dấu hiệu trầm cảm.';
        }
        if (result.advice && result.advice.length > 0) {
            adviceHtml = '<h6>🧾 Gợi ý cải thiện:</h6><ul>';
            result.advice.forEach(item => { adviceHtml += `<li>${item}</li>`; });
            adviceHtml += '</ul>';
        }
        
        resultBox.className = className;
        resultTitle.innerHTML = title;
        resultContent.innerHTML = adviceHtml;

        // 4. Lưu kết quả vào bộ nhớ đệm
        tabResults[tabId] = { className, title, content: adviceHtml };
    }

    function displayIndexResult(result, tabId) {
        const className = 'result-box alert alert-primary';
        const title = '📊 Kết quả Chỉ số';
        const content = `
            <p class="mb-2">Kết quả tính toán cho chỉ số:</p>
            <h5 class="text-primary">${result.index_name}</h5>
            <h2><span class="badge bg-primary">${result.score} / 5</span></h2>
            <p class="mt-3 fst-italic">Lưu ý: Điểm càng cao cho thấy mức độ cảm nhận về chỉ số đó càng lớn.</p>
        `;

        resultBox.className = className;
        resultTitle.innerHTML = title;
        resultContent.innerHTML = content;
        
        // 4. Lưu kết quả vào bộ nhớ đệm
        tabResults[tabId] = { className, title, content };
    }
});