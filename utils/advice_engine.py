def generate_support_resources(user_input):
    """
    Phân tích dữ liệu thô của người dùng để cung cấp thông tin,
    gợi mở các hướng hành động và kết nối đến các nguồn lực hỗ trợ.
    KHÔNG đưa ra lời khuyên trực tiếp.

    Args:
        user_input (dict): Một dictionary chứa dữ liệu thô từ form.
    
    Returns:
        dict: Một dictionary chứa các thông điệp đã được phân loại.
    """
    # Khởi tạo các danh mục kết quả
    results = {
        "disclaimer": "Lưu ý: Kết quả và các gợi ý dưới đây chỉ mang tính chất tham khảo. Hệ thống này không phải là một công cụ chẩn đoán y khoa và không thể thay thế cho sự tư vấn từ các chuyên gia tâm lý hoặc bác sĩ.",
        "critical_alerts": [], # Cảnh báo khẩn cấp
        "observations": [],    # Các nhận định về trạng thái
        "suggestions": []      # Các gợi ý và nguồn lực
    }
    
    # --- Bước 1: Phân tích dữ liệu đầu vào ---
    try:
        academic_pressure = float(user_input.get('academic_pressure', 0))
        financial_stress = float(user_input.get('financial_stress', 0))
        work_study_hours = float(user_input.get('work/study_hours', 0))
        sleep_hours_map = {'Less than 5 hours': 4.5, '5-6 hours': 5.5, '7-8 hours': 7.5, 'More than 8 hours': 9.0}
        sleep_hours = sleep_hours_map.get(user_input.get('sleep_duration'), 7.5) # Mặc định 7.5 nếu giá trị không hợp lệ
        had_suicidal_thoughts = 1 if user_input.get('have_you_ever_had_suicidal_thoughts_?') == 'Yes' else 0

    except (ValueError, TypeError):
        # Trả về lỗi nếu dữ liệu không hợp lệ
        results["critical_alerts"].append("Dữ liệu đầu vào không hợp lệ, không thể xử lý.")
        return results

    total_stress_score = academic_pressure + financial_stress + work_study_hours

    # --- Bước 2: Tạo các thông điệp dựa trên quy tắc ---

    # 1. Cảnh báo khẩn cấp (quan trọng nhất)
    if had_suicidal_thoughts == 1:
        critical_message = (
            "Hệ thống ghi nhận bạn đã có những suy nghĩ tiêu cực. Đây là một dấu hiệu rất quan trọng cần được quan tâm. "
            "Việc trò chuyện với một người bạn tin tưởng hoặc chuyên gia có thể giúp ích rất nhiều. "
        )
        results["critical_alerts"].append(critical_message)

    # 2. Các nhận định về trạng thái
    if total_stress_score >= 12: # Ngưỡng căng thẳng cao
        observation_message = (
            "Các chỉ số cho thấy bạn đang trải qua một giai đoạn có mức độ căng thẳng và áp lực tổng thể ở ngưỡng cao. "
            "Đây là điều rất nhiều sinh viên gặp phải."
        )
        results["observations"].append(observation_message)

    if sleep_hours < 6:
        observation_message = (
            f"Thời gian ngủ ({sleep_hours} tiếng/đêm) của bạn đang ít hơn mức được khuyến nghị (7-9 tiếng). "
            "Giấc ngủ có ảnh hưởng trực tiếp đến khả năng điều tiết cảm xúc và đối phó với căng thẳng."
        )
        results["observations"].append(observation_message)

    # 3. Gợi ý các hướng hành động và nguồn lực
    suggestion_list = {
        "Thể chất": "Các hoạt động thể chất nhẹ nhàng như đi bộ, yoga, hoặc thiền định đã được chứng minh là giúp giảm căng thẳng hiệu quả.",
        "Kết nối xã hội": "Dành thời gian cho bạn bè, người thân hoặc tham gia các câu lạc bộ có thể giúp tạo ra một mạng lưới hỗ trợ tinh thần vững chắc.",
        "Quản lý thời gian": "Tìm hiểu các phương pháp quản lý thời gian như Pomodoro hoặc lập kế hoạch hàng tuần có thể giúp giảm cảm giác quá tải.",
        "Tìm hiểu chuyên sâu": "Bạn có thể đọc thêm các bài viết về sức khỏe tinh thần từ các nguồn uy tín như WHO hoặc UNICEF Việt Nam để hiểu hơn về trạng thái của mình."
    }
    
    # Chỉ thêm gợi ý nếu có nhận định về căng thẳng
    if results["observations"]:
        results["suggestions"].extend(suggestion_list.values())

    # Thông điệp mặc định nếu không có nhận định nào
    if not results["observations"] and not results["critical_alerts"]:
        results["observations"].append("🎉 Các chỉ số của bạn cho thấy một trạng thái tương đối cân bằng. Hãy tiếp tục duy trì những thói quen tốt để giữ gìn sức khỏe tinh thần của mình nhé!")
        
    return results