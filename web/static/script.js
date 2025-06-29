document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN ---
    const predictForm = document.getElementById('predict-form');
    const indexForms = document.querySelectorAll('.index-form'); 
    
    const resultBox = document.getElementById('result-box');
    const resultTitle = document.getElementById('result-title');
    const resultContent = document.getElementById('result-content');
    
    const tabTriggers = document.querySelectorAll('#mainTab button[data-bs-toggle="tab"]');
    const tabResults = {}; // Bộ nhớ đệm để lưu kết quả của từng tab

    // --- XỬ LÝ SỰ KIỆN ---

    // Hàm ẩn và xóa nội dung hộp kết quả
    function hideResultBox() {
        if (resultBox) {
            resultBox.style.display = 'none';
            resultTitle.innerText = '';
            resultContent.innerHTML = '';
        }
    }

    // Gán sự kiện cho mỗi nút tab để ẩn kết quả cũ khi chuyển tab
    tabTriggers.forEach(triggerEl => {
        triggerEl.addEventListener('shown.bs.tab', function (event) {
            const newTabId = event.target.getAttribute('data-bs-target').substring(1);
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

    // Xử lý sự kiện cho form "Dự đoán Trầm cảm"
    if (predictForm) {
        predictForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const data = Object.fromEntries(new FormData(predictForm).entries());
            handleRequest('/predict', data, 'Đang phân tích, vui lòng chờ...', displayPredictionResult);
        });
    }

    // Xử lý sự kiện cho các form "Tính Chỉ số"
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

    // Logic cho các thanh trượt (slider)
    const sliders = document.querySelectorAll('.slider-input');
    sliders.forEach(slider => {
        const valueDisplay = slider.nextElementSibling;

        function updateSliderAppearance() {
            if (valueDisplay) {
                valueDisplay.textContent = slider.value;
            }
        }

        slider.addEventListener('input', updateSliderAppearance);
        updateSliderAppearance(); // Gọi lần đầu để đặt giá trị ban đầu
    });


    // --- CÁC HÀM TIỆN ÍCH ---
    function handleRequest(url, data, loadingMessage, callback) {
        showLoading(loadingMessage);
        const activeTabPaneId = document.querySelector('.tab-pane.active').id;

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Lỗi không xác định từ server') });
            }
            return response.json();
        })
        .then(result => {
            if (result.error) {
                displayError(result.error);
            } else {
                callback(result, activeTabPaneId);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayError(error.message || 'Có lỗi xảy ra khi kết nối đến máy chủ.');
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
            title = '⚠️ Mức độ Lo âu / Căng thẳng: CAO';
            adviceHtml = `<p>Dựa trên các thông tin bạn cung cấp, hệ thống nhận thấy bạn đang có nhiều yếu tố rủi ro có thể ảnh hưởng đến sức khỏe tinh thần.</p>`;
        } else {
            className = 'result-box alert alert-success';
            title = '✅ Mức độ Lo âu / Căng thẳng: THẤP - TRUNG BÌNH';
            adviceHtml = `<p>Các chỉ số của bạn cho thấy một trạng thái tinh thần tương đối ổn định. Hãy tiếp tục duy trì nhé!</p>`;
        }

        if (result.advice && result.advice.length > 0) {
            adviceHtml += '<h6>🧾 Gợi ý để cải thiện:</h6><ul>';
            result.advice.forEach(item => { adviceHtml += `<li>${item}</li>`; });
            adviceHtml += '</ul>';
        }
        
        resultBox.className = className;
        resultTitle.innerHTML = title;
        resultContent.innerHTML = adviceHtml;

        // Lưu kết quả vào bộ nhớ đệm
        tabResults[tabId] = { className, title, content: resultContent.innerHTML };
    }

    function displayIndexResult(result, tabId) {
        const className = 'result-box alert alert-primary';
        const title = '📊 Kết quả Chỉ số';
        const content = `
            <p class="mb-2">Kết quả tính toán cho chỉ số:</p>
            <h5 class="text-primary">${result.index_name}</h5>
            <h2><span class="badge bg-primary">${result.score} / 5</span></h2>
             <hr class="my-3">
            
            <div>
                <strong>Diễn giải:</strong>
                <p class="fst-italic">${result.interpretation}</p>
            </div>
            <p class="mt-3 fst-italic">Lưu ý: Điểm càng cao cho thấy mức độ cảm nhận về chỉ số đó càng lớn.</p>
        `;

        resultBox.className = className;
        resultTitle.innerHTML = title;
        resultContent.innerHTML = content;
        
        // Lưu kết quả vào bộ nhớ đệm
        tabResults[tabId] = { 
            className: 'result-box alert alert-primary', 
            title: '📊 Kết quả Chỉ số', 
            content: content 
        };
    }
});