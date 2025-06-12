import pandas as pd
import joblib
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocessing import preprocess_user_data

# ==== Đường dẫn ====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'interim', 'user_uploaded.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'predict', 'predicted_results.csv')

# ==== Load mô hình và encoders ====
model = joblib.load(os.path.join(BASE_DIR, 'models', 'rf_model.pkl'))
label_encoders = joblib.load(os.path.join(BASE_DIR, 'models', 'label_encoders.pkl'))
feature_order = joblib.load(os.path.join(BASE_DIR, 'models', 'feature_order.pkl'))

# ==== Đọc dữ liệu người dùng ====
df_raw = pd.read_csv(INPUT_FILE)

# ==== Tiền xử lý dữ liệu ====
df_processed = preprocess_user_data(df_raw, label_encoders)

# ==== Đảm bảo đúng thứ tự cột ====
df_processed = df_processed[feature_order]

# ==== Dự đoán ====
preds = model.predict(df_processed)
df_raw['prediction'] = preds

# ==== Lưu kết quả ====
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
df_raw.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Đã dự đoán thành công! Kết quả được lưu tại: {OUTPUT_FILE}")