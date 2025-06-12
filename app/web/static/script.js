document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN ---
    const predictForm = document.getElementById('predict-form');
    const indexForms = document.querySelectorAll('.index-form'); // Lấy tất cả các form tính chỉ số
    
    const resultBox = document.getElementById('result-box');
    const resultTitle = document.getElementById('result-title');
    const resultContent = document.getElementById('result-content');

    // --- XỬ LÝ SỰ KIỆN ---
    if (predictForm) {
        predictForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const data = Object.fromEntries(new FormData(predictForm).entries());
            handleRequest('/predict', data, 'Đang dự đoán...', displayPredictionResult);
        });
    }

    if (indexForms) {
        // Gán sự kiện cho từng form tính chỉ số
        indexForms.forEach(form => {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                const category = form.dataset.category; // Lấy loại chỉ số từ thuộc tính data-
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                data.category = category; // Thêm loại chỉ số vào dữ liệu gửi đi
                
                handleRequest('/calculate_index', data, `Đang tính toán ${category}...`, displayIndexResult);
            });
        });
    }

    // --- CÁC HÀM TIỆN ÍCH ---
    function handleRequest(url, data, loadingMessage, callback) {
        showLoading(loadingMessage);
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
                callback(result);
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
        resultBox.className = 'result-box alert alert-warning';
        resultTitle.innerText = 'Lỗi';
        resultContent.innerText = errorMessage;
    }

    function displayPredictionResult(result) {
        // (Giữ nguyên không đổi)
        if (result.prediction === 1) {
            resultBox.className = 'result-box alert alert-danger';
            resultTitle.innerText = '⚠️ Có dấu hiệu TRẦM CẢM!';
        } else {
            resultBox.className = 'result-box alert alert-success';
            resultTitle.innerText = '✅ Không có dấu hiệu trầm cảm.';
        }
        let adviceHtml = '';
        if (result.advice && result.advice.length > 0) {
            adviceHtml = '<h6>🧾 Gợi ý cải thiện:</h6><ul>';
            result.advice.forEach(item => { adviceHtml += `<li>${item}</li>`; });
            adviceHtml += '</ul>';
        }
        resultContent.innerHTML = adviceHtml;
    }

    function displayIndexResult(result) {
        resultBox.className = 'result-box alert alert-primary';
        resultTitle.innerText = '📊 Kết quả Chỉ số';
        
        const content = `
            <p class="mb-2">Kết quả tính toán cho chỉ số:</p>
            <h5 class="text-primary">${result.index_name}</h5>
            <h2><span class="badge bg-primary">${result.score} / 5</span></h2>
            <p class="mt-3 fst-italic">Lưu ý: Điểm càng cao cho thấy mức độ cảm nhận về chỉ số đó càng lớn.</p>
        `;
        resultContent.innerHTML = content;
    }
});