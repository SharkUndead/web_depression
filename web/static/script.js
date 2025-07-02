document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN ---
    const predictForm = document.getElementById('predict-form');
    const indexForms = document.querySelectorAll('.index-form');
    const resultBox = document.getElementById('result-box');
    const resultTitle = document.getElementById('result-title');
    const resultContent = document.getElementById('result-content');
    const tabTriggers = document.querySelectorAll('#mainTab button[data-bs-toggle="tab"]');
    const tabResults = {};

    // --- LOGIC KIỂM TRA LỖI (VALIDATION) ---

    /**
     * Hàm này kiểm tra một trường (field) duy nhất và trả về true/false.
     * Nó cũng sẽ cập nhật giao diện (thêm/xóa class lỗi).
     * @param {HTMLElement} field - Phần tử input/select cần kiểm tra.
     * @returns {boolean} - True nếu hợp lệ, false nếu không.
     */
    function validateField(field) {
        let isValid = true;
        const group = field.closest('.radio-group');

        // Reset trạng thái lỗi trước
        field.classList.remove('is-invalid');
        if (group) {
            group.classList.remove('is-invalid');
        }

        // Bắt đầu kiểm tra
        if (field.id === 'age_input') {
            const ageFeedback = document.getElementById('age-feedback');
            if (field.value.trim() === '') {
                isValid = false;
                ageFeedback.textContent = 'Vui lòng nhập tuổi của bạn.';
            } else {
                const age = parseInt(field.value, 10);
                if (!(age >= 18 && age <= 24)) {
                    isValid = false;
                    ageFeedback.textContent = 'Hệ thống chỉ hỗ trợ độ tuổi từ 18 đến 24.';
                }
            }
        } else if (field.type === 'radio') {
            if (group && !group.querySelector('input[type="radio"]:checked')) {
                isValid = false;
            }
        } else { // Các trường input text, number, select khác
            if (!field.value.trim()) {
                isValid = false;
            }
        }

        // Cập nhật giao diện dựa trên kết quả kiểm tra
        if (!isValid) {
            if (field.type === 'radio' && group) {
                group.classList.add('is-invalid');
            } else {
                field.classList.add('is-invalid');
            }
        }
        return isValid;
    }

    /**
     * Hàm này kiểm tra TOÀN BỘ form bằng cách gọi validateField cho từng trường.
     * Được sử dụng khi người dùng nhấn nút "Dự đoán".
     * @returns {boolean} - True nếu toàn bộ form hợp lệ.
     */
    function validatePredictForm() {
        let isFormValid = true;
        predictForm.querySelectorAll('[required]').forEach(field => {
            if (!validateField(field)) {
                isFormValid = false;
            }
        });
        return isFormValid;
    }

    // --- GÁN SỰ KIỆN ---

    if (predictForm) {
        // 1. Gán sự kiện SUBMIT: Kiểm tra toàn bộ form
        predictForm.addEventListener('submit', function(event) {
            event.preventDefault();
            if (validatePredictForm()) {
                const data = Object.fromEntries(new FormData(predictForm).entries());
                handleRequest('/predict', data, 'Hệ thông đang phân tích, vui lòng chờ...', displayPredictionResult);
            } else {
                console.log('Thông tin không hợp lệ. Vui lòng kiểm tra lại.');
            }
        });

        // 2. Gán sự kiện BLUR: Kiểm tra tức thì để nâng cao trải nghiệm người dùng
        predictForm.querySelectorAll('[required]').forEach(field => {
            field.addEventListener('blur', function() {
                validateField(this);
            });
        });
    }

    function hideResultBox() {
        if (resultBox) {
            resultBox.style.display = 'none';
            resultTitle.innerText = '';
            resultContent.innerHTML = '';
        }
    }

    tabTriggers.forEach(triggerEl => {
        triggerEl.addEventListener('shown.bs.tab', function(event) {
            const newTabId = event.target.getAttribute('data-bs-target').substring(1);
            const storedResult = tabResults[newTabId];
            if (storedResult) {
                resultBox.style.display = 'block';
                resultBox.className = storedResult.className;
                resultTitle.innerHTML = storedResult.title;
                resultContent.innerHTML = storedResult.content;
            } else {
                hideResultBox();
            }
        });
    });

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

    const sliders = document.querySelectorAll('.slider-input');
    sliders.forEach(slider => {
        const valueDisplay = slider.nextElementSibling;
        function updateSliderAppearance() {
            if (valueDisplay) { valueDisplay.textContent = slider.value; }
        }
        slider.addEventListener('input', updateSliderAppearance);
        updateSliderAppearance();
    });

    // --- CÁC HÀM TIỆN ÍCH (Gửi request, hiển thị kết quả) ---
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
            if (result.error) { displayError(result.error); } 
            else { callback(result, activeTabPaneId); }
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
        let className, title, content = '';
        if (result.support_info && result.support_info.disclaimer) {
            content += `<p class="fst-italic small text-secondary">${result.support_info.disclaimer}</p><hr>`;
        }
        if (result.prediction === 1) {
            className = 'result-box alert alert-danger';
            title = '⚠️ Mức độ Lo âu / Căng thẳng: CAO';
        } else {
            className = 'result-box alert alert-success';
            title = '✅ Mức độ Lo âu / Căng thẳng: THẤP - TRUNG BÌNH';
        }
        if (result.support_info) {
            if (result.support_info.critical_alerts && result.support_info.critical_alerts.length > 0) {
                content += `<h6>❗ Cảnh báo Quan trọng:</h6><p>${result.support_info.critical_alerts.join('<br>')}</p>`;
            }
            if (result.support_info.observations && result.support_info.observations.length > 0) {
                content += '<h6>💡 Nhận định từ hệ thống:</h6><ul>';
                result.support_info.observations.forEach(item => { content += `<li>${item}</li>`; });
                content += '</ul>';
            }
            if (result.support_info.resource_categories && result.support_info.resource_categories.length > 0) {
                content += '<h6>🧾 Gợi ý và Nguồn lực:</h6>';
                result.support_info.resource_categories.forEach(cat => { content += `<p><strong>- ${cat.title}:</strong> ${cat.content}</p>`; });
            }
        }
        resultBox.className = className;
        resultTitle.innerHTML = title;
        resultContent.innerHTML = content;
        tabResults[tabId] = { className, title, content };
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
            <p class="mt-3 fst-italic small">Lưu ý: Điểm càng cao cho thấy mức độ cảm nhận về chỉ số đó càng lớn.</p>
        `;
        resultBox.className = className;
        resultTitle.innerHTML = title;
        resultContent.innerHTML = content;
        tabResults[tabId] = { className, title, content };
    }
});