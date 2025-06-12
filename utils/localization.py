# utils/localization.py

# Từ điển ánh xạ tên trường (key) sang nhãn hiển thị Tiếng Việt
FIELD_LABELS = {
    'age': 'Tuổi của bạn',
    'city': 'Thành phố bạn đang sống',
    'degree': 'Bằng cấp/Trình độ học vấn',
    'sleep_duration': 'Thời gian ngủ trung bình mỗi đêm',
    'dietary_habits': 'Thói quen ăn uống',
    'work/study_hours': 'Số giờ học/làm việc mỗi ngày',
    'academic_pressure': 'Mức độ áp lực học tập',
    'study_satisfaction': 'Mức độ hài lòng với việc học',
    'financial_stress': 'Mức độ áp lực về tài chính',
    'cgpa': 'Điểm trung bình tích lũy (GPA)',
    'gender': 'Giới tính',

    # --- CÂU HỎI ĐÃ ĐƯỢC SỬA LẠI ĐỂ CÓ TÂM HƠN ---
    'have_you_ever_had_suicidal_thoughts_?': 'Bạn có từng có ý nghĩ tự tử không?',
    'family_history_of_mental_illness': 'Gia đình bạn có tiền sử bệnh tâm lý không?'    
}

# Lựa chọn cho các câu hỏi Có/Không
# (Hiển thị Tiếng Việt, giá trị gửi đi là Tiếng Anh để không ảnh hưởng đến logic xử lý)
YES_NO_OPTIONS = [
    ("Có", "Yes"),
    ("Không", "No")
]

# Lựa chọn cho giới tính
GENDER_OPTIONS = [
    ("Nam", "Male"),
    ("Nữ", "Female")
]