import os
import pandas as pd
import joblib
from utils.preprocessing import preprocess_user_data

def predict_from_file(path, output_filename, model_path, encoder_path, feature_order_path, base_dir):
    """
    Dự đoán trầm cảm từ file CSV người dùng.
    - path: Đường dẫn file người dùng.
    - output_filename: Tên file xuất kết quả (.csv).
    - model_path: Đường dẫn file mô hình.
    - encoder_path: Đường dẫn file encoders.
    - feature_order_path: Đường dẫn file feature_order.pkl.
    - base_dir: Thư mục gốc của dự án.
    """
    if not os.path.exists(path):
        return "❌ File không tồn tại"

    try:
        model = joblib.load(model_path)
        label_encoders = joblib.load(encoder_path)
        feature_order = joblib.load(feature_order_path)

        df_raw = pd.read_csv(path)
        df_processed = preprocess_user_data(df_raw, label_encoders)
        df_processed = df_processed[feature_order]
        preds = model.predict(df_processed)
        df_raw['prediction'] = preds

        result_path = os.path.join(base_dir, 'data', 'predict', output_filename)
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        df_raw.to_csv(result_path, index=False)

        return f"✅ Đã lưu kết quả tại: {result_path}"
    except Exception as e:
        return f"❌ Lỗi: {e}"
