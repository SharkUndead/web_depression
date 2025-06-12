import pandas as pd
import numpy as np

# Các hàm ánh xạ được giữ nguyên
from .mapping_degree import degree_mapping
from .mapping_VN_IN import map_indian_city_to_vietnamese

def remove_outliers_iqr(df, cols):
    """
    Hàm loại bỏ các giá trị ngoại lệ trong các cột cho trước bằng phương pháp IQR.
    """
    df_out = df.copy()
    for col in cols:
        if col in df_out.columns:
            Q1 = df_out[col].quantile(0.25)
            Q3 = df_out[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_out = df_out[(df_out[col] >= lower_bound) & (df_out[col] <= upper_bound)]
    return df_out

def preprocess_user_data(df, label_encoders):
    """
    Quy trình tiền xử lý dữ liệu người dùng một cách hoàn chỉnh và an toàn.
    """
    df_processed = df.copy()

    # --- BƯỚC 1: LÀM SẠCH CƠ BẢN ---
    df_processed.columns = df_processed.columns.str.strip().str.lower().str.replace(' ', '_')
    cols_to_drop = ['id', 'work_pressure', 'job_satisfaction', 'profession']
    df_processed.drop(columns=[col for col in cols_to_drop if col in df_processed.columns], inplace=True, errors='ignore')

    # --- BƯỚC 2: CHUYỂN ĐỔI KIỂU DỮ LIỆU ---
    numeric_cols = [
        'age', 'work/study_hours', 'academic_pressure',
        'study_satisfaction', 'financial_stress', 'cgpa'
    ]
    for col in numeric_cols:
        if col in df_processed.columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')

    # --- BƯỚC 3: XỬ LÝ GIÁ TRỊ THIẾU (MISSING VALUES) ---
    for col in df_processed.columns:
        if df_processed[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df_processed[col]):
                df_processed[col].fillna(df_processed[col].median(), inplace=True)
            else:
                df_processed[col].fillna(df_processed[col].mode()[0], inplace=True)

    # --- BƯỚC 4: ÁNH XẠ (MAPPING) VÀ MÃ HÓA (ENCODING) ---
    if 'city' in df_processed.columns:
        df_processed['city'] = df_processed['city'].apply(map_indian_city_to_vietnamese)
    if 'degree' in df_processed.columns:
        df_processed['degree'] = df_processed['degree'].map(degree_mapping)

    binary_map = {
        'gender': {'Male': 1, 'Female': 0},
        'have_you_ever_had_suicidal_thoughts_?': {'Yes': 1, 'No': 0},
        'family_history_of_mental_illness': {'Yes': 1, 'No': 0}
    }
    for col, mapping in binary_map.items():
        if col in df_processed.columns:
            df_processed[col] = df_processed[col].astype(str).str.strip().str.capitalize().map(mapping)
            
    for col_name, le in label_encoders.items():
        if col_name in df_processed.columns:
            known_values = list(le.classes_)
            # Chuyển các giá trị lạ thành NaN
            df_processed[col_name] = df_processed[col_name].apply(lambda x: x if x in known_values else np.nan)
            
            # <<<<<<<<<<<<<<<< SỬA LỖI KEYERROR: 0 Ở ĐÂY >>>>>>>>>>>>>>>>
            if df_processed[col_name].isnull().any():
                # Tính mode trước
                mode_series = df_processed[col_name].mode()
                # Chỉ fillna nếu mode tồn tại (không rỗng)
                if not mode_series.empty:
                    df_processed[col_name].fillna(mode_series[0], inplace=True)
                # Nếu mode rỗng (tức cả cột là NaN), ta có thể bỏ qua hoặc xử lý khác
                # Trong trường hợp này, ta sẽ điền một giá trị mặc định nào đó mà encoder biết, ví dụ giá trị đầu tiên
                else:
                    df_processed[col_name].fillna(known_values[0], inplace=True)
            
            # Bây giờ mới thực hiện transform
            df_processed[col_name] = le.transform(df_processed[col_name])

    # --- BƯỚC 5: XỬ LÝ NGOẠI LỆ (OUTLIERS) ---
    df_processed = remove_outliers_iqr(df_processed, numeric_cols)
    if df_processed.empty:
        return df_processed

    # --- BƯỚC 6: TẠO ĐẶC TRƯNG MỚI (FEATURE ENGINEERING) ---
    df_processed['balanced_life_score'] = (df_processed['sleep_duration'] + df_processed['study_satisfaction'] - df_processed['work/study_hours']) / 3
    df_processed['total_stress'] = df_processed['academic_pressure'] + df_processed['financial_stress'] + df_processed['work/study_hours']
    df_processed['sleep_stress_ratio'] = df_processed['sleep_duration'] / (df_processed['total_stress'] + 1)
    df_processed['multidimensional_stress'] = df_processed['academic_pressure'] * 0.5 + df_processed['financial_stress'] * 0.3 + df_processed['work/study_hours'] * 0.2
    df_processed['resilience_index'] = (df_processed['cgpa'] + df_processed['study_satisfaction']) / (1 + df_processed['family_history_of_mental_illness'])
    df_processed['suicidal_risk_index'] = df_processed['academic_pressure'] * 1.5 + (10 - df_processed['sleep_duration']) + 3 * df_processed['have_you_ever_had_suicidal_thoughts_?']

    return df_processed