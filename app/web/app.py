from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os
import sys
import math

# Thêm đường dẫn gốc của dự án vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.preprocessing import preprocess_user_data
from utils.advice_engine import generate_advice_from_features
from utils.localization import FIELD_LABELS, GENDER_OPTIONS, YES_NO_OPTIONS

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# --- Tải mô hình và các tài nguyên một lần khi ứng dụng khởi động ---
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

# <<<<<<<<<<<<<<<< THÊM TỪ ĐIỂN NÀY VÀO >>>>>>>>>>>>>>>>
FIELD_PLACEHOLDERS = {
    'age': 'Ví dụ: 21',
    'work/study_hours': 'Ví dụ: 8',
    'academic_pressure': 'Thang điểm từ 1-5',
    'study_satisfaction': 'Thang điểm từ 1-5',
    'financial_stress': 'Thang điểm từ 1-5',
    'cgpa': 'Ví dụ: 8.5'
}

INDEX_QUESTIONS = {
    "pressure": {
        "title": "Áp lực học tập/công việc",
        "description": "Hãy chọn mức độ phù hợp nhất với cảm nhận của bạn về áp lực học tập/công việc trong khoảng thời gian gần đây.",
        "questions": [
            "Trong tháng vừa qua, bạn có thường cảm thấy gánh nặng từ khối lượng công việc/học tập quá lớn không?",
            "Bạn có thường cảm thấy không đủ thời gian để hoàn thành các nhiệm vụ học tập/công việc một cách hiệu quả không?",
            "Mức độ lo lắng hoặc căng thẳng của bạn về kết quả học tập/hiệu suất công việc là bao nhiêu?",
            "Bạn có thường xuyên cảm thấy kiệt sức, mệt mỏi về tinh thần hoặc thể chất do việc học/công việc không?",
            "Việc học/công việc có thường xuyên ảnh hưởng tiêu cực đến giấc ngủ, bữa ăn hoặc thời gian thư giãn của bạn không?"
        ],
        "options": [(1, "Không bao giờ / Không đáng kể"), (2, "Hiếm khi / Thấp"), (3, "Thỉnh thoảng / Trung bình"), (4, "Thường xuyên / Cao"), (5, "Rất thường xuyên / Rất cao")]
    },
    "satisfaction": {
        "title": "Mức độ hài lòng với việc học",
        "description": "Hãy chọn mức độ phù hợp nhất với cảm nhận của bạn về việc học tập hiện tại.",
        "questions": [
            "Tôi cảm thấy hứng thú và được truyền cảm hứng bởi các môn học/nội dung học tập hiện tại của mình.",
            "Tôi tin rằng việc học của mình đang mang lại giá trị và trang bị tốt cho tương lai nghề nghiệp/cuộc sống của tôi.",
            "Tôi cảm thấy mình đang tiến bộ và đạt được các mục tiêu học tập đã đề ra.",
            "Tôi hài lòng với môi trường học tập (giảng viên, bạn bè, cơ sở vật chất, hỗ trợ) mà tôi đang có.",
            "Tổng thể, tôi cảm thấy hài lòng với trải nghiệm học tập của mình."
        ],
        "options": [(1, "Hoàn toàn không đồng ý / Rất không hài lòng"), (2, "Không đồng ý / Không hài lòng"), (3, "Bình thường / Trung lập"), (4, "Đồng ý / Hài lòng"), (5, "Hoàn toàn đồng ý / Rất hài lòng")]
    },
    "financial_pressure": {
        "title": "Áp lực tài chính",
        "description": "Hãy chọn mức độ phù hợp nhất với cảm nhận của bạn về tình hình tài chính cá nhân.",
        "questions": [
            "Trong tháng vừa qua, bạn có thường xuyên lo lắng về việc không đủ tiền chi trả các chi phí sinh hoạt cơ bản không?",
            "Bạn có cảm thấy căng thẳng khi nghĩ đến các khoản nợ hoặc các nghĩa vụ tài chính khác của mình không?",
            "Bạn có lo lắng về khả năng đối phó với một chi phí bất ngờ mà không có đủ tiền dự phòng không?",
            "Tình hình tài chính hiện tại có thường xuyên ảnh hưởng tiêu cực đến giấc ngủ, tâm trạng hoặc các mối quan hệ của bạn không?",
            "Tổng thể, bạn cảm thấy áp lực hoặc bất an về tình hình tài chính cá nhân của mình ở mức độ nào?"
        ],
        "options": [(1, "Không bao giờ / Không đáng kể"), (2, "Hiếm khi / Thấp"), (3, "Thỉnh thoảng / Trung bình"), (4, "Thường xuyên / Cao"), (5, "Rất thường xuyên / Rất cao")]
    }
}


@app.route('/')
def home():
    """Hiển thị trang chủ với đầy đủ dữ liệu cho các form."""
    form_options = {col: le.classes_.tolist() for col, le in label_encoders.items()}
    return render_template(
        'index.html', 
        form_options=form_options, 
        field_labels=FIELD_LABELS, 
        gender_options=GENDER_OPTIONS, 
        yes_no_options=YES_NO_OPTIONS,
        index_questions_data=INDEX_QUESTIONS,
        # <<<<<<<<<<<<<<<< TRUYỀN BIẾN CÒN THIẾU Ở ĐÂY >>>>>>>>>>>>>>>>
        field_placeholders=FIELD_PLACEHOLDERS
    )

@app.route('/predict', methods=['POST'])
def predict():
    # (Hàm này giữ nguyên không đổi)
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
    # (Hàm này giữ nguyên không đổi)
    try:
        data = request.json
        category = data.get('category')
        if not category: return jsonify({'error': 'Không rõ loại chỉ số cần tính.'}), 400
        raw_score = sum(int(v) for k, v in data.items() if k.startswith(category))
        scaled_score = (raw_score - 5) / 4.0
        final_score = round(scaled_score)
        result = {
            'index_name': INDEX_QUESTIONS[category]['title'],
            'score': final_score
        }
        return jsonify(result)
    except Exception as e: return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)