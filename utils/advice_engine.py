def generate_advice_from_features(row):
    advice = []

    print("🔍 Dữ liệu nhận vào advice_engine:", row.to_dict())

    sleep_map = {
        'Less than 5 hours': 4.5,
        '5-6 hours': 5.5,
        '7-8 hours': 7.5,
        'More than 8 hours': 9.0
    }

    # Lấy sleep_duration từ dữ liệu (bắt buộc có)
    sleep_raw = row.get('sleep_duration')
    if sleep_raw is None:
        advice.append("⚠️ Không có thông tin sleep_duration. Không thể đánh giá giấc ngủ.")
        sleep_hours = None
    elif isinstance(sleep_raw, str):
        sleep_hours = sleep_map.get(sleep_raw)
        if sleep_hours is None:
            advice.append(f"⚠️ Giá trị sleep_duration '{sleep_raw}' không hợp lệ.")
    else:
        sleep_hours = float(sleep_raw)

    suicidal_risk = row.get('suicidal_risk_index', 0)
    total_stress = row.get('total_stress', 0)
    resilience = row.get('resilience_index', 3)

    if suicidal_risk >= 20:
        advice.append("⚠️ Nguy cơ trầm cảm rất cao! Hãy tìm gặp chuyên gia tâm lý hoặc liên hệ người thân ngay.")
    elif suicidal_risk >= 15:
        advice.append("⚠️ Nguy cơ trầm cảm cao. Cần chú ý và hỗ trợ kịp thời.")

    # Chỉ đánh giá sleep nếu sleep_hours đã xác định
    if sleep_hours is not None:
        if sleep_hours < 6 and total_stress >= 15:
            advice.append("Bạn đang thiếu ngủ và chịu căng thẳng cao. Hãy nghỉ ngơi, tập thể dục nhẹ nhàng, thiền.")
        elif sleep_hours < 6:
            advice.append("Cố gắng ngủ ít nhất 7-9 tiếng mỗi ngày để cải thiện sức khỏe tâm thần.") 
        elif sleep_hours > 9:
            advice.append("Ngủ quá nhiều cũng không tốt, hãy duy trì 7-9 tiếng/đêm.")

    if total_stress >= 20:
        advice.append("Tổng stress của bạn đang rất cao. Hãy giảm áp lực học tập/công việc, tìm kiếm sự hỗ trợ.")
    elif total_stress >= 15:
        advice.append("Bạn đang có dấu hiệu căng thẳng. Hãy sắp xếp thời gian hợp lý và thư giãn.")

    if resilience < 2:
        advice.append("Tăng cường sức khỏe tinh thần bằng thể dục, thiền, yoga hoặc gặp chuyên gia.")

    if not advice:
        advice.append("🎉 Bạn đang duy trì thói quen khá tốt. Hãy tiếp tục giữ gìn sức khỏe và tinh thần nhé!")

    return advice
