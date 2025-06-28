import sys
import os
import pandas as pd
import joblib
import math
from flask import Flask, render_template, request, jsonify

# ================== SỬA LỖI ĐƯỜNG DẪN ==================
# Thêm thư mục gốc của dự án vào sys.path để có thể tìm thấy 'utils'
# Điều này giúp file app.py có thể chạy được dù bạn đang ở đâu
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.preprocessing import preprocess_user_data
from utils.advice_engine import generate_advice_from_features
from utils.localization import FIELD_LABELS, GENDER_OPTIONS, YES_NO_OPTIONS
# =======================================================

# Khởi tạo ứng dụng Flask với đường dẫn được chỉ định rõ ràng
app = Flask(__name__, template_folder='templates', static_folder='static')


# --- Tải mô hình và các tài nguyên một lần khi ứng dụng khởi động ---
try:
    BASE_DIR = project_root
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'lgbm_model.pkl')
    ENCODER_PATH = os.path.join(BASE_DIR, 'models', 'label_encoders.pkl')
    FEATURE_ORDER_PATH = os.path.join(BASE_DIR, 'models', 'feature_order_lightgbm.pkl')

    model = joblib.load(MODEL_PATH)
    label_encoders = joblib.load(ENCODER_PATH)
    feature_order = joblib.load(FEATURE_ORDER_PATH)
    print("✅  Tải mô hình và tài nguyên thành công!")
except Exception as e:
    print(f"❌ Lỗi khi tải mô hình: {e}")
    model = None

# --- ĐỊNH NGHĨA CÁC BIẾN DỮ LIỆU TĨNH ---
FIELD_PLACEHOLDERS = {
    'age': 'Ví dụ: 21', 'work/study_hours': 'Ví dụ: 8', 'academic_pressure': 'Thang điểm từ 1-5',
    'study_satisfaction': 'Thang điểm từ 1-5', 'financial_stress': 'Thang điểm từ 1-5', 'cgpa': 'Ví dụ: 8.5'
}

INDEX_QUESTIONS = {
    "pressure": {
        "title": "Áp lực học tập",
        "description": "Với mỗi phát biểu dưới đây, hãy kéo thanh trượt để thể hiện mức độ bạn cảm nhận về nó trong 1 tháng qua (1: Hoàn toàn không đúng, 100: Hoàn toàn đúng).",
        "questions": [
            "Tôi cảm thấy khối lượng bài tập, bài đọc và các dự án là quá sức đối với tôi.",
            "Tôi thường xuyên có cảm giác không bao giờ có đủ thời gian để hoàn thành tất cả các yêu cầu của việc học.",
            "Tôi cảm thấy một áp lực rất lớn phải đạt được điểm số cao trong các kỳ thi và bài kiểm tra.",
            "Môi trường học tập có tính cạnh tranh cao và điều đó khiến tôi cảm thấy căng thẳng.",
            "Tôi tự đặt ra cho mình những kỳ vọng rất cao về thành tích học tập, và cảm thấy áp lực phải đạt được chúng."
        ]
    },
    "satisfaction": {
        "title": "Mức độ hài lòng với việc học",
        "description": "Với mỗi phát biểu dưới đây, hãy kéo thanh trượt để thể hiện mức độ bạn đồng ý (1: Hoàn toàn không đồng ý, 100: Hoàn toàn đồng ý).",
        "questions": [
            "Các môn học tôi đang theo học thật sự thử thách cách suy nghĩ của tôi và khiến tôi cảm thấy hứng thú.",
            "Tôi cảm thấy mình có thể trao đổi và nhận được sự hỗ trợ cần thiết từ giảng viên.",
            "Tôi có những mối quan hệ bạn bè tích cực và mang tính hỗ trợ trong môi trường học tập.",
            "Tôi nhận thấy những gì mình đang học có sự liên quan và hữu ích cho các mục tiêu tương lai của tôi.",
            "Nhìn chung, tôi cảm thấy hài lòng với lựa chọn ngành học và trải nghiệm của mình tại trường."
        ]
    },
    "financial_pressure": {
        "title": "Áp lực tài chính",
        "description": "Với mỗi phát biểu dưới đây, hãy kéo thanh trượt để thể hiện mức độ bạn cảm nhận về tài chính cá nhân (1: Hoàn toàn không đúng, 100: Hoàn toàn đúng).",
        "questions": [
            "Việc chi trả cho các nhu cầu cơ bản hàng tháng (như nhà ở, ăn uống, đi lại) là một gánh nặng tài chính đối với tôi.",
            "Tôi thường xuyên cảm thấy căng thẳng về các khoản nợ hoặc các nghĩa vụ tài chính mà tôi đang có.",
            "Tôi không cảm thấy an toàn về tình hình tài chính của mình.",
            "Các vấn đề về tiền bạc thường gây ra căng thẳng hoặc xung đột trong cuộc sống của tôi.",
            "Tôi lo lắng rằng tình hình tài chính hiện tại sẽ ảnh hưởng tiêu cực đến các kế hoạch trong tương lai của tôi."
        ]
    }
}

def convert_score_by_thresholds(raw_score):
    if 5 <= raw_score <= 100: return 1
    elif 101 <= raw_score <= 200: return 2
    elif 201 <= raw_score <= 350: return 3
    elif 351 <= raw_score <= 450: return 4
    elif 451 <= raw_score <= 500: return 5
    return 0

@app.route('/')
def home():
    form_options = {col: le.classes_.tolist() for col, le in label_encoders.items()}
    return render_template(
        'index.html', form_options=form_options, field_labels=FIELD_LABELS, 
        gender_options=GENDER_OPTIONS, yes_no_options=YES_NO_OPTIONS,
        index_questions_data=INDEX_QUESTIONS, field_placeholders=FIELD_PLACEHOLDERS
    )

@app.route('/predict', methods=['POST'])
def predict():
    if not model: return jsonify({'error': 'Mô hình chưa được tải.'}), 500
    try:
        user_input = request.json
        df_raw = pd.DataFrame([user_input])
        df_processed = preprocess_user_data(df_raw.copy(), label_encoders)
        if df_processed.empty: return jsonify({'error': 'Dữ liệu không hợp lệ.'})
        advice = generate_advice_from_features(df_processed.iloc[0])
        df_final = df_processed[feature_order]
        prediction = model.predict(df_final)[0]
        result = {'prediction': int(prediction), 'advice': advice}
        return jsonify(result)
    except Exception as e: return jsonify({'error': str(e)}), 400

@app.route('/calculate_index', methods=['POST'])
def calculate_index():
    try:
        data = request.json
        category = data.get('category')
        if not category: return jsonify({'error': 'Không rõ loại chỉ số cần tính.'}), 400
        raw_score = sum(int(v) for k, v in data.items() if k.startswith(category))
        final_score = convert_score_by_thresholds(raw_score)
        result = { 'index_name': INDEX_QUESTIONS[category]['title'], 'score': final_score }
        return jsonify(result)
    except Exception as e: return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)